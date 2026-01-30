# JsonTools - Module Generator Guide

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

---

## Overview

The Module Generator creates complete, importable Python modules from folders of JSON Schema files.

---

## Usage

### Command Line

```bash
python -m jsontools generate-module \
    --schema-dir ./schemas \
    --output-dir ./output \
    --module-name mymodels
```

### Or use generate.py

```bash
python generate.py -s ./schemas -o ./output -m mymodels
```

### Python API

```python
from jsontools import generate_module

result = generate_module(
    schema_dir="schemas/",
    output_dir="output/",
    module_name="mymodels"
)

print(f"Generated {len(result['classes_generated'])} classes")
print(f"Module path: {result['module_path']}")
```

---

## Generated Structure

```
output/
+-- mymodels/              # Module folder (named by --module-name)
    +-- __init__.py        # Main exports
    +-- __main__.py        # CLI entry point
    +-- driver.py          # JSON utilities
    +-- main.py            # High-level functions
    +-- generated/         # Generated dataclasses
        +-- __init__.py    # Class registry
        +-- user.py        # User class
        +-- product.py     # Product class
        +-- ...            # Other classes
```

---

## Using Generated Modules

### Import Classes

```python
import sys
sys.path.insert(0, "./output")

from mymodels import User, Product, Order
from mymodels import load_json, to_json, list_classes, get_class
```

### Create and Populate Objects

```python
# Create with no arguments
user = User()

# Assign values
user.id_ = "user-123"
user.username = "johndoe"
user.email = "john@example.com"
user.role = "admin"
user.status = "active"

# Validate
result = user.validate()
if result.is_valid:
    print("User is valid")
else:
    print("Errors:", result.errors)
```

### Serialization

```python
# To JSON file
to_json(user, "user.json")

# To JSON string
from mymodels import to_json_string
json_str = to_json_string(user)

# From JSON file
loaded = load_json("user.json", "User")
```

### Class Discovery

```python
# List all classes
classes = list_classes()
print(classes)  # ['User', 'Product', 'Order', ...]

# Get class by name
UserClass = get_class("User")
user = UserClass()
```

---

## Generated Module CLI

```bash
# List available classes
python -m mymodels list

# Show class information
python -m mymodels info User

# Generate sample data
python -m mymodels sample User
python -m mymodels sample User -o sample.json
python -m mymodels sample User -c 5  # 5 samples

# Validate JSON file
python -m mymodels validate user.json User
```

---

## Validation Features

### Required Fields

```python
user = User()  # Empty instance
result = user.validate()
# result.is_valid = False
# result.errors = ["Required field 'id_' is not set", ...]
```

### Enum Validation

```python
user.role = "superadmin"  # Invalid enum value
result = user.validate()
# result.errors = ["Field 'role' has invalid value 'superadmin'. Must be one of: ['admin', 'user', 'guest']"]
```

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| --schema-dir, -s | Schema directory | Required |
| --output-dir, -o | Output directory | Required |
| --module-name, -m | Module name | mymodule |
| --overwrite | Overwrite existing | True |

---

Copyright (C) 2025-2030, Ashutosh Sinha. All Rights Reserved.
