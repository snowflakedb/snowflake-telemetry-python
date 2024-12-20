# Generated by the protoc compiler with a custom plugin. DO NOT EDIT!
# sources: opentelemetry/proto/collector/trace/v1/trace_service.proto
#
# Copyright (c) 2012-2024 Snowflake Inc. All rights reserved.
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
# This file has been generated from the original proto schema at
#
#     https://github.com/open-telemetry/opentelemetry-proto
#
# using a custom protoc compiler plugin by Snowflake Inc.

from __future__ import annotations

import struct
from typing import List

from snowflake.telemetry._internal.opentelemetry.proto.trace.v1.trace_marshaler import *
from snowflake.telemetry._internal.serialize import (
    Enum,
    MessageMarshaler,
    Varint,
)


class ExportTraceServiceRequest(MessageMarshaler):
    @property
    def resource_spans(self) -> List[ResourceSpans]:
        if self._resource_spans is None:
            self._resource_spans = list()
        return self._resource_spans

    def __init__(
        self,
        resource_spans: List[ResourceSpans] = None,
    ):
        self._resource_spans: List[ResourceSpans] = resource_spans

    def calculate_size(self) -> int:
        size = 0
        if self._resource_spans:
            size += sum(
                message._get_size()
                + len(b"\n")
                + Varint.size_varint_u32(message._get_size())
                for message in self._resource_spans
            )
        return size

    def write_to(self, out: bytearray) -> None:
        if self._resource_spans:
            for v in self._resource_spans:
                out += b"\n"
                Varint.write_varint_u32(out, v._get_size())
                v.write_to(out)


class ExportTraceServiceResponse(MessageMarshaler):
    @property
    def partial_success(self) -> ExportTracePartialSuccess:
        if self._partial_success is None:
            self._partial_success = ExportTracePartialSuccess()
        return self._partial_success

    def __init__(
        self,
        partial_success: ExportTracePartialSuccess = None,
    ):
        self._partial_success: ExportTracePartialSuccess = partial_success

    def calculate_size(self) -> int:
        size = 0
        if self._partial_success is not None:
            size += (
                len(b"\n")
                + Varint.size_varint_u32(self._partial_success._get_size())
                + self._partial_success._get_size()
            )
        return size

    def write_to(self, out: bytearray) -> None:
        if self._partial_success is not None:
            out += b"\n"
            Varint.write_varint_u32(out, self._partial_success._get_size())
            self._partial_success.write_to(out)


class ExportTracePartialSuccess(MessageMarshaler):
    rejected_spans: int
    error_message: str

    def __init__(
        self,
        rejected_spans: int = 0,
        error_message: str = "",
    ):
        self.rejected_spans: int = rejected_spans
        self.error_message: str = error_message

    def calculate_size(self) -> int:
        size = 0
        if self.rejected_spans:
            size += len(b"\x08") + Varint.size_varint_i64(self.rejected_spans)
        if self.error_message:
            v = self.error_message.encode("utf-8")
            size += len(b"\x12") + Varint.size_varint_u32(len(v)) + len(v)
        return size

    def write_to(self, out: bytearray) -> None:
        if self.rejected_spans:
            out += b"\x08"
            Varint.write_varint_i64(out, self.rejected_spans)
        if self.error_message:
            v = self.error_message.encode("utf-8")
            out += b"\x12"
            Varint.write_varint_u32(out, len(v))
            out += v
