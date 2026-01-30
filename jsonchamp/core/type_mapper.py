"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Type Mapper - Maps JSON Schema types to Python types.

Handles complex type mappings including:
- Basic types (string, number, integer, boolean, null)
- Complex types (array, object)
- Format-specific types (date, datetime, email, uri, uuid)
- Nullable types
- Union types (anyOf, oneOf)
- Custom type mappings
"""

from typing import Any, Dict, List, Optional, Set, Type, Union, get_type_hints
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field
import re


@dataclass
class TypeMapping:
    """Represents a mapping from JSON Schema to Python type."""
    python_type: Type
    type_hint: str  # String representation for code generation
    import_statement: Optional[str] = None
    is_optional: bool = False
    is_list: bool = False
    list_item_type: Optional["TypeMapping"] = None
    is_dict: bool = False
    dict_value_type: Optional["TypeMapping"] = None
    is_union: bool = False
    union_types: List["TypeMapping"] = field(default_factory=list)
    is_custom_class: bool = False
    custom_class_name: Optional[str] = None
    default_value: Optional[str] = None  # String representation for code gen
    enum_values: Optional[List[Any]] = None


class TypeMapper:
    """
    Maps JSON Schema types to Python types.
    
    Supports customization and extension for specific use cases.
    """
    
    # Default type mappings
    DEFAULT_TYPE_MAP = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "null": type(None),
        "array": list,
        "object": dict,
    }
    
    # Format-specific type mappings
    DEFAULT_FORMAT_MAP = {
        "date": date,
        "date-time": datetime,
        "time": time,
        "email": str,
        "uri": str,
        "url": str,
        "uuid": UUID,
        "hostname": str,
        "ipv4": str,
        "ipv6": str,
        "regex": str,
        "json-pointer": str,
        "relative-json-pointer": str,
        "uri-reference": str,
        "uri-template": str,
        "iri": str,
        "iri-reference": str,
        "duration": str,
    }
    
    # Type hints for code generation
    DEFAULT_TYPE_HINTS = {
        str: "str",
        int: "int",
        float: "float",
        bool: "bool",
        type(None): "None",
        list: "List",
        dict: "Dict",
        date: "date",
        datetime: "datetime",
        time: "time",
        UUID: "UUID",
        Decimal: "Decimal",
        Any: "Any",
    }
    
    # Import statements needed for types
    DEFAULT_IMPORTS = {
        date: "from datetime import date",
        datetime: "from datetime import datetime",
        time: "from datetime import time",
        UUID: "from uuid import UUID",
        Decimal: "from decimal import Decimal",
    }
    
    def __init__(
        self,
        custom_type_map: Optional[Dict[str, Type]] = None,
        custom_format_map: Optional[Dict[str, Type]] = None,
        use_decimal_for_number: bool = False,
        use_strict_types: bool = False,
    ):
        """
        Initialize the type mapper.
        
        Args:
            custom_type_map: Custom type mappings to override defaults
            custom_format_map: Custom format mappings to override defaults
            use_decimal_for_number: Use Decimal instead of float for numbers
            use_strict_types: Use stricter type mappings
        """
        self.type_map = dict(self.DEFAULT_TYPE_MAP)
        if custom_type_map:
            self.type_map.update(custom_type_map)
        
        self.format_map = dict(self.DEFAULT_FORMAT_MAP)
        if custom_format_map:
            self.format_map.update(custom_format_map)
        
        if use_decimal_for_number:
            self.type_map["number"] = Decimal
        
        self.use_strict_types = use_strict_types
        
        # Track generated custom classes
        self.custom_classes: Dict[str, Dict[str, Any]] = {}
    
    def map_schema(self, schema: Dict[str, Any], property_name: Optional[str] = None) -> TypeMapping:
        """
        Map a JSON Schema to a Python type.
        
        Args:
            schema: The JSON Schema
            property_name: Optional property name for context
            
        Returns:
            TypeMapping with Python type information
        """
        # Handle $ref (should be resolved already, but handle gracefully)
        if "$ref" in schema:
            ref = schema["$ref"]
            class_name = self._ref_to_class_name(ref)
            return TypeMapping(
                python_type=dict,
                type_hint=f'"{class_name}"',
                is_custom_class=True,
                custom_class_name=class_name,
            )
        
        # Handle const
        if "const" in schema:
            const_val = schema["const"]
            py_type = type(const_val)
            return TypeMapping(
                python_type=py_type,
                type_hint=self._get_type_hint(py_type),
            )
        
        # Handle enum
        if "enum" in schema:
            return self._map_enum(schema, property_name)
        
        # Handle composition keywords
        if "anyOf" in schema:
            return self._map_any_of(schema["anyOf"])
        if "oneOf" in schema:
            return self._map_one_of(schema["oneOf"])
        if "allOf" in schema:
            return self._map_all_of(schema["allOf"])
        
        # Get the type
        schema_type = schema.get("type")
        
        # Handle multiple types (e.g., ["string", "null"])
        if isinstance(schema_type, list):
            return self._map_union_types(schema_type, schema)
        
        # Handle single type
        if schema_type:
            return self._map_single_type(schema_type, schema, property_name)
        
        # No type specified - try to infer
        return self._infer_type(schema, property_name)
    
    def _map_single_type(
        self,
        schema_type: str,
        schema: Dict[str, Any],
        property_name: Optional[str] = None
    ) -> TypeMapping:
        """Map a single schema type."""
        # Check for format first
        format_type = schema.get("format")
        if format_type and format_type in self.format_map:
            py_type = self.format_map[format_type]
            return TypeMapping(
                python_type=py_type,
                type_hint=self._get_type_hint(py_type),
                import_statement=self.DEFAULT_IMPORTS.get(py_type),
            )
        
        # Map the base type
        py_type = self.type_map.get(schema_type, Any)
        
        # Handle arrays
        if schema_type == "array":
            return self._map_array(schema)
        
        # Handle objects
        if schema_type == "object":
            return self._map_object(schema, property_name)
        
        # Get default value representation
        default_val = self._get_default_repr(schema, py_type)
        
        return TypeMapping(
            python_type=py_type,
            type_hint=self._get_type_hint(py_type),
            default_value=default_val,
        )
    
    def _map_array(self, schema: Dict[str, Any]) -> TypeMapping:
        """Map an array schema."""
        items_schema = schema.get("items", {})
        
        if items_schema:
            item_mapping = self.map_schema(items_schema)
            type_hint = f"List[{item_mapping.type_hint}]"
        else:
            item_mapping = TypeMapping(python_type=Any, type_hint="Any")
            type_hint = "List[Any]"
        
        return TypeMapping(
            python_type=list,
            type_hint=type_hint,
            import_statement="from typing import List",
            is_list=True,
            list_item_type=item_mapping,
            default_value="field(default_factory=list)",
        )
    
    def _map_object(
        self,
        schema: Dict[str, Any],
        property_name: Optional[str] = None
    ) -> TypeMapping:
        """Map an object schema."""
        # If it has properties, it might be a custom class
        if "properties" in schema:
            class_name = self._generate_class_name(schema, property_name)
            self.custom_classes[class_name] = schema
            
            return TypeMapping(
                python_type=dict,
                type_hint=f'"{class_name}"',
                is_custom_class=True,
                custom_class_name=class_name,
            )
        
        # Check additionalProperties for dict value type
        additional = schema.get("additionalProperties")
        if isinstance(additional, dict):
            value_mapping = self.map_schema(additional)
            type_hint = f"Dict[str, {value_mapping.type_hint}]"
        else:
            type_hint = "Dict[str, Any]"
        
        return TypeMapping(
            python_type=dict,
            type_hint=type_hint,
            import_statement="from typing import Dict, Any",
            is_dict=True,
            default_value="field(default_factory=dict)",
        )
    
    def _map_union_types(
        self,
        types: List[str],
        schema: Dict[str, Any]
    ) -> TypeMapping:
        """Map a union of types (e.g., ["string", "null"])."""
        # Check if it's just nullable
        non_null_types = [t for t in types if t != "null"]
        is_nullable = "null" in types
        
        if len(non_null_types) == 1:
            # Simple nullable type
            base_schema = dict(schema)
            base_schema["type"] = non_null_types[0]
            base_mapping = self._map_single_type(non_null_types[0], base_schema)
            
            if is_nullable:
                return TypeMapping(
                    python_type=base_mapping.python_type,
                    type_hint=f"Optional[{base_mapping.type_hint}]",
                    import_statement="from typing import Optional",
                    is_optional=True,
                    default_value="None",
                )
            return base_mapping
        
        # True union type
        union_mappings = []
        for t in non_null_types:
            type_schema = dict(schema)
            type_schema["type"] = t
            union_mappings.append(self._map_single_type(t, type_schema))
        
        type_hints = [m.type_hint for m in union_mappings]
        if is_nullable:
            type_hints.append("None")
        
        return TypeMapping(
            python_type=object,
            type_hint=f"Union[{', '.join(type_hints)}]",
            import_statement="from typing import Union",
            is_union=True,
            union_types=union_mappings,
            is_optional=is_nullable,
        )
    
    def _map_any_of(self, schemas: List[Dict[str, Any]]) -> TypeMapping:
        """Map anyOf schema."""
        mappings = [self.map_schema(s) for s in schemas]
        
        # Check if it's just a nullable type
        non_null = [m for m in mappings if m.python_type != type(None)]
        is_nullable = len(non_null) < len(mappings)
        
        if len(non_null) == 1:
            base = non_null[0]
            if is_nullable:
                return TypeMapping(
                    python_type=base.python_type,
                    type_hint=f"Optional[{base.type_hint}]",
                    import_statement="from typing import Optional",
                    is_optional=True,
                    default_value="None",
                )
            return base
        
        type_hints = [m.type_hint for m in mappings]
        return TypeMapping(
            python_type=object,
            type_hint=f"Union[{', '.join(type_hints)}]",
            import_statement="from typing import Union",
            is_union=True,
            union_types=mappings,
        )
    
    def _map_one_of(self, schemas: List[Dict[str, Any]]) -> TypeMapping:
        """Map oneOf schema (treated same as anyOf for typing purposes)."""
        return self._map_any_of(schemas)
    
    def _map_all_of(self, schemas: List[Dict[str, Any]]) -> TypeMapping:
        """Map allOf schema (merge all schemas)."""
        # For type mapping, we treat allOf as the intersection
        # Usually one of them has the main type
        for schema in schemas:
            if "type" in schema or "properties" in schema:
                return self.map_schema(schema)
        
        # Fall back to first schema
        if schemas:
            return self.map_schema(schemas[0])
        
        return TypeMapping(python_type=Any, type_hint="Any")
    
    def _map_enum(
        self,
        schema: Dict[str, Any],
        property_name: Optional[str] = None
    ) -> TypeMapping:
        """Map an enum schema."""
        enum_values = schema["enum"]
        
        # Determine the value type
        value_types = set(type(v) for v in enum_values if v is not None)
        
        if len(value_types) == 1:
            py_type = value_types.pop()
        else:
            py_type = object
        
        # Check if all values are strings (could generate a string enum)
        all_strings = all(isinstance(v, str) for v in enum_values if v is not None)
        
        if all_strings and property_name:
            # Could generate a proper Enum class
            enum_name = self._to_class_name(property_name) + "Enum"
            type_hint = f'"{enum_name}"'
        else:
            type_hint = self._get_type_hint(py_type)
        
        return TypeMapping(
            python_type=py_type,
            type_hint=type_hint,
            enum_values=enum_values,
        )
    
    def _infer_type(
        self,
        schema: Dict[str, Any],
        property_name: Optional[str] = None
    ) -> TypeMapping:
        """Infer type from schema keywords."""
        # Check for object-like schemas
        if "properties" in schema:
            return self._map_object(schema, property_name)
        
        # Check for array-like schemas
        if "items" in schema:
            return self._map_array(schema)
        
        # Check for string-like constraints
        if any(k in schema for k in ["minLength", "maxLength", "pattern", "format"]):
            return TypeMapping(python_type=str, type_hint="str")
        
        # Check for numeric constraints
        if any(k in schema for k in ["minimum", "maximum", "multipleOf"]):
            return TypeMapping(python_type=float, type_hint="float")
        
        # Default to Any
        return TypeMapping(
            python_type=Any,
            type_hint="Any",
            import_statement="from typing import Any",
        )
    
    def _get_type_hint(self, py_type: Type) -> str:
        """Get the type hint string for a Python type."""
        return self.DEFAULT_TYPE_HINTS.get(py_type, py_type.__name__)
    
    def _get_default_repr(self, schema: Dict[str, Any], py_type: Type) -> Optional[str]:
        """Get the default value representation for code generation."""
        if "default" in schema:
            default = schema["default"]
            if isinstance(default, str):
                return f'"{default}"'
            elif isinstance(default, bool):
                return str(default)
            elif default is None:
                return "None"
            else:
                return repr(default)
        return None
    
    def _ref_to_class_name(self, ref: str) -> str:
        """Convert a $ref to a class name."""
        # Extract the last part of the reference path
        parts = ref.split("/")
        name = parts[-1]
        return self._to_class_name(name)
    
    def _generate_class_name(
        self,
        schema: Dict[str, Any],
        property_name: Optional[str] = None
    ) -> str:
        """Generate a class name for an object schema."""
        if "title" in schema:
            return self._to_class_name(schema["title"])
        if property_name:
            return self._to_class_name(property_name)
        return "AnonymousObject"
    
    def _to_class_name(self, name: str) -> str:
        """Convert a name to a valid Python class name."""
        # Remove special characters and convert to PascalCase
        words = re.split(r'[-_\s]+', name)
        return "".join(word.capitalize() for word in words if word)
    
    def get_required_imports(self, mappings: List[TypeMapping]) -> Set[str]:
        """Get all required import statements for a list of mappings."""
        imports = set()
        
        for mapping in mappings:
            if mapping.import_statement:
                imports.add(mapping.import_statement)
            
            if mapping.list_item_type:
                imports.update(self.get_required_imports([mapping.list_item_type]))
            
            if mapping.dict_value_type:
                imports.update(self.get_required_imports([mapping.dict_value_type]))
            
            if mapping.union_types:
                imports.update(self.get_required_imports(mapping.union_types))
        
        return imports
    
    def get_custom_classes(self) -> Dict[str, Dict[str, Any]]:
        """Get all custom classes discovered during mapping."""
        return dict(self.custom_classes)


def map_schema_type(schema: Dict[str, Any]) -> TypeMapping:
    """
    Convenience function to map a schema to a Python type.
    
    Args:
        schema: The JSON Schema
        
    Returns:
        TypeMapping with Python type information
    """
    mapper = TypeMapper()
    return mapper.map_schema(schema)
