"""
JSON Utilities - Helper functions for JSON Schema manipulation.

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

import copy
from typing import Any, Dict, List, Optional, Set


def deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Values from overlay take precedence. Nested dictionaries are merged recursively.
    Lists are concatenated.
    
    Args:
        base: Base dictionary
        overlay: Dictionary to merge on top
        
    Returns:
        Merged dictionary
    """
    result = copy.deepcopy(base)
    
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        elif key in result and isinstance(result[key], list) and isinstance(value, list):
            result[key] = result[key] + value
        else:
            result[key] = copy.deepcopy(value)
    
    return result


def flatten_schema(
    schema: Dict[str, Any],
    definitions: Optional[Dict[str, Dict[str, Any]]] = None,
    seen_refs: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """
    Flatten a schema by inlining all $ref references.
    
    Args:
        schema: The schema to flatten
        definitions: Dictionary of definitions
        seen_refs: Set of already seen references (for cycle detection)
        
    Returns:
        Flattened schema with no $ref
    """
    if definitions is None:
        definitions = schema.get("definitions", schema.get("$defs", {}))
    
    if seen_refs is None:
        seen_refs = set()
    
    result = {}
    
    for key, value in schema.items():
        if key in ("definitions", "$defs"):
            continue
        
        if key == "$ref":
            ref = value
            if ref in seen_refs:
                # Circular reference - return as-is
                result["$ref"] = ref
            else:
                # Resolve reference
                resolved = resolve_ref(ref, schema, definitions)
                if resolved:
                    new_seen = seen_refs | {ref}
                    flattened = flatten_schema(resolved, definitions, new_seen)
                    result.update(flattened)
        elif isinstance(value, dict):
            result[key] = flatten_schema(value, definitions, seen_refs)
        elif isinstance(value, list):
            result[key] = [
                flatten_schema(item, definitions, seen_refs) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    
    return result


def resolve_ref(
    ref: str,
    schema: Dict[str, Any],
    definitions: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Resolve a $ref to its target schema.
    
    Args:
        ref: The $ref string
        schema: The root schema
        definitions: Dictionary of definitions
        
    Returns:
        The resolved schema or None if not found
    """
    if definitions is None:
        definitions = schema.get("definitions", schema.get("$defs", {}))
    
    if ref.startswith("#/definitions/"):
        name = ref[14:]
        return definitions.get(name)
    elif ref.startswith("#/$defs/"):
        name = ref[8:]
        return definitions.get(name)
    elif ref == "#":
        return schema
    
    return None


def collect_refs(schema: Dict[str, Any]) -> Set[str]:
    """
    Collect all $ref values from a schema.
    
    Args:
        schema: The schema to search
        
    Returns:
        Set of all $ref values
    """
    refs = set()
    
    def _collect(obj: Any):
        if isinstance(obj, dict):
            if "$ref" in obj:
                refs.add(obj["$ref"])
            for value in obj.values():
                _collect(value)
        elif isinstance(obj, list):
            for item in obj:
                _collect(item)
    
    _collect(schema)
    return refs


def get_schema_type(schema: Dict[str, Any]) -> Optional[str]:
    """
    Get the primary type of a schema.
    
    Args:
        schema: The schema
        
    Returns:
        The type string or None
    """
    schema_type = schema.get("type")
    
    if isinstance(schema_type, list):
        # Return first non-null type
        for t in schema_type:
            if t != "null":
                return t
        return schema_type[0] if schema_type else None
    
    return schema_type


def is_nullable(schema: Dict[str, Any]) -> bool:
    """
    Check if a schema allows null values.
    
    Args:
        schema: The schema
        
    Returns:
        True if null is allowed
    """
    schema_type = schema.get("type")
    
    if isinstance(schema_type, list):
        return "null" in schema_type
    
    # Check anyOf/oneOf for null type
    for key in ("anyOf", "oneOf"):
        if key in schema:
            for sub_schema in schema[key]:
                if sub_schema.get("type") == "null":
                    return True
    
    return False


def extract_definitions(schema: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Extract all definitions from a schema.
    
    Args:
        schema: The schema
        
    Returns:
        Combined definitions dictionary
    """
    definitions = {}
    
    if "definitions" in schema:
        definitions.update(schema["definitions"])
    
    if "$defs" in schema:
        definitions.update(schema["$defs"])
    
    return definitions


def normalize_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a schema to a consistent format.
    
    - Converts $defs to definitions
    - Sorts properties alphabetically
    - Removes empty arrays and objects
    
    Args:
        schema: The schema to normalize
        
    Returns:
        Normalized schema
    """
    result = {}
    
    for key, value in sorted(schema.items()):
        # Convert $defs to definitions
        if key == "$defs":
            key = "definitions"
        
        # Skip empty values
        if value is None:
            continue
        if isinstance(value, (list, dict)) and len(value) == 0:
            continue
        
        # Recursively normalize nested structures
        if isinstance(value, dict):
            result[key] = normalize_schema(value)
        elif isinstance(value, list):
            result[key] = [
                normalize_schema(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    
    return result
