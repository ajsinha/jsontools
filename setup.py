"""
JsonSchemaCodeGen - Setup Configuration

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version
version = "1.2.1"

# Read long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")
else:
    long_description = "Commercial Grade JSON Schema to Python Code Generator"

setup(
    name="jsonschemacodegen",
    version=version,
    author="Ashutosh Sinha",
    author_email="ajsinha@gmail.com",
    description="Commercial Grade JSON Schema to Python Code Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ajsinha/jsonschemacodegen",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    package_data={
        "jsonschemacodegen": ["py.typed"],
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
    python_requires=">=3.8",
    install_requires=[],  # No required dependencies
    extras_require={
        "faker": ["faker>=18.0.0"],
        "requests": ["requests>=2.28.0"],
        "jsonschema": ["jsonschema>=4.17.0"],
        "all": [
            "faker>=18.0.0",
            "requests>=2.28.0",
            "jsonschema>=4.17.0",
        ],
        "dev": [
            "faker>=18.0.0",
            "requests>=2.28.0",
            "jsonschema>=4.17.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jsonschemacodegen=jsonschemacodegen.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
