"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Class Generator - Generate Python classes dynamically from JSON Schema.

Features:
- Dynamic dataclass generation
- Proper field ordering (required before optional)
- JSON serialization/deserialization methods
- Nested class support
- Validation integration
"""

import json
from dataclasses import dataclass, field, fields, asdict
from typing import Any, Dict, List, Optional, Set, Type, Union, get_type_hints
from datetime import datetime, date

from ..core.reference_resolver import ReferenceResolver
from ..core.type_mapper import TypeMapper, TypeMapping


class ClassGenerator:
    """
    Generates Python dataclasses dynamically from JSON Schema.
    
    The generated classes include:
    - Proper type hints
    - Default values for optional fields
    - to_dict() and to_json() serialization methods
    - from_dict() and from_json() deserialization class methods
    - Nested class support for object properties
    """
    
    def __init__(
        self,
        schema: Dict[str, Any],
        resolver: Optional[ReferenceResolver] = None,
        type_mapper: Optional[TypeMapper] = None,
        root_class_name: str = "Root",
    ):
        """
        Initialize the class generator.
        
        Args:
            schema: The JSON Schema
            resolver: Reference resolver (created if not provided)
            type_mapper: Type mapper (created if not provided)
            root_class_name: Name for the root class
        """
        self.schema = schema
        self.resolver = resolver or ReferenceResolver(schema)
        self.type_mapper = type_mapper or TypeMapper()
        self.root_class_name = root_class_name
        
        # Get resolved schema
        self.resolved_schema = self.resolver.resolve_all()
        
        # Extract definitions
        self.definitions = self.resolved_schema.get(
            "definitions",
            self.resolved_schema.get("$defs", {})
        )
        
        # Track generated classes
        self.classes: Dict[str, Type] = {}
        
        # Track class dependencies for ordering
        self._class_dependencies: Dict[str, Set[str]] = {}
    
    def generate(self) -> Dict[str, Type]:
        """
        Generate all classes from the schema.
        
        Returns:
            Dictionary mapping class names to generated classes
        """
        # First, generate classes for all definitions
        for def_name, def_schema in self.definitions.items():
            if def_schema.get("type") == "object" or "properties" in def_schema:
                self._generate_class(def_name, def_schema)
        
        # Generate the root class
        if self.resolved_schema.get("type") == "object" or "properties" in self.resolved_schema:
            self._generate_class(self.root_class_name, self.resolved_schema)
        
        return self.classes
    
    def _generate_class(
        self,
        class_name: str,
        schema: Dict[str, Any],
    ) -> Type:
        """Generate a single class from a schema."""
        if class_name in self.classes:
            return self.classes[class_name]
        
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        
        # Analyze properties
        required_fields = []
        optional_fields = []
        
        for prop_name, prop_schema in properties.items():
            safe_name = self._to_safe_name(prop_name)
            
            # Check if this is a nested object that needs its own class
            if prop_schema.get("type") == "object" and "properties" in prop_schema:
                nested_class_name = self._to_class_name(prop_name)
                self._generate_class(nested_class_name, prop_schema)
            
            # Determine if required
            is_required = prop_name in required
            
            # Get type mapping
            mapping = self.type_mapper.map_schema(prop_schema, prop_name)
            
            # Build field info
            field_info = {
                "name": safe_name,
                "original_name": prop_name,
                "mapping": mapping,
                "schema": prop_schema,
            }
            
            if is_required:
                required_fields.append(field_info)
            else:
                optional_fields.append(field_info)
        
        # Build class
        annotations = {}
        defaults = {}
        property_mapping = {}
        
        # Add required fields first
        for field_info in required_fields:
            name = field_info["name"]
            mapping = field_info["mapping"]
            
            annotations[name] = self._get_annotation(mapping)
            property_mapping[name] = field_info["original_name"]
        
        # Add optional fields with defaults
        for field_info in optional_fields:
            name = field_info["name"]
            mapping = field_info["mapping"]
            
            # Make type optional
            base_type = self._get_annotation(mapping)
            annotations[name] = Optional[base_type]
            
            # Set default
            if mapping.is_list:
                defaults[name] = field(default_factory=list)
            elif mapping.is_dict:
                defaults[name] = field(default_factory=dict)
            else:
                defaults[name] = None
            
            property_mapping[name] = field_info["original_name"]
        
        # Create class dictionary
        class_dict = {
            "__annotations__": annotations,
            "_property_mapping": property_mapping,
            "_schema": schema,
            **defaults,
        }
        
        # Create the class
        new_class = type(class_name, (), class_dict)
        
        # Apply dataclass decorator
        new_class = dataclass(new_class)
        
        # Add methods
        self._add_serialization_methods(new_class)
        
        # Store the class
        self.classes[class_name] = new_class
        
        return new_class
    
    def _get_annotation(self, mapping: TypeMapping) -> type:
        """Get the Python type annotation from a mapping."""
        if mapping.is_custom_class and mapping.custom_class_name:
            # Return the class if already generated, otherwise use str forward ref
            if mapping.custom_class_name in self.classes:
                return self.classes[mapping.custom_class_name]
            return dict  # Fallback to dict for not-yet-generated classes
        
        if mapping.is_list:
            return list
        
        if mapping.is_dict:
            return dict
        
        return mapping.python_type
    
    def _add_serialization_methods(self, cls: Type) -> None:
        """Add serialization methods to a class."""
        
        def to_dict(self) -> Dict[str, Any]:
            """Convert to dictionary with original property names."""
            result = {}
            for py_name, json_name in self._property_mapping.items():
                value = getattr(self, py_name, None)
                if value is not None:
                    result[json_name] = self._serialize_value(value)
            return result
        
        def _serialize_value(self, value: Any) -> Any:
            """Serialize a single value."""
            if hasattr(value, "to_dict"):
                return value.to_dict()
            elif isinstance(value, list):
                return [self._serialize_value(item) for item in value]
            elif isinstance(value, dict):
                return {k: self._serialize_value(v) for k, v in value.items()}
            elif isinstance(value, (datetime, date)):
                return value.isoformat()
            return value
        
        def to_json(self, indent: int = 2) -> str:
            """Serialize to JSON string."""
            return json.dumps(self.to_dict(), indent=indent, default=str)
        
        @classmethod
        def from_dict(cls, data: Dict[str, Any]):
            """Create instance from dictionary."""
            reverse_mapping = {v: k for k, v in cls._property_mapping.items()}
            kwargs = {}
            for json_name, value in data.items():
                py_name = reverse_mapping.get(json_name, json_name)
                if py_name in cls.__annotations__:
                    kwargs[py_name] = value
            return cls(**kwargs)
        
        @classmethod
        def from_json(cls, json_str: str):
            """Create instance from JSON string."""
            return cls.from_dict(json.loads(json_str))
        
        # Attach methods
        cls.to_dict = to_dict
        cls._serialize_value = _serialize_value
        cls.to_json = to_json
        cls.from_dict = from_dict
        cls.from_json = from_json
    
    def _to_safe_name(self, name: str) -> str:
        """Convert a name to a valid Python identifier."""
        # Replace special characters
        safe = name.replace("-", "_").replace(" ", "_").replace(".", "_")
        safe = safe.replace("@", "_at_").replace("#", "_hash_")
        
        # Ensure doesn't start with a digit
        if safe and safe[0].isdigit():
            safe = "_" + safe
        
        # Handle Python keywords
        keywords = {
            "class", "def", "return", "import", "from", "for", "while",
            "if", "else", "elif", "try", "except", "finally", "with",
            "as", "is", "in", "not", "and", "or", "True", "False", "None",
            "lambda", "yield", "assert", "break", "continue", "del",
            "exec", "global", "pass", "print", "raise", "type",
        }
        if safe in keywords:
            safe = safe + "_"
        
        return safe
    
    def _to_class_name(self, name: str) -> str:
        """Convert a name to a valid Python class name."""
        # Split on separators and capitalize each part
        import re
        words = re.split(r"[-_\s]+", name)
        return "".join(word.capitalize() for word in words if word)


def generate_classes(
    schema: Dict[str, Any],
    root_class_name: str = "Root",
    **kwargs,
) -> Dict[str, Type]:
    """
    Convenience function to generate classes from a schema.
    
    Args:
        schema: The JSON Schema
        root_class_name: Name for the root class
        **kwargs: Additional arguments for ClassGenerator
        
    Returns:
        Dictionary mapping class names to generated classes
    """
    generator = ClassGenerator(schema, root_class_name=root_class_name, **kwargs)
    return generator.generate()
