"""
AST-related functionality
"""
import argparse
import ast
from dataclasses import dataclass, field
from enum import Enum
import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union

from google.protobuf.json_format import MessageToDict, Parse, ParseDict
from pydantic import BaseModel
from pygit2 import Repository

from . import git
from .parse_pb2 import RawDefinition, LocustChange, ParseResult, DefinitionParent


class LocustASTTraversalError(Exception):
    pass


class ContextType(Enum):
    UNKNOWN = "unknown"
    FUNCTION_DEF = "function"
    ASYNC_FUNCTION_DEF = "async_function"
    CLASS_DEF = "class"
    DEPENDENCY = "dependency"
    USAGE = "usage"


@dataclass
class Scope:
    name: str
    lineno: int
    end_lineno: Optional[int] = None
    # symbols is an association of symbols to possible qualifications. The values are lists because
    # it is possible that some symbols can only be correctly qualified at runtime (e.g. because of
    # conditional imports).
    symbols: Dict[str, List[str]] = field(default_factory=dict)


class LocustVisitor(ast.NodeVisitor):
    def __init__(self):
        self.scope: List[Scope] = []
        self.definitions: List[RawDefinition] = []
        self.context_type: ContextType = ContextType.UNKNOWN
        self.global_symbols: Dict[str, List[str]] = {}

    def _current_symbols(self) -> Dict[str, List[str]]:
        if self.scope:
            return self.scope[-1].symbols
        return self.global_symbols

    def _add_symbol_qualification(self, symbol: str, qualification: str) -> None:
        symbols = self.global_symbols
        if self.scope:
            symbols = self.scope[-1].symbols

        if symbols.get(symbol) is None:
            symbols[symbol] = []
        symbols[symbol].append(qualification)

    def _prune_scope(self, lineno: int) -> None:
        self.scope = [
            spec
            for spec in self.scope
            if spec.end_lineno is not None and spec.end_lineno > lineno
        ]

    def _current_scope_parent(self) -> Optional[DefinitionParent]:
        parent: Optional[DefinitionParent] = None
        if len(self.scope) > 1:
            parent = DefinitionParent(
                name=".".join([spec.name for spec in self.scope[:-1]]),
                line=self.scope[-2].lineno,
            )
        return parent

    def _visit_class_or_function_def(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef],
    ) -> None:
        self._prune_scope(node.lineno)
        self.scope.append(
            Scope(
                name=node.name,
                lineno=node.lineno,
                end_lineno=node.end_lineno,
                symbols=self._current_symbols(),
            )
        )
        parent = self._current_scope_parent()

        self.definitions.append(
            RawDefinition(
                name=".".join([spec.name for spec in self.scope]),
                change_type=self.context_type.value,
                line=node.lineno,
                offset=node.col_offset,
                end_line=node.end_lineno,
                end_offset=node.end_col_offset,
                parent=parent,
            )
        )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.context_type = ContextType.FUNCTION_DEF
        self._visit_class_or_function_def(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.context_type = ContextType.ASYNC_FUNCTION_DEF
        self._visit_class_or_function_def(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.context_type = ContextType.CLASS_DEF
        self._visit_class_or_function_def(node)

    def visit_Import(self, node: ast.Import) -> None:
        self.context_type = ContextType.DEPENDENCY
        self._prune_scope(node.lineno)
        parent = self._current_scope_parent()
        for alias in node.names:
            signifier = alias.asname if alias.asname is not None else alias.name
            self._add_symbol_qualification(signifier, alias.name)
            definition = RawDefinition(
                name=alias.name,
                change_type=self.context_type.value,
                line=node.lineno,
                offset=node.col_offset,
                end_line=node.end_lineno,
                end_offset=node.end_col_offset,
                parent=parent,
            )
            self.definitions.append(definition)

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.context_type = ContextType.DEPENDENCY
        self._prune_scope(node.lineno)
        parent = self._current_scope_parent()
        module_name = node.module
        dots = "" if not node.level else "." * node.level
        import_prefix = f"{dots}{module_name}"
        for alias in node.names:
            if alias.name == "*":
                continue
            signifier = alias.asname if alias.asname is not None else alias.name
            qualified_name = f"{import_prefix}.{alias.name}"
            self._add_symbol_qualification(signifier, qualified_name)
            definition = RawDefinition(
                name=qualified_name,
                change_type=self.context_type.value,
                line=node.lineno,
                offset=node.col_offset,
                end_line=node.end_lineno,
                end_offset=node.end_col_offset,
                parent=parent,
            )
            self.definitions.append(definition)

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        self.context_type = ContextType.USAGE
        symbols = self._current_symbols()
        qualifications = symbols.get(node.id)
        if qualifications:
            parent = self._current_scope_parent()
            for qualification in qualifications:
                definition = RawDefinition(
                    name=qualification,
                    change_type=self.context_type.value,
                    line=node.lineno,
                    offset=node.col_offset,
                    end_line=node.end_lineno,
                    end_offset=node.end_col_offset,
                    parent=parent,
                )
                self.definitions.append(definition)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.context_type = ContextType.USAGE
        # Components of the symbol, from right to left.
        components = [node.attr]
        current = node.value
        done = False
        while not done:
            if isinstance(current, ast.Name):
                components.append(current.id)
                done = True
            elif isinstance(current, ast.Attribute):
                components.append(current.attr)
                current = current.value
            else:
                raise LocustASTTraversalError(
                    f"Could not process attribute component: {current}"
                )
        components.reverse()
        cumulative_components = [
            ".".join(components[: i + 1]) for i in range(len(components))
        ]
        symbols = self._current_symbols()
        parent = self._current_scope_parent()
        for cumulative_component in cumulative_components:
            qualifications = symbols.get(cumulative_component)
            if qualifications:
                for qualification in qualifications:
                    definition = RawDefinition(
                        name=qualification,
                        change_type=self.context_type.value,
                        line=node.lineno,
                        offset=node.col_offset,
                        end_line=node.end_lineno,
                        end_offset=node.end_col_offset,
                        parent=parent,
                    )
                    self.definitions.append(definition)

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


def definitions_by_patch(
    git_result: git.GitResult,
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
    git_result: git.GitResult,
    patch_definitions: List[Tuple[git.PatchInfo, List[RawDefinition]]],
) -> List[LocustChange]:
    changes: List[LocustChange] = []
    for patch, definitions in patch_definitions:
        _, patch_changes = locust_changes_in_patch(
            patch, definitions, git_result.terminal_ref
        )
        changes.extend(patch_changes)
    return changes


def calculate_python_changes(git_result: git.GitResult) -> List[LocustChange]:
    patch_definitions = definitions_by_patch(git_result)
    return calculate_changes(git_result, patch_definitions)


def calculate_changes_from_file(
    git_result: git.GitResult, patch_definitions_json: str
) -> List[LocustChange]:
    with open(patch_definitions_json, "r") as ifp:
        patch_definitions_raw = json.load(ifp)
    patch_definitions = [
        (
            ParseDict(item[0], git.PatchInfo()),
            [ParseDict(definition_obj, RawDefinition()) for definition_obj in item[1]],
        )
        for item in patch_definitions_raw
    ]
    return calculate_changes(git_result, patch_definitions)


def calculate_plugin_changes(
    plugins: List[str], git_result: git.GitResult
) -> Dict[str, List[LocustChange]]:
    """
    Accepts a list of plugins (which can be invoked using subprocess.run and accept -i and -o
    parameters) and a git.GitResult object.

    Returns a dictionary whose keys are the plugins and whose values are tuples of the form:
    (locust changes, errors)
    """
    results: Dict[str, List[LocustChange]] = {}
    if not plugins:
        return results
    fd, git_result_filename = tempfile.mkstemp()
    os.close(fd)
    with open(git_result_filename, "w") as ofp:
        json.dump(MessageToDict(git_result, preserving_proto_field_name=True), ofp)

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


def run(git_result: git.GitResult, plugins: List[str]) -> ParseResult:
    changes = calculate_python_changes(git_result)
    plugin_changes_dict = calculate_plugin_changes(plugins, git_result)
    for _, plugin_changes in plugin_changes_dict.items():
        changes.extend(plugin_changes)
    return ParseResult(
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
        git_result = Parse(ifp.read(), git.GitResult())

    result = run(git_result, args.plugins)

    try:
        with args.output as ofp:
            print(
                json.dumps(MessageToDict(result, preserving_proto_field_name=True)),
                file=ofp,
            )
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
