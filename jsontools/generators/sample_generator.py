"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Sample Generator - Generate realistic sample JSON data from JSON Schema.

Features:
- Faker integration for realistic data
- Constraint-aware generation (min/max, patterns, formats)
- Recursive schema handling
- Customizable generation strategies
"""

import json
import random
import string
import re
from datetime import datetime, date, time, timedelta
from typing import Any, Dict, List, Optional, Callable, Union
from uuid import uuid4

try:
    from faker import Faker
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False


class SampleGenerator:
    """
    Generates sample JSON data from JSON Schema.
    
    Supports all JSON Schema types and constraints, with optional
    Faker integration for realistic data generation.
    """
    
    def __init__(
        self,
        schema: Dict[str, Any],
        use_faker: bool = True,
        locale: str = "en_US",
        seed: Optional[int] = None,
        custom_generators: Optional[Dict[str, Callable]] = None,
        include_optional: float = 0.7,
    ):
        """
        Initialize the sample generator.
        
        Args:
            schema: The JSON Schema to generate from
            use_faker: Whether to use Faker for realistic data
            locale: Faker locale
            seed: Random seed for reproducibility
            custom_generators: Custom generators by format or property name
            include_optional: Probability of including optional properties (0-1)
        """
        self.schema = schema
        self.use_faker = use_faker and HAS_FAKER
        self.include_optional = include_optional
        self.custom_generators = custom_generators or {}
        
        # Extract definitions
        self.definitions = schema.get("definitions", schema.get("$defs", {}))
        
        # Initialize random
        if seed is not None:
            random.seed(seed)
        
        # Initialize Faker
        if self.use_faker:
            self.fake = Faker(locale)
            if seed is not None:
                Faker.seed(seed)
        else:
            self.fake = None
        
        # Track recursion depth to prevent infinite loops
        self._recursion_depth = 0
        self._max_recursion = 10
    
    def generate(self) -> Any:
        """
        Generate a sample JSON value from the schema.
        
        Returns:
            Generated sample data
        """
        self._recursion_depth = 0
        return self._generate_value(self.schema)
    
    def generate_many(self, count: int) -> List[Any]:
        """
        Generate multiple samples.
        
        Args:
            count: Number of samples to generate
            
        Returns:
            List of generated samples
        """
        return [self.generate() for _ in range(count)]
    
    def _generate_value(
        self,
        schema: Dict[str, Any],
        property_name: Optional[str] = None,
    ) -> Any:
        """Generate a value based on the schema."""
        if not schema:
            return None
        
        # Check recursion limit
        self._recursion_depth += 1
        if self._recursion_depth > self._max_recursion:
            self._recursion_depth -= 1
            return None
        
        try:
            # Handle $ref
            if "$ref" in schema:
                return self._generate_from_ref(schema["$ref"])
            
            # Handle const
            if "const" in schema:
                return schema["const"]
            
            # Handle enum
            if "enum" in schema:
                return random.choice(schema["enum"])
            
            # Handle default
            if "default" in schema:
                return schema["default"]
            
            # Handle examples
            if "examples" in schema and schema["examples"]:
                return random.choice(schema["examples"])
            
            # Handle composition keywords
            if "anyOf" in schema:
                return self._generate_value(random.choice(schema["anyOf"]))
            if "oneOf" in schema:
                return self._generate_value(random.choice(schema["oneOf"]))
            if "allOf" in schema:
                return self._generate_all_of(schema["allOf"])
            
            # Get type
            schema_type = schema.get("type")
            
            # Handle multiple types
            if isinstance(schema_type, list):
                # Filter out null for generation (unless it's the only type)
                non_null_types = [t for t in schema_type if t != "null"]
                if non_null_types:
                    schema_type = random.choice(non_null_types)
                else:
                    return None
            
            # Check for custom generator
            if property_name and property_name in self.custom_generators:
                return self.custom_generators[property_name](schema)
            
            format_type = schema.get("format")
            if format_type and format_type in self.custom_generators:
                return self.custom_generators[format_type](schema)
            
            # Generate based on type
            generators = {
                "object": self._generate_object,
                "array": self._generate_array,
                "string": self._generate_string,
                "integer": self._generate_integer,
                "number": self._generate_number,
                "boolean": self._generate_boolean,
                "null": lambda s: None,
            }
            
            generator = generators.get(schema_type)
            if generator:
                return generator(schema)
            
            # Try to infer type
            return self._generate_inferred(schema, property_name)
        
        finally:
            self._recursion_depth -= 1
    
    def _generate_from_ref(self, ref: str) -> Any:
        """Generate value from a $ref."""
        # Parse reference
        if ref.startswith("#/definitions/"):
            def_name = ref[14:]
            if def_name in self.definitions:
                return self._generate_value(self.definitions[def_name])
        elif ref.startswith("#/$defs/"):
            def_name = ref[8:]
            if def_name in self.definitions:
                return self._generate_value(self.definitions[def_name])
        
        return {}
    
    def _generate_all_of(self, schemas: List[Dict[str, Any]]) -> Any:
        """Generate value from allOf schemas."""
        result = {}
        for sub_schema in schemas:
            value = self._generate_value(sub_schema)
            if isinstance(value, dict):
                result.update(value)
        return result
    
    def _generate_object(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an object."""
        result = {}
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        
        for prop_name, prop_schema in properties.items():
            # Always include required, randomly include optional
            if prop_name in required or random.random() < self.include_optional:
                result[prop_name] = self._generate_value(prop_schema, prop_name)
        
        return result
    
    def _generate_array(self, schema: Dict[str, Any]) -> List[Any]:
        """Generate an array."""
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 1)
        max_items = schema.get("maxItems", 5)
        
        # Respect uniqueItems
        unique_items = schema.get("uniqueItems", False)
        
        count = random.randint(min_items, max_items)
        
        if unique_items:
            # Generate unique items
            items = set()
            attempts = 0
            while len(items) < count and attempts < count * 10:
                item = self._generate_value(items_schema)
                # Convert to tuple for hashability if needed
                try:
                    if isinstance(item, dict):
                        item_key = json.dumps(item, sort_keys=True)
                    elif isinstance(item, list):
                        item_key = tuple(item)
                    else:
                        item_key = item
                    
                    if item_key not in items:
                        items.add(item_key)
                except TypeError:
                    # Not hashable, just add it
                    pass
                attempts += 1
            
            # Convert back from keys
            result = []
            for item in items:
                if isinstance(item, str) and item.startswith("{"):
                    try:
                        result.append(json.loads(item))
                    except:
                        result.append(item)
                else:
                    result.append(item)
            return result
        
        return [self._generate_value(items_schema) for _ in range(count)]
    
    def _generate_string(self, schema: Dict[str, Any]) -> str:
        """Generate a string value."""
        format_type = schema.get("format")
        pattern = schema.get("pattern")
        min_length = schema.get("minLength", 1)
        max_length = schema.get("maxLength", 100)
        
        # Format-based generation
        if format_type and self.use_faker:
            format_generators = {
                "email": lambda: self.fake.email(),
                "uri": lambda: self.fake.url(),
                "url": lambda: self.fake.url(),
                "date": lambda: self.fake.date(),
                "date-time": lambda: self.fake.iso8601(),
                "time": lambda: self.fake.time(),
                "uuid": lambda: str(uuid4()),
                "ipv4": lambda: self.fake.ipv4(),
                "ipv6": lambda: self.fake.ipv6(),
                "hostname": lambda: self.fake.hostname(),
                "phone": lambda: self.fake.phone_number(),
                "credit-card": lambda: self.fake.credit_card_number(),
                "ssn": lambda: self.fake.ssn(),
                "first-name": lambda: self.fake.first_name(),
                "last-name": lambda: self.fake.last_name(),
                "full-name": lambda: self.fake.name(),
                "company": lambda: self.fake.company(),
                "address": lambda: self.fake.address(),
                "city": lambda: self.fake.city(),
                "country": lambda: self.fake.country(),
                "zip-code": lambda: self.fake.zipcode(),
                "paragraph": lambda: self.fake.paragraph(),
                "sentence": lambda: self.fake.sentence(),
            }
            
            if format_type in format_generators:
                return format_generators[format_type]()
        
        # Pattern-based generation
        if pattern:
            return self._generate_from_pattern(pattern, min_length, max_length)
        
        # Faker-based generation for common patterns
        if self.use_faker:
            # Try to infer from property name or other context
            return self.fake.pystr(min_chars=min_length, max_chars=max_length)
        
        # Basic random string
        length = random.randint(min_length, min(max_length, 50))
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _generate_from_pattern(
        self,
        pattern: str,
        min_length: int,
        max_length: int,
    ) -> str:
        """Generate a string matching a regex pattern."""
        # Simple pattern handling
        # For complex patterns, consider using exrex library
        
        simple_patterns = {
            r"^\d+$": lambda: "".join(random.choices(string.digits, k=random.randint(min_length, max_length))),
            r"^[a-z]+$": lambda: "".join(random.choices(string.ascii_lowercase, k=random.randint(min_length, max_length))),
            r"^[A-Z]+$": lambda: "".join(random.choices(string.ascii_uppercase, k=random.randint(min_length, max_length))),
            r"^[a-zA-Z]+$": lambda: "".join(random.choices(string.ascii_letters, k=random.randint(min_length, max_length))),
            r"^[a-zA-Z0-9]+$": lambda: "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(min_length, max_length))),
        }
        
        for pat, gen in simple_patterns.items():
            if re.match(pat.replace("^", "").replace("$", ""), pattern):
                return gen()
        
        # Fallback to basic string
        return "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(min_length, max_length)))
    
    def _generate_integer(self, schema: Dict[str, Any]) -> int:
        """Generate an integer value."""
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 10000)
        exclusive_min = schema.get("exclusiveMinimum")
        exclusive_max = schema.get("exclusiveMaximum")
        multiple_of = schema.get("multipleOf")
        
        if exclusive_min is not None:
            minimum = exclusive_min + 1
        if exclusive_max is not None:
            maximum = exclusive_max - 1
        
        value = random.randint(int(minimum), int(maximum))
        
        if multiple_of:
            value = (value // multiple_of) * multiple_of
            if value < minimum:
                value += multiple_of
        
        return int(value)
    
    def _generate_number(self, schema: Dict[str, Any]) -> float:
        """Generate a number value."""
        minimum = schema.get("minimum", 0.0)
        maximum = schema.get("maximum", 10000.0)
        exclusive_min = schema.get("exclusiveMinimum")
        exclusive_max = schema.get("exclusiveMaximum")
        multiple_of = schema.get("multipleOf")
        
        if exclusive_min is not None:
            minimum = exclusive_min + 0.0001
        if exclusive_max is not None:
            maximum = exclusive_max - 0.0001
        
        value = random.uniform(minimum, maximum)
        
        if multiple_of:
            value = round(value / multiple_of) * multiple_of
        
        return round(value, 4)
    
    def _generate_boolean(self, schema: Dict[str, Any]) -> bool:
        """Generate a boolean value."""
        return random.choice([True, False])
    
    def _generate_inferred(
        self,
        schema: Dict[str, Any],
        property_name: Optional[str] = None,
    ) -> Any:
        """Try to infer and generate a value when type is not specified."""
        # Check for properties (implies object)
        if "properties" in schema:
            return self._generate_object(schema)
        
        # Check for items (implies array)
        if "items" in schema:
            return self._generate_array(schema)
        
        # Check for string constraints
        if any(k in schema for k in ["minLength", "maxLength", "pattern", "format"]):
            return self._generate_string(schema)
        
        # Check for numeric constraints
        if any(k in schema for k in ["minimum", "maximum", "multipleOf"]):
            return self._generate_number(schema)
        
        # Default to empty object
        return {}


def generate_samples(
    schema: Dict[str, Any],
    count: int = 1,
    use_faker: bool = True,
    **kwargs,
) -> List[Any]:
    """
    Convenience function to generate sample data from a schema.
    
    Args:
        schema: The JSON Schema
        count: Number of samples to generate
        use_faker: Whether to use Faker for realistic data
        **kwargs: Additional arguments for SampleGenerator
        
    Returns:
        List of generated samples
    """
    generator = SampleGenerator(schema, use_faker=use_faker, **kwargs)
    return generator.generate_many(count)
