#!/usr/bin/env python3

import re
import os
import sys
import struct
import inspect
from enum import IntEnum
from typing import List, Optional, Union
from textwrap import dedent, indent
from dataclasses import dataclass, field
from snowflake.telemetry._internal.serialize import (
    Enum,
    MessageMarshaler,
    size_varint32,
    size_varint64,
    write_varint_unsigned
)

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

# 
# Size calculation functions
# 
self = MessageMarshaler() # Dummy object to allow caching in the inline functions

def size_bool(tag: bytes, _) -> int:
    return len(tag) + 1

def size_enum(tag: bytes, value: Union[Enum, int]) -> int:
    v = value
    if not isinstance(v, int):
        v = v.value
    return len(tag) + size_varint32(v)

def size_uint32(tag: bytes, value: int) -> int:
    return len(tag) + size_varint32(value)

def size_uint64(tag: bytes, value: int) -> int:
    return len(tag) + size_varint64(value)

def size_sint32(tag: bytes, value: int) -> int:
    return len(tag) + size_varint32(value << 1 if value >= 0 else (value << 1) ^ (~0))

def size_sint64(tag: bytes, value: int) -> int: 
    return len(tag) + size_varint64(value << 1 if value >= 0 else (value << 1) ^ (~0))

def size_int32(tag: bytes, value: int) -> int:
    return len(tag) + size_varint32(value + (1 << 32) if value < 0 else value)

def size_int64(tag: bytes, value: int) -> int:
    return len(tag) + size_varint64(value + (1 << 64) if value < 0 else value)

def size_float(tag: bytes, value: float) -> int:
    return len(tag) + 4

def size_double(tag: bytes, value: float) -> int:
    return len(tag) + 8

def size_fixed32(tag: bytes, value: int) -> int:
    return len(tag) + 4

def size_fixed64(tag: bytes, value: int) -> int:
    return len(tag) + 8

def size_sfixed32(tag: bytes, value: int) -> int:
    return len(tag) + 4

def size_sfixed64(tag: bytes, value: int) -> int:
    return len(tag) + 8

def size_bytes(tag: bytes, value: bytes) -> int:
    return len(tag) + size_varint32(len(value)) + len(value)

def size_string(tag: bytes, value: str) -> int:
    v = value.encode("utf-8")
    self._fieldname_encoded = v
    return len(tag) + size_varint32(len(v)) + len(v)

def size_message(tag: bytes, value: MessageMarshaler) -> int: 
    return len(tag) + size_varint32(value._get_size()) + value._get_size()

def size_repeated_message(tag: bytes, value: List[MessageMarshaler]) -> int:
    return sum(message._get_size() + len(tag) + size_varint32(message._get_size()) for message in value)

def size_repeated_double(tag: bytes, value: List[float]): 
    return len(tag) + len(value) * 8 + size_varint32(len(value) * 8)

def size_repeated_fixed64(tag: bytes, value: List[int]): 
    return len(tag) + len(value) * 8 + size_varint32(len(value) * 8)

def size_repeated_uint64(tag: bytes, value: List[int]):
    s = sum(size_varint64(uint32) for uint32 in value)
    self._fieldname_size = s
    return len(tag) + s + size_varint32(s)

# 
# Serialization functions
# 

def serialize_bool(out: bytearray, tag: bytes, value: bool) -> None:
    out += tag
    write_varint_unsigned(out, 1 if value else 0)

def serialize_enum(out: bytearray, tag: bytes, value: Union[Enum, int]) -> None:
    v = value
    if not isinstance(v, int):
        v = v.value
    out += tag
    write_varint_unsigned(out, v)

def serialize_uint32(out: bytearray, tag: bytes, value: int) -> None:
    out += tag
    write_varint_unsigned(out, value)

def serialize_uint64(out: bytearray, tag: bytes, value: int) -> None:
    out += tag
    write_varint_unsigned(out, value)

def serialize_sint32(out: bytearray, tag: bytes, value: int) -> None:
    out += tag
    write_varint_unsigned(out, value << 1 if value >= 0 else (value << 1) ^ (~0))

def serialize_sint64(out: bytearray, tag: bytes, value: int) -> None:
    out += tag
    write_varint_unsigned(out, value << 1 if value >= 0 else (value << 1) ^ (~0))

def serialize_int32(out: bytearray, tag: bytes, value: int) -> None:
    out += tag
    write_varint_unsigned(out, value + (1 << 32) if value < 0 else value)

def serialize_int64(out: bytearray, tag: bytes, value: int) -> None:
    out += tag
    write_varint_unsigned(out, value + (1 << 64) if value < 0 else value)

def serialize_fixed32(out: bytearray, tag: bytes, value: int) -> None:
    out += tag
    out += struct.pack("<I", value)

def serialize_fixed64(out: bytearray, tag: bytes, value: int) -> None:
    out += tag
    out += struct.pack("<Q", value)

def serialize_sfixed32(out: bytearray, tag: bytes, value: int) -> None:
    out += tag
    out += struct.pack("<i", value)

def serialize_sfixed64(out: bytearray, tag: bytes, value: int) -> None:
    out += tag
    out += struct.pack("<q", value)

def serialize_float(out: bytearray, tag: bytes, value: float) -> None:
    out += tag
    out += struct.pack("<f", value)

def serialize_double(out: bytearray, tag: bytes, value: float) -> None:
    out += tag
    out += struct.pack("<d", value)

def serialize_bytes(out: bytearray, tag: bytes, value: bytes) -> None:
    out += tag
    write_varint_unsigned(out, len(value))
    out += value

def serialize_string(out: bytearray, tag: bytes, value: str) -> None:
    v = self._fieldname_encoded
    out += tag
    write_varint_unsigned(out, len(v))
    out += v

def serialize_message(out: bytearray, tag: bytes, value: MessageMarshaler) -> None:
    out += tag
    write_varint_unsigned(out, value._get_size())
    value.write_to(out)

def serialize_repeated_message(out: bytearray, tag: bytes, value: List[MessageMarshaler]) -> None:
    for v in value:
        out += tag
        write_varint_unsigned(out, v._get_size())
        v.write_to(out)

def serialize_repeated_double(out: bytearray, tag: bytes, value: List[float]) -> None:
    out += tag
    write_varint_unsigned(out, len(value) * 8)
    for v in value:
        out += struct.pack("<d", v)

def serialize_repeated_fixed64(out: bytearray, tag: bytes, value: List[int]) -> None:
    out += tag
    write_varint_unsigned(out, len(value) * 8)
    for v in value:
        out += struct.pack("<Q", v)

def serialize_repeated_uint64(out: bytearray, tag: bytes, value: List[int]) -> None:
    out += tag
    write_varint_unsigned(out, self._fieldname_size)
    for v in value:
        write_varint_unsigned(out, v)

# 
# Inline utility functions
# 
def inline_size_function(proto_type: str, field_name: str, field_tag: str) -> str:
    function_definition = inspect.getsource(globals()[f"size_{proto_type}"])
    # Remove the function header and unindent the function body
    function_definition = function_definition.splitlines()[1:]
    function_definition = "\n".join(function_definition)
    function_definition = dedent(function_definition)
    # Replace the field name
    function_definition = function_definition.replace("value", f"self.{field_name}")
    function_definition = function_definition.replace("fieldname", field_name)
    # Replace the tag
    function_definition = function_definition.replace("tag", field_tag)
    # Inline the return statement
    function_definition = function_definition.replace("return ", "size += ")
    return function_definition

def inline_serialize_function(proto_type: str, field_name: str, field_tag: str) -> str:
    function_definition = inspect.getsource(globals()[f"serialize_{proto_type}"])
    # Remove the function header and unindent the function body
    function_definition = function_definition.splitlines()[1:]
    function_definition = "\n".join(function_definition)
    function_definition = dedent(function_definition)
    # Replace the field name
    function_definition = function_definition.replace("value", f"self.{field_name}")
    function_definition = function_definition.replace("fieldname", field_name)
    # Replace the tag
    function_definition = function_definition.replace("tag", field_tag)
    return function_definition

def add_presence_check(encode_presence: bool, field_name: str, function_definition: str) -> str:
    # oneof and optional (virtual oneof) field are encoded if they are not None
    function_definition = indent(function_definition, "    ")
    if encode_presence:
        return f"if self.{field_name} is not None:\n{function_definition}"
    return f"if self.{field_name}:\n{function_definition}"

# 
# Templating code
# 

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
    values: List["EnumValueTemplate"] = field(default_factory=list)

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
    number: int
    tag: str
    python_type: str
    proto_type: str
    repeated: bool
    group: str
    default_val: str
    encode_presence: bool
    serialize_field_inline: str
    size_field_inline: str

    @staticmethod
    def from_descriptor(descriptor: FieldDescriptorProto, group: Optional[str] = None) -> "FieldTemplate":
        repeated = descriptor.label == FieldDescriptorProto.LABEL_REPEATED
        type_descriptor = proto_type_to_descriptor[descriptor.type]

        python_type = type_descriptor.python_type
        proto_type = type_descriptor.name
        default_val = type_descriptor.default_val
        if proto_type == "message":
            python_type = re.sub(r"^[a-zA-Z0-9_\.]+\.v1\.", "", descriptor.type_name)

        if repeated:
            python_type = f"List[{python_type}]"
            proto_type = f"repeated_{proto_type}"
            default_val = "None"
        
        name = descriptor.name

        tag = (descriptor.number << 3) | type_descriptor.wire_type.value
        if repeated and type_descriptor.wire_type != WireType.LEN:
            # Special case: repeated primitive fields are packed
            # So we need to use the length-delimited wire type
            tag = (descriptor.number << 3) | WireType.LEN.value
        # Convert the tag to a varint representation
        # Saves us from having to calculate the tag at runtime
        tag = tag_to_repr_varint(tag)

        # For group / oneof fields, we need to encode the presence of the field
        # For message fields, we need to encode the presence of the field if it is not None
        encode_presence = group is not None or proto_type == "message"
        if group is not None:
            default_val = "None"
        
        serialize_field_inline = inline_serialize_function(proto_type, name, tag)
        serialize_field_inline = add_presence_check(encode_presence, name, serialize_field_inline)
        size_field_inline = inline_size_function(proto_type, name, tag)
        size_field_inline = add_presence_check(encode_presence, name, size_field_inline)

        return FieldTemplate(
            name=name,
            tag=tag,
            number=descriptor.number,
            python_type=python_type,
            proto_type=proto_type,
            repeated=repeated,
            group=group,
            default_val=default_val,
            encode_presence=encode_presence,
            serialize_field_inline=serialize_field_inline,
            size_field_inline=size_field_inline,
        )

@dataclass
class MessageTemplate:
    name: str
    fields: List[FieldTemplate] = field(default_factory=list)
    enums: List["EnumTemplate"] = field(default_factory=list)
    messages: List["MessageTemplate"] = field(default_factory=list)
    type_hints: List[str] = field(default_factory=list)

    @staticmethod
    def from_descriptor(descriptor: DescriptorProto) -> "MessageTemplate":
        def get_group(field: FieldDescriptorProto) -> str:
            return descriptor.oneof_decl[field.oneof_index].name if field.HasField("oneof_index") else None
        fields = [FieldTemplate.from_descriptor(field, get_group(field)) for field in descriptor.field]
        fields.sort(key=lambda field: field.number)

        name = descriptor.name
        return MessageTemplate(
            name=name,
            fields=fields,
            enums=[EnumTemplate.from_descriptor(enum) for enum in descriptor.enum_type],
            messages=[MessageTemplate.from_descriptor(message) for message in descriptor.nested_type],
        )

@dataclass
class FileTemplate:
    messages: List["MessageTemplate"] = field(default_factory=list)
    enums: List["EnumTemplate"] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    name: str = ""

    @staticmethod
    def from_descriptor(descriptor: FileDescriptorProto) -> "FileTemplate":
        imports = []
        for dependency in descriptor.dependency:
            path = re.sub(r"/[a-zA-Z0-9_]+\.proto$", "", dependency)
            if descriptor.name.startswith(path):
                continue
            path = path.replace("/", ".")
            path = "snowflake.telemetry._internal." + path
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
    # needed since metrics.proto uses proto3 optional fields
    response.supported_features = plugin.CodeGeneratorResponse.FEATURE_PROTO3_OPTIONAL

    template_env = Environment(loader=FileSystemLoader(f"{os.path.dirname(os.path.realpath(__file__))}/templates"))
    jinja_body_template = template_env.get_template("template.py.jinja2")

    for proto_file in request.proto_file:
        file_name = re.sub(r"[a-zA-Z0-9_]+\.proto$", "__init__.py", proto_file.name)
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
