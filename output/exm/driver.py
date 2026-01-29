"""
Driver Code - JSON Loading and Serialization Utilities

Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
Generated at: 2026-01-29T13:36:20.833319

This module provides utility functions for:
- Loading JSON files/strings into dataclass instances
- Serializing dataclass instances to JSON
- Class introspection and validation
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from dataclasses import is_dataclass, fields
from datetime import datetime, date

from .generated import CLASS_REGISTRY, get_class


T = TypeVar('T')


# ============================================================================
# JSON LOADING FUNCTIONS
# ============================================================================

def load_json(file_path: Union[str, Path], class_name: str) -> Any:
    """
    Load a JSON file into a dataclass instance.
    
    Args:
        file_path: Path to the JSON file
        class_name: Name of the target class
        
    Returns:
        Instance of the specified class
        
    Example:
        user = load_json("user.json", "User")
    """
    target_class = get_class(class_name)
    if target_class is None:
        raise ValueError(f"Unknown class: {class_name}. Available: {list_classes()}")
    return load_json_file(file_path, target_class)


def load_json_file(file_path: Union[str, Path], target_class: Type[T]) -> T:
    """
    Load a JSON file into a dataclass instance.
    
    Args:
        file_path: Path to the JSON file
        target_class: The dataclass type to instantiate
        
    Returns:
        Instance of target_class populated with JSON data
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return load_dict(data, target_class)


def load_json_string(json_str: str, target_class: Type[T]) -> T:
    """
    Load a JSON string into a dataclass instance.
    
    Args:
        json_str: JSON string
        target_class: The dataclass type to instantiate
        
    Returns:
        Instance of target_class populated with JSON data
    """
    data = json.loads(json_str)
    return load_dict(data, target_class)


def load_dict(data: Dict[str, Any], target_class: Type[T]) -> T:
    """
    Load a dictionary into a dataclass instance.
    
    Args:
        data: Dictionary with data
        target_class: The dataclass type to instantiate
        
    Returns:
        Instance of target_class populated with data
    """
    if not is_dataclass(target_class):
        raise TypeError(f"{target_class} is not a dataclass")
    
    field_types = {f.name: f.type for f in fields(target_class)}
    processed_data = {}
    
    # Handle JSON property name mapping
    json_mapping = {}
    if hasattr(target_class, '_get_json_mapping'):
        mapping = target_class._get_json_mapping()
        json_mapping = {v: k for k, v in mapping.items()}  # Reverse: json_name -> py_name
    
    for json_name, value in data.items():
        # Convert JSON name to Python field name
        py_name = json_mapping.get(json_name, json_name)
        
        if py_name not in field_types:
            continue
            
        field_type = field_types[py_name]
        processed_data[py_name] = _convert_value(value, field_type)
    
    return target_class(**processed_data)


def _convert_value(value: Any, target_type: Any) -> Any:
    """Convert a value to the target type."""
    if value is None:
        return None
    
    origin = getattr(target_type, '__origin__', None)
    
    if origin is Union:
        args = target_type.__args__
        non_none = [t for t in args if t is not type(None)]
        if non_none:
            target_type = non_none[0]
            origin = getattr(target_type, '__origin__', None)
    
    if origin is list:
        item_type = target_type.__args__[0] if target_type.__args__ else Any
        return [_convert_value(item, item_type) for item in value]
    
    if origin is dict:
        return value
    
    if is_dataclass(target_type) and isinstance(value, dict):
        return load_dict(value, target_class=target_type)
    
    if target_type is datetime and isinstance(value, str):
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    
    if target_type is date and isinstance(value, str):
        return date.fromisoformat(value)
    
    return value


def create_instance(class_name: str, **kwargs) -> Any:
    """
    Create an instance of a class by name.
    
    Args:
        class_name: Name of the class
        **kwargs: Field values
        
    Returns:
        Instance of the class
        
    Example:
        user = create_instance("User", name="John", email="john@example.com")
    """
    target_class = get_class(class_name)
    if target_class is None:
        raise ValueError(f"Unknown class: {class_name}. Available: {list_classes()}")
    return target_class(**kwargs)


# ============================================================================
# JSON SERIALIZATION FUNCTIONS
# ============================================================================

def to_json(obj: Any, file_path: Union[str, Path], indent: int = 2) -> None:
    """
    Serialize a dataclass instance to a JSON file.
    
    Args:
        obj: The dataclass instance to serialize
        file_path: Output file path
        indent: JSON indentation
        
    Example:
        to_json(user, "user.json")
    """
    to_json_file(obj, file_path, indent)


def to_json_file(obj: Any, file_path: Union[str, Path], indent: int = 2) -> None:
    """
    Serialize a dataclass instance to a JSON file.
    
    Args:
        obj: The dataclass instance to serialize
        file_path: Output file path
        indent: JSON indentation
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    json_str = to_json_string(obj, indent=indent)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json_str)


def to_json_string(obj: Any, indent: int = 2) -> str:
    """
    Serialize a dataclass instance to a JSON string.
    
    Args:
        obj: The dataclass instance to serialize
        indent: JSON indentation
        
    Returns:
        JSON string
    """
    data = to_dict(obj)
    return json.dumps(data, indent=indent, default=_json_serializer)


def to_dict(obj: Any) -> Dict[str, Any]:
    """
    Convert a dataclass instance to a dictionary.
    
    Uses the JSON property name mapping if available.
    """
    if obj is None:
        return None
    
    if is_dataclass(obj) and not isinstance(obj, type):
        # Get JSON mapping if available
        json_mapping = {}
        if hasattr(obj, '_get_json_mapping'):
            json_mapping = obj._get_json_mapping()
        
        result = {}
        for field in fields(obj):
            value = getattr(obj, field.name)
            # Use JSON name if mapping exists
            json_name = json_mapping.get(field.name, field.name)
            result[json_name] = to_dict(value)
        return result
    
    if isinstance(obj, list):
        return [to_dict(item) for item in obj]
    
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    
    return obj


def _json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for special types."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def list_classes() -> List[str]:
    """
    List all available generated classes.
    
    Returns:
        List of class names
    """
    return list(CLASS_REGISTRY.keys())


def get_class_info(class_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a generated class.
    
    Args:
        class_name: Name of the class
        
    Returns:
        Dictionary with class information
    """
    target_class = get_class(class_name)
    if target_class is None:
        return None
    
    if not is_dataclass(target_class):
        return None
    
    field_info = []
    for field in fields(target_class):
        has_default = field.default is not field.default_factory
        field_info.append({
            "name": field.name,
            "type": str(field.type),
            "required": not has_default and field.default_factory is field.default_factory,
        })
    
    return {
        "name": class_name,
        "fields": field_info,
        "docstring": target_class.__doc__,
    }


def validate_data(data: Dict[str, Any], class_name: str) -> Dict[str, Any]:
    """
    Validate data against a class structure.
    
    Args:
        data: Dictionary to validate
        class_name: Name of the target class
        
    Returns:
        Dictionary with validation results
    """
    target_class = get_class(class_name)
    if target_class is None:
        return {"valid": False, "errors": [f"Unknown class: {class_name}"]}
    
    errors = []
    warnings = []
    
    if not is_dataclass(target_class):
        return {"valid": False, "errors": ["Not a dataclass"]}
    
    # Check for required fields
    for field in fields(target_class):
        has_default = field.default is not field.default_factory
        if not has_default and field.default_factory is field.default_factory:
            # Required field
            json_name = field.name
            if hasattr(target_class, '_get_json_mapping'):
                mapping = target_class._get_json_mapping()
                json_name = mapping.get(field.name, field.name)
            
            if json_name not in data and field.name not in data:
                errors.append(f"Missing required field: {json_name}")
    
    # Try to instantiate
    try:
        load_dict(data, target_class)
    except Exception as e:
        errors.append(f"Instantiation error: {e}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
