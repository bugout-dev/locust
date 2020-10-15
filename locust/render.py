"""
Rendering utilities for locust parse results.
"""
import copy
from dataclasses import asdict, dataclass
import os
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from . import parse

IndexKey = Tuple[str, Optional[str], str, int]


@dataclass
class NestedDefinition:
    key: IndexKey
    definition: parse.LocustDefinition
    children: Any


def get_key(definition: parse.LocustDefinition) -> IndexKey:
    return (definition.filepath, definition.revision, definition.name, definition.line)


def parent_key(definition: parse.LocustDefinition) -> Optional[IndexKey]:
    if definition.parent is None:
        return None
    return (
        definition.filepath,
        definition.revision,
        definition.parent[0],
        definition.parent[1],
    )


def nest_results(
    definitions: List[parse.LocustDefinition],
) -> Dict[str, List[NestedDefinition]]:
    results: Dict[str, List[NestedDefinition]] = {}
    index: Dict[IndexKey, parse.LocustDefinition] = {
        get_key(definition): definition for definition in definitions
    }

    children: Dict[IndexKey, List[IndexKey]] = {key: [] for key in index}

    for definition in definitions:
        definition_parent = parent_key(definition)
        if definition_parent:
            children[definition_parent].append(get_key(definition))

    nested_results: Dict[str, List[NestedDefinition]] = {}
    keys_to_process = sorted(
        [k for k in index], key=lambda k: len(children[k]), reverse=True
    )
    visited_keys: Set[IndexKey] = set()

    def process_definition(
        definition_key: IndexKey, visited: Set[IndexKey]
    ) -> NestedDefinition:
        visited.add(definition_key)
        if not children[definition_key]:
            return NestedDefinition(
                key=definition_key, definition=index[definition_key], children=[]
            )

        definition_children = [
            process_definition(child_key, visited)
            for child_key in children[definition_key]
        ]
        return NestedDefinition(
            key=definition_key,
            definition=index[definition_key],
            children=definition_children,
        )

    for key in keys_to_process:
        if key in visited_keys:
            continue
        definition = index[key]
        if definition.filepath not in results:
            results[definition.filepath] = []

        nested_definition = process_definition(key, visited_keys)

        results[definition.filepath].append(nested_definition)

    return results


def repo_relative_filepath(
    repo_dir: str, definition: parse.LocustDefinition
) -> parse.LocustDefinition:
    """
    Changes the filepath on a LocustDefinition so that it is relative to the repo directory.
    """
    updated_definition = copy.copy(definition)
    updated_definition.filepath = os.path.relpath(definition.filepath, start=repo_dir)
    return updated_definition


def nested_definition_to_json(definition: NestedDefinition) -> Dict[str, Any]:
    children_list: List[Dict[str, Any]] = []
    if definition.children:
        children_list = [
            nested_definition_to_json(child) for child in definition.children
        ]
    json_form = {"definition": asdict(definition), "children": children_list}
    return json_form


def render_json(definitions: Dict[str, List[NestedDefinition]]) -> Dict[str, Any]:
    result = {
        filepath: [
            nested_definition_to_json(definition) for definition in nested_definitions
        ]
        for filepath, nested_definitions in definitions.items()
    }

    return result
