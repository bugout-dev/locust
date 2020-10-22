"""
Command-line utility to help process GitHub Actions.
"""

import argparse
import json
import os
from typing import Any, Callable, Dict, List, Optional


def generate_argument_parser() -> argparse.ArgumentParser:
    commands = ["type", "initial", "terminal", "repo"]
    parser = argparse.ArgumentParser(description="Locust GitHub Actions helper")
    parser.add_argument(
        "command",
        choices=commands,
        help="Information you would like this helper to provide",
    )
    return parser


def helper_push(command: str, event: Dict[str, Any]) -> str:
    """
    Event structure defined here:
    https://docs.github.com/en/free-pro-team@latest/developers/webhooks-and-events/webhook-events-and-payloads#push
    """
    if command == "initial":
        return event["before"]
    elif command == "terminal":
        return event["after"]
    elif command == "repo":
        return event["repository"]["html_url"]

    raise Exception(f"Unknown command: {command}")


def helper_pr(command: str, event: Dict[str, Any]) -> str:
    """
    Event structure defined here:
    https://docs.github.com/en/free-pro-team@latest/developers/webhooks-and-events/webhook-events-and-payloads#pull_request
    """
    pull_request = event["pull_request"]
    if command == "initial":
        return pull_request["base"]["sha"]
    elif command == "terminal":
        return pull_request["head"]["sha"]
    elif command == "repo":
        return pull_request["head"]["repo"]["html_url"]

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
