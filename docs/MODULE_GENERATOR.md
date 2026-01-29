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
3. [Generated Module Structure](#generated-module-structure)
4. [Command Line Usage](#command-line-usage)
5. [Programmatic Usage](#programmatic-usage)
6. [Using the Generated Module](#using-the-generated-module)
7. [Driver Functions](#driver-functions)
8. [Main Module Functions](#main-module-functions)
9. [CLI in Generated Module](#cli-in-generated-module)
10. [Best Practices](#best-practices)

---

## Overview

The **Module Generator** creates a complete, ready-to-use Python module from a folder of JSON Schema files.

### What It Creates

```
output_dir/
└── module_name/              # Default: "mymodule"
    ├── __init__.py           # Main module with all exports
    ├── __main__.py           # Enables python -m module_name
    ├── driver.py             # JSON loading/saving utilities
    ├── main.py               # High-level utility functions + CLI
    └── generated/
        ├── __init__.py       # Generated classes exports
        ├── user.py           # User dataclass
        ├── product.py        # Product dataclass
        └── ...               # One file per schema
```

### Key Features

- **Named Module**: Creates a properly named Python module inside the output directory
- **Ready to Use**: Import and use immediately after generation
- **Driver Utilities**: Built-in functions for JSON parsing and serialization
- **Main Functions**: High-level functions for common operations
- **CLI Support**: Run `python -m module_name` for command-line operations
- **Class Registry**: Dynamic lookup of classes by name

---

## Quick Start

### From Command Line

```bash
# Generate module with default name (mymodule)
python -m jsonschemacodegen generate-module \
    --schema-dir schemas/ \
    --output-dir output/

# Generate module with custom name
python -m jsonschemacodegen generate-module \
    --schema-dir schemas/ \
    --output-dir output/ \
    --module-name mymodels
```

### From Python

```python
from jsonschemacodegen import generate_module

# With default module name (mymodule)
result = generate_module(
    schema_dir="schemas/",
    output_dir="output/"
)

# With custom module name
result = generate_module(
    schema_dir="schemas/",
    output_dir="output/",
    module_name="mymodels"
)

print(f"Module created at: {result['module_path']}")
print(f"Generated {len(result['classes_generated'])} classes")
```

### Using the Generated Module

```python
# Add output directory to path if needed
import sys
sys.path.insert(0, "output")

# Import from generated module
from mymodels import User, Product, Order

# Import utilities
from mymodels import load_json, to_json, list_classes

# Create an instance
user = User(
    id_="123",
    name="John Doe",
    email="john@example.com"
)

# Serialize to JSON file
to_json(user, "output/user.json")

# Load from JSON file
loaded_user = load_json("output/user.json", "User")
```

---

## Generated Module Structure

### Directory Layout

```
output_dir/
└── module_name/                    # e.g., "mymodule" or custom name
    │
    ├── __init__.py                 # Main module entry point
    │   - Imports all generated classes
    │   - Imports driver functions
    │   - Imports main functions
    │   - Exports everything via __all__
    │
    ├── __main__.py                 # Module entry point
    │   - Enables: python -m module_name
    │
    ├── driver.py                   # Low-level utility functions
    │   - load_json()               Load by class name
    │   - load_json_file()          Load with class type
    │   - load_json_string()        Parse JSON string
    │   - load_dict()               Load from dictionary
    │   - to_json()                 Save to file
    │   - to_json_file()            Save to file (alias)
    │   - to_json_string()          Serialize to string
    │   - to_dict()                 Convert to dictionary
    │   - list_classes()            List all classes
    │   - get_class_info()          Get class metadata
    │   - create_instance()         Create by class name
    │   - validate_data()           Validate against class
    │
    ├── main.py                     # High-level functions + CLI
    │   - load_and_parse()          Load and parse JSON
    │   - create_and_save()         Create and save to JSON
    │   - generate_sample()         Generate sample data
    │   - convert_json()            Load, parse, and save
    │   - run_cli()                 Command-line interface
    │
    └── generated/                  # Generated dataclasses
        ├── __init__.py             # Exports all classes
        │   - CLASS_REGISTRY        Dictionary of classes
        │   - get_class()           Get class by name
        │
        ├── user.py                 # Individual dataclass files
        ├── product.py
        ├── order.py
        └── ...
```

---

## Command Line Usage

### Basic Usage

```bash
# Default module name (mymodule)
python -m jsonschemacodegen generate-module \
    --schema-dir <path-to-schemas> \
    --output-dir <output-directory>

# Custom module name
python -m jsonschemacodegen generate-module \
    --schema-dir <path-to-schemas> \
    --output-dir <output-directory> \
    --module-name <module-name>
```

### Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--schema-dir` | Yes | - | Path to directory containing JSON Schema files |
| `--output-dir` | Yes | - | Path where the module folder will be created |
| `--module-name` | No | mymodule | Name for the generated module |
| `--overwrite` | No | True | Overwrite existing files |

### Examples

```bash
# Generate with default name
python -m jsonschemacodegen generate-module \
    --schema-dir ./schemas \
    --output-dir ./output
# Creates: ./output/mymodule/

# Generate with custom name
python -m jsonschemacodegen generate-module \
    --schema-dir ./api/schemas \
    --output-dir ./src \
    --module-name data_models
# Creates: ./src/data_models/
```

### Output

```
✓ Module generation complete!
  Module name: mymodels
  Module path: /path/to/output/mymodels
  Schemas processed: 22
  Classes generated: 22
  Files created: 47

  Generated classes:
    - ApiGateway
    - ApiResponse
    - BlogPost
    - Config
    - Event
    ...

  Usage:
    from mymodels import User, load_json, to_json
    python -m mymodels --help
```

---

## Programmatic Usage

### Basic Usage

```python
from jsonschemacodegen import generate_module

result = generate_module(
    schema_dir="schemas/",
    output_dir="output/",
    module_name="mymodels"  # Optional, defaults to "mymodule"
)
```

### Using ModuleGenerator Class

```python
from jsonschemacodegen import ModuleGenerator

generator = ModuleGenerator(
    schema_dir="schemas/",
    output_dir="output/",
    module_name="mymodels",
    overwrite=True,
)

result = generator.generate()

# Check results
print(f"Module: {result['module_name']}")
print(f"Path: {result['module_path']}")
print(f"Classes: {result['classes_generated']}")
print(f"Errors: {result['errors']}")
```

### Result Dictionary

| Key | Type | Description |
|-----|------|-------------|
| `schemas_processed` | int | Number of schemas successfully processed |
| `classes_generated` | List[str] | Names of generated classes |
| `files_created` | List[str] | Paths of all created files |
| `errors` | List[str] | Any errors encountered |
| `module_path` | str | Full path to generated module |
| `module_name` | str | Name of the generated module |

---

## Using the Generated Module

### Importing

```python
# Import specific classes
from mymodule import User, Product, Order

# Import all classes
from mymodule import *

# Import utilities
from mymodule import load_json, to_json, list_classes

# Import high-level functions
from mymodule import load_and_parse, create_and_save, generate_sample
```

### Creating Instances

```python
from mymodule import User, create_instance

# Direct instantiation
user = User(
    id_="user-123",
    name="John Doe",
    email="john@example.com"
)

# Create by class name
user = create_instance("User", 
    id_="user-123",
    name="John Doe",
    email="john@example.com"
)
```

### Loading from JSON

```python
from mymodule import load_json, load_and_parse

# Load by class name
user = load_json("user.json", "User")

# Load with verbose output
user = load_and_parse("user.json", "User", verbose=True)
```

### Saving to JSON

```python
from mymodule import to_json, create_and_save

# Save instance to file
to_json(user, "output/user.json")

# Create and save in one call
user = create_and_save(
    "User",
    "output/user.json",
    id_="123",
    name="John",
    email="john@example.com"
)
```

### Generating Sample Data

```python
from mymodule import generate_sample

# Generate random sample
sample_user = generate_sample("User")
print(sample_user.name)  # Random name

# With seed for reproducibility
sample = generate_sample("User", seed=42)
```

---

## Driver Functions

### load_json(file_path, class_name)

Load a JSON file into a class instance by class name.

```python
user = load_json("data/user.json", "User")
```

### load_json_file(file_path, target_class)

Load a JSON file into a class instance by class type.

```python
from mymodule import User, load_json_file
user = load_json_file("data/user.json", User)
```

### to_json(obj, file_path)

Save a class instance to a JSON file.

```python
to_json(user, "output/user.json")
```

### to_json_string(obj)

Serialize a class instance to a JSON string.

```python
json_str = to_json_string(user)
print(json_str)
```

### list_classes()

Get a list of all available class names.

```python
classes = list_classes()
print(classes)  # ['User', 'Product', 'Order', ...]
```

### get_class_info(class_name)

Get metadata about a class.

```python
info = get_class_info("User")
print(info['fields'])  # Field information
```

### validate_data(data, class_name)

Validate a dictionary against a class structure.

```python
result = validate_data({"name": "John"}, "User")
if result["valid"]:
    print("Valid!")
else:
    print("Errors:", result["errors"])
```

---

## Main Module Functions

### load_and_parse(file_path, class_name, verbose=False)

Load and parse a JSON file with optional verbose output.

```python
user = load_and_parse("user.json", "User", verbose=True)
# Output: Loading user.json as User...
#         Successfully loaded User instance
```

### create_and_save(class_name, output_path, **kwargs)

Create a class instance and save it to JSON in one call.

```python
user = create_and_save(
    "User",
    "output/user.json",
    verbose=True,
    id_="123",
    name="John",
    email="john@example.com"
)
```

### generate_sample(class_name, seed=None)

Generate a sample instance with random data.

```python
sample = generate_sample("User")
print(sample.name)  # Random name like "Alice"
print(sample.email)  # Random email like "user123@example.com"
```

### convert_json(input_path, output_path, class_name)

Load JSON, parse through class, and save (validates and normalizes).

```python
user = convert_json("input.json", "output.json", "User")
```

---

## CLI in Generated Module

The generated module includes a command-line interface:

```bash
# Show help
python -m mymodule --help

# List available classes
python -m mymodule list

# Show class information
python -m mymodule info User

# Load and display JSON
python -m mymodule load user.json User

# Generate sample data
python -m mymodule sample User
python -m mymodule sample User -o sample_user.json
python -m mymodule sample User -n 5 -o samples.json

# Validate JSON against class
python -m mymodule validate user.json User
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `list` | List all available classes |
| `info <class>` | Show information about a class |
| `load <file> <class>` | Load and display JSON file |
| `sample <class>` | Generate sample data |
| `validate <file> <class>` | Validate JSON against class |

---

## Best Practices

### 1. Use Meaningful Module Names

```bash
# Good
python -m jsonschemacodegen generate-module \
    --schema-dir api/schemas \
    --output-dir src \
    --module-name api_models

# Avoid
python -m jsonschemacodegen generate-module \
    --schema-dir schemas \
    --output-dir output
    # Creates "mymodule" - less descriptive
```

### 2. Organize Output by Project

```
project/
├── src/
│   ├── api_models/          # Generated from API schemas
│   ├── db_models/           # Generated from DB schemas
│   └── app/
│       └── ...
└── schemas/
    ├── api/
    └── database/
```

### 3. Add Output Directory to Python Path

```python
import sys
sys.path.insert(0, "output")

from mymodels import User
```

Or use package installation:

```bash
cd output/mymodels
pip install -e .
```

### 4. Use Schema Titles

```json
{
    "title": "CustomerOrder",
    "type": "object"
}
```

The `title` field becomes the class name.

### 5. Don't Edit Generated Files

Generated files include a warning:
```python
# DO NOT EDIT - Changes will be overwritten.
```

Create wrapper classes in separate files if needed.

---

## Summary

The Module Generator provides:

1. **Complete Module**: Named Python module with all necessary files
2. **Ready to Use**: Import classes and utilities immediately
3. **Driver Functions**: Low-level JSON operations
4. **Main Functions**: High-level utilities for common tasks
5. **CLI Support**: Command-line interface in the generated module
6. **Type Safe**: Full type hints and dataclass support

```bash
# Generate
python -m jsonschemacodegen generate-module \
    --schema-dir schemas/ \
    --output-dir output/ \
    --module-name mymodels

# Use in Python
from mymodels import User, load_json, to_json, generate_sample
user = load_json("user.json", "User")
sample = generate_sample("User")

# Use CLI
python -m mymodels list
python -m mymodels sample User -o sample.json
```

---

**Copyright © 2025-2030, Ashutosh Sinha. All Rights Reserved.**
