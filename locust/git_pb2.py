# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: git.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='git.proto',
  package='locust.git',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\tgit.proto\x12\nlocust.git\"]\n\x08LineInfo\x12\x17\n\x0fold_line_number\x18\x01 \x01(\x05\x12\x17\n\x0fnew_line_number\x18\x02 \x01(\x05\x12\x11\n\tline_type\x18\x03 \x01(\t\x12\x0c\n\x04line\x18\x04 \x01(\t\"B\n\x0cHunkBoundary\x12\r\n\x05start\x18\x01 \x01(\x05\x12\x0b\n\x03\x65nd\x18\x02 \x01(\x05\x12\x16\n\x0eoperation_type\x18\x03 \x01(\t\"\xde\x01\n\x08HunkInfo\x12\x0e\n\x06header\x18\x01 \x01(\t\x12#\n\x05lines\x18\x02 \x03(\x0b\x32\x14.locust.git.LineInfo\x12\x30\n\x0etotal_boundary\x18\x03 \x01(\x0b\x32\x18.locust.git.HunkBoundary\x12\x35\n\x13insertions_boundary\x18\x04 \x01(\x0b\x32\x18.locust.git.HunkBoundary\x12\x34\n\x12\x64\x65letions_boundary\x18\x05 \x01(\x0b\x32\x18.locust.git.HunkBoundary\"|\n\tPatchInfo\x12\x10\n\x08old_file\x18\x01 \x01(\t\x12\x10\n\x08new_file\x18\x02 \x01(\t\x12\x12\n\nold_source\x18\x03 \x01(\t\x12\x12\n\nnew_source\x18\x04 \x01(\t\x12#\n\x05hunks\x18\x05 \x03(\x0b\x32\x14.locust.git.HunkInfo\"l\n\tGitResult\x12\x0c\n\x04repo\x18\x01 \x01(\t\x12\x13\n\x0binitial_ref\x18\x02 \x01(\t\x12\x14\n\x0cterminal_ref\x18\x03 \x01(\t\x12&\n\x07patches\x18\x04 \x03(\x0b\x32\x15.locust.git.PatchInfob\x06proto3'
)




_LINEINFO = _descriptor.Descriptor(
  name='LineInfo',
  full_name='locust.git.LineInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='old_line_number', full_name='locust.git.LineInfo.old_line_number', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='new_line_number', full_name='locust.git.LineInfo.new_line_number', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='line_type', full_name='locust.git.LineInfo.line_type', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='line', full_name='locust.git.LineInfo.line', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=25,
  serialized_end=118,
)


_HUNKBOUNDARY = _descriptor.Descriptor(
  name='HunkBoundary',
  full_name='locust.git.HunkBoundary',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='start', full_name='locust.git.HunkBoundary.start', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='end', full_name='locust.git.HunkBoundary.end', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='operation_type', full_name='locust.git.HunkBoundary.operation_type', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=120,
  serialized_end=186,
)


_HUNKINFO = _descriptor.Descriptor(
  name='HunkInfo',
  full_name='locust.git.HunkInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='locust.git.HunkInfo.header', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='lines', full_name='locust.git.HunkInfo.lines', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='total_boundary', full_name='locust.git.HunkInfo.total_boundary', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='insertions_boundary', full_name='locust.git.HunkInfo.insertions_boundary', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='deletions_boundary', full_name='locust.git.HunkInfo.deletions_boundary', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=189,
  serialized_end=411,
)


_PATCHINFO = _descriptor.Descriptor(
  name='PatchInfo',
  full_name='locust.git.PatchInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='old_file', full_name='locust.git.PatchInfo.old_file', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='new_file', full_name='locust.git.PatchInfo.new_file', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='old_source', full_name='locust.git.PatchInfo.old_source', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='new_source', full_name='locust.git.PatchInfo.new_source', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='hunks', full_name='locust.git.PatchInfo.hunks', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=413,
  serialized_end=537,
)


_GITRESULT = _descriptor.Descriptor(
  name='GitResult',
  full_name='locust.git.GitResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='repo', full_name='locust.git.GitResult.repo', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='initial_ref', full_name='locust.git.GitResult.initial_ref', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='terminal_ref', full_name='locust.git.GitResult.terminal_ref', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='patches', full_name='locust.git.GitResult.patches', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=539,
  serialized_end=647,
)

_HUNKINFO.fields_by_name['lines'].message_type = _LINEINFO
_HUNKINFO.fields_by_name['total_boundary'].message_type = _HUNKBOUNDARY
_HUNKINFO.fields_by_name['insertions_boundary'].message_type = _HUNKBOUNDARY
_HUNKINFO.fields_by_name['deletions_boundary'].message_type = _HUNKBOUNDARY
_PATCHINFO.fields_by_name['hunks'].message_type = _HUNKINFO
_GITRESULT.fields_by_name['patches'].message_type = _PATCHINFO
DESCRIPTOR.message_types_by_name['LineInfo'] = _LINEINFO
DESCRIPTOR.message_types_by_name['HunkBoundary'] = _HUNKBOUNDARY
DESCRIPTOR.message_types_by_name['HunkInfo'] = _HUNKINFO
DESCRIPTOR.message_types_by_name['PatchInfo'] = _PATCHINFO
DESCRIPTOR.message_types_by_name['GitResult'] = _GITRESULT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LineInfo = _reflection.GeneratedProtocolMessageType('LineInfo', (_message.Message,), {
  'DESCRIPTOR' : _LINEINFO,
  '__module__' : 'git_pb2'
  # @@protoc_insertion_point(class_scope:locust.git.LineInfo)
  })
_sym_db.RegisterMessage(LineInfo)

HunkBoundary = _reflection.GeneratedProtocolMessageType('HunkBoundary', (_message.Message,), {
  'DESCRIPTOR' : _HUNKBOUNDARY,
  '__module__' : 'git_pb2'
  # @@protoc_insertion_point(class_scope:locust.git.HunkBoundary)
  })
_sym_db.RegisterMessage(HunkBoundary)

HunkInfo = _reflection.GeneratedProtocolMessageType('HunkInfo', (_message.Message,), {
  'DESCRIPTOR' : _HUNKINFO,
  '__module__' : 'git_pb2'
  # @@protoc_insertion_point(class_scope:locust.git.HunkInfo)
  })
_sym_db.RegisterMessage(HunkInfo)

PatchInfo = _reflection.GeneratedProtocolMessageType('PatchInfo', (_message.Message,), {
  'DESCRIPTOR' : _PATCHINFO,
  '__module__' : 'git_pb2'
  # @@protoc_insertion_point(class_scope:locust.git.PatchInfo)
  })
_sym_db.RegisterMessage(PatchInfo)

GitResult = _reflection.GeneratedProtocolMessageType('GitResult', (_message.Message,), {
  'DESCRIPTOR' : _GITRESULT,
  '__module__' : 'git_pb2'
  # @@protoc_insertion_point(class_scope:locust.git.GitResult)
  })
_sym_db.RegisterMessage(GitResult)


# @@protoc_insertion_point(module_scope)