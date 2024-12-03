from setuptools import (
    find_namespace_packages,
    setup,
)

DESCRIPTION = 'Snowflake Telemetry Test Utils'
LONG_DESCRIPTION = 'This package provides test utils for testing snowflake-telemetry-python'


setup(
    name="snowflake-telemetry-test-utils",
    version="0.0.1.dev",
    author="Snowflake, Inc",
    author_email="support@snowflake.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    install_requires=[
        "opentelemetry-exporter-otlp-proto-common == 1.26.0",
        "pytest >= 7.0.0",
        "snowflake-telemetry-python == 0.6.0.dev",
        "Jinja2 == 3.1.4",
        "grpcio-tools >= 1.62.3", 
        "black >= 24.1.0", 
        "isort >= 5.12.0",
        "hypothesis >= 6.0.0",
        "google-benchmark",
    ],
    packages=find_namespace_packages(
        where='src'
    ),
    package_dir={
        "": "src",
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
     ],
    zip_safe=True,
)
