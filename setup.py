#!/usr/bin/env python3
"""
JsonChamp - Commercial Grade JSON Schema Tools

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version
version_file = Path(__file__).parent / "VERSION"
version = version_file.read_text().strip() if version_file.exists() else "1.3.0"

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="jsonchamp",
    version=version,
    author="Ashutosh Sinha",
    author_email="ajsinha@gmail.com",
    description="Commercial Grade JSON Schema to Python Code Generator with SchemaMap Transformation DSL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ajsinha/jsonchamp",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    package_data={
        "jsonchamp": ["py.typed"],
    },
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "faker": ["faker>=18.0.0"],
        "requests": ["requests>=2.28.0"],
        "validation": ["jsonschema>=4.17.0"],
        "all": ["faker>=18.0.0", "requests>=2.28.0", "jsonschema>=4.17.0"],
        "dev": [
            "faker>=18.0.0",
            "requests>=2.28.0", 
            "jsonschema>=4.17.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jsonchamp=jsonchamp.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    keywords="json schema codegen dataclass transformation dsl schemamap",
)
