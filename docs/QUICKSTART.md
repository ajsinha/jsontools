# JsonTools - Quick Start Guide

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

---

## Installation

```bash
cd jsontools
pip install .
```

---

## Option 1: Generate Module from Schema Folder (Recommended)

### Step 1: Generate the Module

```bash
python -m jsontools generate-module \
    --schema-dir ./schemas \
    --output-dir ./output \
    --module-name mymodels
```

### Step 2: Use the Generated Module

```python
import sys
sys.path.insert(0, "./output")

from mymodels import User, Product, load_json, to_json

# Create instance with no arguments
user = User()

# Assign values
user.id_ = "user-123"
user.username = "johndoe"
user.email = "john@example.com"

# Validate
result = user.validate()
if result.is_valid:
    print("Valid!")
else:
    print("Errors:", result.errors)

# Serialize
to_json(user, "user.json")
```

### Generated Module Structure

```
output/
+-- mymodels/
    +-- __init__.py      # Main exports
    +-- __main__.py      # CLI entry point
    +-- driver.py        # JSON utilities
    +-- main.py          # High-level functions
    +-- generated/
        +-- __init__.py
        +-- *.py         # Generated classes
```

---

## Option 2: Single Schema Processing

```python
from jsontools import SchemaProcessor

schema = {
    "type": "object",
    "title": "User",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "email"]
}

processor = SchemaProcessor(schema)

# Generate code
code = processor.generate_code()
print(code)

# Generate samples
samples = processor.generate_samples(count=3)
```

---

## Command Line Interface

```bash
# Generate module
python -m jsontools generate-module -s schemas/ -o output/ -m mymodels

# Generate code
python -m jsontools generate -s schema.json -o output.py

# Generate samples
python -m jsontools sample -s schema.json -c 5

# Validate
python -m jsontools validate -s schema.json -d data.json
```

---

## Generated Module CLI

```bash
python -m mymodels list              # List classes
python -m mymodels info User         # Show class info
python -m mymodels sample User       # Generate sample
python -m mymodels validate data.json User  # Validate
```

---

Copyright (C) 2025-2030, Ashutosh Sinha. All Rights Reserved.
