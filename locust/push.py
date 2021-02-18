"""
Send locust report to provided url.
Arg --action should be specified only when you run locust in GitHub Actions.
"""
import argparse
import json
import os
from typing import Any, Dict, Optional

import requests

from . import parse
from . import render


class ErrorDueSendingSummary(Exception):
    """
    Raised when error occured due sending locust summary.
    """


def extract_comments_url() -> str:
    """
    Extracting comments url from GitHub Actions event json file.
    """
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path is None:
        raise ValueError("Cannot read $GITHUB_EVENT_PATH file in GitHub Action")

    with open(event_path, "r") as ifp:
        event_data = json.load(ifp)
    comments_url = (
        event_data.get("pull_request").get("_links").get("comments").get("href")
    )
    return comments_url


def populate_argument_parser(parser: argparse.ArgumentParser) -> None:
    """
    Populates an argparse ArgumentParser object with the commonly used arguments for this module.

    Mutates the provided parser.
    """
    parser.add_argument(
        "-u",
        "--url",
        help="Url where to send locust summary",
    )
    parser.add_argument(
        "-t",
        "--token",
        help="Bearer user token",
    )
    parser.add_argument(
        "-a",
        "--action",
        action="store_true",
        help="Mention if locust runs in GitHub Actions",
    )


def run(
    parse_result: parse.ParseResult,
    url: str,
    github_action: bool,
    github_url: Optional[str],
    token: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> None:
    if github_action:
        comments_url = extract_comments_url()
        bugout_additional_metadata: Dict[str, Any] = {
            "comments_url": comments_url,
            "terminal_hash": parse_result.terminal_ref,
        }
    headers = {}
    if token is not None:
        headers.update({"Authorization": f"Bearer {token}"})

    results_json = render.run(
        parse_result,
        "json",
        github_url,
        bugout_additional_metadata if github_action else additional_metadata,
    )

    try:
        r = requests.post(url=url, data=results_json, headers=headers)
        r.raise_for_status()
    except Exception as e:
        raise ErrorDueSendingSummary(f"Exception {str(e)}")
