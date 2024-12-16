#
# Copyright (c) 2012-2024 Snowflake Inc. All rights reserved.
#

try:
    import google.protobuf
    protobuf_version = google.protobuf.__version__
    major = int(protobuf_version.split('.')[0])
    minor = int(protobuf_version.split('.')[1])
    if major >= 6:
        raise ImportError
    # protobuf >=5.0, <6.0 is supported by v5
    if major >= 5 and major < 6:
        PROTOBUF_VERSION_MAJOR = 5
    # protobuf >=3.19, <5.0 is supported by v3
    elif major == 3 and minor >= 19:
        PROTOBUF_VERSION_MAJOR = 3
    else:
        raise ImportError
except ImportError:
    PROTOBUF_VERSION_MAJOR = -1
