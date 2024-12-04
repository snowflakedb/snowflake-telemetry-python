#
# Copyright (c) 2012-2024 Snowflake Computing Inc. All rights reserved.
#

from __future__ import annotations

import struct
from enum import IntEnum
from typing import List, Union, Dict, Any

# Alias Enum to IntEnum
Enum = IntEnum

# Static class to handle varint encoding
# There is code duplication for performance reasons
# https://developers.google.com/protocol-buffers/docs/encoding#varints
class Varint:
    @staticmethod
    def size_varint_u32(value: int) -> int:
        size = 1
        while value >= 128:
            value >>= 7
            size += 1
        return size

    size_varint_u64 = size_varint_u32

    @staticmethod
    def size_varint_i32(value: int) -> int:
        value = value + (1 << 32) if value < 0 else value
        size = 1
        while value >= 128:
            value >>= 7
            size += 1
        return size

    @staticmethod
    def size_varint_i64(value: int) -> int:
        value = value + (1 << 64) if value < 0 else value
        size = 1
        while value >= 128:
            value >>= 7
            size += 1
        return size

    @staticmethod
    def size_varint_s32(value: int) -> int:
        value = value << 1 if value >= 0 else (value << 1) ^ (~0)
        size = 1
        while value >= 128:
            value >>= 7
            size += 1
        return size

    size_varint_s64 = size_varint_s32

    @staticmethod
    def write_varint_u32(out: bytearray, value: int) -> None:
        while value >= 128:
            out.append((value & 0x7F) | 0x80)
            value >>= 7
        out.append(value)

    write_varint_u64 = write_varint_u32

    @staticmethod
    def write_varint_i32(out: bytearray, value: int) -> None:
        value = value + (1 << 32) if value < 0 else value
        while value >= 128:
            out.append((value & 0x7F) | 0x80)
            value >>= 7
        out.append(value)

    @staticmethod
    def write_varint_i64(out: bytearray, value: int) -> None:
        value = value + (1 << 64) if value < 0 else value
        while value >= 128:
            out.append((value & 0x7F) | 0x80)
            value >>= 7
        out.append(value)

    @staticmethod
    def write_varint_s32(out: bytearray, value: int) -> None:
        value = value << 1 if value >= 0 else (value << 1) ^ (~0)
        while value >= 128:
            out.append((value & 0x7F) | 0x80)
            value >>= 7
        out.append(value)

    write_varint_s64 = write_varint_s32

# Base class for all custom messages
class MessageMarshaler:
    # There is a high overhead for creating an empty dict
    # For this reason, the cache dict is lazily initialized
    @property
    def marshaler_cache(self) -> Dict[bytes, Any]:
        if not hasattr(self, "_marshaler_cache"):
            self._marshaler_cache = {}
        return self._marshaler_cache

    def write_to(self, out: bytearray) -> None:
        ...
    
    def calculate_size(self) -> int:
        ...

    def _get_size(self) -> int:
        if not hasattr(self, "_size"):
            self._size = self.calculate_size()
        return self._size
    
    def SerializeToString(self) -> bytes:
        # size MUST be calculated before serializing since some preprocessing is done
        self._get_size() 
        stream = bytearray()
        self.write_to(stream)
        return bytes(stream)
    
    def __bytes__(self) -> bytes:
        return self.SerializeToString()
    
    # The following size and serialize functions may be inlined by the code generator
    # The following strings are replaced by the code generator for inlining:
    #   - TAG
    #   - FIELD_ATTR

    def size_bool(self, TAG: bytes, _) -> int:
        return len(TAG) + 1

    def size_enum(self, TAG: bytes, FIELD_ATTR: Union[Enum, int]) -> int:
        v = FIELD_ATTR
        if not isinstance(v, int):
            v = v.value
        return len(TAG) + Varint.size_varint_u32(v)

    def size_uint32(self, TAG: bytes, FIELD_ATTR: int) -> int:
        return len(TAG) + Varint.size_varint_u32(FIELD_ATTR)

    def size_uint64(self, TAG: bytes, FIELD_ATTR: int) -> int:
        return len(TAG) + Varint.size_varint_u64(FIELD_ATTR)

    def size_sint32(self, TAG: bytes, FIELD_ATTR: int) -> int:
        return len(TAG) + Varint.size_varint_s32(FIELD_ATTR)

    def size_sint64(self, TAG: bytes, FIELD_ATTR: int) -> int: 
        return len(TAG) + Varint.size_varint_s64(FIELD_ATTR)

    def size_int32(self, TAG: bytes, FIELD_ATTR: int) -> int:
        return len(TAG) + Varint.size_varint_i32(FIELD_ATTR)

    def size_int64(self, TAG: bytes, FIELD_ATTR: int) -> int:
        return len(TAG) + Varint.size_varint_i64(FIELD_ATTR)

    def size_float(self, TAG: bytes, FIELD_ATTR: float) -> int:
        return len(TAG) + 4

    def size_double(self, TAG: bytes, FIELD_ATTR: float) -> int:
        return len(TAG) + 8

    def size_fixed32(self, TAG: bytes, FIELD_ATTR: int) -> int:
        return len(TAG) + 4

    def size_fixed64(self, TAG: bytes, FIELD_ATTR: int) -> int:
        return len(TAG) + 8

    def size_sfixed32(self, TAG: bytes, FIELD_ATTR: int) -> int:
        return len(TAG) + 4

    def size_sfixed64(self, TAG: bytes, FIELD_ATTR: int) -> int:
        return len(TAG) + 8

    def size_bytes(self, TAG: bytes, FIELD_ATTR: bytes) -> int:
        return len(TAG) + Varint.size_varint_u32(len(FIELD_ATTR)) + len(FIELD_ATTR)

    def size_string(self, TAG: bytes, FIELD_ATTR: str) -> int:
        v = FIELD_ATTR.encode("utf-8")
        return len(TAG) + Varint.size_varint_u32(len(v)) + len(v)

    def size_message(self, TAG: bytes, FIELD_ATTR: MessageMarshaler) -> int: 
        return len(TAG) + Varint.size_varint_u32(FIELD_ATTR._get_size()) + FIELD_ATTR._get_size()

    def size_repeated_message(self, TAG: bytes, FIELD_ATTR: List[MessageMarshaler]) -> int:
        return sum(message._get_size() + len(TAG) + Varint.size_varint_u32(message._get_size()) for message in FIELD_ATTR)

    def size_repeated_double(self, TAG: bytes, FIELD_ATTR: List[float]): 
        return len(TAG) + len(FIELD_ATTR) * 8 + Varint.size_varint_u32(len(FIELD_ATTR) * 8)

    def size_repeated_fixed64(self, TAG: bytes, FIELD_ATTR: List[int]): 
        return len(TAG) + len(FIELD_ATTR) * 8 + Varint.size_varint_u32(len(FIELD_ATTR) * 8)

    def size_repeated_uint64(self, TAG: bytes, FIELD_ATTR: List[int]):
        s = sum(Varint.size_varint_u64(uint64) for uint64 in FIELD_ATTR)
        self.marshaler_cache[TAG] = s
        return len(TAG) + s + Varint.size_varint_u32(s)

    def serialize_bool(self, out: bytearray, TAG: bytes, FIELD_ATTR: bool) -> None:
        out += TAG
        Varint.write_varint_u32(out, 1 if FIELD_ATTR else 0)

    def serialize_enum(self, out: bytearray, TAG: bytes, FIELD_ATTR: Union[Enum, int]) -> None:
        v = FIELD_ATTR
        if not isinstance(v, int):
            v = v.value
        out += TAG
        Varint.write_varint_u32(out, v)

    def serialize_uint32(self, out: bytearray, TAG: bytes, FIELD_ATTR: int) -> None:
        out += TAG
        Varint.write_varint_u32(out, FIELD_ATTR)

    def serialize_uint64(self, out: bytearray, TAG: bytes, FIELD_ATTR: int) -> None:
        out += TAG
        Varint.write_varint_u64(out, FIELD_ATTR)

    def serialize_sint32(self, out: bytearray, TAG: bytes, FIELD_ATTR: int) -> None:
        out += TAG
        Varint.write_varint_s32(out, FIELD_ATTR)

    def serialize_sint64(self, out: bytearray, TAG: bytes, FIELD_ATTR: int) -> None:
        out += TAG
        Varint.write_varint_s64(out, FIELD_ATTR)

    def serialize_int32(self, out: bytearray, TAG: bytes, FIELD_ATTR: int) -> None:
        out += TAG
        Varint.write_varint_i32(out, FIELD_ATTR)

    def serialize_int64(self, out: bytearray, TAG: bytes, FIELD_ATTR: int) -> None:
        out += TAG
        Varint.write_varint_i64(out, FIELD_ATTR)

    def serialize_fixed32(self, out: bytearray, TAG: bytes, FIELD_ATTR: int) -> None:
        out += TAG
        out += struct.pack("<I", FIELD_ATTR)

    def serialize_fixed64(self, out: bytearray, TAG: bytes, FIELD_ATTR: int) -> None:
        out += TAG
        out += struct.pack("<Q", FIELD_ATTR)

    def serialize_sfixed32(self, out: bytearray, TAG: bytes, FIELD_ATTR: int) -> None:
        out += TAG
        out += struct.pack("<i", FIELD_ATTR)

    def serialize_sfixed64(self, out: bytearray, TAG: bytes, FIELD_ATTR: int) -> None:
        out += TAG
        out += struct.pack("<q", FIELD_ATTR)

    def serialize_float(self, out: bytearray, TAG: bytes, FIELD_ATTR: float) -> None:
        out += TAG
        out += struct.pack("<f", FIELD_ATTR)

    def serialize_double(self, out: bytearray, TAG: bytes, FIELD_ATTR: float) -> None:
        out += TAG
        out += struct.pack("<d", FIELD_ATTR)

    def serialize_bytes(self, out: bytearray, TAG: bytes, FIELD_ATTR: bytes) -> None:
        out += TAG
        Varint.write_varint_u32(out, len(FIELD_ATTR))
        out += FIELD_ATTR

    def serialize_string(self, out: bytearray, TAG: bytes, FIELD_ATTR: str) -> None:
        v = FIELD_ATTR.encode("utf-8")
        out += TAG
        Varint.write_varint_u32(out, len(v))
        out += v

    def serialize_message(self, out: bytearray, TAG: bytes, FIELD_ATTR: MessageMarshaler) -> None:
        out += TAG
        Varint.write_varint_u32(out, FIELD_ATTR._get_size())
        FIELD_ATTR.write_to(out)

    def serialize_repeated_message(self, out: bytearray, TAG: bytes, FIELD_ATTR: List[MessageMarshaler]) -> None:
        for v in FIELD_ATTR:
            out += TAG
            Varint.write_varint_u32(out, v._get_size())
            v.write_to(out)

    def serialize_repeated_double(self, out: bytearray, TAG: bytes, FIELD_ATTR: List[float]) -> None:
        out += TAG
        Varint.write_varint_u32(out, len(FIELD_ATTR) * 8)
        for v in FIELD_ATTR:
            out += struct.pack("<d", v)

    def serialize_repeated_fixed64(self, out: bytearray, TAG: bytes, FIELD_ATTR: List[int]) -> None:
        out += TAG
        Varint.write_varint_u32(out, len(FIELD_ATTR) * 8)
        for v in FIELD_ATTR:
            out += struct.pack("<Q", v)

    def serialize_repeated_uint64(self, out: bytearray, TAG: bytes, FIELD_ATTR: List[int]) -> None:
        out += TAG
        Varint.write_varint_u32(out, self.marshaler_cache[TAG])
        for v in FIELD_ATTR:
            Varint.write_varint_u64(out, v)
