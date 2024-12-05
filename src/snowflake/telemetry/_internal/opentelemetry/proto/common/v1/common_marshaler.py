# Generated by the protoc compiler with a custom plugin. DO NOT EDIT!
# sources: opentelemetry/proto/common/v1/common.proto
#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#
# Copyright 2019, OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This file has been generated from the original proto definition at
#
#     https://github.com/open-telemetry/opentelemetry-proto
#
# using a custom protoc compiler plugin by Snowflake Computing Inc.

from __future__ import annotations

import struct
from typing import List

from snowflake.telemetry._internal.serialize import (
    Enum,
    MessageMarshaler,
    Varint,
)


class AnyValue(MessageMarshaler):
    string_value: str
    bool_value: bool
    int_value: int
    double_value: float

    @property
    def array_value(self) -> ArrayValue:
        if self._array_value is None:
            self._array_value = ArrayValue()
        return self._array_value

    @property
    def kvlist_value(self) -> KeyValueList:
        if self._kvlist_value is None:
            self._kvlist_value = KeyValueList()
        return self._kvlist_value

    bytes_value: bytes

    def __init__(
        self,
        string_value: str = None,
        bool_value: bool = None,
        int_value: int = None,
        double_value: float = None,
        array_value: ArrayValue = None,
        kvlist_value: KeyValueList = None,
        bytes_value: bytes = None,
    ):
        self.string_value: str = string_value
        self.bool_value: bool = bool_value
        self.int_value: int = int_value
        self.double_value: float = double_value
        self._array_value: ArrayValue = array_value
        self._kvlist_value: KeyValueList = kvlist_value
        self.bytes_value: bytes = bytes_value

    def calculate_size(self) -> int:
        size = 0
        if self.string_value is not None:
            v = self.string_value.encode("utf-8")
            size += len(b"\n") + Varint.size_varint_u32(len(v)) + len(v)
        if self.bool_value is not None:
            size += len(b"\x10") + 1
        if self.int_value is not None:
            size += len(b"\x18") + Varint.size_varint_i64(self.int_value)
        if self.double_value is not None:
            size += len(b"!") + 8
        if self._array_value is not None:
            size += (
                len(b"*")
                + Varint.size_varint_u32(self._array_value._get_size())
                + self._array_value._get_size()
            )
        if self._kvlist_value is not None:
            size += (
                len(b"2")
                + Varint.size_varint_u32(self._kvlist_value._get_size())
                + self._kvlist_value._get_size()
            )
        if self.bytes_value is not None:
            size += (
                len(b":")
                + Varint.size_varint_u32(len(self.bytes_value))
                + len(self.bytes_value)
            )
        return size

    def write_to(self, out: bytearray) -> None:
        if self.string_value is not None:
            v = self.string_value.encode("utf-8")
            out += b"\n"
            Varint.write_varint_u32(out, len(v))
            out += v
        if self.bool_value is not None:
            out += b"\x10"
            Varint.write_varint_u32(out, 1 if self.bool_value else 0)
        if self.int_value is not None:
            out += b"\x18"
            Varint.write_varint_i64(out, self.int_value)
        if self.double_value is not None:
            out += b"!"
            out += struct.pack("<d", self.double_value)
        if self._array_value is not None:
            out += b"*"
            Varint.write_varint_u32(out, self._array_value._get_size())
            self._array_value.write_to(out)
        if self._kvlist_value is not None:
            out += b"2"
            Varint.write_varint_u32(out, self._kvlist_value._get_size())
            self._kvlist_value.write_to(out)
        if self.bytes_value is not None:
            out += b":"
            Varint.write_varint_u32(out, len(self.bytes_value))
            out += self.bytes_value


class ArrayValue(MessageMarshaler):
    @property
    def values(self) -> List[AnyValue]:
        if self._values is None:
            self._values = list()
        return self._values

    def __init__(
        self,
        values: List[AnyValue] = None,
    ):
        self._values: List[AnyValue] = values

    def calculate_size(self) -> int:
        size = 0
        if self._values:
            size += sum(
                message._get_size()
                + len(b"\n")
                + Varint.size_varint_u32(message._get_size())
                for message in self._values
            )
        return size

    def write_to(self, out: bytearray) -> None:
        if self._values:
            for v in self._values:
                out += b"\n"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)


class KeyValueList(MessageMarshaler):
    @property
    def values(self) -> List[KeyValue]:
        if self._values is None:
            self._values = list()
        return self._values

    def __init__(
        self,
        values: List[KeyValue] = None,
    ):
        self._values: List[KeyValue] = values

    def calculate_size(self) -> int:
        size = 0
        if self._values:
            size += sum(
                message._get_size()
                + len(b"\n")
                + Varint.size_varint_u32(message._get_size())
                for message in self._values
            )
        return size

    def write_to(self, out: bytearray) -> None:
        if self._values:
            for v in self._values:
                out += b"\n"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)


class KeyValue(MessageMarshaler):
    key: str

    @property
    def value(self) -> AnyValue:
        if self._value is None:
            self._value = AnyValue()
        return self._value

    def __init__(
        self,
        key: str = "",
        value: AnyValue = None,
    ):
        self.key: str = key
        self._value: AnyValue = value

    def calculate_size(self) -> int:
        size = 0
        if self.key:
            v = self.key.encode("utf-8")
            size += len(b"\n") + Varint.size_varint_u32(len(v)) + len(v)
        if self._value is not None:
            size += (
                len(b"\x12")
                + Varint.size_varint_u32(self._value._get_size())
                + self._value._get_size()
            )
        return size

    def write_to(self, out: bytearray) -> None:
        if self.key:
            v = self.key.encode("utf-8")
            out += b"\n"
            Varint.write_varint_u32(out, len(v))
            out += v
        if self._value is not None:
            out += b"\x12"
            Varint.write_varint_u32(out, self._value._get_size())
            self._value.write_to(out)


class InstrumentationScope(MessageMarshaler):
    name: str
    version: str

    @property
    def attributes(self) -> List[KeyValue]:
        if self._attributes is None:
            self._attributes = list()
        return self._attributes

    dropped_attributes_count: int

    def __init__(
        self,
        name: str = "",
        version: str = "",
        attributes: List[KeyValue] = None,
        dropped_attributes_count: int = 0,
    ):
        self.name: str = name
        self.version: str = version
        self._attributes: List[KeyValue] = attributes
        self.dropped_attributes_count: int = dropped_attributes_count

    def calculate_size(self) -> int:
        size = 0
        if self.name:
            v = self.name.encode("utf-8")
            size += len(b"\n") + Varint.size_varint_u32(len(v)) + len(v)
        if self.version:
            v = self.version.encode("utf-8")
            size += len(b"\x12") + Varint.size_varint_u32(len(v)) + len(v)
        if self._attributes:
            size += sum(
                message._get_size()
                + len(b"\x1a")
                + Varint.size_varint_u32(message._get_size())
                for message in self._attributes
            )
        if self.dropped_attributes_count:
            size += len(b" ") + Varint.size_varint_u32(self.dropped_attributes_count)
        return size

    def write_to(self, out: bytearray) -> None:
        if self.name:
            v = self.name.encode("utf-8")
            out += b"\n"
            Varint.write_varint_u32(out, len(v))
            out += v
        if self.version:
            v = self.version.encode("utf-8")
            out += b"\x12"
            Varint.write_varint_u32(out, len(v))
            out += v
        if self._attributes:
            for v in self._attributes:
                out += b"\x1a"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)
        if self.dropped_attributes_count:
            out += b" "
            Varint.write_varint_u32(out, self.dropped_attributes_count)
