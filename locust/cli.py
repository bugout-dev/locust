"""
The Locust CLI
"""
import argparse
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
    git.populate_argument_parser(parser)
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Path to which to write results",
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

    git_result = git.run(args.repo, args.initial, args.terminal)

    parse_results = parse.run(git_result)

    normalized_changes = [
        render.repo_relative_filepath(args.repo, change)
        for change in parse_results.changes
    ]

    nested_results = render.nest_results(normalized_changes)
    results = render.results_dict(nested_results)
    results = render.enrich_with_refs(
        results, git_result.initial_ref, git_result.terminal_ref
    )
    if args.github is not None and args.terminal is not None:
        results = render.enrich_with_github_links(
            results, args.github, git_result.terminal_ref
        )
    renderer = render.renderers[args.format]
    results_string = renderer(results)
    with args.output as ofp:
        print(results_string, file=ofp)


if __name__ == "__main__":
    main()
