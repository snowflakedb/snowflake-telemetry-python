# Generated by the protoc compiler with a custom plugin. DO NOT EDIT!
# sources: opentelemetry/proto/common/v1/common.proto

from typing import (
    List,
    Optional,
)

from snowflake.telemetry._internal.serialize import (
    Enum,
    ProtoSerializer,
)


def AnyValue(
    string_value: Optional[str] = None,
    bool_value: Optional[bool] = None,
    int_value: Optional[int] = None,
    double_value: Optional[float] = None,
    array_value: Optional[bytes] = None,
    kvlist_value: Optional[bytes] = None,
    bytes_value: Optional[bytes] = None,
) -> bytes:
    proto_serializer = ProtoSerializer()
    if string_value is not None:  # oneof group value
        proto_serializer.serialize_string(b"\n", string_value)
    if bool_value is not None:  # oneof group value
        proto_serializer.serialize_bool(b"\x10", bool_value)
    if int_value is not None:  # oneof group value
        proto_serializer.serialize_int64(b"\x18", int_value)
    if double_value is not None:  # oneof group value
        proto_serializer.serialize_double(b"!", double_value)
    if array_value is not None:  # oneof group value
        proto_serializer.serialize_message(b"*", array_value)
    if kvlist_value is not None:  # oneof group value
        proto_serializer.serialize_message(b"2", kvlist_value)
    if bytes_value is not None:  # oneof group value
        proto_serializer.serialize_bytes(b":", bytes_value)
    return proto_serializer.out


def ArrayValue(
    values: Optional[List[bytes]] = None,
) -> bytes:
    proto_serializer = ProtoSerializer()
    if values:
        proto_serializer.serialize_repeated_message(b"\n", values)
    return proto_serializer.out


def KeyValueList(
    values: Optional[List[bytes]] = None,
) -> bytes:
    proto_serializer = ProtoSerializer()
    if values:
        proto_serializer.serialize_repeated_message(b"\n", values)
    return proto_serializer.out


def KeyValue(
    key: Optional[str] = None,
    value: Optional[bytes] = None,
) -> bytes:
    proto_serializer = ProtoSerializer()
    if key:
        proto_serializer.serialize_string(b"\n", key)
    if value is not None:
        proto_serializer.serialize_message(b"\x12", value)
    return proto_serializer.out


def InstrumentationScope(
    name: Optional[str] = None,
    version: Optional[str] = None,
    attributes: Optional[List[bytes]] = None,
    dropped_attributes_count: Optional[int] = None,
) -> bytes:
    proto_serializer = ProtoSerializer()
    if name:
        proto_serializer.serialize_string(b"\n", name)
    if version:
        proto_serializer.serialize_string(b"\x12", version)
    if attributes:
        proto_serializer.serialize_repeated_message(b"\x1a", attributes)
    if dropped_attributes_count:
        proto_serializer.serialize_uint32(b" ", dropped_attributes_count)
    return proto_serializer.out