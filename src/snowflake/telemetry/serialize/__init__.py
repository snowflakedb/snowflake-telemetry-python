import struct
from enum import IntEnum
from typing import Callable, Any, List, Union

Enum = IntEnum

class MessageMarshaler:
    def __bytes__(self) -> bytes:
        out = ProtoSerializer()
        self.write_to(out)
        return bytes(out)

    def write_to(self, out: "ProtoSerializer") -> None:
        ...

class ProtoSerializer:
    __slots__ = ("out",)

    def __init__(self) -> None:
        self.out = bytearray()
    
    def __bytes__(self) -> bytes:
        return bytes(self.out)[::-1]
    
    def serialize_bool(self, tag: bytes, value: bool) -> None:
        _write_varint_unsigned(1 if value else 0, self.out)
        self.out.extend(tag[::-1])
    
    def serialize_enum(self, tag: bytes, value: Union[Enum, int]) -> None:
        if not isinstance(value, int):
            value = value.value
        _write_varint_unsigned(value, self.out)
        self.out.extend(tag[::-1])
    
    def serialize_uint32(self, tag: bytes, value: int) -> None:
        _write_varint_unsigned(value, self.out)
        self.out.extend(tag[::-1])
    
    def serialize_uint64(self, tag: bytes, value: int) -> None:
        _write_varint_unsigned(value, self.out)
        self.out.extend(tag[::-1])
    
    def serialize_sint32(self, tag: bytes, value: int) -> None:
        _write_varint_unsigned(encode_zigzag32(value), self.out)
        self.out.extend(tag[::-1])
    
    def serialize_sint64(self, tag: bytes, value: int) -> None:
        _write_varint_unsigned(encode_zigzag64(value), self.out)
        self.out.extend(tag[::-1])
    
    def serialize_int32(self, tag: bytes, value: int) -> None:
        _write_varint_signed(value, self.out)
        self.out.extend(tag[::-1])
    
    def serialize_int64(self, tag: bytes, value: int) -> None:
        _write_varint_signed(value, self.out)
        self.out.extend(tag[::-1])
    
    def serialize_fixed32(self, tag: bytes, value: int) -> None:
        self.out.extend(struct.pack("<I", value)[::-1])
        self.out.extend(tag[::-1])
    
    def serialize_fixed64(self, tag: bytes, value: int) -> None:
        self.out.extend(struct.pack("<Q", value)[::-1])
        self.out.extend(tag[::-1])
    
    def serialize_sfixed32(self, tag: bytes, value: int) -> None:
        self.out.extend(struct.pack("<i", value)[::-1])
        self.out.extend(tag[::-1])
    
    def serialize_sfixed64(self, tag: bytes, value: int) -> None:
        self.out.extend(struct.pack("<q", value)[::-1])
        self.out.extend(tag[::-1])
    
    def serialize_float(self, tag: bytes, value: float) -> None:
        self.out.extend(struct.pack("<f", value)[::-1])
        self.out.extend(tag[::-1])
    
    def serialize_double(self, tag: bytes, value: float) -> None:
        self.out.extend(struct.pack("<d", value)[::-1])
        self.out.extend(tag[::-1])
    
    def serialize_bytes(self, tag: bytes, value: bytes) -> None:
        self.out.extend(value[::-1])
        _write_varint_unsigned(len(value), self.out)
        self.out.extend(tag[::-1])
    
    def serialize_string(self, tag: bytes, value: str) -> None:
        self.serialize_bytes(tag, value.encode("utf-8"))

    def serialize_message(
            self, 
            tag: bytes, 
            value: MessageMarshaler,
        ) -> None:
        # If value is None, omit message entirely
        if value is None:
            return
        # Otherwise, write the message
        # Even if all fields are default (ommnited)
        # The presence of the message is still encoded
        before = len(self.out)
        value.write_to(self)
        after = len(self.out)
        _write_varint_unsigned(after - before, self.out)
        self.out.extend(tag[::-1])

    def serialize_repeated_message(
            self, 
            tag: bytes, 
            values: List[MessageMarshaler],
        ) -> None:
        if not values:
            return
        # local reference to avoid repeated lookups
        _self_serialize = self.serialize_message
        for value in reversed(values):
            _self_serialize(tag, value)
    
    def serialize_repeated_packed(
            self, 
            tag: bytes, 
            values: List[Any],
            write_value: Callable[[Any, bytearray], None],
        ) -> None:
        if not values:
            return
        # Packed repeated fields are encoded like a bytearray
        # with a total size prefix and a single tag
        # (similar to a bytes field)
        before = len(self.out)
        for value in reversed(values):
            write_value(value, self.out)
        after = len(self.out)
        _write_varint_unsigned(after - before, self.out)
        self.out.extend(tag[::-1])
    
    def serialize_repeated_double(self, tag: bytes, values: List[float]) -> None:
        self.serialize_repeated_packed(tag, values, write_double_no_tag)
    
    def serialize_repeated_fixed64(self, tag: bytes, values: List[int]) -> None:
        self.serialize_repeated_packed(tag, values, write_fixed64_no_tag)
    
    def serialize_repeated_uint64(self, tag: bytes, values: List[int]) -> None:
        self.serialize_repeated_packed(tag, values, _write_varint_unsigned)

def _write_varint_signed(value: int, out: bytearray) -> None:
    if value < 0:
        value += 1 << 64
    _write_varint_unsigned(value, out)

def _write_varint_unsigned(value: int, out: bytearray) -> None:
    i = len(out)
    while value >= 128:
        out.insert(i, (value & 0x7F) | 0x80)
        value >>= 7
    out.insert(i, value)

def write_tag(tag: bytes, out: bytearray) -> None:
    out.extend(tag[::-1])

def write_double_no_tag(value: float, out: bytearray) -> None:
    out.extend(struct.pack("<d", value)[::-1])

def write_fixed64_no_tag(value: int, out: bytearray) -> None:
    out.extend(struct.pack("<Q", value)[::-1])

def encode_zigzag32(value: int) -> int:
    return value << 1 if value >= 0 else (value << 1) ^ (~0)

def encode_zigzag64(value: int) -> int:
    return value << 1 if value >= 0 else (value << 1) ^ (~0)
