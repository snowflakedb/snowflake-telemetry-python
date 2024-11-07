from __future__ import annotations

from enum import IntEnum

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
    def write_to(self, out: bytearray) -> None:
        ...
    
    def calculate_size(self) -> int:
        ...

    def _get_size(self) -> int:
        if not hasattr(self, "_size"):
            self._size = self.calculate_size()
        return self._size
    
    def __bytes__(self) -> bytes:
        self._get_size()
        stream = bytearray()
        self.write_to(stream)
        return bytes(stream)
    
    def SerializeToString(self) -> bytes:
        self._get_size()
        stream = bytearray()
        self.write_to(stream)
        return bytes(stream)
