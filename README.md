# JsonSchemaCodeGen v1.1.0

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        JsonSchemaCodeGen v1.1.0                              ║
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

### Module Generation (Recommended)

Generate complete, ready-to-use Python modules from schema folders:

```bash
python -m jsonschemacodegen generate-module \
    --schema-dir schemas/ \
    --output-dir output/ \
    --module-name mymodels
```

Creates:
```
output/
└── mymodels/                # Module folder inside output-dir
    ├── __init__.py          # Main module exports
    ├── __main__.py          # CLI support
    ├── driver.py            # JSON utilities
    ├── main.py              # High-level functions
    └── generated/           # Generated dataclasses
        ├── __init__.py
        └── *.py
```

### Code Generation

Generate Python dataclasses with full type hints, serialization methods, and validation.

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

### Generate Module from Schema Folder (Recommended)

```bash
# Generate module - creates output/mymodels/
python -m jsonschemacodegen generate-module \
    --schema-dir schemas/ \
    --output-dir output/ \
    --module-name mymodels
```

```python
# Use the generated module
import sys
sys.path.insert(0, "output")

from mymodels import User, Product, Order
from mymodels import load_json, to_json, generate_sample

# Load from JSON
user = load_json("user.json", "User")

# Generate sample data
sample = generate_sample("User")

# Create and save
user = User(id_="123", name="John", email="john@example.com")
to_json(user, "output/user.json")

# Use CLI
# python -m mymodels list
# python -m mymodels sample User -o sample.json
```

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

### Command Line

```bash
# Generate code from single schema
python -m jsonschemacodegen generate -s schema.json -o models.py

# Generate module from schema folder
python -m jsonschemacodegen generate-module \
    --schema-dir schemas/ \
    --output-dir output/ \
    --module-name mymodels

# Generate sample data
python -m jsonschemacodegen sample -s schema.json -c 10 -o samples.json

# Validate data
python -m jsonschemacodegen validate -s schema.json -d data.json
```

---

## Generated Module CLI

The generated module includes its own CLI:

```bash
# List classes
python -m mymodels list

# Show class info
python -m mymodels info User

# Generate sample
python -m mymodels sample User -o sample.json

# Validate JSON
python -m mymodels validate user.json User
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
