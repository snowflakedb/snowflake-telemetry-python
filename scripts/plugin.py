#!/usr/bin/env python3
from __future__ import annotations

import re
import os
import sys
import inspect
from enum import IntEnum
from typing import List, Optional
from textwrap import dedent, indent
from dataclasses import dataclass, field
# Must be imported into globals for the inline functions to work
from snowflake.telemetry._internal.serialize import MessageMarshaler # noqa

from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf.descriptor_pb2 import (
    FileDescriptorProto,
    FieldDescriptorProto,
    EnumDescriptorProto,
    EnumValueDescriptorProto,
    DescriptorProto,
)
from jinja2 import Environment, FileSystemLoader
import black
import isort.api

INLINE_OPTIMIZATION = True
FILE_PATH_PREFIX = "snowflake.telemetry._internal"
FILE_NAME_SUFFIX = "_marshaler"

# Inline utility functions

# Inline the size function for a given proto message field
def inline_size_function(proto_type: str, attr_name: str, field_tag: str) -> str:
    """
    For example:

    class MessageMarshaler:
        def size_uint32(self, TAG: bytes, FIELD_ATTR: int) -> int:
            return len(TAG) + Varint.size_varint_u32(FIELD_ATTR)
    
    Becomes:

    size += len(b"\x10") + Varint.size_varint_u32(self.int_value)
    """
    function_definition = inspect.getsource(globals()["MessageMarshaler"].__dict__[f"size_{proto_type}"])
    # Remove the function header and unindent the function body
    function_definition = function_definition.splitlines()[1:]
    function_definition = "\n".join(function_definition)
    function_definition = dedent(function_definition)
    # Replace the attribute name
    function_definition = function_definition.replace("FIELD_ATTR", f"self.{attr_name}")
    # Replace the TAG
    function_definition = function_definition.replace("TAG", field_tag)
    # Inline the return statement
    function_definition = function_definition.replace("return ", "size += ")
    return function_definition

# Inline the serialization function for a given proto message field
def inline_serialize_function(proto_type: str, attr_name: str, field_tag: str) -> str:
    """
    For example:

    class MessageMarshaler:
        def serialize_uint32(self, out: BytesIO, TAG: bytes, FIELD_ATTR: int) -> None:
            out.write(TAG)
            Varint.serialize_varint_u32(out, FIELD_ATTR)
    
    Becomes:

    out.write(b"\x10")
    Varint.serialize_varint_u32(out, self.int_value)
    """
    function_definition = inspect.getsource(globals()["MessageMarshaler"].__dict__[f"serialize_{proto_type}"])
    # Remove the function header and unindent the function body
    function_definition = function_definition.splitlines()[1:]
    function_definition = "\n".join(function_definition)
    function_definition = dedent(function_definition)
    # Replace the attribute name
    function_definition = function_definition.replace("FIELD_ATTR", f"self.{attr_name}")
    # Replace the TAG
    function_definition = function_definition.replace("TAG", field_tag)
    return function_definition

# Inline the init function for a proto message
def inline_init() -> str:
    function_definition = inspect.getsource(globals()["MessageMarshaler"].__dict__["__init__"])
    # Remove the function header and unindent the function body
    function_definition = function_definition.splitlines()[1:]
    function_definition = "\n".join(function_definition)
    function_definition = dedent(function_definition)
    return function_definition

# Add a presence check to a function definition
# https://protobuf.dev/programming-guides/proto3/#default
def add_presence_check(proto_type: str, encode_presence: bool, attr_name: str, function_definition: str) -> str:
    # oneof, optional (virtual oneof), and message fields are encoded if they are not None
    function_definition = indent(function_definition, "    ")
    if encode_presence:
        return f"if self.{attr_name} is not None:\n{function_definition}"
    # Other fields are encoded if they are not the default value
    # Which happens to align with the bool(x) check for all primitive types
    # TODO: Except
    #   - double and float -0.0 should be encoded, even though bool(-0.0) is False
    return f"if self.{attr_name}:\n{function_definition}"

class WireType(IntEnum):
    VARINT = 0
    I64 = 1
    LEN = 2
    I32 = 5

@dataclass
class ProtoTypeDescriptor:
    name: str
    wire_type: WireType
    python_type: str
    default_val: str

proto_type_to_descriptor = {
    FieldDescriptorProto.TYPE_BOOL: ProtoTypeDescriptor("bool", WireType.VARINT, "bool", "False"),
    FieldDescriptorProto.TYPE_ENUM: ProtoTypeDescriptor("enum", WireType.VARINT, "int", "0"),
    FieldDescriptorProto.TYPE_INT32: ProtoTypeDescriptor("int32", WireType.VARINT, "int", "0"),
    FieldDescriptorProto.TYPE_INT64: ProtoTypeDescriptor("int64", WireType.VARINT, "int", "0"),
    FieldDescriptorProto.TYPE_UINT32: ProtoTypeDescriptor("uint32", WireType.VARINT, "int", "0"),
    FieldDescriptorProto.TYPE_UINT64: ProtoTypeDescriptor("uint64", WireType.VARINT, "int", "0"),
    FieldDescriptorProto.TYPE_SINT32: ProtoTypeDescriptor("sint32", WireType.VARINT, "int", "0"),
    FieldDescriptorProto.TYPE_SINT64: ProtoTypeDescriptor("sint64", WireType.VARINT, "int", "0"),
    FieldDescriptorProto.TYPE_FIXED32: ProtoTypeDescriptor("fixed32", WireType.I32, "int", "0"),
    FieldDescriptorProto.TYPE_FIXED64: ProtoTypeDescriptor("fixed64", WireType.I64, "int", "0"),
    FieldDescriptorProto.TYPE_SFIXED32: ProtoTypeDescriptor("sfixed32", WireType.I32, "int", "0"),
    FieldDescriptorProto.TYPE_SFIXED64: ProtoTypeDescriptor("sfixed64", WireType.I64, "int", "0"),
    FieldDescriptorProto.TYPE_FLOAT: ProtoTypeDescriptor("float", WireType.I32, "float", "0.0"),
    FieldDescriptorProto.TYPE_DOUBLE: ProtoTypeDescriptor("double", WireType.I64, "float", "0.0"),
    FieldDescriptorProto.TYPE_STRING: ProtoTypeDescriptor("string", WireType.LEN, "str", '""'),
    FieldDescriptorProto.TYPE_BYTES: ProtoTypeDescriptor("bytes", WireType.LEN, "bytes", 'b""'),
    FieldDescriptorProto.TYPE_MESSAGE: ProtoTypeDescriptor("message", WireType.LEN, "PLACEHOLDER", "None"),
}

@dataclass
class EnumValueTemplate:
    name: str
    number: int

    @staticmethod
    def from_descriptor(descriptor: EnumValueDescriptorProto) -> "EnumValueTemplate":
        return EnumValueTemplate(
            name=descriptor.name,
            number=descriptor.number,
        )

@dataclass
class EnumTemplate:
    name: str
    values: List[EnumValueTemplate] = field(default_factory=list)

    @staticmethod
    def from_descriptor(descriptor: EnumDescriptorProto) -> "EnumTemplate":
        return EnumTemplate(
            name=descriptor.name,
            values=[EnumValueTemplate.from_descriptor(value) for value in descriptor.value],
        )

def tag_to_repr_varint(tag: int) -> str:
    out = bytearray()
    while tag >= 128:
        out.append((tag & 0x7F) | 0x80)
        tag >>= 7
    out.append(tag)
    return repr(bytes(out))

@dataclass
class FieldTemplate:
    name: str
    attr_name: str
    number: int
    generator: str
    python_type: str
    proto_type: str
    default_val: str
    serialize_field_inline: str
    size_field_inline: str

    @staticmethod
    def from_descriptor(descriptor: FieldDescriptorProto, group: Optional[str] = None) -> "FieldTemplate":
        type_descriptor = proto_type_to_descriptor[descriptor.type]
        python_type = type_descriptor.python_type
        proto_type = type_descriptor.name
        default_val = type_descriptor.default_val

        if proto_type == "message" or proto_type == "enum":
            # Extract the class name of message fields, to use as python type
            python_type = re.sub(r"^[a-zA-Z0-9_\.]+\.v1\.", "", descriptor.type_name)

        repeated = descriptor.label == FieldDescriptorProto.LABEL_REPEATED
        if repeated:
            # Update type for repeated fields
            python_type = f"List[{python_type}]"
            proto_type = f"repeated_{proto_type}"
            # Default value is None, since we can't use a mutable default value like []
            default_val = "None"

        # Calculate the tag for the field to save some computation at runtime
        tag = (descriptor.number << 3) | type_descriptor.wire_type.value
        if repeated and type_descriptor.wire_type != WireType.LEN:
            # Special case: repeated primitive fields are packed, so need to use LEN wire type
            # Note: packed fields can be disabled in proto files, but we don't handle that case
            # https://protobuf.dev/programming-guides/encoding/#packed
            tag = (descriptor.number << 3) | WireType.LEN.value
        # Convert the tag to a varint representation to inline it in the generated code
        tag = tag_to_repr_varint(tag)

        # For oneof and optional fields, we need to encode the presence of the field.
        # Optional fields are treated as virtual oneof fields, with a single field in the oneof.
        # For message fields, we need to encode the presence of the field if it is not None.
        # https://protobuf.dev/programming-guides/field_presence/
        encode_presence = group is not None or proto_type == "message"
        if group is not None:
            # The default value for oneof fields must be None, so that the default value is not encoded
            default_val = "None"

        field_name = descriptor.name
        attr_name = field_name
        generator = None
        if proto_type == "message" or repeated:
            # For message and repeated fields, store as a private attribute that is
            # initialized on access to match protobuf embedded message access pattern
            if repeated:
                # In python protobuf, repeated fields return an implementation of the list interface 
                # with a self.add() method to add and initialize elements
                # This can be supported with a custom list implementation, but we use a simple list for now
                # https://protobuf.dev/reference/python/python-generated/#repeated-message-fields
                generator = "list()"
            else:
                # https://protobuf.dev/reference/python/python-generated/#embedded_message
                generator = f"{python_type}()"
            # the attribute name is prefixed with an underscore as message and repeated attributes 
            # are hidden behind a property that has the actual proto field name
            attr_name = f"_{field_name}"

        # Inline the size and serialization functions for the field
        if INLINE_OPTIMIZATION:
            serialize_field_inline = inline_serialize_function(proto_type, attr_name, tag)
            size_field_inline = inline_size_function(proto_type, attr_name, tag)
        else:
            serialize_field_inline = f"self.serialize_{proto_type}(out, {tag}, self.{attr_name})"
            size_field_inline = f"size += self.size_{proto_type}({tag}, self.{attr_name})"

        serialize_field_inline = add_presence_check(proto_type, encode_presence, attr_name, serialize_field_inline)
        size_field_inline = add_presence_check(proto_type, encode_presence, attr_name, size_field_inline)

        return FieldTemplate(
            name=field_name,
            attr_name=attr_name,
            number=descriptor.number,
            generator=generator,
            python_type=python_type,
            proto_type=proto_type,
            default_val=default_val,
            serialize_field_inline=serialize_field_inline,
            size_field_inline=size_field_inline,
        )

@dataclass
class MessageTemplate:
    name: str
    super_class_init: str
    fields: List[FieldTemplate] = field(default_factory=list)
    enums: List[EnumTemplate] = field(default_factory=list)
    messages: List[MessageTemplate] = field(default_factory=list)

    @staticmethod
    def from_descriptor(descriptor: DescriptorProto) -> "MessageTemplate":
        # Helper function to extract the group name for a field, if it exists
        def get_group(field: FieldDescriptorProto) -> str:
            return descriptor.oneof_decl[field.oneof_index].name if field.HasField("oneof_index") else None
        fields = [FieldTemplate.from_descriptor(field, get_group(field)) for field in descriptor.field]
        fields.sort(key=lambda field: field.number)

        # Inline the superclass MessageMarshaler init function
        if INLINE_OPTIMIZATION:
            super_class_init = inline_init()
        else:
            super_class_init = "super().__init__()"

        name = descriptor.name
        return MessageTemplate(
            name=name,
            super_class_init=super_class_init,
            fields=fields,
            enums=[EnumTemplate.from_descriptor(enum) for enum in descriptor.enum_type],
            messages=[MessageTemplate.from_descriptor(message) for message in descriptor.nested_type],
        )

@dataclass
class FileTemplate:
    messages: List[MessageTemplate] = field(default_factory=list)
    enums: List[EnumTemplate] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    name: str = ""

    @staticmethod
    def from_descriptor(descriptor: FileDescriptorProto) -> "FileTemplate":

        # Extract the import paths for the proto file
        imports = []
        for dependency in descriptor.dependency:
            path = re.sub(r"\.proto$", "", dependency)
            if descriptor.name.startswith(path):
                continue
            path = path.replace("/", ".")
            path = f"{FILE_PATH_PREFIX}.{path}{FILE_NAME_SUFFIX}"
            imports.append(path)

        return FileTemplate(
            messages=[MessageTemplate.from_descriptor(message) for message in descriptor.message_type],
            enums=[EnumTemplate.from_descriptor(enum) for enum in descriptor.enum_type],
            imports=imports,
            name=descriptor.name,
        )

def main():
    request = plugin.CodeGeneratorRequest()
    request.ParseFromString(sys.stdin.buffer.read())

    response = plugin.CodeGeneratorResponse()
    # Needed since metrics.proto uses proto3 optional fields
    # https://github.com/protocolbuffers/protobuf/blob/main/docs/implementing_proto3_presence.md
    response.supported_features = plugin.CodeGeneratorResponse.FEATURE_PROTO3_OPTIONAL

    template_env = Environment(loader=FileSystemLoader(f"{os.path.dirname(os.path.realpath(__file__))}/templates"))
    jinja_body_template = template_env.get_template("template.py.jinja2")

    for proto_file in request.proto_file:
        file_name = re.sub(r"\.proto$", f"{FILE_NAME_SUFFIX}.py", proto_file.name)
        file_descriptor_proto = proto_file

        file_template = FileTemplate.from_descriptor(file_descriptor_proto)

        code = jinja_body_template.render(file_template=file_template)
        code = isort.api.sort_code_string(
            code = code,
            show_diff=False,
            profile="black",
            combine_as_imports=True,
            lines_after_imports=2,
            quiet=True,
            force_grid_wrap=2,
        )
        code = black.format_str(
            src_contents=code,
            mode=black.Mode(),
        )

        response_file = response.file.add()
        response_file.name = file_name
        response_file.content = code

    sys.stdout.buffer.write(response.SerializeToString())

if __name__ == '__main__':
    main()
