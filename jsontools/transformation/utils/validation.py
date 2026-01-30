"""
SchemaMap Validation Utilities

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

JSON Schema validation for transformed output.
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from pathlib import Path


class ValidationError(Exception):
    """Exception raised when JSON validation fails."""
    def __init__(self, message: str, errors: List[str] = None):
        self.message = message
        self.errors = errors or []
        super().__init__(message)


def validate_json_schema(data: Dict[str, Any], schema_path: str) -> bool:
    """
    Validate JSON data against a JSON Schema.
    
    Args:
        data: The JSON data to validate
        schema_path: Path to the JSON Schema file
        
    Returns:
        True if validation passes
        
    Raises:
        ValidationError: If validation fails
        FileNotFoundError: If schema file not found
    """
    path = Path(schema_path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    errors = _validate_against_schema(data, schema)
    
    if errors:
        raise ValidationError(
            f"Validation failed with {len(errors)} error(s)",
            errors=errors
        )
    
    return True


def _validate_against_schema(data: Any, schema: Dict, path: str = "") -> List[str]:
    """Validate data against schema and return list of errors."""
    errors = []
    
    # Check type
    schema_type = schema.get("type")
    if schema_type:
        if not _check_type(data, schema_type):
            errors.append(f"{path or 'root'}: Expected type '{schema_type}', got '{type(data).__name__}'")
            return errors
    
    # Object validation
    if schema_type == "object":
        if not isinstance(data, dict):
            return errors
        
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                errors.append(f"{path}.{field}: Required field is missing")
        
        # Validate properties
        properties = schema.get("properties", {})
        for prop_name, prop_schema in properties.items():
            if prop_name in data:
                prop_path = f"{path}.{prop_name}" if path else prop_name
                errors.extend(_validate_against_schema(data[prop_name], prop_schema, prop_path))
    
    # Array validation
    elif schema_type == "array":
        if isinstance(data, list):
            items_schema = schema.get("items")
            if items_schema:
                for i, item in enumerate(data):
                    item_path = f"{path}[{i}]"
                    errors.extend(_validate_against_schema(item, items_schema, item_path))
            
            # Check minItems/maxItems
            min_items = schema.get("minItems")
            max_items = schema.get("maxItems")
            if min_items and len(data) < min_items:
                errors.append(f"{path}: Array has {len(data)} items, minimum is {min_items}")
            if max_items and len(data) > max_items:
                errors.append(f"{path}: Array has {len(data)} items, maximum is {max_items}")
    
    # String validation
    elif schema_type == "string":
        if isinstance(data, str):
            min_length = schema.get("minLength")
            max_length = schema.get("maxLength")
            pattern = schema.get("pattern")
            enum = schema.get("enum")
            
            if min_length and len(data) < min_length:
                errors.append(f"{path}: String length {len(data)} is less than minimum {min_length}")
            if max_length and len(data) > max_length:
                errors.append(f"{path}: String length {len(data)} exceeds maximum {max_length}")
            if pattern:
                import re
                if not re.match(pattern, data):
                    errors.append(f"{path}: String does not match pattern '{pattern}'")
            if enum and data not in enum:
                errors.append(f"{path}: Value '{data}' is not one of {enum}")
    
    # Number validation
    elif schema_type in ("number", "integer"):
        if isinstance(data, (int, float)):
            minimum = schema.get("minimum")
            maximum = schema.get("maximum")
            
            if minimum is not None and data < minimum:
                errors.append(f"{path}: Value {data} is less than minimum {minimum}")
            if maximum is not None and data > maximum:
                errors.append(f"{path}: Value {data} exceeds maximum {maximum}")
    
    # Check enum for any type
    enum = schema.get("enum")
    if enum and data not in enum:
        errors.append(f"{path}: Value '{data}' is not one of {enum}")
    
    return errors


def _check_type(value: Any, schema_type: str) -> bool:
    """Check if value matches the schema type."""
    if value is None:
        return True  # Null is generally allowed unless required
    
    type_mapping = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }
    
    expected_type = type_mapping.get(schema_type)
    if expected_type:
        return isinstance(value, expected_type)
    
    return True
