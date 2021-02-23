"""
Command-line utility to help process GitHub Actions.
"""

import argparse
import json
import os
from typing import Any, Callable, Dict, List, Optional

import requests

from .. import git
from .. import parse
from .. import render


class ErrorDueSendingSummary(Exception):
    """
    Raised when error occured due sending locust summary.
    """


def generate_argument_parser() -> argparse.ArgumentParser:
    """
    Commands in GitHub Action:
      - name: Generate Locust summary and send to API
        env:
          BUGOUT_SECRET: ${{ secrets.BUGOUT_SECRET }}
          BUGOUT_API_URL: ${{ secrets.BUGOUT_API_URL }}
        run: |
          INITIAL_REF=$(locust.github initial)
          locust.github publish
    """
    commands = ["type", "initial", "terminal", "repo", "publish"]
    parser = argparse.ArgumentParser(description="Locust GitHub Actions helper")
    git.populate_argument_parser(parser)
    parse.populate_argument_parser(parser)
    parser.add_argument(
        "command",
        choices=commands,
        help="Information you would like this helper to provide",
    )
    return parser


def publish(
    repo_url: str,
    initial: str,
    terminal: str,
    comments_url: str,
    plugins: List[str],
    repo_dir: str,
) -> str:
    """
    Publish locust summary to API.
    """
    git_result = git.run(repo_dir, initial, terminal)
    parse_result = parse.run(git_result, plugins)
    metadata: Dict[str, str] = {
        "comments_url": comments_url,
        "terminal_hash": terminal,
    }

    results_json = render.run(
        parse_result,
        "json",
        repo_url,
        metadata,
    )

    url = os.environ.get("BUGOUT_API_URL", "https://spire.bugout.dev/github/summary")
    token = os.environ.get("BUGOUT_SECRET")
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers.update({"Authorization": f"Bearer {token}"})

    try:
        r = requests.post(url=url, data=results_json, headers=headers)
        r.raise_for_status()
    except Exception as e:
        raise ErrorDueSendingSummary(f"Exception {str(e)}")

    return "Locust summary sent to API"


def helper_push(args: argparse.Namespace, event: Dict[str, Any]) -> str:
    """
    Process trigger on: [ push ] at GitHub Actions.

    Event structure defined here:
    https://docs.github.com/en/free-pro-team@latest/developers/webhooks-and-events/webhook-events-and-payloads#push
    """
    pull_request = event["pull_request"]
    initial = event["before"]
    terminal = event["after"]
    repo_url = event["repository"]["html_url"]
    comments_url = pull_request["_links"]["comments"]["href"]

    if args.command == "initial":
        return initial
    elif args.command == "terminal":
        return terminal
    elif args.command == "repo":
        return repo_url
    elif args.command == "publish":
        result = publish(
            repo_url, initial, terminal, comments_url, args.plugins, args.repo
        )
        return result

    raise Exception(f"Unknown command: {args.command}")


def helper_pr(args: argparse.Namespace, event: Dict[str, Any]) -> str:
    """
    Process trigger on: [ pull_request ] or [ pull_request_target ] at GitHub Actions.

    Event structure defined here:
    https://docs.github.com/en/free-pro-team@latest/developers/webhooks-and-events/webhook-events-and-payloads#pull_request
    """
    pull_request = event["pull_request"]
    initial = pull_request["base"]["sha"]
    terminal = pull_request["head"]["sha"]
    repo_url = pull_request["head"]["repo"]["html_url"]
    comments_url = pull_request["_links"]["comments"]["href"]

    if args.command == "initial":
        return initial
    elif args.command == "terminal":
        return terminal
    elif args.command == "repo":
        return repo_url
    elif args.command == "publish":
        result = publish(
            repo_url, initial, terminal, comments_url, args.plugins, args.repo
        )
        return result

    raise Exception(f"Unknown command: {args.command}")


def main():
    parser = generate_argument_parser()
    args = parser.parse_args()

    helpers: Dict[str, Callable[[str, Dict[str, Any]], str]] = {
        "push": helper_push,
        "pull_request": helper_pr,
        "pull_request_target": helper_pr,
    }
    github_event_name: str = os.environ.get("GITHUB_EVENT_NAME", "")
    if github_event_name not in helpers:
        raise ValueError(
            f"Helper only works with events of the following types: {','.join(helpers)}"
        )

    if args.command == "type":
        print(github_event_name)
        return

    github_event_path: Optional[str] = os.environ.get("GITHUB_EVENT_PATH", None)
    if github_event_path is None:
        raise ValueError(
            "No path was provided for the GitHub event (GITHUB_EVENT_PATH not set)"
        )

    with open(github_event_path, "r") as ifp:
        event: Dict[str, Any] = json.load(ifp)

    print(helpers[github_event_name](args, event))
    return


if __name__ == "__main__":
    main()
