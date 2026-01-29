# JsonSchemaCodeGen v1.0.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        JsonSchemaCodeGen v1.0.0                              ║
║                                                                              ║
║            Commercial Grade JSON Schema to Python Code Generator             ║
║                                                                              ║
║                  Copyright © 2025-2030, All Rights Reserved                  ║
║                      Ashutosh Sinha (ajsinha@gmail.com)                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Copyright and Legal Notice

**Copyright © 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

This software is proprietary and confidential. Unauthorized copying, distribution, modification, or use is strictly prohibited without explicit written permission from the copyright holder.

**Patent Pending:** Certain architectural patterns and implementations may be subject to patent applications.

---

## Overview

**JsonSchemaCodeGen** is a comprehensive, commercial-grade Python library for working with JSON Schema. It provides powerful, production-ready tools for:

- 🔧 **Schema Parsing**: Parse and analyze JSON Schema documents with full Draft-07 support
- 💻 **Code Generation**: Generate Python dataclasses from JSON Schema
- 📊 **Sample Data Generation**: Create realistic test data with Faker integration
- ✅ **Validation**: Validate schemas and data with detailed error reporting
- 🔗 **Reference Resolution**: Handle complex `$ref` references including remote schemas
- 📦 **Module Generation**: Generate complete Python modules from schema folders

---

## Key Features

### Code Generation

Generate Python dataclasses with full type hints, serialization methods, and validation.

### Module Generation

Generate complete Python modules from a folder of JSON schemas with:
- Driver code for JSON loading/saving
- Class registry for dynamic instantiation
- Proper `__init__.py` files

### Sample Data Generation

- 🎭 **Faker Integration**: Realistic names, emails, addresses, etc.
- 📏 **Constraint-Aware**: Respects min/max, patterns, formats
- 🎯 **Format-Specific**: Proper UUID, email, datetime generation

### Validation

- 📋 Schema structure validation
- 📊 Data validation against schema
- 📍 Detailed error paths

---

## Installation

### From Source

```bash
cd jsonschemacodegen
pip install .
```

### With Optional Dependencies

```bash
pip install .[all]        # All features
pip install .[faker]      # Realistic sample data
pip install .[dev]        # Development tools
```

---

## Quick Start

### Single Schema Processing

```python
from jsonschemacodegen import SchemaProcessor

schema = {
    "type": "object",
    "title": "User",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["id", "name", "email"]
}

processor = SchemaProcessor(schema, root_class_name="User")

# Generate Python dataclass
code = processor.generate_code()
print(code)

# Generate sample data
samples = processor.generate_samples(count=3)
```

### Module Generation (From Schema Folder)

```python
from jsonschemacodegen import generate_module

# Generate complete Python module from schema folder
result = generate_module(
    schema_dir="schemas/",
    output_dir="myapp/models/"
)

print(f"Generated {len(result['classes_generated'])} classes")
```

```python
# Use the generated module
from myapp.models import User, Product, Order
from myapp.models import load_json, to_json

# Load from JSON file
user = load_json("user.json", User)

# Create and serialize
user = User(id="123", name="John", email="john@example.com")
to_json(user, "output/user.json")
```

### Command Line

```bash
# Generate code from single schema
python -m jsonschemacodegen generate -s schema.json -o models.py

# Generate module from schema folder
python -m jsonschemacodegen generate-module \
    --schema-dir schemas/ \
    --output-dir myapp/models/

# Generate sample data
python -m jsonschemacodegen sample -s schema.json -c 10 -o samples.json

# Validate data
python -m jsonschemacodegen validate -s schema.json -d data.json
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](docs/QUICKSTART.md) | Get started in 5 minutes |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture and design |
| [MODULE_GENERATOR.md](docs/MODULE_GENERATOR.md) | Complete module generation guide |
| [EXAMPLES.md](docs/EXAMPLES.md) | Guide to 22+ example schemas |

---

## Project Structure

```
jsonschemacodegen/
├── jsonschemacodegen/           # Main package
│   ├── __init__.py              # Public API exports
│   ├── cli.py                   # CLI implementation
│   ├── module_generator.py      # Module generation
│   ├── core/                    # Core processing
│   ├── generators/              # Code generators
│   ├── models/                  # Data models
│   └── utils/                   # Utilities
├── examples/schemas/            # 22+ example schemas
├── docs/                        # Documentation
├── tests/                       # Test suite
├── main.py                      # Demo script
└── README.md
```

---

## Dependencies

### Required
- **Python 3.8+**
- No external dependencies (pure Python core)

### Optional

| Package | Purpose |
|---------|---------|
| faker | Realistic sample data |
| requests | Remote schema fetching |
| jsonschema | Enhanced validation |

---

## Support

**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## License

This software is proprietary and confidential. See [LICENSE](LICENSE) for full terms.

**Copyright © 2025-2030, All Rights Reserved**
