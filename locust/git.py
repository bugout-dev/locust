"""
git-related utilities
"""
import argparse
from typing import Any, List, Optional

import pygit2


class GitRepositoryNotFound(Exception):
    """
    Raised when a git repository was not found where one was expected.
    """


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
    repository: pygit2.Repository, initial: Optional[str], terminal: Optional[str]
) -> List[Any]:
    """
    Returns a list of patches taking the given repository from the initial revision to the terminal
    one.
    """
    diff = repository.diff(a=initial, b=terminal, context_lines=0)
    return [patch for patch in diffs]


def get_patch_lines(patch: pygit2.Patch) -> List[pygit2.DiffLine]:
    """
    Returns all the lines in a patch.
    """
