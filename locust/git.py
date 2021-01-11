"""
git-related functionality
"""
import argparse
import json
import os
import sys
from typing import Any, List, Optional, Tuple

from google.protobuf.json_format import MessageToDict
import pygit2

from .git_pb2 import LineInfo, HunkBoundary, HunkInfo, PatchInfo, GitResult


class GitRepositoryNotFound(Exception):
    """
    Raised when a git repository was not found where one was expected.
    """


NULL_REVISION = "null"


def get_repository(path: str = ".") -> pygit2.Repository:
    """
    Returns a git repository object if it can find one at the given path, otherwise raises a
    GitRepositoryNotFound error.
    """
    repository_path: Optional[str] = pygit2.discover_repository(path)
    if repository_path is None:
        raise GitRepositoryNotFound(f"No git repository found at path: {path}")
    return pygit2.Repository(repository_path)


def get_empty_tree_hash(repo: pygit2.Repository) -> str:
    """
    The hash for the empty tree can be generated using: `git hash-object -t tree /dev/null`
    (see this Stack Overflow post for more details: https://stackoverflow.com/q/9765453)
    We prefer to generate the empty hash using the pygit2 Repository's TreeBuilder, which avoids use
    of the SHA-1 magic number: `4b825dc642cb6eb9a060e54bf8d69288fbee4904`.
    This makes locust as future-compatible as pygit2.
    """
    tree_builder = repo.TreeBuilder()
    return str(tree_builder.write())


def get_patches(
    repository: pygit2.Repository,
    initial: Optional[str] = None,
    terminal: Optional[str] = None,
) -> List[PatchInfo]:
    """
    Returns a list of patches taking the given repository from the initial revision to the terminal
    one.
    """
    rev_initial = initial
    rev_terminal = terminal
    if rev_initial is None:
        rev_initial = "HEAD"
    elif initial == NULL_REVISION:
        rev_initial = get_empty_tree_hash(repository)
        if terminal is None:
            rev_terminal = "HEAD"

    if terminal == NULL_REVISION:
        rev_terminal = get_empty_tree_hash(repository)

    diff = repository.diff(a=rev_initial, b=rev_terminal, context_lines=0)

    # We have to handle the case where initial=NULL_REVISION and terminal=None separately because of
    # the lack of tracked file objects in the empty revision and how git handles the default empty
    # argument for the terminal revision (checks against tracked files in initial revision).
    if initial == NULL_REVISION and terminal is None:
        status_diff = repository.diff()
        diff.merge(status_diff)

    patches = [
        PatchInfo(
            old_file=patch.delta.old_file.path,
            new_file=patch.delta.new_file.path,
            hunks=[process_hunk(hunk) for hunk in patch.hunks],
        )
        for patch in diff
    ]

    for patch in patches:
        old_filepath = os.path.join(repository.workdir, patch.old_file)
        new_filepath = os.path.join(repository.workdir, patch.new_file)
        old_source = None
        if initial != NULL_REVISION:
            old_source = revision_file(repository, rev_initial, old_filepath)
        new_source = None
        if terminal != NULL_REVISION:
            new_source = revision_file(repository, terminal, new_filepath)
        # The following awkward workaround is because mypy-protobuf has weird behaviour around
        # fields. They are defined as optional in the __init__ method of the message class, but not
        # optional as attributes of the message class.
        if old_source is not None:
            patch.old_source = old_source
        if new_source is not None:
            patch.new_source = new_source

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
    pre_hunk_info = HunkInfo(
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

    total_boundary = hunk_boundary(pre_hunk_info, None)
    insertions_boundary = hunk_boundary(pre_hunk_info, "+")
    deletions_boundary = hunk_boundary(pre_hunk_info, "-")

    hunk_info = HunkInfo(
        header=pre_hunk_info.header,
        lines=pre_hunk_info.lines,
        total_boundary=total_boundary,
        insertions_boundary=insertions_boundary,
        deletions_boundary=deletions_boundary,
    )

    return hunk_info


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

    return content.decode(errors="ignore")


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
        help='Initial git revision (to take diff against empty git tree, pass the value "null")',
    )
    parser.add_argument(
        "terminal",
        nargs="?",
        default=None,
        help="Terminal git revision",
    )


def run(repo_dir: str, initial: Optional[str], terminal: Optional[str]) -> GitResult:
    repo = get_repository(repo_dir)

    initial_ref: Optional[str] = None
    if initial is None:
        initial_ref = repo.revparse_single("HEAD").short_id
    elif initial == NULL_REVISION:
        initial_ref = NULL_REVISION
    else:
        initial_ref = repo.revparse_single(initial).short_id

    terminal_ref = None
    if terminal is None:
        pass
    elif terminal == NULL_REVISION:
        terminal_ref = NULL_REVISION
    else:
        terminal_ref = repo.revparse_single(terminal).short_id

    patches = get_patches(repo, initial_ref, terminal_ref)
    response = GitResult(
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
            response_dict = MessageToDict(response, preserving_proto_field_name=True)
            print(json.dumps(response_dict), file=ofp)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
