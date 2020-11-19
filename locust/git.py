"""
git-related functionality
"""
import argparse
import json
import os
import sys
from typing import Any, List, Optional, Tuple

from pydantic import BaseModel
import pygit2


class GitRepositoryNotFound(Exception):
    """
    Raised when a git repository was not found where one was expected.
    """


class LineInfo(BaseModel):
    old_line_number: int
    new_line_number: int
    line_type: str
    line: str


class HunkBoundary(BaseModel):
    operation_type: Optional[str] = None
    start: int
    end: int


class HunkInfo(BaseModel):
    header: str
    lines: List[LineInfo]
    total_boundary: Optional[HunkBoundary] = None
    insertions_boundary: Optional[HunkBoundary] = None
    deletions_boundary: Optional[HunkBoundary] = None


class PatchInfo(BaseModel):
    old_file: str
    new_file: str
    hunks: List[HunkInfo]
    old_source: Optional[str] = None
    new_source: Optional[str] = None


class RunResponse(BaseModel):
    repo: str
    initial_ref: str
    terminal_ref: Optional[str]
    patches: List[PatchInfo]


def get_repository(path: str = ".") -> pygit2.Repository:
    """
    Returns a git repository object if it can find one at the given path, otherwise raises a
    GitRepositoryNotFound error.
    """
    repository_path: Optional[str] = pygit2.discover_repository(path)
    if repository_path is None:
        raise GitRepositoryNotFound(f"No git repository found at path: {path}")
    return pygit2.Repository(repository_path)


def get_patches(
    repository: pygit2.Repository,
    initial: Optional[str] = None,
    terminal: Optional[str] = None,
) -> List[PatchInfo]:
    """
    Returns a list of patches taking the given repository from the initial revision to the terminal
    one.
    """
    diff = repository.diff(a=initial, b=terminal, context_lines=0)
    patches = [
        PatchInfo(
            old_file=patch.delta.old_file.path,
            new_file=patch.delta.new_file.path,
            hunks=[process_hunk(hunk) for hunk in patch.hunks],
        )
        for patch in diff
    ]

    rev_initial = initial
    if rev_initial is None:
        rev_initial = "HEAD"

    for patch in patches:
        old_filepath = os.path.join(repository.workdir, patch.old_file)
        new_filepath = os.path.join(repository.workdir, patch.new_file)
        try:
            patch.old_source = revision_file(repository, rev_initial, old_filepath)
        except:
            pass
        try:
            patch.new_source = revision_file(repository, terminal, new_filepath)
        except:
            pass

    return patches


def hunk_boundary(
    hunk: HunkInfo, operation_type: Optional[str] = None
) -> Optional[HunkBoundary]:
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

    return HunkBoundary(
        operation_type=operation_type,
        start=admissible_lines[0].new_line_number,
        end=admissible_lines[-1].new_line_number,
    )


def process_hunk(hunk: pygit2.DiffHunk) -> HunkInfo:
    """
    Processes a hunk from a git diff into a HunkInfo object.
    """
    hunk = HunkInfo(
        header=hunk.header,
        lines=[
            LineInfo(
                old_line_number=line.old_lineno,
                new_line_number=line.new_lineno,
                line_type=line.origin,
                line=line.content,
            )
            for line in hunk.lines
        ],
    )

    hunk.total_boundary = hunk_boundary(hunk, None)
    hunk.insertions_boundary = hunk_boundary(hunk, "+")
    hunk.deletions_boundary = hunk_boundary(hunk, "-")

    return hunk


def revision_file(
    repository: pygit2.Repository, revision: Optional[str], filepath: str
) -> Optional[str]:
    """
    Returns the source from the file at the given filepath on the given revision. If revision is
    None, returns the bytes from the filepath in the current working tree.

    Filepath is expected to be an absolute, normalized path.
    """
    repo_path = os.path.normpath(repository.workdir)

    content = bytes()

    if revision is None:
        assert (
            os.path.commonpath([repo_path, filepath]) == repo_path
        ), f"File ({filepath}) is not contained in repository ({repo_path})"
        with open(filepath, "rb") as ifp:
            content = ifp.read()
    else:
        relative_path = os.path.relpath(filepath, repo_path)
        dirname, basename = os.path.split(relative_path)
        components: List[str] = [basename]
        while dirname:
            dirname, basename = os.path.split(dirname)
            components.append(basename)
        components.reverse()

        commit = repository.revparse_single(revision)
        current_tree = commit.tree
        for component in components:
            try:
                current_tree = current_tree[component]
            except KeyError:
                return None
        content = current_tree.data

    return content.decode()


def populate_argument_parser(parser: argparse.ArgumentParser) -> None:
    """
    Populates an argparse ArgumentParser object with the commonly used arguments for this module.

    Mutates the provided parser.
    """
    parser.add_argument(
        "-r", "--repo", required=False, default=".", help="Path to git repository"
    )
    parser.add_argument(
        "initial",
        nargs="?",
        default=None,
        help="Initial git revision",
    )
    parser.add_argument(
        "terminal",
        nargs="?",
        default=None,
        help="Terminal git revision",
    )


def run(repo_dir: str, initial: Optional[str], terminal: Optional[str]) -> RunResponse:
    repo = get_repository(repo_dir)

    initial_ref = repo.revparse_single("HEAD").short_id
    if initial is not None:
        initial_ref = repo.revparse_single(initial).short_id

    terminal_ref = None
    if terminal is not None:
        terminal_ref = repo.revparse_single(terminal).short_id

    patches = get_patches(repo, initial_ref, terminal_ref)
    response = RunResponse(
        repo=os.path.normpath(repo.workdir),
        initial_ref=initial_ref,
        terminal_ref=terminal_ref,
        patches=patches,
    )
    return response


def main():
    parser = argparse.ArgumentParser(description="Locust: git functionality")
    populate_argument_parser(parser)
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        type=argparse.FileType("w"),
        default=sys.stdout,
        help=(
            "Path to which to write list of PatchInfo objects generated by this module (in JSON "
            "format)"
        ),
    )

    args = parser.parse_args()

    response = run(args.repo, args.initial, args.terminal)

    try:
        with args.output as ofp:
            print(response.json(), file=ofp)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
