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
from .. import version


class ErrorDueSendingSummary(Exception):
    """
    Raised when error occured due sending locust summary.
    """


def generate_argument_parser() -> argparse.ArgumentParser:
    commands = ["type", "initial", "terminal", "repo", "send"]
    parser = argparse.ArgumentParser(description="Locust GitHub Actions helper")
    parser.add_argument(
        "command",
        choices=commands,
        help="Information you would like this helper to provide",
    )
    return parser


def send(
    repo_dir: str,
    initial: str,
    terminal: str,
    comments_url: str,
) -> str:
    """
    Bugout GitHub Bot application.
    Send locust summary to Bugout API.
    """
    git_result = git.run(repo_dir, initial, terminal)
    plugins: List[str] = []
    parse_result = parse.run(git_result, plugins)
    metadata: Dict[str, str] = {
        "comments_url": comments_url,
        "terminal_hash": terminal,
    }

    results_json = render.run(
        parse_result,
        "json",
        repo_dir,
        metadata,
    )

    url = os.environ.get("BUGOUT_API_URL", "https://spire.bugout.dev/github/summary")
    token = os.environ.get("BUGOUT_SECRET")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        r = requests.post(url=url, data=results_json, headers=headers)
        r.raise_for_status()
    except Exception as e:
        raise ErrorDueSendingSummary(f"Exception {str(e)}")

    return "Locust summary sent to API"


def helper_push(command: str, event: Dict[str, Any]) -> str:
    """
    Process trigger on: [ push ] at GitHub Actions.

    Event structure defined here:
    https://docs.github.com/en/free-pro-team@latest/developers/webhooks-and-events/webhook-events-and-payloads#push
    """
    pull_request = event["pull_request"]
    initial = event["before"]
    terminal = event["after"]
    repo = event["repository"]["html_url"]
    comments_url = pull_request["_links"]["comments"]["href"]

    if command == "initial":
        return initial
    elif command == "terminal":
        return terminal
    elif command == "repo":
        return repo
    elif command == "send":
        result = send(repo, initial, terminal, comments_url)
        return result

    raise Exception(f"Unknown command: {command}")


def helper_pr(command: str, event: Dict[str, Any]) -> str:
    """
    Process trigger on: [ pull_request ] or [ pull_request_target ] at GitHub Actions.

    Event structure defined here:
    https://docs.github.com/en/free-pro-team@latest/developers/webhooks-and-events/webhook-events-and-payloads#pull_request
    """
    pull_request = event["pull_request"]
    initial = pull_request["base"]["sha"]
    terminal = pull_request["head"]["sha"]
    repo = pull_request["head"]["repo"]["html_url"]
    comments_url = pull_request["_links"]["comments"]["href"]

    if command == "initial":
        return initial
    elif command == "terminal":
        return terminal
    elif command == "repo":
        return repo
    elif command == "send":
        result = send(repo, initial, terminal, comments_url)
        return result

    raise Exception(f"Unknown command: {command}")


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

    print(helpers[github_event_name](args.command, event))
    return


if __name__ == "__main__":
    main()
