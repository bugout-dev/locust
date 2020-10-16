"""
The Locust CLI
"""
import argparse
from dataclasses import asdict
import json
import os
import sys
from typing import Any, Dict, Optional

from . import git
from . import parse
from . import render
from . import version


def generate_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Locust: Analyze Python code across git references",
        epilog=f"Version {version.LOCUST_VERSION}",
    )
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
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Path to which to write results (as JSON)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=render.renderers,
        default="json",
        help="Format in which to render results",
    )
    parser.add_argument(
        "--github",
        required=False,
        default=None,
        help=(
            "[Optional] URL for GitHub repository where code is hosted "
            "(e.g. https://github.com/git/git)"
        ),
    )

    return parser


def main():
    parser = generate_argument_parser()
    args = parser.parse_args()

    repo = git.get_repository(args.repo)

    initial_ref = repo.revparse_single("HEAD")
    if args.initial is not None:
        initial_ref = repo.revparse_single(args.initial)

    terminal_ref = None
    if args.terminal is not None:
        terminal_ref = repo.revparse_single(args.terminal)

    patches = git.get_patches(repo, args.initial, args.terminal)
    visitor = parse.LocustVisitor(repo, args.terminal, patches)
    changes = visitor.parse_all()
    normalized_changes = [
        render.repo_relative_filepath(args.repo, change) for change in changes
    ]

    nested_results = render.nest_results(normalized_changes)
    results = render.results_dict(nested_results)
    results = render.enrich_with_refs(results, args.initial, args.terminal)
    if args.github is not None and args.terminal is not None:
        results = render.enrich_with_github_links(results, args.github, args.terminal)
    renderer = render.renderers[args.format]
    results_string = renderer(results)
    with args.output as ofp:
        print(results_string, file=ofp)


if __name__ == "__main__":
    main()
