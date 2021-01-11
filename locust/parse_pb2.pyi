# @generated by generate_proto_mypy_stubs.py.  Do not edit!
import sys
from .git_pb2 import(
    PatchInfo as git_pb2___PatchInfo,
)

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

class DefinitionParent(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    name: typing___Text = ...
    line: builtin___int = ...

    def __init__(self,
        *,
        name : typing___Optional[typing___Text] = None,
        line : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"line",b"line",u"name",b"name"]) -> None: ...
type___DefinitionParent = DefinitionParent

class RawDefinition(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    name: typing___Text = ...
    change_type: typing___Text = ...
    line: builtin___int = ...
    offset: builtin___int = ...
    end_line: builtin___int = ...
    end_offset: builtin___int = ...

    @property
    def parent(self) -> type___DefinitionParent: ...

    def __init__(self,
        *,
        name : typing___Optional[typing___Text] = None,
        change_type : typing___Optional[typing___Text] = None,
        line : typing___Optional[builtin___int] = None,
        offset : typing___Optional[builtin___int] = None,
        end_line : typing___Optional[builtin___int] = None,
        end_offset : typing___Optional[builtin___int] = None,
        parent : typing___Optional[type___DefinitionParent] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"parent",b"parent"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"change_type",b"change_type",u"end_line",b"end_line",u"end_offset",b"end_offset",u"line",b"line",u"name",b"name",u"offset",b"offset",u"parent",b"parent"]) -> None: ...
type___RawDefinition = RawDefinition

class LocustChange(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    name: typing___Text = ...
    change_type: typing___Text = ...
    filepath: typing___Text = ...
    revision: typing___Text = ...
    line: builtin___int = ...
    changed_lines: builtin___int = ...
    total_lines: builtin___int = ...

    @property
    def parent(self) -> type___DefinitionParent: ...

    def __init__(self,
        *,
        name : typing___Optional[typing___Text] = None,
        change_type : typing___Optional[typing___Text] = None,
        filepath : typing___Optional[typing___Text] = None,
        revision : typing___Optional[typing___Text] = None,
        line : typing___Optional[builtin___int] = None,
        changed_lines : typing___Optional[builtin___int] = None,
        total_lines : typing___Optional[builtin___int] = None,
        parent : typing___Optional[type___DefinitionParent] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"parent",b"parent"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"change_type",b"change_type",u"changed_lines",b"changed_lines",u"filepath",b"filepath",u"line",b"line",u"name",b"name",u"parent",b"parent",u"revision",b"revision",u"total_lines",b"total_lines"]) -> None: ...
type___LocustChange = LocustChange

class ParseResult(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    repo: typing___Text = ...
    initial_ref: typing___Text = ...
    terminal_ref: typing___Text = ...

    @property
    def patches(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[git_pb2___PatchInfo]: ...

    @property
    def changes(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[type___LocustChange]: ...

    def __init__(self,
        *,
        repo : typing___Optional[typing___Text] = None,
        initial_ref : typing___Optional[typing___Text] = None,
        terminal_ref : typing___Optional[typing___Text] = None,
        patches : typing___Optional[typing___Iterable[git_pb2___PatchInfo]] = None,
        changes : typing___Optional[typing___Iterable[type___LocustChange]] = None,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"changes",b"changes",u"initial_ref",b"initial_ref",u"patches",b"patches",u"repo",b"repo",u"terminal_ref",b"terminal_ref"]) -> None: ...
type___ParseResult = ParseResult
