"""
The Locust CLI
"""
import argparse
import json
import sys

from . import git
from . import parse


def generate_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Locust: Analyze Python code across git references"
    )
    parser.add_argument(
        "-r", "--repo", required=False, default=".", help="Path to git repository"
    )
    parser.add_argument(
        "-i",
        "--initial",
        required=False,
        default=None,
        help="Initial git reference",
    )
    parser.add_argument(
        "-t",
        "--terminal",
        required=False,
        default=None,
        help="Terminal git reference",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Path to which to write results (as JSON)",
    )

    return parser


def main():
    parser = generate_argument_parser()
    args = parser.parse_args()
    repo = git.get_repository(args.repo)
    patches = git.get_patches(repo, args.initial, args.terminal)
    visitor = parse.LocustVisitor(patches)
    changed_definitions = visitor.parse_all()
    with args.output as ofp:
        json.dump(changed_definitions, ofp)


if __name__ == "__main__":
    main()
