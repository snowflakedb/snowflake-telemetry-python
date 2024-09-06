# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: opentelemetry/proto/logs/v1/logs.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import List

import betterproto

from opentelemetry.proto.common.v1 import common_pb2
from opentelemetry.proto.resource.v1 import resource_pb2


class SeverityNumber(betterproto.Enum):
    """Possible values for LogRecord.SeverityNumber."""

    # UNSPECIFIED is the default SeverityNumber, it MUST NOT be used.
    SEVERITY_NUMBER_UNSPECIFIED = 0
    SEVERITY_NUMBER_TRACE = 1
    SEVERITY_NUMBER_TRACE2 = 2
    SEVERITY_NUMBER_TRACE3 = 3
    SEVERITY_NUMBER_TRACE4 = 4
    SEVERITY_NUMBER_DEBUG = 5
    SEVERITY_NUMBER_DEBUG2 = 6
    SEVERITY_NUMBER_DEBUG3 = 7
    SEVERITY_NUMBER_DEBUG4 = 8
    SEVERITY_NUMBER_INFO = 9
    SEVERITY_NUMBER_INFO2 = 10
    SEVERITY_NUMBER_INFO3 = 11
    SEVERITY_NUMBER_INFO4 = 12
    SEVERITY_NUMBER_WARN = 13
    SEVERITY_NUMBER_WARN2 = 14
    SEVERITY_NUMBER_WARN3 = 15
    SEVERITY_NUMBER_WARN4 = 16
    SEVERITY_NUMBER_ERROR = 17
    SEVERITY_NUMBER_ERROR2 = 18
    SEVERITY_NUMBER_ERROR3 = 19
    SEVERITY_NUMBER_ERROR4 = 20
    SEVERITY_NUMBER_FATAL = 21
    SEVERITY_NUMBER_FATAL2 = 22
    SEVERITY_NUMBER_FATAL3 = 23
    SEVERITY_NUMBER_FATAL4 = 24


class LogRecordFlags(betterproto.Enum):
    """
    LogRecordFlags represents constants used to interpret the LogRecord.flags
    field, which is protobuf 'fixed32' type and is to be used as bit-fields.
    Each non-zero value defined in this enum is a bit-mask.  To extract the
    bit-field, for example, use an expression like:   (logRecord.flags &
    LOG_RECORD_FLAGS_TRACE_FLAGS_MASK)
    """

    # The zero value for the enum. Should not be used for comparisons. Instead
    # use bitwise "and" with the appropriate mask as shown above.
    LOG_RECORD_FLAGS_DO_NOT_USE = 0
    # Bits 0-7 are used for trace flags.
    LOG_RECORD_FLAGS_TRACE_FLAGS_MASK = 255


@dataclass
class LogsData(betterproto.Message):
    """
    LogsData represents the logs data that can be stored in a persistent
    storage, OR can be embedded by other protocols that transfer OTLP logs data
    but do not implement the OTLP protocol. The main difference between this
    message and collector protocol is that in this message there will not be
    any "control" or "metadata" specific to OTLP protocol. When new fields are
    added into this message, the OTLP request MUST be updated as well.
    """

    # An array of ResourceLogs. For data coming from a single resource this array
    # will typically contain one element. Intermediary nodes that receive data
    # from multiple origins typically batch the data before forwarding further
    # and in that case this array will contain multiple elements.
    resource_logs: List["ResourceLogs"] = betterproto.message_field(1)


@dataclass
class ResourceLogs(betterproto.Message):
    """A collection of ScopeLogs from a Resource."""

    # The resource for the logs in this message. If this field is not set then
    # resource info is unknown.
    resource: resource_pb2.Resource = betterproto.message_field(1)
    # A list of ScopeLogs that originate from a resource.
    scope_logs: List["ScopeLogs"] = betterproto.message_field(2)
    # The Schema URL, if known. This is the identifier of the Schema that the
    # resource data is recorded in. To learn more about Schema URL see
    # https://opentelemetry.io/docs/specs/otel/schemas/#schema-url This
    # schema_url applies to the data in the "resource" field. It does not apply
    # to the data in the "scope_logs" field which have their own schema_url
    # field.
    schema_url: str = betterproto.string_field(3)


@dataclass
class ScopeLogs(betterproto.Message):
    """A collection of Logs produced by a Scope."""

    # The instrumentation scope information for the logs in this message.
    # Semantically when InstrumentationScope isn't set, it is equivalent with an
    # empty instrumentation scope name (unknown).
    scope: common_pb2.InstrumentationScope = betterproto.message_field(1)
    # A list of log records.
    log_records: List["LogRecord"] = betterproto.message_field(2)
    # The Schema URL, if known. This is the identifier of the Schema that the log
    # data is recorded in. To learn more about Schema URL see
    # https://opentelemetry.io/docs/specs/otel/schemas/#schema-url This
    # schema_url applies to all logs in the "logs" field.
    schema_url: str = betterproto.string_field(3)


@dataclass
class LogRecord(betterproto.Message):
    """
    A log record according to OpenTelemetry Log Data Model:
    https://github.com/open-telemetry/oteps/blob/main/text/logs/0097-log-data-
    model.md
    """

    # time_unix_nano is the time when the event occurred. Value is UNIX Epoch
    # time in nanoseconds since 00:00:00 UTC on 1 January 1970. Value of 0
    # indicates unknown or missing timestamp.
    time_unix_nano: float = betterproto.fixed64_field(1)
    # Time when the event was observed by the collection system. For events that
    # originate in OpenTelemetry (e.g. using OpenTelemetry Logging SDK) this
    # timestamp is typically set at the generation time and is equal to
    # Timestamp. For events originating externally and collected by OpenTelemetry
    # (e.g. using Collector) this is the time when OpenTelemetry's code observed
    # the event measured by the clock of the OpenTelemetry code. This field MUST
    # be set once the event is observed by OpenTelemetry. For converting
    # OpenTelemetry log data to formats that support only one timestamp or when
    # receiving OpenTelemetry log data by recipients that support only one
    # timestamp internally the following logic is recommended:   - Use
    # time_unix_nano if it is present, otherwise use observed_time_unix_nano.
    # Value is UNIX Epoch time in nanoseconds since 00:00:00 UTC on 1 January
    # 1970. Value of 0 indicates unknown or missing timestamp.
    observed_time_unix_nano: float = betterproto.fixed64_field(11)
    # Numerical value of the severity, normalized to values described in Log Data
    # Model. [Optional].
    severity_number: "SeverityNumber" = betterproto.enum_field(2)
    # The severity text (also known as log level). The original string
    # representation as it is known at the source. [Optional].
    severity_text: str = betterproto.string_field(3)
    # A value containing the body of the log record. Can be for example a human-
    # readable string message (including multi-line) describing the event in a
    # free form or it can be a structured data composed of arrays and maps of
    # other values. [Optional].
    body: common_pb2.AnyValue = betterproto.message_field(5)
    # Additional attributes that describe the specific event occurrence.
    # [Optional]. Attribute keys MUST be unique (it is not allowed to have more
    # than one attribute with the same key).
    attributes: List[common_pb2.KeyValue] = betterproto.message_field(6)
    dropped_attributes_count: int = betterproto.uint32_field(7)
    # Flags, a bit field. 8 least significant bits are the trace flags as defined
    # in W3C Trace Context specification. 24 most significant bits are reserved
    # and must be set to 0. Readers must not assume that 24 most significant bits
    # will be zero and must correctly mask the bits when reading 8-bit trace flag
    # (use flags & LOG_RECORD_FLAGS_TRACE_FLAGS_MASK). [Optional].
    flags: float = betterproto.fixed32_field(8)
    # A unique identifier for a trace. All logs from the same trace share the
    # same `trace_id`. The ID is a 16-byte array. An ID with all zeroes OR of
    # length other than 16 bytes is considered invalid (empty string in OTLP/JSON
    # is zero-length and thus is also invalid). This field is optional. The
    # receivers SHOULD assume that the log record is not associated with a trace
    # if any of the following is true:   - the field is not present,   - the
    # field contains an invalid value.
    trace_id: bytes = betterproto.bytes_field(9)
    # A unique identifier for a span within a trace, assigned when the span is
    # created. The ID is an 8-byte array. An ID with all zeroes OR of length
    # other than 8 bytes is considered invalid (empty string in OTLP/JSON is
    # zero-length and thus is also invalid). This field is optional. If the
    # sender specifies a valid span_id then it SHOULD also specify a valid
    # trace_id. The receivers SHOULD assume that the log record is not associated
    # with a span if any of the following is true:   - the field is not present,
    # - the field contains an invalid value.
    span_id: bytes = betterproto.bytes_field(10)