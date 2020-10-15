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
        "--pretty",
        action="store_true",
        help="Specifies that result should be pretty printed",
    )

    return parser


def main():
    parser = generate_argument_parser()
    args = parser.parse_args()

    repo = git.get_repository(args.repo)
    patches = git.get_patches(repo, args.initial, args.terminal)
    visitor = parse.LocustVisitor(repo, args.terminal, patches)
    changed_definitions = visitor.parse_all()
    normalized_definitions = [
        render.repo_relative_filepath(args.repo, definition)
        for definition in changed_definitions
    ]

    nested_results = render.nest_results(normalized_definitions)
    json_results = render.render_json(nested_results)

    indent: Optional[int] = None
    if args.pretty:
        indent = 4

    with args.output as ofp:
        print(json.dumps(json_results, indent=indent), file=ofp)


if __name__ == "__main__":
    main()
