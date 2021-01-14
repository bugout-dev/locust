"""
Rendering utilities for locust parse results.
"""
import argparse
import copy
import json
import os
import sys
import textwrap
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, Union

from google.protobuf.json_format import Parse
import lxml
from lxml.html import builder as E
import yaml

from . import parse
from .render_pb2 import IndexKey, NestedChange

SerializedIndexKey = Tuple[str, Optional[str], str, int]


def serialize_index_key(index_key: IndexKey) -> SerializedIndexKey:
    return (index_key.filepath, index_key.revision, index_key.name, index_key.line)


def deserialize_index_key(serialized_index_key: SerializedIndexKey) -> IndexKey:
    filepath, maybe_revision, name, line = serialized_index_key
    return IndexKey(filepath=filepath, revision=maybe_revision, name=name, line=line)


def get_key(change: parse.LocustChange) -> IndexKey:
    return IndexKey(
        filepath=change.filepath,
        revision=change.revision,
        name=change.name,
        line=change.line,
    )


def parent_key(change: parse.LocustChange) -> Optional[IndexKey]:
    if change.parent is None:
        return None
    return IndexKey(
        filepath=change.filepath,
        revision=change.revision,
        name=change.parent.name,
        line=change.parent.line,
    )


def nest_results(
    changes: Iterable[parse.LocustChange],
) -> Dict[str, List[NestedChange]]:
    results: Dict[str, List[NestedChange]] = {}
    index: Dict[SerializedIndexKey, parse.LocustChange] = {
        serialize_index_key(get_key(change)): change for change in changes
    }

    children: Dict[SerializedIndexKey, List[SerializedIndexKey]] = {
        key: [] for key in index
    }

    for change in changes:
        change_parent = parent_key(change)
        if change_parent and change_parent.name:
            children[serialize_index_key(change_parent)].append(
                serialize_index_key(get_key(change))
            )

    nested_results: Dict[str, List[NestedChange]] = {}
    keys_to_process = sorted(
        [k for k in index], key=lambda k: len(children[k]), reverse=True
    )
    visited_keys: Set[SerializedIndexKey] = set()

    def process_change(
        change_key: SerializedIndexKey, visited: Set[SerializedIndexKey]
    ) -> NestedChange:
        visited.add(change_key)
        if not children[change_key]:
            return NestedChange(
                key=deserialize_index_key(change_key),
                change=index[change_key],
                children=[],
            )

        change_children = [
            process_change(child_key, visited) for child_key in children[change_key]
        ]
        return NestedChange(
            key=deserialize_index_key(change_key),
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


def change_representation_full(
    change: Dict[str, Any], link: str, filepath: str, current_depth: int, max_depth: int
) -> Optional[Any]:
    """
    Generator of uncompressed html markdown.
    """
    change_elements: List[Any] = [
        E.B("Name: "),
        E.A(change["name"], href=link),
        E.BR(),
        E.B("Type: "),
        E.SPAN(change["type"]),
        E.BR(),
        E.B("Changed lines: "),
        E.SPAN(str(change["changed_lines"])),
    ]

    if change["total_lines"]:
        change_elements.extend(
            [E.BR(), E.B("Total lines: "), E.SPAN(str(change["total_lines"]))]
        )

    if change["children"]:
        change_elements.extend([E.BR(), E.B("Changes:")])
    child_elements = []
    for child in change["children"]:
        child_element = render_change_as_html(
            child, filepath, current_depth + 1, max_depth
        )
        if child_element is not None:
            child_elements.append(child_element)
    change_elements.append(E.UL(*child_elements))

    return change_elements


def change_representation_compressed(
    change: Dict[str, Any], link: str, filepath: str, current_depth: int, max_depth: int
) -> Optional[Any]:
    """
    Generator of compressed html markdown.
    """
    change_elements: List[Any] = [
        E.B(change["type"]),
        E.SPAN(" "),
        E.A(change["name"], href=link),
        E.B(" changed lines: "),
        E.SPAN(str(change["changed_lines"])),
    ]

    if change["total_lines"]:
        change_elements.extend([E.SPAN("/"), E.SPAN(str(change["total_lines"]))])

    if change["children"]:
        change_elements.extend([E.BR()])
    child_elements = []
    for child in change["children"]:
        child_element = render_change_as_html(
            child, filepath, current_depth + 1, max_depth, True
        )
        if child_element is not None:
            child_elements.append(child_element)
    change_elements.append(E.UL(*child_elements))

    return change_elements


def render_change_as_html(
    change: Dict[str, Any],
    filepath: str,
    current_depth: int,
    max_depth: int,
    compressed: Optional[bool] = False,
) -> Optional[Any]:
    """
    Returns nested part of report in compressed or uncompressed format.
    """
    if current_depth >= max_depth:
        return None

    link = change.get("link")
    if link is None:
        link = filepath

    if compressed:
        change_elements = change_representation_compressed(
            change, link, filepath, current_depth, max_depth
        )
    else:
        change_elements = change_representation_full(
            change, link, filepath, current_depth, max_depth
        )

    return E.LI(*change_elements)


def html_file_section_handler_vanilla(item: Dict[str, Any]) -> Any:
    filepath = item["file"]
    file_url = item.get("file_url", filepath)
    change_elements = [
        render_change_as_html(change, filepath, 0, 2) for change in item["changes"]
    ]
    file_elements = [
        E.H4(E.A(filepath, href=file_url)),
        E.B("Changes:"),
        E.UL(*change_elements),
    ]
    return E.DIV(*file_elements)


def generate_html_section_handler_github(
    render_change: Callable[
        [Dict[str, Any], str, int, int, Optional[bool]], Optional[Any]
    ],
    compressed: Optional[bool] = False,
) -> Callable[[Any], Any]:
    """
    Generates a change wrapper, inside which contains a report on each
    function or class depending on the compressed or full format.
    """

    def html_file_section_handler_github(item: Dict[str, Any]) -> Any:
        filepath = item["file"]
        file_url = item.get("file_url", filepath)
        change_elements = [
            render_change(change, filepath, 0, 2, compressed)
            for change in item["changes"]
        ]
        file_summary_element = E.A(filepath, href=file_url)
        file_elements = [
            E.B("Changes:"),
            E.UL(*change_elements),
        ]
        file_elements_div = E.DIV(*file_elements)
        file_details_element = E.DIV(
            lxml.html.fromstring(
                f"<details><summary>{lxml.html.tostring(file_summary_element).decode()}</summary>"
                f"{lxml.html.tostring(file_elements_div).decode()}</details>"
            )
        )

        return file_details_element

    return html_file_section_handler_github


def generate_render_html(
    file_section_handler: Callable[[Dict[str, Any]], Any]
) -> Callable[[Dict[str, Any]], str]:
    def render_html(results: Dict[str, Any]) -> str:
        heading = E.H2(
            E.A("Locust", href="https://github.com/simiotics/locust"), " summary"
        )
        body_elements = [heading]

        refs = results.get("refs")
        if refs is not None:
            body_elements.extend([E.H3("Git references")])
            body_elements.extend([E.B("Initial: "), E.SPAN(refs["initial"]), E.BR()])
            if refs["terminal"] is not None:
                body_elements.extend(
                    [E.B("Terminal: "), E.SPAN(refs["terminal"]), E.BR()]
                )

        body_elements.append(E.HR())

        changes_by_file = results["locust"]
        for item in changes_by_file:
            item_element = file_section_handler(item)
            body_elements.append(item_element)

        html = E.HTML(E.BODY(*body_elements))
        results_string = lxml.html.tostring(html).decode()
        return results_string

    return render_html


def enrich_with_refs(
    results: Dict[str, Any], initial_ref: str, terminal_ref: Optional[str]
) -> Dict[str, Any]:
    enriched_results = copy.deepcopy(results)
    enriched_results["refs"] = {
        "initial": initial_ref,
        "terminal": terminal_ref,
    }
    return enriched_results


def enrich_with_metadata(
    results: Dict[str, Any], metadata: Dict[str, Any]
) -> Dict[str, Any]:
    enriched_results = copy.deepcopy(results)
    for key, value in metadata.items():
        enriched_results[key] = value
    return enriched_results


# TODO(neeraj): Recursively enrich change children with GitHub links
def enrich_with_github_links(
    results: Dict[str, Any], github_repo_url: str, terminal_ref: Optional[str]
) -> Dict[str, Any]:
    if terminal_ref is None:
        raise ValueError("Cannot create GitHub links without a reference to link to")

    if github_repo_url[-1] == "/":
        github_repo_url = github_repo_url[:-1]

    enriched_results = copy.deepcopy(results)

    def _enrich_changes(changes: List[Dict[str, Any]], root_url: str) -> None:
        """
        Mutates a list of changes with the updated root URL
        """
        for change in changes:
            change["link"] = f"{root_url}#L{change['line']}"
            if change.get("children") is not None:
                _enrich_changes(change["children"], root_url)

    for item in enriched_results["locust"]:
        relative_filepath = "/".join(item["file"].split(os.sep))
        if relative_filepath[0] == "/":
            relative_filepath = relative_filepath[1:]
        file_url = f"{github_repo_url}/blob/{terminal_ref}/{relative_filepath}"
        item["file_url"] = file_url
        _enrich_changes(item["changes"], file_url)

    return enriched_results


renderers: Dict[str, Callable[[Dict[str, List[NestedChange]]], str]] = {
    "json": render_json,
    "yaml": render_yaml,
    "html": generate_render_html(html_file_section_handler_vanilla),
    # html-github kept for for backwards compatibility
    "html-github": generate_render_html(
        generate_html_section_handler_github(render_change_as_html)
    ),
    "github": generate_render_html(
        generate_html_section_handler_github(render_change_as_html, compressed=True)
    ),
    "github-full": generate_render_html(
        generate_html_section_handler_github(render_change_as_html)
    ),
}


def populate_argument_parser(parser: argparse.ArgumentParser) -> None:
    """
    Populates an argparse ArgumentParser object with the commonly used arguments for this module.

    Mutates the provided parser.
    """
    parser.add_argument(
        "-f",
        "--format",
        choices=renderers,
        default="json",
        help="Format in which to render results",
    )
    parser.add_argument(
        "--github",
        required=False,
        default=None,
        help=(
            "[Optional] URL for GitHub repository where code is hosted "
            "(e.g. https://github.com/git/git)"
        ),
    )
    parser.add_argument(
        "-m",
        "--metadata",
        type=json.loads,
        default=None,
        help="JSON object specifying additional metadata for Locust summary",
    )


def run(
    parse_result: parse.ParseResult,
    render_format: str,
    github_url: Optional[str],
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> str:
    changes = parse_result.changes
    nested_results = nest_results(changes)
    results = results_dict(nested_results)
    results = enrich_with_refs(
        results, parse_result.initial_ref, parse_result.terminal_ref
    )
    if additional_metadata is not None:
        results = enrich_with_metadata(results, additional_metadata)
    if github_url is not None and parse_result.terminal_ref is not None:
        results = enrich_with_github_links(
            results, github_url, parse_result.terminal_ref
        )
    renderer = renderers[render_format]
    results_string = renderer(results)
    return results_string


def main():
    parser = argparse.ArgumentParser(description="Locust: rendering functionality")
    populate_argument_parser(parser)
    parser.add_argument(
        "-i",
        "--input",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Path to parse result. If not specified, reads from stdin.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Path to write summary to",
    )

    args = parser.parse_args()

    with args.input as ifp:
        parse_result = Parse(ifp.read(), parse.ParseResult())

    summary = run(parse_result, args.format, args.github, args.metadata)

    try:
        with args.output as ofp:
            print(summary, file=ofp)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
