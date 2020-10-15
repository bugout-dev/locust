"""
Rendering utilities for locust parse results.
"""
import copy
from dataclasses import asdict, dataclass
import json
import os
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

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


def nested_change_to_json(change: NestedChange) -> Dict[str, Any]:
    children_list: List[Dict[str, Any]] = []
    if change.children:
        children_list = [nested_change_to_json(child) for child in change.children]
    json_form = {"change": asdict(change), "children": children_list}
    return json_form


def render_json(changes: Dict[str, List[NestedChange]]) -> str:
    result = {
        filepath: [nested_change_to_json(change) for change in nested_changes]
        for filepath, nested_changes in changes.items()
    }

    return json.dumps(result)


def render_markdown(changes: Dict[str, List[NestedChange]], level: int = 2) -> str:
    pass


renderers: Dict[str, Callable[[Dict[str, List[NestedChange]]], str]] = {
    "json": render_json,
    "markdown": render_markdown,
}
