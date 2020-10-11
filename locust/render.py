"""
Rendering utilities for locust parse results.
"""
import copy
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from . import parse


@dataclass
class NestedDefinition:
    definition: parse.LocustDefinition
    children: List[parse.LocustDefinition]


IndexKey = Tuple[str, Optional[str], str, int]


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


def nest_results(definitions: List[parse.LocustDefinition]) -> List[NestedDefinition]:
    index: Dict[IndexKey, parse.LocustDefinition] = {
        get_key(definition): definition for definition in definitions
    }

    children: Dict[IndexKey, List[IndexKey]] = {key: [] for key in index}
    for definition in definitions:
        parent_key = parent_key(definition)
        if parent_key:
            children[parent_key].append(get_key(definition))

    nested_results: List[NestedDefinition] = []
    for key, definition in index.items():
        current_children = [index[child_key] for child_key in children[key]]
        nested_results.append(
            NestedDefinition(definition=definition, children=current_children)
        )

    return nested_results


def render_json(
    definitions: Union[List[parse.LocustDefinition], List[NestedDefinition]]
) -> List[Dict[str, Any]]:
    return [asdict(item) for item in definitions]
