# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: opentelemetry/proto/resource/v1/resource.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import List

import betterproto

from opentelemetry.proto.common.v1 import common_pb2


@dataclass
class Resource(betterproto.Message):
    """Resource information."""

    # Set of attributes that describe the resource. Attribute keys MUST be unique
    # (it is not allowed to have more than one attribute with the same key).
    attributes: List[common_pb2.KeyValue] = betterproto.message_field(1)
    # dropped_attributes_count is the number of dropped attributes. If the value
    # is 0, then no attributes were dropped.
    dropped_attributes_count: int = betterproto.uint32_field(2)