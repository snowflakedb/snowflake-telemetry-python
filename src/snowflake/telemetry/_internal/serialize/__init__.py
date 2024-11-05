from __future__ import annotations

from enum import IntEnum

def size_varint32(value: int) -> int:
    size = 1
    while value >= 128:
        value >>= 7
        size += 1
    return size

def size_varint64(value: int) -> int:
    size = 1
    while value >= 128:
        value >>= 7
        size += 1
    return size

def write_varint_unsigned(out: bytearray, value: int) -> None:
    while value >= 128:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)

Enum = IntEnum

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
