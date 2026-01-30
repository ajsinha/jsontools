# JsonTools v1.4.0

```
+==============================================================================+
|                                                                              |
|                           JsonTools v1.4.0                                   |
|                                                                              |
|            Commercial Grade JSON Schema to Python Code Generator             |
|                      with SchemaMap Transformation DSL                       |
|                                                                              |
|                  Copyright (C) 2025-2030, All Rights Reserved                |
|                      Ashutosh Sinha (ajsinha@gmail.com)                      |
|                                                                              |
+==============================================================================+
```

---

## Copyright and Legal Notice

**Copyright (C) 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Overview

**JsonTools** is a comprehensive, commercial-grade Python library for working with JSON Schema. It provides powerful, production-ready tools for:

- **Schema Parsing**: Parse and analyze JSON Schema documents with full Draft-07 support
- **Code Generation**: Generate Python dataclasses from JSON Schema
- **Sample Data Generation**: Create realistic test data with Faker integration
- **Validation**: Validate schemas and data with detailed error reporting
- **Reference Resolution**: Handle complex `$ref` references including remote schemas
- **Module Generation**: Generate complete Python modules from schema folders
- **SchemaMap Transformation**: Transform JSON between schemas using a declarative DSL
- **External Python Functions**: Call custom Python functions from SchemaMap DSL
- **Code Compilation**: Compile SchemaMap to optimized Python code (5-10x faster!)

---

## What's New in v1.4.0

### Compiled Transformations (5-10x Faster!)

SchemaMap can now compile `.smap` files to standalone Python code:

```bash
# Compile to Python
python transform.py --compile mapping.smap -o transformer.py

# Benchmark interpreted vs compiled
python transform.py --benchmark mapping.smap input.json
```

**Benchmark Results:**
```
  Interpreted Transformer:
    Ops/second:     7,927
    μs/operation:   126.15

  Compiled Transformer:
    Ops/second:     41,236
    μs/operation:   24.25

  SPEEDUP: 5.2x faster with compiled code!
```

The generated code is:
- **Standalone** - No SchemaMap runtime dependency
- **Optimized** - Transforms inlined, no function lookups
- **Type-hinted** - Full IDE support
- **Production-ready** - Use directly in your applications

---

## Quick Start

### Install

```bash
pip install .
```

### Generate Python Module from JSON Schemas

```bash
python -m jsontools generate-module \
    --schema-dir ./schemas \
    --output-dir ./generated \
    --module-name my_models
```

### Transform JSON Data

```bash
# Interpreted (flexible, good for development)
python transform.py mapping.smap input.json

# Compiled (fast, good for production)
python transform.py --compile mapping.smap -o transformer.py
python transformer.py input.json
```

### Python API

```python
from jsontools.transformation import transform, load_mapping

# Simple transformation
result = transform(source_data, "mapping.smap")

# With custom functions
transformer = load_mapping("mapping.smap")
transformer.register_function("calc_tax", lambda x, r: round(x * r, 2))
result = transformer.transform(data)
```

---

## SchemaMap Transformation DSL

SchemaMap is a declarative DSL for transforming JSON between schemas.

### Example Mapping File

```
@config {
    null_handling : omit
}

@lookups {
    status_codes : { "A": "ACTIVE", "I": "INACTIVE" }
}

# Simple mappings
user.id                                 : userId
user.email                              : email | lowercase | trim

# Concatenation
user.first + " " + user.last            : fullName | titlecase

# Coalescing
user.mobile ?? user.phone               : primaryPhone

# Lookups
user.status                             : status | lookup(@status_codes)

# Computed fields
@compute(sum(items[*].price))           : total
@now                                    : processedAt
@uuid                                   : transactionId

# External functions
@compute(calculate_tax(subtotal, 0.08)) : tax
```

### Run Transformation

```bash
# Interpret (development)
python transform.py mapping.smap input.json

# Compile (production)
python transform.py --compile mapping.smap -o transformer.py

# Benchmark
python transform.py --benchmark mapping.smap input.json --iterations 10000
```

### Key Features

- **90+ Built-in Functions**: String, numeric, date, array transforms
- **External Python Functions**: Call custom functions from DSL
- **Aliases**: Define reusable transform chains
- **Lookups**: Map codes to values
- **Array Support**: Transform arrays element-by-element
- **Computed Fields**: Generate values with expressions
- **Schema Validation**: Validate output against JSON Schema
- **Code Compilation**: Generate optimized Python code

See [docs/SCHEMAMAP.md](docs/SCHEMAMAP.md) for full documentation.

---

## CLI Reference

### Transform Data

```bash
python transform.py mapping.smap input.json
python transform.py mapping.smap input.json --output result.json
python transform.py mapping.smap input.json --schema target_schema.json
python transform.py mapping.smap input.json --functions custom_funcs.py
```

### Compile to Python

```bash
python transform.py --compile mapping.smap
python transform.py --compile mapping.smap -o my_transformer.py
python transform.py --compile mapping.smap -o transformer.py --class-name CustomerTransformer
```

### Benchmark Performance

```bash
python transform.py --benchmark mapping.smap input.json
python transform.py --benchmark mapping.smap input.json --iterations 50000
```

---

## Project Structure

```
jsontools/
├── jsontools/                   # Main package
│   ├── __init__.py              # Public API
│   ├── cli.py                   # CLI implementation
│   ├── module_generator.py      # Module generation
│   ├── core/                    # Core processing
│   ├── generators/              # Code generators
│   ├── models/                  # Data models
│   ├── utils/                   # Utilities
│   └── transformation/          # SchemaMap module
│       ├── parser/              # Lexer, parser, AST
│       ├── engine/              # Transformer, evaluator
│       └── compiler/            # Python code generator
├── examples/
│   ├── schemas/                 # 22+ JSON schemas
│   └── transformation/          # SchemaMap examples
│       ├── source_data/         # Input JSON files
│       ├── mappings/            # .smap files
│       ├── compiled/            # Generated Python code
│       └── target_schemas/      # Output schemas
├── docs/                        # Documentation
├── transform.py                 # CLI runner & compiler
└── README.md
```

---

## Dependencies

### Required
- **Python 3.8+**
- No external dependencies (pure Python core)

### Optional
- **faker**: Realistic sample data
- **requests**: Remote schema fetching
- **jsonschema**: Enhanced validation

---

## License

This software is proprietary and confidential. See [LICENSE](LICENSE) for full terms.

**Copyright (C) 2025-2030, All Rights Reserved**  
**Ashutosh Sinha - ajsinha@gmail.com**
