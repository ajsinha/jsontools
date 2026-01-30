# JsonChamp - Examples Guide

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

---

## Example Schemas

The `examples/schemas/` directory contains 22 production-ready schemas:

| # | Schema | Description |
|---|--------|-------------|
| 01 | user.json | User account with preferences |
| 02 | product.json | E-commerce product catalog |
| 03 | order.json | Order with line items |
| 04 | api_response.json | API response wrapper |
| 05 | blog_post.json | Blog content management |
| 06 | config.json | Application configuration |
| 07 | invoice.json | Financial invoice |
| 08 | event.json | Event scheduling |
| 09 | workflow.json | Business process workflow |
| 10 | notification.json | Multi-channel notifications |
| 11 | healthcare_patient.json | Patient records (HIPAA) |
| 12 | iot_device.json | IoT device telemetry |
| 13 | graphql_schema.json | GraphQL type definitions |
| 14 | kubernetes_deployment.json | K8s deployment spec |
| 15 | financial_transaction.json | Banking transactions |
| 16 | media_library.json | Media asset management |
| 17 | survey.json | Survey with questions |
| 18 | cicd_pipeline.json | CI/CD pipeline config |
| 19 | ml_model.json | ML model metadata |
| 20 | api_gateway.json | API Gateway config |
| 21 | game_entity.json | Game object definitions |
| 22 | openapi_spec.json | OpenAPI specification |

---

## Using Example Schemas

### Generate Module from All Examples

```bash
python -m jsonchamp generate-module \
    --schema-dir examples/schemas \
    --output-dir output \
    --module-name models
```

### Process Single Schema

```python
from jsonchamp import SchemaProcessor
from jsonchamp.utils import load_schema

schema = load_schema("examples/schemas/01_user.json")
processor = SchemaProcessor(schema, root_class_name="User")

code = processor.generate_code()
samples = processor.generate_samples(count=3)
```

---

## Schema Features Demonstrated

### Basic Types
- Strings with formats (email, uuid, date-time)
- Numbers with constraints (min, max, multipleOf)
- Booleans with defaults
- Arrays with item validation

### Advanced Features
- Nested objects
- $ref references
- allOf composition
- oneOf unions
- Enums and constants
- Pattern validation
- Required fields

---

## Example: User Schema

```json
{
  "type": "object",
  "title": "User",
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "email": {"type": "string", "format": "email"},
    "username": {"type": "string", "minLength": 3},
    "role": {"enum": ["admin", "user", "guest"]},
    "status": {"enum": ["active", "inactive"]}
  },
  "required": ["id", "email", "username", "role", "status"]
}
```

### Generated Usage

```python
from models import User

user = User()
user.id_ = "123e4567-e89b-12d3-a456-426614174000"
user.email = "john@example.com"
user.username = "johndoe"
user.role = "admin"
user.status = "active"

result = user.validate()
print(f"Valid: {result.is_valid}")
```

---

Copyright (C) 2025-2030, Ashutosh Sinha. All Rights Reserved.
