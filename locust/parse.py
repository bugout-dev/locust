"""
AST-related functionality
"""
import argparse
import ast
import os
from typing import Any, Dict, List, Optional, Tuple, Union

from . import git


def hunk_boundary(
    hunk: git.HunkInfo, operation_type: Optional[str] = None
) -> Optional[Tuple[int, int]]:
    """
    Calculates boundary for the given hunk, returning a tuple of the form:
    (<line number of boundary start>, <line number of boundary end>)

    If operation_type is provided, it is used to filter down only to lines whose line_type matches
    the operation_type. Possible values: "+", "-", None.

    If there are no lines of the  given type in the hunk, returns None.
    """
    line_type_p = lambda line: True
    if operation_type is not None:
        line_type_p = lambda line: line.line_type == operation_type

    admissible_lines = [line for line in hunk.lines if line_type_p(line)]

    if not admissible_lines:
        return None

    return (admissible_lines[0].new_line_number, admissible_lines[-1].new_line_number)


class LocustVisitor(ast.NodeVisitor):
    def __init__(self, patches: List[git.PatchInfo]):
        self.insertion_boundaries: Dict[str, List[Tuple[int, int]]] = {}
        for patch in patches:
            raw_insertion_boundaries = [
                hunk_boundary(hunk, "+") for hunk in patch.hunks
            ]
            self.insertion_boundaries[os.path.abspath(patch.new_file)] = [
                boundary
                for boundary in raw_insertion_boundaries
                if boundary is not None
            ]

        self.scope: List[Tuple[str, int, Optional[int]]] = []
        self.definitions: List[Tuple[str, int, int, Optional[int], Optional[int]]] = []
        self.imports: Dict[str, str] = {}

    def _visit_class_or_function_def(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]
    ) -> None:
        self.scope = [
            spec for spec in self.scope if spec[2] is not None and spec[2] > node.lineno
        ]
        self.scope.append((node.name, node.lineno, node.end_lineno))
        self.definitions.append(
            (
                ".".join([spec[0] for spec in self.scope]),
                node.lineno,
                node.col_offset,
                node.end_lineno,
                node.end_col_offset,
            )
        )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_class_or_function_def(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_class_or_function_def(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._visit_class_or_function_def(node)

    def reset(self):
        self.scope = []
        self.definitions = []
        self.imports = {}

    def parse(self, filepath: str) -> List[Tuple[str, str]]:
        abs_filepath = os.path.abspath(filepath)
        if (
            abs_filepath not in self.insertion_boundaries
            or not self.insertion_boundaries[abs_filepath]
        ):
            return []

        insertion_boundaries = sorted(
            self.insertion_boundaries[abs_filepath], key=lambda p: p[0]
        )

        with open(abs_filepath, "r") as ifp:
            source = ifp.read()

        root = ast.parse(source)
        self.reset()
        self.visit(root)

        changed_definitions: List[Tuple[str, str]] = []
        for symbol, lineno, _, end_lineno, _ in self.definitions:
            candidate_insertion = max(
                [
                    boundary
                    for boundary in insertion_boundaries
                    if end_lineno is None or boundary[0] <= end_lineno
                ],
                key=lambda p: p[0],
            )
            if candidate_insertion[1] >= lineno:
                changed_definitions.append((symbol, f"{filepath}:{lineno}"))
        return changed_definitions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run locust AST visitor over a given Python file and dump its state"
    )
    parser.add_argument("-r", "--repo", default=".", help="Path to git repository")
    parser.add_argument(
        "-i",
        "--initial",
        required=False,
        default=None,
        help="Reference to initial repository state",
    )
    parser.add_argument(
        "-t",
        "--terminal",
        required=False,
        default=None,
        help="Reference to terminal repository state",
    )
    parser.add_argument("python_file", help="File containing Python code")

    args = parser.parse_args()
    repo = git.get_repository(args.repo)
    patches = git.get_patches(repo, args.initial, args.terminal)
    visitor = LocustVisitor(patches)
    changed_definitions = visitor.parse(args.python_file)
    print(changed_definitions)
