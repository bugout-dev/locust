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

    return parser


def main():
    parser = generate_argument_parser()
    args = parser.parse_args()

    repo = git.get_repository(args.repo)
    patches = git.get_patches(repo, args.initial, args.terminal)
    visitor = parse.LocustVisitor(repo, args.terminal, patches)
    changes = visitor.parse_all()
    normalized_changes = [
        render.repo_relative_filepath(args.repo, change) for change in changes
    ]

    nested_results = render.nest_results(normalized_changes)
    renderer = render.renderers[args.format]
    results = renderer(nested_results)

    with args.output as ofp:
        print(results, file=ofp)


if __name__ == "__main__":
    main()
