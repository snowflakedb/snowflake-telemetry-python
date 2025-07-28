# Copyright The OpenTelemetry Authors
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
# This file has been modified from the original source code at
#
#     https://github.com/open-telemetry/opentelemetry-python/tree/v1.35.0
#
# by Snowflake Inc.


from snowflake.telemetry._internal.opentelemetry.exporter.otlp.proto.common._internal._log_encoder import (
    encode_logs,
)

__all__ = ["encode_logs"]
