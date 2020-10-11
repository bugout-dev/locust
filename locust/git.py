"""
git-related functionality
"""
import argparse
from dataclasses import asdict, dataclass
import json
from typing import Any, List, Optional, Tuple

import pygit2


class GitRepositoryNotFound(Exception):
    """
    Raised when a git repository was not found where one was expected.
    """


@dataclass
class LineInfo:
    old_line_number: int
    new_line_number: int
    line_type: str
    line: str


@dataclass
class HunkInfo:
    header: str
    lines: List[LineInfo]


@dataclass
class PatchInfo:
    old_file: str
    new_file: str
    hunks: List[HunkInfo]


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
    return [
        PatchInfo(
            old_file=patch.delta.old_file.path,
            new_file=patch.delta.new_file.path,
            hunks=[process_hunk(hunk) for hunk in patch.hunks],
        )
        for patch in diff
    ]


def process_hunk(hunk: pygit2.DiffHunk) -> HunkInfo:
    """
    Processes a hunk from a git diff into a HunkInfo object.
    """
    return HunkInfo(
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Locust git utilities")
    parser.add_argument("-r", "--repo", default=".", help="Path to git repository")
    parser.add_argument(
        "initial",
        nargs="?",
        default=None,
        help="Initial revision",
    )
    parser.add_argument(
        "terminal",
        nargs="?",
        default=None,
        help="Terminal revision",
    )

    args = parser.parse_args()

    repo = get_repository(args.repo)
    patches = get_patches(repo, args.initial, args.terminal)
    print(json.dumps([asdict(patch) for patch in patches], indent=2))
