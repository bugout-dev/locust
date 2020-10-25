"""
AST-related functionality
"""
import argparse
import ast
import json
import os
import sys
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

    def __init__(
        self,
        git_result: git.RunResponse
        # repository: Repository,
        # revision: Optional[str],
        # patches: List[git.PatchInfo],
    ):
        # self.repository = repository
        # self.revision = None
        # if revision is not None:
        #     self.revision = repository.revparse_single(revision).short_id

        # self.insertion_boundaries: Dict[str, List[Tuple[int, int]]] = {}
        # for patch in patches:
        #     _, extension = os.path.splitext(patch.new_file)
        #     if extension != ".py":
        #         continue
        #     patch_filepath = os.path.realpath(
        #         os.path.join(repository.workdir, patch.new_file)
        #     )
        #     raw_insertion_boundaries = [
        #         hunk_boundary(hunk, "+") for hunk in patch.hunks
        #     ]
        #     self.insertion_boundaries[os.path.abspath(patch_filepath)] = [
        #         boundary
        #         for boundary in raw_insertion_boundaries
        #         if boundary is not None
        #     ]
        self.repo = git_result.repo
        self.initial_ref = git_result.initial_ref
        self.terminal_ref = git_result.terminal_ref

        self.patches: Dict[str, git.PatchInfo] = {}
        for patch in git_result.patches:
            _, extension = os.path.splitext(patch.new_file)
            if extension != ".py":
                continue
            self.patches[patch.new_file] = patch

        self.scope: List[Tuple[str, int, Optional[int]]] = []
        self.definitions: List[RawDefinition] = []
        self.imports: Dict[str, str] = {}

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
        self.imports = {}

    def parse(self, filepath: str) -> List[LocustChange]:
        patch = self.patches.get(filepath)
        if patch is None:
            return []

        source = patch.new_source
        if source is None:
            return []

        insertions_boundaries: List[Tuple[int, int]] = []
        for hunk in patch.hunks:
            if hunk.insertions_boundary is not None:
                insertions_boundaries.append(
                    (hunk.insertions_boundary.start, hunk.insertions_boundary.end)
                )
        insertions_boundaries.sort(key=lambda p: p[0])

        root = ast.parse(source)
        self.reset()
        self.visit(root)

        locust_changes: List[LocustChange] = []
        for definition in self.definitions:
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
                        if (
                            definition.end_line is not None
                            and definition.end_line < end
                        ):
                            end_line = definition.end_line

                        changed_lines += end_line - max(start, definition.line) + 1

                locust_changes.append(
                    LocustChange(
                        name=definition.name,
                        change_type=definition.change_type,
                        filepath=filepath,
                        revision=self.terminal_ref,
                        line=definition.line,
                        changed_lines=changed_lines,
                        total_lines=total_lines,
                        parent=definition.parent,
                    )
                )

        return locust_changes

    def parse_all(self) -> List[LocustChange]:
        changed_definitions: List[LocustChange] = []
        for filepath in self.patches:
            changed_definitions.extend(self.parse(filepath))
        return changed_definitions


class RunResponse(BaseModel):
    repo: str
    initial_ref: str
    terminal_ref: Optional[str]
    patches: List[git.PatchInfo]
    changes: List[LocustChange]


def run(git_result: git.RunResponse) -> RunResponse:
    visitor = LocustVisitor(git_result)
    changes = visitor.parse_all()
    return RunResponse(
        repo=git_result.repo,
        initial_ref=git_result.initial_ref,
        terminal_ref=git_result.terminal_ref,
        patches=git_result.patches,
        changes=changes,
    )


def main():
    parser = argparse.ArgumentParser(description="Locust: Python parsing functionality")
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

    result = run(git_result)

    try:
        with args.output as ofp:
            print(result.json(), file=ofp)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
