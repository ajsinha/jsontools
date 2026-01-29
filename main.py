#!/usr/bin/env python3
"""
JsonSchemaCodeGen - Main Demonstration Script

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

This script demonstrates all the key features of JsonSchemaCodeGen.
"""

import json
import os
import sys
from pathlib import Path

# Add package to path for direct execution
sys.path.insert(0, str(Path(__file__).parent))

from jsonschemacodegen import (
    SchemaProcessor,
    generate_code,
    generate_samples,
    generate_module,
    __version__,
)
from jsonschemacodegen.utils import load_schema


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_subheader(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---\n")


def demo_basic_usage():
    """Demonstrate basic schema processing."""
    print_header("BASIC USAGE DEMONSTRATION")
    
    # Simple schema
    schema = {
        "type": "object",
        "title": "Person",
        "description": "A simple person record",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "name": {"type": "string", "minLength": 1, "maxLength": 100},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "isActive": {"type": "boolean", "default": True}
        },
        "required": ["id", "name", "email"]
    }
    
    print_subheader("Input Schema")
    print(json.dumps(schema, indent=2))
    
    # Create processor
    processor = SchemaProcessor(schema, root_class_name="Person")
    
    # Parse schema
    print_subheader("Parsed Schema Info")
    info = processor.parse()
    print(f"Title: {info.title}")
    print(f"Description: {info.description}")
    print(f"Properties: {len(info.properties)}")
    for name, prop in info.properties.items():
        req = " (required)" if prop.required else ""
        print(f"  - {name}: {[t.value for t in prop.types]}{req}")
    
    # Generate code
    print_subheader("Generated Python Dataclass")
    code = processor.generate_code()
    print(code)
    
    # Generate samples
    print_subheader("Generated Sample Data")
    samples = processor.generate_samples(count=3)
    for i, sample in enumerate(samples, 1):
        print(f"Sample {i}:")
        print(json.dumps(sample, indent=2, default=str))
        print()


def demo_complex_schema():
    """Demonstrate complex schema with nested objects."""
    print_header("COMPLEX SCHEMA DEMONSTRATION")
    
    schema = {
        "type": "object",
        "title": "Order",
        "definitions": {
            "Address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "zipCode": {"type": "string"},
                    "country": {"type": "string", "default": "US"}
                },
                "required": ["street", "city", "zipCode"]
            },
            "LineItem": {
                "type": "object",
                "properties": {
                    "productId": {"type": "string"},
                    "name": {"type": "string"},
                    "quantity": {"type": "integer", "minimum": 1},
                    "unitPrice": {"type": "number", "minimum": 0}
                },
                "required": ["productId", "name", "quantity", "unitPrice"]
            }
        },
        "properties": {
            "orderId": {"type": "string", "format": "uuid"},
            "customer": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"}
                },
                "required": ["id", "name", "email"]
            },
            "shippingAddress": {"$ref": "#/definitions/Address"},
            "billingAddress": {"$ref": "#/definitions/Address"},
            "items": {
                "type": "array",
                "items": {"$ref": "#/definitions/LineItem"},
                "minItems": 1
            },
            "totalAmount": {"type": "number", "minimum": 0},
            "status": {"type": "string", "enum": ["pending", "processing", "shipped", "delivered"]}
        },
        "required": ["orderId", "customer", "items", "totalAmount", "status"]
    }
    
    print_subheader("Complex Schema with $ref")
    print(json.dumps(schema, indent=2)[:500] + "...")
    
    processor = SchemaProcessor(schema, root_class_name="Order")
    
    print_subheader("Generated Code (truncated)")
    code = processor.generate_code()
    print(code[:1500] + "...")
    
    print_subheader("Generated Sample Order")
    sample = processor.generate_samples(count=1)[0]
    print(json.dumps(sample, indent=2, default=str))


def demo_validation():
    """Demonstrate validation capabilities."""
    print_header("VALIDATION DEMONSTRATION")
    
    schema = {
        "type": "object",
        "title": "User",
        "properties": {
            "username": {"type": "string", "minLength": 3, "maxLength": 20, "pattern": "^[a-z0-9_]+$"},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 18, "maximum": 120}
        },
        "required": ["username", "email"]
    }
    
    processor = SchemaProcessor(schema)
    
    # Valid data
    print_subheader("Validating Valid Data")
    valid_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "age": 30
    }
    print(f"Data: {json.dumps(valid_data)}")
    result = processor.validate_data(valid_data)
    print(f"Valid: {result.is_valid}")
    
    # Invalid data
    print_subheader("Validating Invalid Data")
    invalid_data = {
        "username": "JD",  # Too short, has uppercase
        "email": "not-an-email",
        "age": 15  # Below minimum
    }
    print(f"Data: {json.dumps(invalid_data)}")
    result = processor.validate_data(invalid_data)
    print(f"Valid: {result.is_valid}")
    if not result.is_valid:
        print("Issues:")
        for issue in result.issues:
            print(f"  - {issue.path}: {issue.message}")


def demo_file_schemas():
    """Demonstrate loading and processing file-based schemas."""
    print_header("FILE-BASED SCHEMA DEMONSTRATION")
    
    # Check if examples exist
    examples_dir = Path(__file__).parent / "examples" / "schemas"
    
    if not examples_dir.exists():
        print(f"Examples directory not found: {examples_dir}")
        return
    
    schema_files = list(examples_dir.glob("*.json"))[:3]
    
    if not schema_files:
        print("No schema files found in examples directory")
        return
    
    for schema_file in schema_files:
        print_subheader(f"Processing: {schema_file.name}")
        
        try:
            schema = load_schema(str(schema_file))
            title = schema.get("title", schema_file.stem)
            
            processor = SchemaProcessor(schema, root_class_name=title)
            
            # Generate code
            code = processor.generate_code()
            print(f"Generated class: {title}")
            print(f"Code length: {len(code)} characters")
            
            # Generate sample
            sample = processor.generate_samples(count=1)[0]
            print(f"Sample keys: {list(sample.keys())[:5]}...")
            
        except Exception as e:
            print(f"Error: {e}")


def demo_module_generation():
    """Demonstrate module generation from schema folder."""
    print_header("MODULE GENERATION DEMONSTRATION")
    
    # Check if examples exist
    examples_dir = Path(__file__).parent / "examples" / "schemas"
    output_dir = Path(__file__).parent / "demo_output"
    
    if not examples_dir.exists():
        print(f"Examples directory not found: {examples_dir}")
        return
    
    print_subheader("Generating Module from Schema Folder")
    print(f"Schema directory: {examples_dir}")
    print(f"Output directory: {output_dir}")
    
    try:
        result = generate_module(
            schema_dir=str(examples_dir),
            output_dir=str(output_dir),
            module_name="demo_models",
            overwrite=True,
        )
        
        print(f"\nSchemas processed: {result['schemas_processed']}")
        print(f"Classes generated: {len(result['classes_generated'])}")
        
        print("\nGenerated classes:")
        for class_name in sorted(result['classes_generated'])[:10]:
            print(f"  - {class_name}")
        if len(result['classes_generated']) > 10:
            print(f"  ... and {len(result['classes_generated']) - 10} more")
        
        if result['errors']:
            print("\nErrors:")
            for error in result['errors']:
                print(f"  - {error}")
        
        print(f"\nOutput directory created at: {output_dir}")
        print("\nTo use the generated module:")
        print(f"  from demo_models import User, load_json, to_json")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all demonstrations."""
    print("=" * 70)
    print("  JsonSchemaCodeGen v{} - Demonstration".format(__version__))
    print("=" * 70)
    print("\nCopyright © 2025-2030, Ashutosh Sinha. All Rights Reserved.")
    print("This software is proprietary and confidential.\n")
    
    demos = [
        ("Basic Usage", demo_basic_usage),
        ("Complex Schema", demo_complex_schema),
        ("Validation", demo_validation),
        ("File-Based Schemas", demo_file_schemas),
        ("Module Generation", demo_module_generation),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\nError during {name} demonstration: {e}")
            import traceback
            traceback.print_exc()
    
    print_header("DEMONSTRATION COMPLETE")
    print("Thank you for using JsonSchemaCodeGen!")
    print("\nFor more information, see:")
    print("  - README.md")
    print("  - docs/QUICKSTART.md")
    print("  - docs/ARCHITECTURE.md")
    print("  - docs/MODULE_GENERATOR.md")
    print("  - docs/EXAMPLES.md")


if __name__ == "__main__":
    main()
