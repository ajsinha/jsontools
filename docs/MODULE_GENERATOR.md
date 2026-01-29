# Module Generator Guide

## Copyright and Legal Notice

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

This document and the associated software architecture are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this document or the software system it describes is strictly prohibited without explicit written permission from the copyright holder.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Command Line Usage](#command-line-usage)
4. [Programmatic Usage](#programmatic-usage)
5. [Generated Module Structure](#generated-module-structure)
6. [Driver Functions](#driver-functions)
7. [Working with Generated Models](#working-with-generated-models)
8. [Advanced Configuration](#advanced-configuration)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The **Module Generator** is a powerful feature of JsonSchemaCodeGen that creates a complete, ready-to-use Python module from a folder of JSON Schema files. 

### What It Creates

```
output_module/
├── __init__.py          # Main module with all exports
├── driver.py            # JSON loading/saving utilities
└── generated/
    ├── __init__.py      # Generated classes exports
    ├── user.py          # User dataclass
    ├── product.py       # Product dataclass
    ├── order.py         # Order dataclass
    └── ...              # One file per schema
```

### Key Benefits

- **Consistent Code**: All schemas processed with identical settings
- **Ready to Use**: Generated module can be imported immediately
- **Driver Utilities**: Built-in functions for JSON parsing and serialization
- **Class Registry**: Dynamic lookup of classes by name
- **Type Safe**: Full type hints throughout

---

## Quick Start

### From Command Line

```bash
# Generate module from schema folder
python -m jsonschemacodegen generate-module \
    --schema-dir schemas/ \
    --output-dir myapp/models/
```

### From Python

```python
from jsonschemacodegen import generate_module

result = generate_module(
    schema_dir="schemas/",
    output_dir="myapp/models/"
)

print(f"Generated {len(result['classes_generated'])} classes")
```

### Using the Generated Module

```python
# Import models
from myapp.models import User, Product, Order

# Import utilities
from myapp.models import load_json, to_json, list_classes

# Create an instance
user = User(
    id="123",
    name="John Doe",
    email="john@example.com"
)

# Serialize to JSON file
to_json(user, "output/user.json")

# Load from JSON file
loaded_user = load_json("output/user.json", User)
```

---

## Command Line Usage

### Basic Command

```bash
python -m jsonschemacodegen generate-module \
    --schema-dir <path-to-schemas> \
    --output-dir <path-to-output>
```

### Options

| Option | Required | Description |
|--------|----------|-------------|
| `--schema-dir` | Yes | Path to directory containing JSON Schema files |
| `--output-dir` | Yes | Path where the Python module will be created |
| `--module-name` | No | Custom name for the module (default: output dir name) |
| `--overwrite` | No | Overwrite existing files (default: True) |

### Examples

```bash
# Basic usage
python -m jsonschemacodegen generate-module \
    --schema-dir ./schemas \
    --output-dir ./myapp/models

# With custom module name
python -m jsonschemacodegen generate-module \
    --schema-dir ./api/schemas \
    --output-dir ./src/models \
    --module-name data_models

# Process all schemas including subdirectories
python -m jsonschemacodegen generate-module \
    --schema-dir ./schemas \
    --output-dir ./generated
```

### Output

```
✓ Module generation complete!
  Schemas processed: 22
  Classes generated: 22
  Files created: 47

  Generated classes:
    - ApiGateway
    - ApiResponse
    - BlogPost
    - Config
    - Event
    - FinancialTransaction
    - GameEntity
    - ...

  Output directory: myapp/models/
```

---

## Programmatic Usage

### Basic Usage

```python
from jsonschemacodegen import generate_module

result = generate_module(
    schema_dir="schemas/",
    output_dir="myapp/models/"
)
```

### Using ModuleGenerator Class

```python
from jsonschemacodegen import ModuleGenerator

generator = ModuleGenerator(
    schema_dir="schemas/",
    output_dir="myapp/models/",
    module_name="models",
    overwrite=True,
    include_samples=True,
)

result = generator.generate()

# Check results
print(f"Processed: {result['schemas_processed']}")
print(f"Classes: {result['classes_generated']}")
print(f"Errors: {result['errors']}")
```

### Result Dictionary

The `generate()` method returns a dictionary with:

| Key | Type | Description |
|-----|------|-------------|
| `schemas_processed` | int | Number of schemas successfully processed |
| `classes_generated` | List[str] | Names of generated classes |
| `files_created` | List[str] | Paths of all created files |
| `errors` | List[str] | Any errors encountered |

---

## Generated Module Structure

### Directory Layout

```
output_module/
├── __init__.py              # Main module entry point
│   - Imports all generated classes
│   - Imports driver functions
│   - Exports everything via __all__
│
├── driver.py                # Utility functions
│   - load_json()            Load JSON file to dataclass
│   - load_json_string()     Load JSON string to dataclass
│   - load_dict()            Load dictionary to dataclass
│   - to_json()              Save dataclass to JSON file
│   - to_json_string()       Serialize to JSON string
│   - to_dict()              Convert to dictionary
│   - list_classes()         List all available classes
│   - get_class_info()       Get class metadata
│
└── generated/               # Generated dataclasses
    ├── __init__.py          # Exports all classes
    │   - CLASS_REGISTRY     Dictionary of class_name -> class
    │   - get_class()        Get class by name
    │
    ├── user.py              # Individual dataclass files
    ├── product.py
    ├── order.py
    └── ...
```

### Import Examples

```python
# Import specific classes
from myapp.models import User, Product, Order

# Import all classes
from myapp.models import *

# Import driver functions
from myapp.models import load_json, to_json, list_classes

# Import from generated submodule directly
from myapp.models.generated import User
from myapp.models.generated import CLASS_REGISTRY, get_class
```

---

## Driver Functions

### Loading JSON Data

#### load_json(file_path, target_class)

Load a JSON file into a dataclass instance.

```python
from myapp.models import load_json, User

user = load_json("data/user.json", User)
print(user.name)  # Access fields
```

#### load_json_string(json_str, target_class)

Parse a JSON string into a dataclass instance.

```python
from myapp.models import load_json_string, User

json_data = '{"id": "123", "name": "John", "email": "john@example.com"}'
user = load_json_string(json_data, User)
```

#### load_dict(data, target_class)

Convert a dictionary to a dataclass instance.

```python
from myapp.models import load_dict, User

data = {"id": "123", "name": "John", "email": "john@example.com"}
user = load_dict(data, User)
```

#### load_by_class_name(data, class_name)

Load data using class name as string (useful for dynamic loading).

```python
from myapp.models import load_by_class_name

# From file path
user = load_by_class_name("data/user.json", "User")

# From JSON string
user = load_by_class_name('{"name": "John"}', "User")

# From dictionary
user = load_by_class_name({"name": "John"}, "User")
```

### Serializing to JSON

#### to_json(obj, file_path, indent=2)

Save a dataclass instance to a JSON file.

```python
from myapp.models import to_json, User

user = User(id="123", name="John", email="john@example.com")
to_json(user, "output/user.json")
```

#### to_json_string(obj, indent=2)

Serialize a dataclass instance to a JSON string.

```python
from myapp.models import to_json_string, User

user = User(id="123", name="John", email="john@example.com")
json_str = to_json_string(user)
print(json_str)
```

#### to_dict(obj)

Convert a dataclass instance to a dictionary.

```python
from myapp.models import to_dict, User

user = User(id="123", name="John", email="john@example.com")
data = to_dict(user)
print(data)  # {'id': '123', 'name': 'John', 'email': 'john@example.com'}
```

### Utility Functions

#### list_classes()

Get a list of all available class names.

```python
from myapp.models import list_classes

classes = list_classes()
print(classes)  # ['User', 'Product', 'Order', ...]
```

#### get_class(name)

Get a class by its name (for dynamic instantiation).

```python
from myapp.models import get_class

UserClass = get_class("User")
user = UserClass(id="123", name="John", email="john@example.com")
```

#### get_class_info(class_name)

Get metadata about a class.

```python
from myapp.models import get_class_info

info = get_class_info("User")
print(info)
# {
#     'name': 'User',
#     'fields': [
#         {'name': 'id', 'type': 'str'},
#         {'name': 'name', 'type': 'str'},
#         {'name': 'email', 'type': 'str'},
#     ],
#     'docstring': 'User account information'
# }
```

---

## Working with Generated Models

### Creating Instances

```python
from myapp.models import User

# Direct instantiation
user = User(
    id="user-123",
    name="John Doe",
    email="john@example.com",
    age=30
)

# From dictionary
data = {"id": "user-123", "name": "John", "email": "john@example.com"}
user = User(**data)
```

### Accessing Fields

```python
# Access fields directly
print(user.name)
print(user.email)

# Iterate over fields
from dataclasses import fields

for field in fields(user):
    print(f"{field.name}: {getattr(user, field.name)}")
```

### Nested Objects

The driver functions handle nested dataclasses automatically:

```python
# Schema with nested objects
{
    "type": "object",
    "properties": {
        "user": {"$ref": "#/definitions/User"},
        "items": {"type": "array", "items": {"$ref": "#/definitions/Product"}}
    }
}

# Loading nested data
order_data = {
    "user": {"id": "1", "name": "John"},
    "items": [
        {"id": "p1", "name": "Widget", "price": 9.99},
        {"id": "p2", "name": "Gadget", "price": 19.99}
    ]
}

order = load_dict(order_data, Order)
print(order.user.name)       # "John"
print(order.items[0].name)   # "Widget"
```

### Round-Trip Conversion

```python
from myapp.models import User, load_json, to_json, to_json_string, load_json_string

# Create instance
user = User(id="123", name="John", email="john@example.com")

# Convert to JSON string
json_str = to_json_string(user)

# Parse back to instance
user2 = load_json_string(json_str, User)

# Verify they're equal
assert user.id == user2.id
assert user.name == user2.name
```

---

## Advanced Configuration

### Custom Module Name

```python
result = generate_module(
    schema_dir="schemas/",
    output_dir="myapp/data/",
    module_name="data_models"  # Custom name
)

# Usage:
# from myapp.data import User  # Works!
# from data_models import User  # Also works from the module directory
```

### Schema File Organization

The generator recursively processes all `.json` files:

```
schemas/
├── core/
│   ├── user.json
│   └── product.json
├── api/
│   ├── request.json
│   └── response.json
└── definitions/
    └── common.json
```

All schemas become classes in the same flat `generated/` directory.

### Handling Duplicate Class Names

If multiple schemas would generate the same class name, the generator automatically appends numbers:

- `user.json` → `User`
- `api/user.json` → `User2`

---

## Best Practices

### 1. Organize Schemas by Domain

```
schemas/
├── users/
├── products/
├── orders/
└── common/
    └── definitions.json
```

### 2. Use Meaningful Titles

```json
{
    "title": "CustomerOrder",
    "description": "Represents a customer's order"
}
```

The `title` field is used as the class name.

### 3. Define Common Types in Definitions

```json
{
    "definitions": {
        "Money": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "currency": {"type": "string"}
            }
        }
    }
}
```

### 4. Version Your Generated Code

Include generation in your build process:

```python
# scripts/generate_models.py
from jsonschemacodegen import generate_module

result = generate_module(
    schema_dir="api/schemas/",
    output_dir="src/models/"
)

with open("src/models/VERSION", "w") as f:
    f.write(f"Generated: {datetime.now().isoformat()}\n")
    f.write(f"Schemas: {result['schemas_processed']}\n")
```

### 5. Don't Edit Generated Files

Generated files include a warning:

```python
"""
DO NOT EDIT THIS FILE MANUALLY - Changes will be overwritten.
"""
```

If you need custom logic, create wrapper classes in a separate file.

---

## Troubleshooting

### Common Issues

#### "No schema files found"

```
Error: No schema files found in schemas/
```

**Solution**: Ensure the schema directory contains `.json` files:
```bash
ls schemas/*.json
```

#### "File not found" when loading JSON

```python
FileNotFoundError: File not found: user.json
```

**Solution**: Use absolute paths or check working directory:
```python
from pathlib import Path

file_path = Path(__file__).parent / "data" / "user.json"
user = load_json(file_path, User)
```

#### "Not a dataclass" error

```
TypeError: User is not a dataclass
```

**Solution**: Ensure you're importing from the generated module:
```python
# Wrong
from myapp.models.driver import User

# Correct
from myapp.models import User
```

#### Duplicate class names

If you see `User`, `User2`, `User3`:

**Solution**: Add unique `title` fields to your schemas:
```json
{
    "title": "CustomerUser",
    ...
}
```

### Getting Help

1. Check schema validation: `python -m jsonschemacodegen validate -s schema.json`
2. Review the generation output for errors
3. Ensure all `$ref` references are resolvable

---

## Summary

The Module Generator provides a complete solution for converting JSON Schema folders into usable Python modules:

1. **One Command**: Generate entire module from schema folder
2. **Ready to Use**: Import and use immediately
3. **Full Utilities**: Built-in JSON loading and serialization
4. **Type Safe**: Dataclasses with type hints
5. **Extensible**: Class registry for dynamic usage

```python
# Generate
from jsonschemacodegen import generate_module
generate_module("schemas/", "myapp/models/")

# Use
from myapp.models import User, load_json, to_json
user = load_json("user.json", User)
to_json(user, "output.json")
```

---

**Copyright © 2025-2030, Ashutosh Sinha. All Rights Reserved.**
