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

### Step 1: Import

```python
from jsonschemacodegen import SchemaProcessor
```

### Step 2: Define Schema

```python
schema = {
    "type": "object",
    "title": "User",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["id", "name", "email"]
}
```

### Step 3: Create Processor

```python
processor = SchemaProcessor(schema, root_class_name="User")
```

### Step 4: Generate What You Need

```python
# Generate Python dataclass code
code = processor.generate_code()
print(code)

# Generate sample data
samples = processor.generate_samples(count=3)
for sample in samples:
    print(sample)

# Validate data
data = {"id": "123e4567-e89b-12d3-a456-426614174000", "name": "John", "email": "john@example.com"}
result = processor.validate_data(data)
print(f"Valid: {result.is_valid}")
```

---

## Generate Module from Schema Folder

```python
from jsonschemacodegen import generate_module

# Generate complete Python module
result = generate_module(
    schema_dir="schemas/",
    output_dir="myapp/models/"
)

print(f"Generated {len(result['classes_generated'])} classes")
```

Then use the generated module:

```python
from myapp.models import User, Product, load_json, to_json

# Load from JSON file
user = load_json("user.json", User)

# Serialize to JSON
user = User(id="123", name="John", email="john@example.com")
to_json(user, "output/user.json")
```

---

## CLI Usage

```bash
# Generate code from schema
python -m jsonschemacodegen generate -s schema.json -o models.py

# Generate module from folder
python -m jsonschemacodegen generate-module --schema-dir schemas/ --output-dir models/

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
