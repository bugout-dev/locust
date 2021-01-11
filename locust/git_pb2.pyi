# @generated by generate_proto_mypy_stubs.py.  Do not edit!
import sys
from google.protobuf.descriptor import (
    Descriptor as google___protobuf___descriptor___Descriptor,
    FileDescriptor as google___protobuf___descriptor___FileDescriptor,
)

from google.protobuf.internal.containers import (
    RepeatedCompositeFieldContainer as google___protobuf___internal___containers___RepeatedCompositeFieldContainer,
)

from google.protobuf.message import (
    Message as google___protobuf___message___Message,
)

from typing import (
    Iterable as typing___Iterable,
    Optional as typing___Optional,
    Text as typing___Text,
)

from typing_extensions import (
    Literal as typing_extensions___Literal,
)


builtin___bool = bool
builtin___bytes = bytes
builtin___float = float
builtin___int = int


DESCRIPTOR: google___protobuf___descriptor___FileDescriptor = ...

class LineInfo(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    old_line_number: builtin___int = ...
    new_line_number: builtin___int = ...
    line_type: typing___Text = ...
    line: typing___Text = ...

    def __init__(self,
        *,
        old_line_number : typing___Optional[builtin___int] = None,
        new_line_number : typing___Optional[builtin___int] = None,
        line_type : typing___Optional[typing___Text] = None,
        line : typing___Optional[typing___Text] = None,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"line",b"line",u"line_type",b"line_type",u"new_line_number",b"new_line_number",u"old_line_number",b"old_line_number"]) -> None: ...
type___LineInfo = LineInfo

class HunkBoundary(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    start: builtin___int = ...
    end: builtin___int = ...
    operation_type: typing___Text = ...

    def __init__(self,
        *,
        start : typing___Optional[builtin___int] = None,
        end : typing___Optional[builtin___int] = None,
        operation_type : typing___Optional[typing___Text] = None,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"end",b"end",u"operation_type",b"operation_type",u"start",b"start"]) -> None: ...
type___HunkBoundary = HunkBoundary

class HunkInfo(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    header: typing___Text = ...

    @property
    def lines(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[type___LineInfo]: ...

    @property
    def total_boundary(self) -> type___HunkBoundary: ...

    @property
    def insertions_boundary(self) -> type___HunkBoundary: ...

    @property
    def deletions_boundary(self) -> type___HunkBoundary: ...

    def __init__(self,
        *,
        header : typing___Optional[typing___Text] = None,
        lines : typing___Optional[typing___Iterable[type___LineInfo]] = None,
        total_boundary : typing___Optional[type___HunkBoundary] = None,
        insertions_boundary : typing___Optional[type___HunkBoundary] = None,
        deletions_boundary : typing___Optional[type___HunkBoundary] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"deletions_boundary",b"deletions_boundary",u"insertions_boundary",b"insertions_boundary",u"total_boundary",b"total_boundary"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"deletions_boundary",b"deletions_boundary",u"header",b"header",u"insertions_boundary",b"insertions_boundary",u"lines",b"lines",u"total_boundary",b"total_boundary"]) -> None: ...
type___HunkInfo = HunkInfo

class PatchInfo(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    old_file: typing___Text = ...
    new_file: typing___Text = ...
    old_source: typing___Text = ...
    new_source: typing___Text = ...

    @property
    def hunks(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[type___HunkInfo]: ...

    def __init__(self,
        *,
        old_file : typing___Optional[typing___Text] = None,
        new_file : typing___Optional[typing___Text] = None,
        old_source : typing___Optional[typing___Text] = None,
        new_source : typing___Optional[typing___Text] = None,
        hunks : typing___Optional[typing___Iterable[type___HunkInfo]] = None,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"hunks",b"hunks",u"new_file",b"new_file",u"new_source",b"new_source",u"old_file",b"old_file",u"old_source",b"old_source"]) -> None: ...
type___PatchInfo = PatchInfo

class GitResult(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    repo: typing___Text = ...
    initial_ref: typing___Text = ...
    terminal_ref: typing___Text = ...

    @property
    def patches(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[type___PatchInfo]: ...

    def __init__(self,
        *,
        repo : typing___Optional[typing___Text] = None,
        initial_ref : typing___Optional[typing___Text] = None,
        terminal_ref : typing___Optional[typing___Text] = None,
        patches : typing___Optional[typing___Iterable[type___PatchInfo]] = None,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"initial_ref",b"initial_ref",u"patches",b"patches",u"repo",b"repo",u"terminal_ref",b"terminal_ref"]) -> None: ...
type___GitResult = GitResult
