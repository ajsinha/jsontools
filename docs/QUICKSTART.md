# JsonSchemaCodeGen Quick Start Guide

## Copyright and Legal Notice

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Installation

```bash
# Basic installation
pip install .

# With all optional features
pip install .[all]
```

---

## 5-Minute Quick Start

### Option 1: Single Schema Processing

```python
from jsonschemacodegen import SchemaProcessor

schema = {
    "type": "object",
    "title": "User",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"},
    },
    "required": ["id", "name", "email"]
}

processor = SchemaProcessor(schema, root_class_name="User")

# Generate Python dataclass code
code = processor.generate_code()
print(code)

# Generate sample data
samples = processor.generate_samples(count=3)
for sample in samples:
    print(sample)
```

### Option 2: Generate Module from Schema Folder (Recommended)

```bash
# Command line
python -m jsonschemacodegen generate-module \
    --schema-dir schemas/ \
    --output-dir output/ \
    --module-name mymodels
```

```python
# Or in Python
from jsonschemacodegen import generate_module

result = generate_module(
    schema_dir="schemas/",
    output_dir="output/",
    module_name="mymodels"
)
print(f"Created module at: {result['module_path']}")
```

Then use the generated module:

```python
import sys
sys.path.insert(0, "output")

from mymodels import User, Product, load_json, to_json, generate_sample

# Load from JSON file
user = load_json("user.json", "User")

# Generate sample data
sample = generate_sample("User")
print(sample.name)

# Create and save
user = User(id_="123", name="John", email="john@example.com")
to_json(user, "output/user.json")
```

---

## Generated Module Structure

```
output/
└── mymodels/
    ├── __init__.py      # Main exports
    ├── __main__.py      # CLI entry point
    ├── driver.py        # JSON utilities
    ├── main.py          # High-level functions
    └── generated/
        ├── __init__.py
        └── *.py         # Generated classes
```

---

## Using the Generated Module CLI

```bash
# List available classes
python -m mymodels list

# Show class info
python -m mymodels info User

# Generate sample data
python -m mymodels sample User -o sample.json

# Load and display JSON
python -m mymodels load user.json User

# Validate JSON
python -m mymodels validate user.json User
```

---

## CLI Commands

```bash
# Generate code from single schema
python -m jsonschemacodegen generate -s schema.json -o models.py

# Generate module from folder
python -m jsonschemacodegen generate-module \
    --schema-dir schemas/ \
    --output-dir output/ \
    --module-name mymodels

# Generate sample data
python -m jsonschemacodegen sample -s schema.json -c 10 -o samples.json

# Validate
python -m jsonschemacodegen validate -s schema.json -d data.json
```

---

## Next Steps

- See [MODULE_GENERATOR.md](MODULE_GENERATOR.md) for module generation details
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [EXAMPLES.md](EXAMPLES.md) for example schemas

---

**Copyright © 2025-2030, Ashutosh Sinha. All Rights Reserved.**
