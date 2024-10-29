import struct
from enum import IntEnum
from typing import List, Union

Enum = IntEnum

class ProtoSerializer:
    __slots__ = ("out")

    def __init__(self) -> None:
        self.out = bytearray()

    def __bytes__(self) -> bytes:
        return bytes(self.out)

    def serialize_bool(self, tag: bytes, value: bool) -> None:
        self.out += tag
        self._write_varint_unsigned(1 if value else 0)

    def serialize_enum(self, tag: bytes, value: Union[Enum, int]) -> None:
        if not isinstance(value, int):
            value = value.value
        self.out += tag
        self._write_varint_unsigned(value)

    def serialize_uint32(self, tag: bytes, value: int) -> None:
        self.out += tag
        self._write_varint_unsigned(value)

    def serialize_uint64(self, tag: bytes, value: int) -> None:
        self.out += tag
        self._write_varint_unsigned(value)

    def serialize_sint32(self, tag: bytes, value: int) -> None:
        self.out += tag
        self._write_varint_unsigned(value << 1 if value >= 0 else (value << 1) ^ (~0))

    def serialize_sint64(self, tag: bytes, value: int) -> None:
        self.out += tag
        self._write_varint_unsigned(value << 1 if value >= 0 else (value << 1) ^ (~0))

    def serialize_int32(self, tag: bytes, value: int) -> None:
        self.out += tag
        self._write_varint_unsigned(value + (1 << 32) if value < 0 else value)

    def serialize_int64(self, tag: bytes, value: int) -> None:
        self.out += tag
        self._write_varint_unsigned(value + (1 << 64) if value < 0 else value)

    def serialize_fixed32(self, tag: bytes, value: int) -> None:
        self.out += tag
        self.out += struct.pack("<I", value)

    def serialize_fixed64(self, tag: bytes, value: int) -> None:
        self.out += tag
        self.out += struct.pack("<Q", value)

    def serialize_sfixed32(self, tag: bytes, value: int) -> None:
        self.out += tag
        self.out += struct.pack("<i", value)

    def serialize_sfixed64(self, tag: bytes, value: int) -> None:
        self.out += tag
        self.out += struct.pack("<q", value)

    def serialize_float(self, tag: bytes, value: float) -> None:
        self.out += tag
        self.out += struct.pack("<f", value)

    def serialize_double(self, tag: bytes, value: float) -> None:
        self.out += tag
        self.out += struct.pack("<d", value)

    def serialize_bytes(self, tag: bytes, value: bytes) -> None:
        self.out += tag
        self._write_varint_unsigned(len(value))
        self.out += value

    def serialize_string(self, tag: bytes, value: str) -> None:
        self.serialize_bytes(tag, value.encode("utf-8"))

    def serialize_message(
            self, 
            tag: bytes, 
            value: bytes,
        ) -> None:
        # If value is None, omit message entirely
        if value is None:
            return
        # Otherwise, write the message
        # Even if all fields are default (ommnited)
        # The presence of the message is still encoded
        self.out += tag
        self._write_varint_unsigned(len(value))
        self.out += value

    def serialize_repeated_message(
            self, 
            tag: bytes, 
            values: List[bytes],
        ) -> None:
        if not values:
            return
        # local reference to avoid repeated lookups
        _self_serialize = self.serialize_message
        for value in values:
            _self_serialize(tag, value)

    def serialize_repeated_double(self, tag: bytes, values: List[float]) -> None:
        if not values:
            return
        self.out += tag
        self._write_varint_unsigned(len(values) * 8)
        for value in values:
            self.write_double_no_tag(value)

    def serialize_repeated_fixed64(self, tag: bytes, values: List[int]) -> None:
        if not values:
            return
        self.out += tag
        self._write_varint_unsigned(len(values) * 8)
        for value in values:
            self.write_fixed64_no_tag(value)

    def serialize_repeated_uint64(self, tag: bytes, values: List[int]) -> None:
        if not values:
            return
        self.out += tag
        tmp = ProtoSerializer()
        for value in values:
            tmp._write_varint_unsigned(value)
        self._write_varint_unsigned(len(tmp.out))
        self.out += tmp.out

    def _write_varint_unsigned(self, value: int) -> None:
        while value >= 128:
            self.out.append((value & 0x7F) | 0x80)
            value >>= 7
        self.out.append(value)

    def write_double_no_tag(self, value: float) -> None:
        self.out += struct.pack("<d", value)

    def write_fixed64_no_tag(self, value: int) -> None:
        self.out += struct.pack("<Q", value)
