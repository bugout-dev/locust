"""
Rendering utilities for locust parse results.
"""
import copy
from dataclasses import asdict, dataclass
import json
import os
import textwrap
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import yaml

from . import parse

IndexKey = Tuple[str, Optional[str], str, int]


@dataclass
class NestedChange:
    key: IndexKey
    change: parse.LocustChange
    children: Any


def get_key(change: parse.LocustChange) -> IndexKey:
    return (change.filepath, change.revision, change.name, change.line)


def parent_key(change: parse.LocustChange) -> Optional[IndexKey]:
    if change.parent is None:
        return None
    return (
        change.filepath,
        change.revision,
        change.parent[0],
        change.parent[1],
    )


def nest_results(
    changes: List[parse.LocustChange],
) -> Dict[str, List[NestedChange]]:
    results: Dict[str, List[NestedChange]] = {}
    index: Dict[IndexKey, parse.LocustChange] = {
        get_key(change): change for change in changes
    }

    children: Dict[IndexKey, List[IndexKey]] = {key: [] for key in index}

    for change in changes:
        change_parent = parent_key(change)
        if change_parent:
            children[change_parent].append(get_key(change))

    nested_results: Dict[str, List[NestedChange]] = {}
    keys_to_process = sorted(
        [k for k in index], key=lambda k: len(children[k]), reverse=True
    )
    visited_keys: Set[IndexKey] = set()

    def process_change(change_key: IndexKey, visited: Set[IndexKey]) -> NestedChange:
        visited.add(change_key)
        if not children[change_key]:
            return NestedChange(key=change_key, change=index[change_key], children=[])

        change_children = [
            process_change(child_key, visited) for child_key in children[change_key]
        ]
        return NestedChange(
            key=change_key,
            change=index[change_key],
            children=change_children,
        )

    for key in keys_to_process:
        if key in visited_keys:
            continue
        change = index[key]
        if change.filepath not in results:
            results[change.filepath] = []

        nested_change = process_change(key, visited_keys)

        results[change.filepath].append(nested_change)

    return results


def repo_relative_filepath(
    repo_dir: str, change: parse.LocustChange
) -> parse.LocustChange:
    """
    Changes the filepath on a LocustChange so that it is relative to the repo directory.
    """
    updated_change = copy.copy(change)
    updated_change.filepath = os.path.relpath(change.filepath, start=repo_dir)
    return updated_change


def nested_change_to_dict(nested_change: NestedChange) -> Dict[str, Any]:
    result = {
        "name": nested_change.change.name,
        "type": nested_change.change.change_type,
        "line": nested_change.change.line,
        "changed_lines": nested_change.change.changed_lines,
        "total_lines": nested_change.change.total_lines,
    }

    children_list: List[Dict[str, Any]] = []
    if nested_change.children:
        children_list = [
            nested_change_to_dict(child) for child in nested_change.children
        ]

    result["children"] = children_list

    return result


def results_dict(raw_results: Dict[str, List[NestedChange]]) -> Dict[str, Any]:
    results = {
        "locust": [
            {
                "file": filepath,
                "changes": [
                    nested_change_to_dict(nested_change)
                    for nested_change in nested_changes
                ],
            }
            for filepath, nested_changes in raw_results.items()
        ]
    }

    return results


def render_json(results: Dict[str, Any]) -> str:
    return json.dumps(results)


def render_yaml(results: Dict[str, Any]) -> str:
    return yaml.dump(results, sort_keys=False)


def enrich_with_refs(
    results: Dict[str, Any], initial_ref: str, terminal_ref: Optional[str]
) -> Dict[str, Any]:
    enriched_results = copy.deepcopy(results)
    enriched_results["refs"] = {"initial": initial_ref, "terminal": terminal_ref}
    return enriched_results


def enrich_with_github_links(
    results: Dict[str, Any], github_repo_url: str, terminal_ref: Optional[str]
) -> Dict[str, Any]:
    if terminal_ref is None:
        raise ValueError("Cannot create GitHub links without a reference to link to")

    if github_repo_url[-1] == "/":
        github_repo_url = github_repo_url[:-1]

    enriched_results = copy.deepcopy(results)

    for item in enriched_results["locust"]:
        relative_filepath = "/".join(item["file"].split(os.sep))
        if relative_filepath[0] == "/":
            relative_filepath = relative_filepath[1:]
        filepath = f"{github_repo_url}/blob/{terminal_ref}/{relative_filepath}"
        item["file"] = filepath
        for change in item["changes"]:
            change["link"] = f"{filepath}#L{change['line']}"

    return enriched_results


renderers: Dict[str, Callable[[Dict[str, List[NestedChange]]], str]] = {
    "json": render_json,
    "yaml": render_yaml,
}
