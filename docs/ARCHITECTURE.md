# JsonChamp - Architecture

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

---

## System Overview

```
+----------------------------------------------------------------------+
|                        JsonChamp                              |
+----------------------------------------------------------------------+
|                                                                       |
|  +---------------------------------------------------------------+   |
|  |                    SchemaProcessor                             |   |
|  |                   (Main Entry Point)                           |   |
|  +---------------------------------------------------------------+   |
|                              |                                        |
|         +--------------------+--------------------+                   |
|         |                    |                    |                   |
|         v                    v                    v                   |
|  +-------------+     +-------------+     +--------------+            |
|  |   Parser    |     |  Validator  |     |  Generators  |            |
|  +-------------+     +-------------+     +--------------+            |
|                                                                       |
+----------------------------------------------------------------------+
```

---

## Core Components

### 1. SchemaProcessor

Main entry point for all operations.

```python
from jsonchamp import SchemaProcessor

processor = SchemaProcessor(schema, root_class_name="User")
info = processor.parse()
code = processor.generate_code()
samples = processor.generate_samples(count=5)
result = processor.validate_data(data)
```

### 2. Core Module (jsonchamp/core/)

| Component | Purpose |
|-----------|---------|
| SchemaParser | Parse JSON Schema structure |
| ReferenceResolver | Resolve $ref references |
| TypeMapper | Map JSON types to Python types |
| SchemaValidator | Validate schema structure |

### 3. Generators Module (jsonchamp/generators/)

| Component | Purpose |
|-----------|---------|
| CodeGenerator | Generate Python dataclasses |
| SampleGenerator | Generate sample data |
| ClassGenerator | Generate class structures |

### 4. Module Generator

Generates complete Python modules from schema folders.

```python
from jsonchamp import generate_module

result = generate_module(
    schema_dir="schemas/",
    output_dir="output/",
    module_name="mymodels"
)
```

---

## Data Flow

```
JSON Schema File
       |
       v
+---------------+
| SchemaParser  |  --> Parse structure
+---------------+
       |
       v
+-------------------+
| ReferenceResolver |  --> Resolve $ref
+-------------------+
       |
       v
+---------------+
| TypeMapper    |  --> Map to Python types
+---------------+
       |
       v
+---------------+
| CodeGenerator |  --> Generate dataclass
+---------------+
       |
       v
Python Source Code
```

---

## Generated Class Structure

Each generated class includes:

- Type hints for all properties
- `to_dict()` - Convert to dictionary
- `to_json()` - Serialize to JSON
- `from_dict()` - Create from dictionary
- `from_json()` - Create from JSON
- `validate()` - Validate required fields and enums

---

## Package Structure

```
jsonchamp/
+-- __init__.py           # Public API
+-- cli.py                # CLI implementation
+-- module_generator.py   # Module generation
+-- core/
|   +-- schema_parser.py
|   +-- reference_resolver.py
|   +-- type_mapper.py
|   +-- schema_processor.py
|   +-- validator.py
+-- generators/
|   +-- code_generator.py
|   +-- sample_generator.py
|   +-- class_generator.py
+-- models/
|   +-- base.py
+-- utils/
    +-- naming.py
    +-- json_utils.py
    +-- file_utils.py
```

---

Copyright (C) 2025-2030, Ashutosh Sinha. All Rights Reserved.
