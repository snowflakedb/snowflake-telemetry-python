from abc import ABC
import dataclasses
import datetime
import enum
from io import BytesIO
import struct
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterable,
    Optional,
    Set, 
    Tuple,
    Type
)

if TYPE_CHECKING:
    from _typeshed import (
        SupportsRead,
        SupportsWrite,
    )

# Proto 3 data types
TYPE_ENUM = "enum"
TYPE_BOOL = "bool"
TYPE_INT32 = "int32"
TYPE_INT64 = "int64"
TYPE_UINT32 = "uint32"
TYPE_UINT64 = "uint64"
TYPE_SINT32 = "sint32"
TYPE_SINT64 = "sint64"
TYPE_FLOAT = "float"
TYPE_DOUBLE = "double"
TYPE_FIXED32 = "fixed32"
TYPE_SFIXED32 = "sfixed32"
TYPE_FIXED64 = "fixed64"
TYPE_SFIXED64 = "sfixed64"
TYPE_STRING = "string"
TYPE_BYTES = "bytes"
TYPE_MESSAGE = "message"
TYPE_MAP = "map"

# Fields that use a fixed amount of space (4 or 8 bytes)
FIXED_TYPES = [
    TYPE_FLOAT,
    TYPE_DOUBLE,
    TYPE_FIXED32,
    TYPE_SFIXED32,
    TYPE_FIXED64,
    TYPE_SFIXED64,
]

# Fields that are numerical 64-bit types
INT_64_TYPES = [TYPE_INT64, TYPE_UINT64, TYPE_SINT64, TYPE_FIXED64, TYPE_SFIXED64]

# Fields that are efficiently packed when
PACKED_TYPES = [
    TYPE_ENUM,
    TYPE_BOOL,
    TYPE_INT32,
    TYPE_INT64,
    TYPE_UINT32,
    TYPE_UINT64,
    TYPE_SINT32,
    TYPE_SINT64,
    TYPE_FLOAT,
    TYPE_DOUBLE,
    TYPE_FIXED32,
    TYPE_SFIXED32,
    TYPE_FIXED64,
    TYPE_SFIXED64,
]

# Wire types
# https://developers.google.com/protocol-buffers/docs/encoding#structure
WIRE_VARINT = 0
WIRE_FIXED_64 = 1
WIRE_LEN_DELIM = 2
WIRE_FIXED_32 = 5

# Mappings of which Proto 3 types correspond to which wire types.
WIRE_VARINT_TYPES = [
    TYPE_ENUM,
    TYPE_BOOL,
    TYPE_INT32,
    TYPE_INT64,
    TYPE_UINT32,
    TYPE_UINT64,
    TYPE_SINT32,
    TYPE_SINT64,
]
WIRE_FIXED_32_TYPES = [
    TYPE_FLOAT, 
    TYPE_FIXED32, 
    TYPE_SFIXED32
]
WIRE_FIXED_64_TYPES = [
    TYPE_DOUBLE, 
    TYPE_FIXED64, 
    TYPE_SFIXED64
]
WIRE_LEN_DELIM_TYPES = [
    TYPE_STRING, 
    TYPE_BYTES, 
    TYPE_MESSAGE, 
    TYPE_MAP
]

SIZE_DELIMITED = -1

PLACEHOLDER: Any = object()

@dataclasses.dataclass(frozen=True)
class FieldMetadata:
    number: int
    proto_type: str
    map_types: Optional[Tuple[str, str]] = None
    group: Optional[str] = None
    wraps: Optional[str] = None
    optional: Optional[bool] = False

def dataclass_field(
    number: int, 
    proto_type: str, 
    *,
    map_types: Optional[Tuple[str, str]] = None,
    group: Optional[str] = None, 
    wraps: Optional[str] = None,
    optional: Optional[bool] = False
) -> FieldMetadata:
    default=None if optional else PLACEHOLDER,
    return dataclasses.field(
        default=default,
        metadata=FieldMetadata(number, proto_type, map_types=map_types, group=group, wraps=wraps, optional=optional)
    )

def enum_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_ENUM, group=group, optional=optional)

def bool_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_BOOL, group=group, optional=optional)

def int32_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_INT32, group=group, optional=optional)

def int64_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_INT64, group=group, optional=optional)

def uint32_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_UINT32, group=group, optional=optional)

def uint64_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_UINT64, group=group, optional=optional)

def sint32_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_SINT32, group=group, optional=optional)

def sint64_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_SINT64, group=group, optional=optional)

def float_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_FLOAT, group=group, optional=optional)

def double_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_DOUBLE, group=group, optional=optional)

def fixed32_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_FIXED32, group=group, optional=optional)

def sfixed32_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_SFIXED32, group=group, optional=optional)

def fixed64_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_FIXED64, group=group, optional=optional)

def sfixed64_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_SFIXED64, group=group, optional=optional)

def string_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_STRING, group=group, optional=optional)

def bytes_field(number: int, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_BYTES, group=group, optional=optional)

def message_field(number: int, group: Optional[str] = None, wraps: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_MESSAGE, group=group, wraps=wraps, optional=optional)

def map_field(number: int, key_type: str, value_type: str, group: Optional[str] = None, optional: bool = False) -> FieldMetadata:
    return dataclass_field(number, TYPE_MAP, map_types=(key_type, value_type), group=group, optional=optional)

def _pack_fmt(proto_type: str) -> str:
    """Returns a little-endian format string for reading/writing binary."""
    return {
        TYPE_DOUBLE: "<d",
        TYPE_FLOAT: "<f",
        TYPE_FIXED32: "<I",
        TYPE_FIXED64: "<Q",
        TYPE_SFIXED32: "<i",
        TYPE_SFIXED64: "<q",
    }[proto_type]

def dump_varint(value: int, stream: 'SupportsWrite[bytes]') -> None:
    """Encodes a single varint and dumps it into the provided stream."""
    if value < -(1 << 63):
        raise ValueError(
            "Negative value is not representable as a 64-bit integer - unable to encode a varint within 10 bytes."
        )
    elif value < 0:
        value += 1 << 64

    bits = value & 0x7F
    value >>= 7
    while value:
        stream.write((0x80 | bits).to_bytes(1, "little"))
        bits = value & 0x7F
        value >>= 7
    stream.write(bits.to_bytes(1, "little"))

def encode_varint(value: int) -> bytes:
    """Encodes a single varint value for serialization."""
    with BytesIO() as stream:
        dump_varint(value, stream)
        return stream.getvalue()

def _preprocess_single(proto_type: str, wraps: str, value: Any) -> bytes:
    """Adjusts values before serialization."""
    if proto_type in (
        TYPE_ENUM,
        TYPE_BOOL,
        TYPE_INT32,
        TYPE_INT64,
        TYPE_UINT32,
        TYPE_UINT64,
    ):
        return encode_varint(value)
    elif proto_type in (TYPE_SINT32, TYPE_SINT64):
        # Handle zig-zag encoding.
        return encode_varint(value << 1 if value >= 0 else (value << 1) ^ (~0))
    elif proto_type in FIXED_TYPES:
        return struct.pack(_pack_fmt(proto_type), value)
    elif proto_type == TYPE_STRING:
        return value.encode("utf-8")
    elif proto_type == TYPE_MESSAGE:
        # if isinstance(value, datetime):
        #     # Convert the `datetime` to a timestamp message.
        #     value = _Timestamp.from_datetime(value)
        # elif isinstance(value, datetime.timedelta):
        #     # Convert the `timedelta` to a duration message.
        #     value = _Duration.from_timedelta(value)
        # elif wraps:
        #     if value is None:
        #         return b""
        #     value = _get_wrapper(wraps)(value=value)

        return bytes(value)

    return value

def _serialize_single(
    field_number: int,
    proto_type: str,
    value: Any,
    *,
    serialize_empty: bool = False,
    wraps: str = "",
) -> bytes:
    """Serializes a single field and value."""
    value = _preprocess_single(proto_type, wraps, value)

    output = bytearray()
    if proto_type in WIRE_VARINT_TYPES:
        key = encode_varint(field_number << 3)
        output += key + value
    elif proto_type in WIRE_FIXED_32_TYPES:
        key = encode_varint((field_number << 3) | 5)
        output += key + value
    elif proto_type in WIRE_FIXED_64_TYPES:
        key = encode_varint((field_number << 3) | 1)
        output += key + value
    elif proto_type in WIRE_LEN_DELIM_TYPES:
        if len(value) or serialize_empty or wraps:
            key = encode_varint((field_number << 3) | 2)
            output += key + encode_varint(len(value)) + value
    else:
        raise NotImplementedError(proto_type)

    return bytes(output)

class ProtoClassMetadata:
    __slots__ = (
        "oneof_group_by_field",
        "oneof_field_by_group",
        "default_gen",
        "cls_by_field",
        "field_name_by_number",
        "meta_by_field_name",
        "sorted_field_names",
    )

    oneof_group_by_field: Dict[str, str]
    oneof_field_by_group: Dict[str, Set[dataclasses.Field]]
    field_name_by_number: Dict[int, str]
    meta_by_field_name: Dict[str, FieldMetadata]
    sorted_field_names: Tuple[str, ...]
    default_gen: Dict[str, Callable[[], Any]]
    cls_by_field: Dict[str, Type]

    def __init__(self, cls: Type['Message']):
        by_field = {}
        by_group: Dict[str, Set] = {}
        by_field_name = {}
        by_field_number = {}

        fields = dataclasses.fields(cls)
        for field in fields:
            meta = FieldMetadata.get(field)

            if meta.group:
                # This is part of a one-of group.
                by_field[field.name] = meta.group

                by_group.setdefault(meta.group, set()).add(field)

            by_field_name[field.name] = meta
            by_field_number[meta.number] = field.name

        self.oneof_group_by_field = by_field
        self.oneof_field_by_group = by_group
        self.field_name_by_number = by_field_number
        self.meta_by_field_name = by_field_name
        self.sorted_field_names = tuple(
            by_field_number[number] for number in sorted(by_field_number)
        )
        self.default_gen = self._get_default_gen(cls, fields)
        self.cls_by_field = self._get_cls_by_field(cls, fields)

    @staticmethod
    def _get_default_gen(
        cls: Type['Message'], fields: Iterable[dataclasses.Field]
    ) -> Dict[str, Callable[[], Any]]:
        return {field.name: cls._get_field_default_gen(field) for field in fields}

    @staticmethod
    def _get_cls_by_field(
        cls: Type['Message'], fields: Iterable[dataclasses.Field]
    ) -> Dict[str, Type]:
        field_cls = {}

        for field in fields:
            meta = FieldMetadata.get(field)
            if meta.proto_type == TYPE_MAP:
                assert meta.map_types
                kt = cls._cls_for(field, index=0)
                vt = cls._cls_for(field, index=1)
                field_cls[field.name] = dataclasses.make_dataclass(
                    "Entry",
                    [
                        ("key", kt, dataclass_field(1, meta.map_types[0])),
                        ("value", vt, dataclass_field(2, meta.map_types[1])),
                    ],
                    bases=(Message,),
                )
                field_cls[f"{field.name}.value"] = vt
            else:
                field_cls[field.name] = cls._cls_for(field)

        return field_cls

class Message(ABC):
    """
    The base class for protobuf messages, all generated messages will inherit from
    this. This class registers the message fields which are used by the serializers and
    parsers to go between the Python, binary and JSON representations of the message.
    """

    _serialized_on_wire: bool
    _unknown_fields: bytes
    _group_current: Dict[str, str]
    _meta: ClassVar[ProtoClassMetadata]

    def __post_init__(self) -> None:
        # Keep track of whether every field was default
        all_sentinel = True

        # Set current field of each group after `__init__` has already been run.
        group_current: Dict[str, Optional[str]] = {}
        for field_name, meta in self._meta.meta_by_field_name.items():
            if meta.group:
                group_current.setdefault(meta.group)

            value = self.__raw_get(field_name)
            if value is not PLACEHOLDER and not (meta.optional and value is None):
                # Found a non-sentinel value
                all_sentinel = False

                if meta.group:
                    # This was set, so make it the selected value of the one-of.
                    group_current[meta.group] = field_name

        # Now that all the defaults are set, reset it!
        self.__dict__["_serialized_on_wire"] = not all_sentinel
        self.__dict__["_unknown_fields"] = b""
        self.__dict__["_group_current"] = group_current
    

    def dump(self, buf: 'SupportsWrite[bytes]', delimit: bool = False) -> None:
        """
        Dumps the binary encoded Protobuf message to the stream.

        Parameters
        -----------
        stream: :class:`BinaryIO`
            The stream to dump the message to.
        delimit:
            Whether to prefix the message with a varint declaring its size.
        """
        with BytesIO() as stream:
            for field_name, meta in self._betterproto.meta_by_field_name.items():
                try:
                    value = getattr(self, field_name)
                except AttributeError:
                    continue

                if value is None:
                    # Optional items should be skipped. This is used for the Google
                    # wrapper types and proto3 field presence/optional fields.
                    continue

                # Being selected in a group means this field is the one that is
                # currently set in a `oneof` group, so it must be serialized even
                # if the value is the default zero value.
                #
                # Note that proto3 field presence/optional fields are put in a
                # synthetic single-item oneof by protoc, which helps us ensure we
                # send the value even if the value is the default zero value.
                selected_in_group = bool(meta.group) or meta.optional

                # Empty messages can still be sent on the wire if they were
                # set (or received empty).
                serialize_empty = isinstance(value, Message) and value._serialized_on_wire

                include_default_value_for_oneof = self._include_default_value_for_oneof(
                    field_name=field_name, meta=meta
                )

                if value == self._get_field_default(field_name) and not (
                    selected_in_group or serialize_empty or include_default_value_for_oneof
                ):
                    # Default (zero) values are not serialized. Two exceptions are
                    # if this is the selected oneof item or if we know we have to
                    # serialize an empty message (i.e. zero value was explicitly
                    # set by the user).
                    continue

                if isinstance(value, list):
                    if meta.proto_type in PACKED_TYPES:
                        # Packed lists look like a length-delimited field. First,
                        # preprocess/encode each value into a buffer and then
                        # treat it like a field of raw bytes.
                        buf = bytearray()
                        for item in value:
                            buf += _preprocess_single(meta.proto_type, "", item)
                        stream.write(_serialize_single(meta.number, TYPE_BYTES, buf))
                    else:
                        for item in value:
                            stream.write(
                                _serialize_single(
                                    meta.number,
                                    meta.proto_type,
                                    item,
                                    wraps=meta.wraps or "",
                                    serialize_empty=True,
                                )
                                # if it's an empty message it still needs to be represented
                                # as an item in the repeated list
                                or b"\n\x00"
                            )

                elif isinstance(value, dict):
                    for k, v in value.items():
                        assert meta.map_types
                        sk = _serialize_single(1, meta.map_types[0], k)
                        sv = _serialize_single(2, meta.map_types[1], v)
                        stream.write(
                            _serialize_single(meta.number, meta.proto_type, sk + sv)
                        )
                else:
                    # If we have an empty string and we're including the default value for
                    # a oneof, make sure we serialize it. This ensures that the byte string
                    # output isn't simply an empty string. This also ensures that round trip
                    # serialization will keep `which_one_of` calls consistent.
                    if (
                        isinstance(value, str)
                        and value == ""
                        and include_default_value_for_oneof
                    ):
                        serialize_empty = True

                    stream.write(
                        _serialize_single(
                            meta.number,
                            meta.proto_type,
                            value,
                            serialize_empty=serialize_empty or bool(selected_in_group),
                            wraps=meta.wraps or "",
                        )
                    )
            
            if delimit == SIZE_DELIMITED:
                dump_varint(len(stream), buf)
            buf.write(stream.getvalue())
        buf.write(self._unknown_fields)

    def __bytes__(self) -> bytes:
        """
        Get the binary encoded Protobuf representation of this message instance.
        """
        with BytesIO() as stream:
            self.dump(stream)
            return stream.getvalue()

    # For compatibility with other libraries
    def SerializeToString(self) -> bytes:
        """
        Get the binary encoded Protobuf representation of this message instance.

        .. note::
            This is a method for compatibility with other libraries,
            you should really use ``bytes(x)``.

        Returns
        --------
        :class:`bytes`
            The binary encoded Protobuf representation of this message instance
        """
        return bytes(self)

class Enum(enum.Enum.IntEnum, metaclass=enum.EnumType):
    pass