"""
AST-related functionality
"""
import argparse
import ast
import os
from typing import Any, Dict, List, Optional, Tuple

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
    def __init__(self, package_dir: Optional[str], patches: List[git.PatchInfo]):
        self.package_dir = None
        if package_dir is not None:
            assert os.path.isdir(package_dir)
            self.package_dir = os.path.abspath(package_dir)

        self.package = None
        if self.package_dir is not None:
            self.package = os.path.basename(self.package_dir)

        self.insertion_boundaries: Dict[str, List[Tuple[int, int]]] = {}
        for patch in patches:
            raw_insertion_boundaries = [
                hunk_boundary(hunk, "+") for hunk in patch.hunks
            ]
            self.insertion_boundaries[patch.new_file] = [
                boundary
                for boundary in raw_insertion_boundaries
                if boundary is not None
            ]

        self.scope: List[str] = []
        self.imports: Dict[str, str] = {}

    def visit_Import(self, node: ast.Import) -> None:
        for name in node.names:
            as_name: Optional[str] = name.asname
            if as_name is None:
                as_name = name.name
            self.imports[as_name] = name.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        level = 0
        if node.level is not None:
            level = node.level

        prefix = "".join(["."] * level)

        if node.module is not None:
            prefix = f"{prefix}{node.module}"

        for name in node.names:
            as_name: Optional[str] = name.asname
            if as_name is None:
                as_name = name.name
            self.imports[as_name] = f"{prefix}.{name.name}"

    def parse(self, filepath: str) -> None:
        abs_filepath = os.path.abspath(filepath)

        with open(abs_filepath, "r") as ifp:
            source = ifp.read()

        root = ast.parse(source)
        self.visit(root)

        if self.package_dir is not None:
            assert (
                os.path.commonpath([self.package_dir, abs_filepath]) == self.package_dir
            ), f"File ({filepath}) is not contained in package directory ({self.package_dir})"

            components: List[str] = []
            current_path = abs_filepath
            while current_path != self.package_dir:
                current_path, basename = os.path.split(current_path)
                components.append(basename)
            components.append(os.path.basename(current_path))

            components.reverse()

            for as_name, name in self.imports.items():
                if name.startswith("."):
                    parts = name.split(".")
                    dots = -1
                    for i in range(len(parts)):
                        if parts[i]:
                            break
                        dots += 1
                    if dots == 0:
                        raise Exception(
                            f"Improper import in file ({filepath}): imported {name} as {as_name}"
                        )
                    package_level = len(components) - dots
                    self.imports[
                        as_name
                    ] = f"{'.'.join(components[:package_level])}.{name.lstrip('.')}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run locust AST visitor over a given Python file and dump its state"
    )
    parser.add_argument("python_file", help="File containing Python code")
    parser.add_argument(
        "-d", "--package-dir", default=None, help="Package root directory"
    )

    args = parser.parse_args()
    visitor = LocustVisitor(args.package_dir, [])
    visitor.parse(args.python_file)
    print(visitor.imports)
