"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Schema Parser - Parses and analyzes JSON Schema documents.

Provides structured access to schema components including:
- Properties and their types
- Required fields
- Composition keywords (allOf, anyOf, oneOf)
- Conditional schemas (if/then/else)
- Dependencies
"""

import copy
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from .reference_resolver import ReferenceResolver


class SchemaType(Enum):
    """JSON Schema primitive types."""
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


@dataclass
class PropertyInfo:
    """Information about a schema property."""
    name: str
    schema: Dict[str, Any]
    required: bool = False
    nullable: bool = False
    types: List[SchemaType] = field(default_factory=list)
    description: Optional[str] = None
    default: Any = None
    has_default: bool = False
    enum_values: Optional[List[Any]] = None
    const_value: Any = None
    has_const: bool = False
    format: Optional[str] = None
    pattern: Optional[str] = None
    ref: Optional[str] = None
    
    # Numeric constraints
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    exclusive_minimum: Optional[float] = None
    exclusive_maximum: Optional[float] = None
    multiple_of: Optional[float] = None
    
    # String constraints
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    
    # Array constraints
    items_schema: Optional[Dict[str, Any]] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    unique_items: bool = False
    
    # Object constraints (for nested objects)
    properties: Optional[Dict[str, Any]] = None
    additional_properties: Union[bool, Dict[str, Any], None] = None


@dataclass
class SchemaInfo:
    """Parsed information about a JSON Schema."""
    schema: Dict[str, Any]
    title: Optional[str] = None
    description: Optional[str] = None
    types: List[SchemaType] = field(default_factory=list)
    properties: Dict[str, PropertyInfo] = field(default_factory=dict)
    required: Set[str] = field(default_factory=set)
    definitions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Composition
    all_of: List[Dict[str, Any]] = field(default_factory=list)
    any_of: List[Dict[str, Any]] = field(default_factory=list)
    one_of: List[Dict[str, Any]] = field(default_factory=list)
    not_schema: Optional[Dict[str, Any]] = None
    
    # Conditional
    if_schema: Optional[Dict[str, Any]] = None
    then_schema: Optional[Dict[str, Any]] = None
    else_schema: Optional[Dict[str, Any]] = None
    
    # Dependencies
    dependencies: Dict[str, Union[List[str], Dict[str, Any]]] = field(default_factory=dict)
    dependent_required: Dict[str, List[str]] = field(default_factory=dict)
    dependent_schemas: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Additional
    additional_properties: Union[bool, Dict[str, Any], None] = None
    pattern_properties: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class SchemaParser:
    """
    Parses JSON Schema documents into structured SchemaInfo objects.
    
    Handles complex schemas with references, composition, and conditionals.
    """
    
    def __init__(
        self,
        schema: Dict[str, Any],
        resolver: Optional[ReferenceResolver] = None,
        resolve_refs: bool = True,
    ):
        """
        Initialize the schema parser.
        
        Args:
            schema: The JSON Schema to parse
            resolver: Optional reference resolver
            resolve_refs: Whether to resolve $ref references
        """
        self.original_schema = schema
        self.resolver = resolver or ReferenceResolver(schema)
        self.resolve_refs = resolve_refs
        
        # Resolve all references if requested
        if resolve_refs:
            self.schema = self.resolver.resolve_all()
        else:
            self.schema = copy.deepcopy(schema)
    
    def parse(self) -> SchemaInfo:
        """
        Parse the schema and return structured information.
        
        Returns:
            SchemaInfo object with parsed schema details
        """
        return self._parse_schema(self.schema)
    
    def _parse_schema(self, schema: Dict[str, Any]) -> SchemaInfo:
        """Parse a schema into SchemaInfo."""
        info = SchemaInfo(schema=schema)
        
        # Basic metadata
        info.title = schema.get("title")
        info.description = schema.get("description")
        
        # Parse types
        info.types = self._parse_types(schema)
        
        # Parse properties
        if "properties" in schema:
            required = set(schema.get("required", []))
            info.required = required
            for prop_name, prop_schema in schema["properties"].items():
                info.properties[prop_name] = self._parse_property(
                    prop_name, prop_schema, prop_name in required
                )
        
        # Parse definitions
        info.definitions = schema.get("definitions", schema.get("$defs", {}))
        
        # Parse composition
        info.all_of = schema.get("allOf", [])
        info.any_of = schema.get("anyOf", [])
        info.one_of = schema.get("oneOf", [])
        info.not_schema = schema.get("not")
        
        # Parse conditionals
        info.if_schema = schema.get("if")
        info.then_schema = schema.get("then")
        info.else_schema = schema.get("else")
        
        # Parse dependencies (Draft-07)
        if "dependencies" in schema:
            for key, value in schema["dependencies"].items():
                if isinstance(value, list):
                    info.dependent_required[key] = value
                else:
                    info.dependent_schemas[key] = value
            info.dependencies = schema["dependencies"]
        
        # Parse dependencies (Draft 2019-09+)
        info.dependent_required.update(schema.get("dependentRequired", {}))
        info.dependent_schemas.update(schema.get("dependentSchemas", {}))
        
        # Additional properties
        info.additional_properties = schema.get("additionalProperties", True)
        info.pattern_properties = schema.get("patternProperties", {})
        
        return info
    
    def _parse_types(self, schema: Dict[str, Any]) -> List[SchemaType]:
        """Parse the type(s) from a schema."""
        types = []
        
        schema_type = schema.get("type")
        if schema_type:
            if isinstance(schema_type, list):
                types = [SchemaType(t) for t in schema_type]
            else:
                types = [SchemaType(schema_type)]
        else:
            # Infer type from other keywords
            if "properties" in schema or "additionalProperties" in schema:
                types = [SchemaType.OBJECT]
            elif "items" in schema:
                types = [SchemaType.ARRAY]
            elif "enum" in schema:
                # Infer from enum values
                types = list(set(self._infer_type(v) for v in schema["enum"]))
        
        return types
    
    def _infer_type(self, value: Any) -> SchemaType:
        """Infer SchemaType from a Python value."""
        if value is None:
            return SchemaType.NULL
        elif isinstance(value, bool):
            return SchemaType.BOOLEAN
        elif isinstance(value, int):
            return SchemaType.INTEGER
        elif isinstance(value, float):
            return SchemaType.NUMBER
        elif isinstance(value, str):
            return SchemaType.STRING
        elif isinstance(value, list):
            return SchemaType.ARRAY
        elif isinstance(value, dict):
            return SchemaType.OBJECT
        return SchemaType.STRING
    
    def _parse_property(
        self,
        name: str,
        schema: Dict[str, Any],
        required: bool = False
    ) -> PropertyInfo:
        """Parse a property schema into PropertyInfo."""
        prop = PropertyInfo(
            name=name,
            schema=schema,
            required=required,
        )
        
        # Handle $ref (if not resolved)
        if "$ref" in schema:
            prop.ref = schema["$ref"]
        
        # Parse types
        prop.types = self._parse_types(schema)
        prop.nullable = SchemaType.NULL in prop.types
        
        # Basic metadata
        prop.description = schema.get("description")
        prop.format = schema.get("format")
        prop.pattern = schema.get("pattern")
        
        # Default value
        if "default" in schema:
            prop.default = schema["default"]
            prop.has_default = True
        
        # Enum and const
        if "enum" in schema:
            prop.enum_values = schema["enum"]
        if "const" in schema:
            prop.const_value = schema["const"]
            prop.has_const = True
        
        # Numeric constraints
        prop.minimum = schema.get("minimum")
        prop.maximum = schema.get("maximum")
        prop.exclusive_minimum = schema.get("exclusiveMinimum")
        prop.exclusive_maximum = schema.get("exclusiveMaximum")
        prop.multiple_of = schema.get("multipleOf")
        
        # String constraints
        prop.min_length = schema.get("minLength")
        prop.max_length = schema.get("maxLength")
        
        # Array constraints
        if "items" in schema:
            prop.items_schema = schema["items"]
        prop.min_items = schema.get("minItems")
        prop.max_items = schema.get("maxItems")
        prop.unique_items = schema.get("uniqueItems", False)
        
        # Object constraints
        prop.properties = schema.get("properties")
        prop.additional_properties = schema.get("additionalProperties")
        
        return prop
    
    def get_all_properties(self, include_composed: bool = True) -> Dict[str, PropertyInfo]:
        """
        Get all properties including those from allOf compositions.
        
        Args:
            include_composed: Whether to include properties from allOf schemas
            
        Returns:
            Dictionary of property names to PropertyInfo
        """
        info = self.parse()
        all_props = dict(info.properties)
        
        if include_composed:
            # Merge properties from allOf
            for sub_schema in info.all_of:
                sub_parser = SchemaParser(sub_schema, self.resolver, self.resolve_refs)
                sub_info = sub_parser.parse()
                for prop_name, prop_info in sub_info.properties.items():
                    if prop_name not in all_props:
                        all_props[prop_name] = prop_info
        
        return all_props
    
    def get_effective_schema(self) -> Dict[str, Any]:
        """
        Get the effective schema after merging allOf schemas.
        
        Returns:
            Merged schema dictionary
        """
        info = self.parse()
        
        if not info.all_of:
            return self.schema
        
        # Start with base schema
        effective = copy.deepcopy(self.schema)
        effective.pop("allOf", None)
        
        # Merge each allOf schema
        for sub_schema in info.all_of:
            effective = self._merge_schemas(effective, sub_schema)
        
        return effective
    
    def _merge_schemas(
        self,
        base: Dict[str, Any],
        overlay: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two schemas together."""
        result = copy.deepcopy(base)
        
        # Merge properties
        if "properties" in overlay:
            if "properties" not in result:
                result["properties"] = {}
            result["properties"].update(overlay["properties"])
        
        # Merge required
        if "required" in overlay:
            existing = set(result.get("required", []))
            existing.update(overlay["required"])
            result["required"] = list(existing)
        
        # Merge other keywords
        for key in ["title", "description"]:
            if key in overlay and key not in result:
                result[key] = overlay[key]
        
        return result
    
    def get_definition(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a definition by name.
        
        Args:
            name: The definition name
            
        Returns:
            The definition schema or None if not found
        """
        info = self.parse()
        return info.definitions.get(name)
    
    def list_definitions(self) -> List[str]:
        """
        List all definition names.
        
        Returns:
            List of definition names
        """
        info = self.parse()
        return list(info.definitions.keys())


def parse_schema(schema: Dict[str, Any], resolve_refs: bool = True) -> SchemaInfo:
    """
    Convenience function to parse a schema.
    
    Args:
        schema: The JSON Schema to parse
        resolve_refs: Whether to resolve $ref references
        
    Returns:
        SchemaInfo object with parsed schema details
    """
    parser = SchemaParser(schema, resolve_refs=resolve_refs)
    return parser.parse()
