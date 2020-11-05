"""
AST-related functionality
"""
import argparse
import ast
import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel
from pygit2 import Repository

from . import git


class RawDefinition(BaseModel):
    name: str
    change_type: str
    line: int
    offset: int
    end_line: Optional[int] = None
    end_offset: Optional[int] = None
    parent: Optional[Tuple[str, int]] = None


class LocustChange(BaseModel):
    name: str
    change_type: str
    filepath: str
    revision: Optional[str]
    line: int
    changed_lines: int
    total_lines: Optional[int] = None
    parent: Optional[Tuple[str, int]] = None


class LocustVisitor(ast.NodeVisitor):
    FUNCTION_DEF = "function"
    ASYNC_FUNCTION_DEF = "async_function"
    CLASS_DEF = "class"

    def __init__(self):
        self.scope: List[Tuple[str, int, Optional[int]]] = []
        self.definitions: List[RawDefinition] = []

    def _visit_class_or_function_def(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef],
        def_type: str,
    ) -> None:
        self.scope = [
            spec for spec in self.scope if spec[2] is not None and spec[2] > node.lineno
        ]
        self.scope.append((node.name, node.lineno, node.end_lineno))
        parent: Optional[Tuple[str, int]] = None
        if len(self.scope) > 1:
            parent = (
                ".".join([spec[0] for spec in self.scope[:-1]]),
                self.scope[-2][1],
            )
        self.definitions.append(
            RawDefinition(
                name=".".join([spec[0] for spec in self.scope]),
                change_type=def_type,
                line=node.lineno,
                offset=node.col_offset,
                end_line=node.end_lineno,
                end_offset=node.end_col_offset,
                parent=parent,
            )
        )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_class_or_function_def(node, self.FUNCTION_DEF)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_class_or_function_def(node, self.ASYNC_FUNCTION_DEF)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._visit_class_or_function_def(node, self.CLASS_DEF)

    def reset(self):
        self.scope = []
        self.definitions = []

    def patch_definitions(self, patch: git.PatchInfo) -> List[RawDefinition]:
        self.reset()
        _, extension = os.path.splitext(patch.new_file)
        if extension != ".py" or patch.new_source is None:
            return []
        root = ast.parse(patch.new_source)
        self.visit(root)
        return self.definitions


class RunResponse(BaseModel):
    repo: str
    initial_ref: str
    terminal_ref: Optional[str]
    patches: List[git.PatchInfo]
    changes: List[LocustChange]


def definitions_by_patch(
    git_result: git.RunResponse,
) -> List[Tuple[git.PatchInfo, List[RawDefinition]]]:
    results: List[Tuple[git.PatchInfo, List[RawDefinition]]] = []
    for patch in git_result.patches:
        visitor = LocustVisitor()
        try:
            definitions = visitor.patch_definitions(patch)
            results.append((patch, definitions))
        except:
            pass
    return results


def locust_changes_in_patch(
    patch: git.PatchInfo, definitions: List[RawDefinition], terminal_ref: Optional[str]
) -> Tuple[git.PatchInfo, List[LocustChange]]:
    pass
    insertions_boundaries: List[Tuple[int, int]] = []
    for hunk in patch.hunks:
        if hunk.insertions_boundary is not None:
            insertions_boundaries.append(
                (hunk.insertions_boundary.start, hunk.insertions_boundary.end)
            )
    insertions_boundaries.sort(key=lambda p: p[0])

    locust_changes: List[LocustChange] = []
    for definition in definitions:
        possible_boundaries = [
            boundary
            for boundary in insertions_boundaries
            if definition.end_line is None or boundary[0] <= definition.end_line
        ]
        if not possible_boundaries:
            continue

        total_lines: Optional[int] = None
        if definition.end_line is not None:
            total_lines = definition.end_line - definition.line + 1

        candidate_insertion = max(
            possible_boundaries,
            key=lambda p: p[0],
        )

        if candidate_insertion[1] >= definition.line:
            changed_lines = 0
            for start, end in possible_boundaries:
                if (end >= definition.line) and (
                    definition.end_line is None or start <= definition.end_line
                ):
                    end_line = end
                    if definition.end_line is not None and definition.end_line < end:
                        end_line = definition.end_line

                    changed_lines += end_line - max(start, definition.line) + 1

            locust_changes.append(
                LocustChange(
                    name=definition.name,
                    change_type=definition.change_type,
                    filepath=patch.new_file,
                    revision=terminal_ref,
                    line=definition.line,
                    changed_lines=changed_lines,
                    total_lines=total_lines,
                    parent=definition.parent,
                )
            )

    return (patch, locust_changes)


def calculate_changes(
    git_result: git.RunResponse,
    patch_definitions: List[Tuple[git.PatchInfo, List[RawDefinition]]],
) -> List[LocustChange]:
    changes: List[LocustChange] = []
    for patch, definitions in patch_definitions:
        _, patch_changes = locust_changes_in_patch(
            patch, definitions, git_result.terminal_ref
        )
        changes.extend(patch_changes)
    return changes


def calculate_python_changes(git_result: git.RunResponse) -> List[LocustChange]:
    patch_definitions = definitions_by_patch(git_result)
    return calculate_changes(git_result, patch_definitions)


def calculate_changes_from_file(
    git_result: git.RunResponse, patch_definitions_json: str
) -> List[LocustChange]:
    with open(patch_definitions_json, "r") as ifp:
        patch_definitions_raw = json.load(ifp)
    patch_definitions = [
        (
            git.PatchInfo.parse_obj(item[0]),
            [RawDefinition.parse_obj(definition_obj) for definition_obj in item[1]],
        )
        for item in patch_definitions_raw
    ]
    return calculate_changes(git_result, patch_definitions)


def calculate_plugin_changes(
    plugins: List[str], git_result: git.RunResponse
) -> Dict[str, List[LocustChange]]:
    """
    Accepts a list of plugins (which can be invoked using subprocess.run and accept -i and -o
    parameters) and a git.RunResponse object.

    Returns a dictionary whose keys are the plugins and whose values are tuples of the form:
    (locust changes, errors)
    """
    results: Dict[str, List[LocustChange]] = {}
    if not plugins:
        return results
    fd, git_result_filename = tempfile.mkstemp()
    os.close(fd)
    with open(git_result_filename, "w") as ofp:
        json.dump(git_result.dict(), ofp)

    outfiles: Dict[str, str] = {}
    for plugin in plugins:
        fd, outfiles[plugin] = tempfile.mkstemp()
        os.close(fd)

    for plugin, outfile in outfiles.items():
        results[plugin] = []
        run_string = f"{plugin} -i {git_result_filename} -o {outfile}"
        try:
            subprocess.run(run_string, check=True, shell=True)
            changes = calculate_changes_from_file(git_result, outfile)
            results[plugin] = changes
        except Exception as e:
            print(
                f"Error getting results from plugin ({plugin}):\n{repr(e)}",
                file=sys.stderr,
            )
            pass

    return results


def run(git_result: git.RunResponse, plugins: List[str]) -> RunResponse:
    changes = calculate_python_changes(git_result)
    plugin_changes_dict = calculate_plugin_changes(plugins, git_result)
    for _, plugin_changes in plugin_changes_dict.items():
        changes.extend(plugin_changes)
    return RunResponse(
        repo=git_result.repo,
        initial_ref=git_result.initial_ref,
        terminal_ref=git_result.terminal_ref,
        patches=git_result.patches,
        changes=changes,
    )

def populate_argument_parser(parser: argparse.ArgumentParser) -> None:
    """
    Populates an argparse ArgumentParser object with the commonly used arguments for this module.

    Mutates the provided parser.
    """
    parser.add_argument(
        "-p",
        "--plugins",
        nargs="*",
        help="List of commands which invoke Locust plugins",
    )


def main():
    parser = argparse.ArgumentParser(description="Locust: Python parsing functionality")
    populate_argument_parser(parser)
    parser.add_argument(
        "-i",
        "--input",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Path to git result. If not specified, reads from stdin.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Path to write parse results to (in JSON format)",
    )

    args = parser.parse_args()

    with args.input as ifp:
        git_result_json = json.load(ifp)
        git_result = git.RunResponse.parse_obj(git_result_json)

    result = run(git_result, args.plugins)

    try:
        with args.output as ofp:
            print(result.json(), file=ofp)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
