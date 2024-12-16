"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
Copyright 2019, OpenTelemetry Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message
import opentelemetry.proto.common.v1.common_pb2
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class Resource(google.protobuf.message.Message):
    """Resource information."""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ATTRIBUTES_FIELD_NUMBER: builtins.int
    DROPPED_ATTRIBUTES_COUNT_FIELD_NUMBER: builtins.int
    @property
    def attributes(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[opentelemetry.proto.common.v1.common_pb2.KeyValue]:
        """Set of attributes that describe the resource.
        Attribute keys MUST be unique (it is not allowed to have more than one
        attribute with the same key).
        """
    dropped_attributes_count: builtins.int
    """dropped_attributes_count is the number of dropped attributes. If the value is 0, then
    no attributes were dropped.
    """
    def __init__(
        self,
        *,
        attributes: collections.abc.Iterable[opentelemetry.proto.common.v1.common_pb2.KeyValue] | None = ...,
        dropped_attributes_count: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["attributes", b"attributes", "dropped_attributes_count", b"dropped_attributes_count"]) -> None: ...

global___Resource = Resource
