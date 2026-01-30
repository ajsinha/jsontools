"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Schema Processor - High-level API for working with JSON Schema.

This is the main entry point for most use cases. It provides a unified
interface for:
- Loading and parsing schemas
- Generating Python classes
- Generating sample data
- Generating source code
"""

import json
import os
from typing import Any, Dict, List, Optional, Type, Union
from pathlib import Path

from .schema_parser import SchemaParser, SchemaInfo
from .reference_resolver import ReferenceResolver, SchemaRegistry
from .type_mapper import TypeMapper, TypeMapping
from .validator import SchemaValidator, ValidationResult


class SchemaProcessor:
    """
    High-level processor for JSON Schema operations.
    
    This class provides a convenient interface for common schema operations
    including class generation, sample generation, and code generation.
    
    Example:
        processor = SchemaProcessor(schema)
        
        # Generate Python classes
        classes = processor.generate_classes()
        User = classes["User"]
        user = User(name="John", email="john@example.com")
        
        # Generate sample data
        samples = processor.generate_samples(count=5)
        
        # Generate source code
        code = processor.generate_code()
    """
    
    def __init__(
        self,
        schema: Union[Dict[str, Any], str, Path],
        base_uri: Optional[str] = None,
        schema_store: Optional[Dict[str, Dict[str, Any]]] = None,
        root_class_name: Optional[str] = None,
    ):
        """
        Initialize the schema processor.
        
        Args:
            schema: JSON Schema as dict, JSON string, or file path
            base_uri: Base URI for resolving references
            schema_store: Pre-loaded schemas for reference resolution
            root_class_name: Name for the root class (auto-detected if not provided)
        """
        # Load schema
        self.schema = self._load_schema(schema)
        self.base_uri = base_uri
        
        # Initialize components
        self.resolver = ReferenceResolver(
            self.schema,
            base_uri=base_uri,
            schema_store=schema_store,
        )
        self.parser = SchemaParser(self.schema, self.resolver)
        self.type_mapper = TypeMapper()
        self.validator = SchemaValidator()
        
        # Determine root class name
        self.root_class_name = root_class_name or self._detect_class_name()
        
        # Cache for generated classes
        self._class_cache: Optional[Dict[str, Type]] = None
    
    def _load_schema(self, schema: Union[Dict[str, Any], str, Path]) -> Dict[str, Any]:
        """Load schema from various sources."""
        if isinstance(schema, dict):
            return schema
        
        if isinstance(schema, Path):
            schema = str(schema)
        
        if isinstance(schema, str):
            # Check if it's a file path
            if os.path.isfile(schema):
                with open(schema, "r", encoding="utf-8") as f:
                    return json.load(f)
            
            # Try parsing as JSON string
            try:
                return json.loads(schema)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid schema: not a valid file path or JSON string")
        
        raise TypeError(f"Schema must be dict, str, or Path, got {type(schema)}")
    
    def _detect_class_name(self) -> str:
        """Detect the class name from schema metadata."""
        if "title" in self.schema:
            # Convert title to class name
            title = self.schema["title"]
            return "".join(word.capitalize() for word in title.split())
        return "Root"
    
    def validate_schema(self) -> ValidationResult:
        """
        Validate that the schema is a valid JSON Schema.
        
        Returns:
            ValidationResult with any issues found
        """
        return self.validator.validate_schema(self.schema)
    
    def validate_data(self, data: Any) -> ValidationResult:
        """
        Validate data against the schema.
        
        Args:
            data: The data to validate
            
        Returns:
            ValidationResult with any issues found
        """
        resolved_schema = self.resolver.resolve_all()
        return self.validator.validate_data(data, resolved_schema)
    
    def parse(self) -> SchemaInfo:
        """
        Parse the schema into structured information.
        
        Returns:
            SchemaInfo with parsed schema details
        """
        return self.parser.parse()
    
    def get_resolved_schema(self) -> Dict[str, Any]:
        """
        Get the fully resolved schema with all $ref replaced.
        
        Returns:
            Resolved schema dictionary
        """
        return self.resolver.resolve_all()
    
    def generate_classes(self, regenerate: bool = False) -> Dict[str, Type]:
        """
        Generate Python classes from the schema.
        
        Args:
            regenerate: Force regeneration even if cached
            
        Returns:
            Dictionary mapping class names to generated classes
        """
        if self._class_cache is not None and not regenerate:
            return self._class_cache
        
        # Import here to avoid circular imports
        from ..generators.class_generator import ClassGenerator
        
        generator = ClassGenerator(
            self.schema,
            resolver=self.resolver,
            type_mapper=self.type_mapper,
            root_class_name=self.root_class_name,
        )
        
        self._class_cache = generator.generate()
        return self._class_cache
    
    def generate_samples(
        self,
        count: int = 1,
        use_faker: bool = True,
    ) -> List[Any]:
        """
        Generate sample JSON data from the schema.
        
        Args:
            count: Number of samples to generate
            use_faker: Whether to use Faker for realistic data
            
        Returns:
            List of generated samples
        """
        # Import here to avoid circular imports
        from ..generators.sample_generator import SampleGenerator
        
        resolved_schema = self.resolver.resolve_all()
        generator = SampleGenerator(resolved_schema, use_faker=use_faker)
        
        return [generator.generate() for _ in range(count)]
    
    def generate_code(
        self,
        style: str = "dataclass",
        include_validators: bool = True,
        all_fields_optional: bool = False,
    ) -> str:
        """
        Generate Python source code from the schema.
        
        Args:
            style: Code style ("dataclass" or "attrs")
            include_validators: Whether to include validation methods
            all_fields_optional: If True, all fields get defaults (allows empty constructor)
            
        Returns:
            Python source code as string
        """
        # Import here to avoid circular imports
        from ..generators.code_generator import CodeGenerator
        
        generator = CodeGenerator(
            self.schema,
            resolver=self.resolver,
            type_mapper=self.type_mapper,
            root_class_name=self.root_class_name,
            style=style,
            include_validators=include_validators,
            all_fields_optional=all_fields_optional,
        )
        
        return generator.generate()
    
    def create_instance(self, data: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Create an instance of the root class.
        
        Args:
            data: Dictionary of values (can also use kwargs)
            **kwargs: Additional or override values
            
        Returns:
            Instance of the generated root class
        """
        classes = self.generate_classes()
        root_class = classes.get(self.root_class_name)
        
        if root_class is None:
            raise ValueError(f"Root class '{self.root_class_name}' not found")
        
        if data:
            kwargs = {**data, **kwargs}
        
        return root_class(**kwargs)
    
    def to_json(self, data: Any, indent: int = 2) -> str:
        """
        Serialize data to JSON string.
        
        Args:
            data: Data to serialize (can be generated class instance)
            indent: JSON indentation
            
        Returns:
            JSON string
        """
        if hasattr(data, "to_dict"):
            data = data.to_dict()
        
        return json.dumps(data, indent=indent, default=str)
    
    def from_json(self, json_str: str) -> Any:
        """
        Deserialize JSON string to class instance.
        
        Args:
            json_str: JSON string
            
        Returns:
            Instance of the root class
        """
        data = json.loads(json_str)
        return self.create_instance(data)
    
    def list_definitions(self) -> List[str]:
        """
        List all definitions in the schema.
        
        Returns:
            List of definition names
        """
        return self.parser.list_definitions()
    
    def get_definition(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a definition by name.
        
        Args:
            name: Definition name
            
        Returns:
            Definition schema or None
        """
        return self.parser.get_definition(name)


def process_schema(
    schema: Union[Dict[str, Any], str, Path],
    **kwargs
) -> SchemaProcessor:
    """
    Convenience function to create a SchemaProcessor.
    
    Args:
        schema: JSON Schema (dict, JSON string, or file path)
        **kwargs: Additional arguments for SchemaProcessor
        
    Returns:
        Configured SchemaProcessor
    """
    return SchemaProcessor(schema, **kwargs)


def load_schema(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load a JSON Schema from a file.
    
    Args:
        path: Path to the schema file
        
    Returns:
        Schema dictionary
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_schemas_from_directory(
    directory: Union[str, Path],
    pattern: str = "*.json",
) -> SchemaRegistry:
    """
    Load all schemas from a directory into a registry.
    
    Args:
        directory: Path to the directory
        pattern: Glob pattern for schema files
        
    Returns:
        SchemaRegistry with all loaded schemas
    """
    registry = SchemaRegistry(str(directory))
    registry.register_directory(".", pattern)
    return registry
