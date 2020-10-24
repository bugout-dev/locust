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
    render.populate_argument_parser(parser)
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Path to which to write results",
    )
    return parser


def main():
    parser = generate_argument_parser()
    args = parser.parse_args()

    git_result = git.run(args.repo, args.initial, args.terminal)

    parse_result = parse.run(git_result)

    results_string = render.run(parse_result, args.format, args.github)

    try:
        with args.output as ofp:
            print(results_string, file=ofp)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
