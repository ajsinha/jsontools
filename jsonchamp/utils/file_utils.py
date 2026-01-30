"""
File Utilities - Load and save schemas and generated code.

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder. This software
is provided "as is" without warranty of any kind.

Patent Pending: Certain implementations may be subject to patent applications.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union


def load_schema(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load a JSON Schema from a file.
    
    Args:
        path: Path to the schema file
        
    Returns:
        Schema dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_schema(
    schema: Dict[str, Any],
    path: Union[str, Path],
    indent: int = 2,
) -> None:
    """
    Save a JSON Schema to a file.
    
    Args:
        schema: The schema dictionary
        path: Output file path
        indent: JSON indentation level
    """
    path = Path(path)
    
    # Create parent directories if needed
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=indent)


def save_code(
    code: str,
    path: Union[str, Path],
    overwrite: bool = True,
) -> None:
    """
    Save generated Python code to a file.
    
    Args:
        code: The Python source code
        path: Output file path
        overwrite: Whether to overwrite existing files
    """
    path = Path(path)
    
    if path.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {path}")
    
    # Create parent directories if needed
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)


def load_schemas_from_directory(
    directory: Union[str, Path],
    pattern: str = "*.json",
    recursive: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """
    Load all JSON schemas from a directory.
    
    Args:
        directory: Directory path
        pattern: Glob pattern for schema files
        recursive: Whether to search recursively
        
    Returns:
        Dictionary mapping filenames to schemas
    """
    directory = Path(directory)
    schemas = {}
    
    if recursive:
        files = directory.rglob(pattern)
    else:
        files = directory.glob(pattern)
    
    for filepath in files:
        try:
            schemas[filepath.name] = load_schema(filepath)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load {filepath}: {e}")
    
    return schemas


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
