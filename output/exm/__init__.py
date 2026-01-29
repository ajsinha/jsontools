"""
exm - Generated Data Models

Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
Generated at: 2026-01-29T13:36:20.833194

This module provides:
- Generated dataclass models from JSON Schema
- Functions to load JSON into model instances
- Functions to serialize models to JSON
- Utility functions for working with models

Usage:
    from exm import User, load_json, to_json

    # Load from JSON file
    user = load_json("user.json", "User")

    # Create and serialize
    user = User(name="John", email="john@example.com")
    json_str = to_json_string(user)

Command-line usage:
    python -m exm --help
    python -m exm list
    python -m exm load user.json User
    python -m exm sample User
"""

# Import all generated classes
from .generated import *
from .generated import CLASS_REGISTRY, get_class

# Import driver functions
from .driver import (
    load_json,
    load_json_file,
    load_json_string,
    load_dict,
    to_json,
    to_json_file,
    to_json_string,
    to_dict,
    list_classes,
    get_class_info,
    create_instance,
    validate_data,
)

# Import main functions
from .main import (
    load_and_parse,
    create_and_save,
    generate_sample,
    convert_json,
    run_cli,
)

__version__ = "1.1.0"
