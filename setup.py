import os
import sys
from setuptools import (
    find_namespace_packages,
    setup,
)

# Custom bdist_wheel to create Python version-specific but platform-independent wheels
try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            # Keep platform as "any" (platform-independent)
            self.root_is_pure = True

        def get_tag(self):
            python, abi, plat = _bdist_wheel.get_tag(self)
            # Use specific Python version tag (e.g., cp311) instead of generic py3
            python = f"cp{sys.version_info.major}{sys.version_info.minor}"
            # No ABI dependency, any platform
            return (python, "none", "any")

    cmdclass = {"bdist_wheel": bdist_wheel}
except ImportError:
    cmdclass = {}

DESCRIPTION = 'Snowflake Telemetry for Python'
LONG_DESCRIPTION = """This package provides a set of telemetry APIs for developers building on the Snowflake platform.

Documentation is available at: https://docs.snowflake.com/en/developer-guide/logging-tracing/tracing-python

Source code is also available at: https://github.com/snowflakedb/snowflake-telemetry-python
"""
SNOWFLAKE_TELEMETRY_SRC_DIR = os.path.join("src", "snowflake", "telemetry")

VERSION = None
with open(os.path.join(SNOWFLAKE_TELEMETRY_SRC_DIR, "version.py"), encoding="utf-8") as f:
    exec(f.read())

REQUIRED_PYTHON_VERSION = ">=3.9, <3.14"


setup(
    name="snowflake-telemetry-python",
    version=VERSION,
    author="Snowflake, Inc",
    author_email="support@snowflake.com",
    url="https://www.snowflake.com/",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    python_requires=REQUIRED_PYTHON_VERSION,
    install_requires=[
        "opentelemetry-api == 1.35.0",
        "opentelemetry-sdk == 1.35.0",
    ],
    packages=find_namespace_packages(
        where='src'
    ),
    package_dir={
        "": "src",
    },
    include_package_data=True,
    package_data={
        "": ["__pycache__/*.pyc"],
    },
    keywords="Snowflake db database cloud analytics warehouse",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: SQL",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Database",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    project_urls={
        "Homepage": "https://www.snowflake.com/",
        "Changelog": "https://github.com/snowflakedb/snowflake-telemetry-python/blob/main/CHANGELOG.md",
        "Documentation": "https://docs.snowflake.com/en/developer-guide/logging-tracing/tracing-python",
        "Issues": "https://github.com/snowflakedb/snowflake-telemetry-python/issues",
        "Repository": "https://github.com/snowflakedb/snowflake-telemetry-python/",
    },
    zip_safe=True,
    cmdclass=cmdclass,
)
