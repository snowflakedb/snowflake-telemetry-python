#
# Copyright (c) 2012-2024 Snowflake Inc. All rights reserved.
#
import os

try:
    if os.environ.get("SNOWFLAKE_TELEMETRY_NO_PROTOBUF") is not None:
        raise ImportError
    import google.protobuf
    protobuf_version = google.protobuf.__version__
    major = int(protobuf_version.split('.')[0])
    minor = int(protobuf_version.split('.')[1])
    if major >= 6:
        raise ImportError
    # support protobuf >=3.19, <6.0
    if major >= 5 and major < 6:
        PROTOBUF_VERSION_MAJOR = 5
    elif major >= 4:
        PROTOBUF_VERSION_MAJOR = 4
    elif major == 3 and minor >= 19:
        PROTOBUF_VERSION_MAJOR = 3
    else:
        raise ImportError
except:
    PROTOBUF_VERSION_MAJOR = -1
