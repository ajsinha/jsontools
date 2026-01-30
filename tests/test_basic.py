"""
JsonSchemaCodeGen - Basic Tests

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

import pytest
from jsontools import SchemaProcessor, __version__


def test_version():
    """Test version is set."""
    assert __version__ == "1.0.0"


def test_basic_schema():
    """Test basic schema processing."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    
    processor = SchemaProcessor(schema)
    info = processor.parse()
    
    assert len(info.properties) == 2
    assert "name" in info.properties
    assert info.properties["name"].required is True


def test_code_generation():
    """Test code generation."""
    schema = {
        "type": "object",
        "title": "Person",
        "properties": {
            "name": {"type": "string"}
        }
    }
    
    processor = SchemaProcessor(schema, root_class_name="Person")
    code = processor.generate_code()
    
    assert "class Person" in code
    assert "name" in code


def test_sample_generation():
    """Test sample data generation."""
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "active": {"type": "boolean"}
        }
    }
    
    processor = SchemaProcessor(schema)
    samples = processor.generate_samples(count=3)
    
    assert len(samples) == 3
    for sample in samples:
        assert isinstance(sample, dict)
