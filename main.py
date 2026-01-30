#!/usr/bin/env python3
"""
JsonSchemaCodeGen - Comprehensive Demonstration Script

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

This script demonstrates all the key features of JsonSchemaCodeGen with
extensive examples covering various use cases.
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, date

# Add package to path for direct execution
sys.path.insert(0, str(Path(__file__).parent))

from jsonchamp import (
    SchemaProcessor,
    generate_code,
    generate_samples,
    generate_module,
    ModuleGenerator,
    __version__,
)
from jsonchamp.core import (
    SchemaParser,
    ReferenceResolver,
    TypeMapper,
    SchemaValidator,
)
from jsonchamp.generators import (
    SampleGenerator,
    ClassGenerator,
    CodeGenerator,
)
from jsonchamp.utils import load_schema


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 78)
    print(f"  {title}")
    print("=" * 78 + "\n")


def print_subheader(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---\n")


def print_code(code: str, max_lines: int = 50) -> None:
    """Print code with line limit."""
    lines = code.split('\n')
    if len(lines) > max_lines:
        print('\n'.join(lines[:max_lines]))
        print(f"\n... ({len(lines) - max_lines} more lines)")
    else:
        print(code)


def print_json(data: any, max_lines: int = 30) -> None:
    """Print JSON with line limit."""
    output = json.dumps(data, indent=2, default=str)
    lines = output.split('\n')
    if len(lines) > max_lines:
        print('\n'.join(lines[:max_lines]))
        print(f"\n... ({len(lines) - max_lines} more lines)")
    else:
        print(output)


# =============================================================================
# EXAMPLE 1: BASIC SCHEMA PROCESSING
# =============================================================================

def demo_basic_schema():
    """Demonstrate basic schema processing with a simple object."""
    print_header("EXAMPLE 1: BASIC SCHEMA PROCESSING")
    
    schema = {
        "type": "object",
        "title": "Person",
        "description": "A simple person record",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "name": {"type": "string", "minLength": 1, "maxLength": 100},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "isActive": {"type": "boolean", "default": True}
        },
        "required": ["id", "name", "email"]
    }
    
    print_subheader("Input Schema")
    print_json(schema)
    
    processor = SchemaProcessor(schema, root_class_name="Person")
    
    print_subheader("Parsed Schema Info")
    info = processor.parse()
    print(f"Title: {info.title}")
    print(f"Description: {info.description}")
    print(f"Properties: {len(info.properties)}")
    for name, prop in info.properties.items():
        req = " (required)" if prop.required else ""
        print(f"  - {name}: {[t.value for t in prop.types]}{req}")
    
    print_subheader("Generated Python Dataclass")
    code = processor.generate_code()
    print_code(code, 60)
    
    print_subheader("Generated Sample Data")
    samples = processor.generate_samples(count=3)
    for i, sample in enumerate(samples, 1):
        print(f"Sample {i}:")
        print_json(sample, 10)


# =============================================================================
# EXAMPLE 2: NESTED OBJECTS
# =============================================================================

def demo_nested_objects():
    """Demonstrate handling of nested object schemas."""
    print_header("EXAMPLE 2: NESTED OBJECTS")
    
    schema = {
        "type": "object",
        "title": "Company",
        "properties": {
            "name": {"type": "string"},
            "founded": {"type": "integer"},
            "headquarters": {
                "type": "object",
                "title": "Address",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "country": {"type": "string"},
                    "postalCode": {"type": "string"}
                },
                "required": ["city", "country"]
            },
            "ceo": {
                "type": "object",
                "title": "Executive",
                "properties": {
                    "name": {"type": "string"},
                    "title": {"type": "string"},
                    "since": {"type": "integer"}
                }
            },
            "departments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "title": "Department",
                    "properties": {
                        "name": {"type": "string"},
                        "headCount": {"type": "integer"},
                        "budget": {"type": "number"}
                    }
                }
            }
        },
        "required": ["name"]
    }
    
    print_subheader("Schema with Nested Objects")
    print_json(schema, 40)
    
    processor = SchemaProcessor(schema, root_class_name="Company")
    
    print_subheader("Generated Code (Multiple Classes)")
    code = processor.generate_code()
    print_code(code, 80)
    
    print_subheader("Sample Data with Nested Objects")
    samples = processor.generate_samples(count=1)
    print_json(samples[0], 40)


# =============================================================================
# EXAMPLE 3: ARRAYS AND COLLECTIONS
# =============================================================================

def demo_arrays():
    """Demonstrate various array types and configurations."""
    print_header("EXAMPLE 3: ARRAYS AND COLLECTIONS")
    
    schema = {
        "type": "object",
        "title": "DataCollection",
        "properties": {
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "maxItems": 10,
                "uniqueItems": True
            },
            "scores": {
                "type": "array",
                "items": {"type": "number", "minimum": 0, "maximum": 100}
            },
            "matrix": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {"type": "integer"}
                },
                "description": "2D matrix of integers"
            },
            "users": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "roles": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            },
            "mixedTuple": {
                "type": "array",
                "items": [
                    {"type": "string"},
                    {"type": "integer"},
                    {"type": "boolean"}
                ],
                "additionalItems": False
            }
        }
    }
    
    print_subheader("Schema with Various Array Types")
    print_json(schema, 50)
    
    processor = SchemaProcessor(schema, root_class_name="DataCollection")
    
    print_subheader("Generated Code")
    code = processor.generate_code()
    print_code(code, 60)
    
    print_subheader("Sample Data")
    samples = processor.generate_samples(count=2)
    for i, sample in enumerate(samples, 1):
        print(f"Sample {i}:")
        print_json(sample, 25)


# =============================================================================
# EXAMPLE 4: STRING FORMATS AND PATTERNS
# =============================================================================

def demo_string_formats():
    """Demonstrate various string formats and patterns."""
    print_header("EXAMPLE 4: STRING FORMATS AND PATTERNS")
    
    schema = {
        "type": "object",
        "title": "FormattedData",
        "properties": {
            "uuid": {"type": "string", "format": "uuid"},
            "email": {"type": "string", "format": "email"},
            "uri": {"type": "string", "format": "uri"},
            "hostname": {"type": "string", "format": "hostname"},
            "ipv4": {"type": "string", "format": "ipv4"},
            "ipv6": {"type": "string", "format": "ipv6"},
            "dateTime": {"type": "string", "format": "date-time"},
            "date": {"type": "string", "format": "date"},
            "time": {"type": "string", "format": "time"},
            "phone": {
                "type": "string",
                "pattern": "^\\+?[1-9]\\d{1,14}$",
                "description": "E.164 phone number format"
            },
            "zipCode": {
                "type": "string",
                "pattern": "^\\d{5}(-\\d{4})?$",
                "description": "US ZIP code"
            },
            "hexColor": {
                "type": "string",
                "pattern": "^#[0-9A-Fa-f]{6}$",
                "description": "Hex color code"
            },
            "slug": {
                "type": "string",
                "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$",
                "minLength": 3,
                "maxLength": 50
            }
        }
    }
    
    print_subheader("Schema with String Formats")
    print_json(schema, 45)
    
    processor = SchemaProcessor(schema, root_class_name="FormattedData")
    
    print_subheader("Generated Samples (Format-Aware)")
    samples = processor.generate_samples(count=2)
    for i, sample in enumerate(samples, 1):
        print(f"Sample {i}:")
        print_json(sample, 20)


# =============================================================================
# EXAMPLE 5: ENUMS AND CONSTANTS
# =============================================================================

def demo_enums():
    """Demonstrate enums and constant values."""
    print_header("EXAMPLE 5: ENUMS AND CONSTANTS")
    
    schema = {
        "type": "object",
        "title": "OrderStatus",
        "properties": {
            "orderId": {"type": "string"},
            "status": {
                "type": "string",
                "enum": ["pending", "processing", "shipped", "delivered", "cancelled"]
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "urgent"],
                "default": "medium"
            },
            "paymentMethod": {
                "type": "string",
                "enum": ["credit_card", "debit_card", "paypal", "bank_transfer", "crypto"]
            },
            "currency": {
                "type": "string",
                "enum": ["USD", "EUR", "GBP", "JPY", "CAD"],
                "default": "USD"
            },
            "version": {
                "const": "1.0",
                "description": "API version (constant)"
            },
            "type": {
                "const": "order",
                "description": "Record type (constant)"
            }
        },
        "required": ["orderId", "status"]
    }
    
    print_subheader("Schema with Enums and Constants")
    print_json(schema)
    
    processor = SchemaProcessor(schema, root_class_name="OrderStatus")
    
    print_subheader("Generated Code with Enum Classes")
    code = processor.generate_code()
    print_code(code, 70)
    
    print_subheader("Sample Data")
    samples = processor.generate_samples(count=3)
    for i, sample in enumerate(samples, 1):
        print(f"Sample {i}: {json.dumps(sample, default=str)}")


# =============================================================================
# EXAMPLE 6: NUMERIC CONSTRAINTS
# =============================================================================

def demo_numeric_constraints():
    """Demonstrate numeric types with constraints."""
    print_header("EXAMPLE 6: NUMERIC CONSTRAINTS")
    
    schema = {
        "type": "object",
        "title": "Metrics",
        "properties": {
            "temperature": {
                "type": "number",
                "minimum": -273.15,
                "maximum": 1000,
                "description": "Temperature in Celsius"
            },
            "percentage": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "multipleOf": 0.01
            },
            "rating": {
                "type": "number",
                "minimum": 1,
                "maximum": 5,
                "multipleOf": 0.5
            },
            "quantity": {
                "type": "integer",
                "minimum": 0,
                "exclusiveMaximum": 1000
            },
            "price": {
                "type": "number",
                "minimum": 0,
                "exclusiveMinimum": 0,
                "multipleOf": 0.01
            },
            "count": {
                "type": "integer",
                "multipleOf": 5,
                "minimum": 0,
                "maximum": 100
            },
            "latitude": {
                "type": "number",
                "minimum": -90,
                "maximum": 90
            },
            "longitude": {
                "type": "number",
                "minimum": -180,
                "maximum": 180
            }
        }
    }
    
    print_subheader("Schema with Numeric Constraints")
    print_json(schema)
    
    processor = SchemaProcessor(schema, root_class_name="Metrics")
    
    print_subheader("Generated Samples (Constraint-Aware)")
    samples = processor.generate_samples(count=3)
    for i, sample in enumerate(samples, 1):
        print(f"Sample {i}:")
        print_json(sample, 15)


# =============================================================================
# EXAMPLE 7: ALLOF (INHERITANCE/COMPOSITION)
# =============================================================================

def demo_allof():
    """Demonstrate allOf for composition/inheritance."""
    print_header("EXAMPLE 7: ALLOF (COMPOSITION)")
    
    schema = {
        "type": "object",
        "title": "Employee",
        "allOf": [
            {
                "type": "object",
                "title": "Person",
                "properties": {
                    "firstName": {"type": "string"},
                    "lastName": {"type": "string"},
                    "email": {"type": "string", "format": "email"}
                },
                "required": ["firstName", "lastName"]
            },
            {
                "type": "object",
                "title": "Employment",
                "properties": {
                    "employeeId": {"type": "string"},
                    "department": {"type": "string"},
                    "title": {"type": "string"},
                    "salary": {"type": "number"},
                    "startDate": {"type": "string", "format": "date"}
                },
                "required": ["employeeId", "department"]
            },
            {
                "type": "object",
                "properties": {
                    "manager": {"type": "string"},
                    "directReports": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        ]
    }
    
    print_subheader("Schema with allOf (Composition)")
    print_json(schema, 45)
    
    processor = SchemaProcessor(schema, root_class_name="Employee")
    
    print_subheader("Parsed Combined Properties")
    info = processor.parse()
    print(f"Combined properties from allOf:")
    for name, prop in info.properties.items():
        req = " (required)" if prop.required else ""
        print(f"  - {name}{req}")
    
    print_subheader("Generated Code")
    code = processor.generate_code()
    print_code(code, 50)
    
    print_subheader("Sample Data")
    samples = processor.generate_samples(count=1)
    print_json(samples[0])


# =============================================================================
# EXAMPLE 8: ONEOF (UNION TYPES)
# =============================================================================

def demo_oneof():
    """Demonstrate oneOf for union types."""
    print_header("EXAMPLE 8: ONEOF (UNION TYPES)")
    
    schema = {
        "type": "object",
        "title": "Notification",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "timestamp": {"type": "string", "format": "date-time"},
            "payload": {
                "oneOf": [
                    {
                        "type": "object",
                        "title": "EmailNotification",
                        "properties": {
                            "type": {"const": "email"},
                            "to": {"type": "string", "format": "email"},
                            "subject": {"type": "string"},
                            "body": {"type": "string"}
                        },
                        "required": ["type", "to", "subject"]
                    },
                    {
                        "type": "object",
                        "title": "SMSNotification",
                        "properties": {
                            "type": {"const": "sms"},
                            "phoneNumber": {"type": "string"},
                            "message": {"type": "string", "maxLength": 160}
                        },
                        "required": ["type", "phoneNumber", "message"]
                    },
                    {
                        "type": "object",
                        "title": "PushNotification",
                        "properties": {
                            "type": {"const": "push"},
                            "deviceToken": {"type": "string"},
                            "title": {"type": "string"},
                            "body": {"type": "string"},
                            "badge": {"type": "integer"}
                        },
                        "required": ["type", "deviceToken", "title"]
                    }
                ]
            }
        },
        "required": ["id", "payload"]
    }
    
    print_subheader("Schema with oneOf (Union Types)")
    print_json(schema, 50)
    
    processor = SchemaProcessor(schema, root_class_name="Notification")
    
    print_subheader("Generated Code")
    code = processor.generate_code()
    print_code(code, 60)
    
    print_subheader("Sample Data (Different Variants)")
    samples = processor.generate_samples(count=3)
    for i, sample in enumerate(samples, 1):
        print(f"Sample {i}:")
        print_json(sample, 15)


# =============================================================================
# EXAMPLE 9: ANYOF (FLEXIBLE TYPES)
# =============================================================================

def demo_anyof():
    """Demonstrate anyOf for flexible types."""
    print_header("EXAMPLE 9: ANYOF (FLEXIBLE TYPES)")
    
    schema = {
        "type": "object",
        "title": "FlexibleConfig",
        "properties": {
            "name": {"type": "string"},
            "value": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "number"},
                    {"type": "boolean"},
                    {"type": "array", "items": {"type": "string"}}
                ],
                "description": "Can be string, number, boolean, or array of strings"
            },
            "timeout": {
                "anyOf": [
                    {"type": "integer", "minimum": 0},
                    {"type": "string", "pattern": "^\\d+[smh]$"}
                ],
                "description": "Timeout as integer (ms) or string like '30s', '5m', '1h'"
            },
            "endpoint": {
                "anyOf": [
                    {"type": "string", "format": "uri"},
                    {
                        "type": "object",
                        "properties": {
                            "host": {"type": "string"},
                            "port": {"type": "integer"},
                            "path": {"type": "string"}
                        }
                    }
                ]
            }
        }
    }
    
    print_subheader("Schema with anyOf (Flexible Types)")
    print_json(schema, 40)
    
    processor = SchemaProcessor(schema, root_class_name="FlexibleConfig")
    
    print_subheader("Generated Code")
    code = processor.generate_code()
    print_code(code, 50)
    
    print_subheader("Sample Data")
    samples = processor.generate_samples(count=3)
    for i, sample in enumerate(samples, 1):
        print(f"Sample {i}:")
        print_json(sample, 12)


# =============================================================================
# EXAMPLE 10: DEFINITIONS AND REFERENCES
# =============================================================================

def demo_definitions():
    """Demonstrate $defs/$definitions and $ref."""
    print_header("EXAMPLE 10: DEFINITIONS AND REFERENCES")
    
    schema = {
        "$defs": {
            "Address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "zip": {"type": "string"},
                    "country": {"type": "string", "default": "USA"}
                },
                "required": ["city", "country"]
            },
            "ContactInfo": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "phone": {"type": "string"},
                    "fax": {"type": "string"}
                }
            },
            "Money": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "minimum": 0},
                    "currency": {"type": "string", "enum": ["USD", "EUR", "GBP"]}
                },
                "required": ["amount", "currency"]
            }
        },
        "type": "object",
        "title": "Customer",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "name": {"type": "string"},
            "billingAddress": {"$ref": "#/$defs/Address"},
            "shippingAddress": {"$ref": "#/$defs/Address"},
            "contact": {"$ref": "#/$defs/ContactInfo"},
            "creditLimit": {"$ref": "#/$defs/Money"},
            "balance": {"$ref": "#/$defs/Money"}
        },
        "required": ["id", "name", "billingAddress"]
    }
    
    print_subheader("Schema with $defs and $ref")
    print_json(schema, 55)
    
    processor = SchemaProcessor(schema, root_class_name="Customer")
    
    print_subheader("Reference Resolution")
    info = processor.parse()
    print(f"Root properties (with resolved refs):")
    for name, prop in info.properties.items():
        print(f"  - {name}: {[t.value for t in prop.types]}")
    
    print_subheader("Generated Code (Reusable Classes)")
    code = processor.generate_code()
    print_code(code, 80)
    
    print_subheader("Sample Data")
    samples = processor.generate_samples(count=1)
    print_json(samples[0], 35)


# =============================================================================
# EXAMPLE 11: ADDITIONAL PROPERTIES
# =============================================================================

def demo_additional_properties():
    """Demonstrate additionalProperties handling."""
    print_header("EXAMPLE 11: ADDITIONAL PROPERTIES")
    
    schema = {
        "type": "object",
        "title": "DynamicConfig",
        "properties": {
            "name": {"type": "string"},
            "version": {"type": "string"}
        },
        "additionalProperties": {
            "type": "object",
            "properties": {
                "value": {"type": "string"},
                "enabled": {"type": "boolean", "default": True},
                "priority": {"type": "integer", "minimum": 0, "maximum": 100}
            }
        }
    }
    
    schema2 = {
        "type": "object",
        "title": "StrictConfig",
        "properties": {
            "host": {"type": "string"},
            "port": {"type": "integer"}
        },
        "additionalProperties": False
    }
    
    schema3 = {
        "type": "object",
        "title": "StringMap",
        "additionalProperties": {"type": "string"}
    }
    
    print_subheader("Schema with Typed additionalProperties")
    print_json(schema)
    
    processor = SchemaProcessor(schema, root_class_name="DynamicConfig")
    code = processor.generate_code()
    print_subheader("Generated Code")
    print_code(code, 40)
    
    print_subheader("Schema with additionalProperties: false")
    print_json(schema2)
    
    print_subheader("Schema with String Map")
    print_json(schema3)


# =============================================================================
# EXAMPLE 12: CONDITIONAL SCHEMAS (IF/THEN/ELSE)
# =============================================================================

def demo_conditional():
    """Demonstrate conditional schemas."""
    print_header("EXAMPLE 12: CONDITIONAL SCHEMAS")
    
    schema = {
        "type": "object",
        "title": "ShippingInfo",
        "properties": {
            "country": {"type": "string"},
            "postalCode": {"type": "string"}
        },
        "required": ["country"],
        "if": {
            "properties": {
                "country": {"const": "USA"}
            }
        },
        "then": {
            "properties": {
                "postalCode": {
                    "type": "string",
                    "pattern": "^\\d{5}(-\\d{4})?$"
                },
                "state": {
                    "type": "string",
                    "enum": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA"]
                }
            },
            "required": ["postalCode", "state"]
        },
        "else": {
            "properties": {
                "postalCode": {"type": "string"},
                "region": {"type": "string"}
            }
        }
    }
    
    print_subheader("Schema with if/then/else")
    print_json(schema)
    
    processor = SchemaProcessor(schema, root_class_name="ShippingInfo")
    
    print_subheader("Generated Code")
    code = processor.generate_code()
    print_code(code, 40)


# =============================================================================
# EXAMPLE 13: COMPLEX E-COMMERCE SCHEMA
# =============================================================================

def demo_ecommerce():
    """Demonstrate a complex real-world e-commerce schema."""
    print_header("EXAMPLE 13: COMPLEX E-COMMERCE SCHEMA")
    
    schema = {
        "type": "object",
        "title": "Order",
        "description": "E-commerce order with full details",
        "properties": {
            "orderId": {"type": "string", "format": "uuid"},
            "orderNumber": {"type": "string", "pattern": "^ORD-\\d{8}$"},
            "status": {
                "type": "string",
                "enum": ["draft", "pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "refunded"]
            },
            "customer": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "name": {"type": "string"},
                    "phone": {"type": "string"},
                    "isGuest": {"type": "boolean", "default": False}
                },
                "required": ["email", "name"]
            },
            "items": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "sku": {"type": "string"},
                        "name": {"type": "string"},
                        "quantity": {"type": "integer", "minimum": 1},
                        "unitPrice": {"type": "number", "minimum": 0},
                        "discount": {"type": "number", "minimum": 0, "default": 0},
                        "tax": {"type": "number", "minimum": 0}
                    },
                    "required": ["sku", "name", "quantity", "unitPrice"]
                }
            },
            "shipping": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "enum": ["standard", "express", "overnight", "pickup"]},
                    "address": {
                        "type": "object",
                        "properties": {
                            "line1": {"type": "string"},
                            "line2": {"type": "string"},
                            "city": {"type": "string"},
                            "state": {"type": "string"},
                            "postalCode": {"type": "string"},
                            "country": {"type": "string"}
                        },
                        "required": ["line1", "city", "country"]
                    },
                    "cost": {"type": "number", "minimum": 0},
                    "estimatedDelivery": {"type": "string", "format": "date"}
                }
            },
            "payment": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "enum": ["credit_card", "paypal", "apple_pay", "google_pay", "bank_transfer"]},
                    "status": {"type": "string", "enum": ["pending", "authorized", "captured", "failed", "refunded"]},
                    "transactionId": {"type": "string"},
                    "amount": {"type": "number"},
                    "currency": {"type": "string", "default": "USD"}
                }
            },
            "totals": {
                "type": "object",
                "properties": {
                    "subtotal": {"type": "number"},
                    "shipping": {"type": "number"},
                    "tax": {"type": "number"},
                    "discount": {"type": "number"},
                    "total": {"type": "number"}
                }
            },
            "notes": {"type": "string"},
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "uniqueItems": True
            },
            "metadata": {
                "type": "object",
                "additionalProperties": {"type": "string"}
            },
            "createdAt": {"type": "string", "format": "date-time"},
            "updatedAt": {"type": "string", "format": "date-time"}
        },
        "required": ["orderId", "status", "customer", "items"]
    }
    
    print_subheader("Complex E-Commerce Order Schema")
    print_json(schema, 80)
    
    processor = SchemaProcessor(schema, root_class_name="Order")
    
    print_subheader("Generated Code")
    code = processor.generate_code()
    print_code(code, 100)
    
    print_subheader("Sample Order Data")
    samples = processor.generate_samples(count=1)
    print_json(samples[0], 60)


# =============================================================================
# EXAMPLE 14: API RESPONSE SCHEMA
# =============================================================================

def demo_api_response():
    """Demonstrate API response schema patterns."""
    print_header("EXAMPLE 14: API RESPONSE PATTERNS")
    
    schema = {
        "type": "object",
        "title": "APIResponse",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "oneOf": [
                    {
                        "type": "object",
                        "title": "UserData",
                        "properties": {
                            "user": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "username": {"type": "string"},
                                    "email": {"type": "string", "format": "email"}
                                }
                            }
                        }
                    },
                    {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"}
                            }
                        }
                    },
                    {"type": "null"}
                ]
            },
            "error": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "message": {"type": "string"},
                    "details": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {"type": "string"},
                                "issue": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "pagination": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "minimum": 1},
                    "perPage": {"type": "integer", "minimum": 1, "maximum": 100},
                    "total": {"type": "integer", "minimum": 0},
                    "totalPages": {"type": "integer", "minimum": 0}
                }
            },
            "meta": {
                "type": "object",
                "properties": {
                    "requestId": {"type": "string", "format": "uuid"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "version": {"type": "string"}
                }
            }
        },
        "required": ["success"]
    }
    
    print_subheader("API Response Schema")
    print_json(schema, 60)
    
    processor = SchemaProcessor(schema, root_class_name="APIResponse")
    
    print_subheader("Generated Code")
    code = processor.generate_code()
    print_code(code, 70)


# =============================================================================
# EXAMPLE 15: VALIDATION DEMONSTRATION
# =============================================================================

def demo_validation():
    """Demonstrate validation capabilities."""
    print_header("EXAMPLE 15: VALIDATION")
    
    schema = {
        "type": "object",
        "title": "UserRegistration",
        "properties": {
            "username": {
                "type": "string",
                "minLength": 3,
                "maxLength": 20,
                "pattern": "^[a-z0-9_]+$"
            },
            "email": {"type": "string", "format": "email"},
            "password": {"type": "string", "minLength": 8},
            "age": {"type": "integer", "minimum": 18, "maximum": 120},
            "acceptedTerms": {"type": "boolean", "const": True}
        },
        "required": ["username", "email", "password", "acceptedTerms"]
    }
    
    processor = SchemaProcessor(schema)
    
    print_subheader("Validation Schema")
    print_json(schema)
    
    # Valid data
    print_subheader("Validating Valid Data")
    valid_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "securepass123",
        "age": 30,
        "acceptedTerms": True
    }
    print(f"Data: {json.dumps(valid_data)}")
    result = processor.validate_data(valid_data)
    print(f"Valid: {result.is_valid}")
    
    # Invalid data examples
    print_subheader("Validating Invalid Data")
    
    invalid_examples = [
        {
            "name": "Missing required field",
            "data": {"username": "john", "email": "john@example.com"}
        },
        {
            "name": "Invalid email format",
            "data": {"username": "john", "email": "not-an-email", "password": "pass1234", "acceptedTerms": True}
        },
        {
            "name": "Username too short",
            "data": {"username": "jo", "email": "john@example.com", "password": "pass1234", "acceptedTerms": True}
        },
        {
            "name": "Invalid username pattern",
            "data": {"username": "John-Doe", "email": "john@example.com", "password": "pass1234", "acceptedTerms": True}
        },
        {
            "name": "Password too short",
            "data": {"username": "john_doe", "email": "john@example.com", "password": "short", "acceptedTerms": True}
        },
        {
            "name": "Age below minimum",
            "data": {"username": "john_doe", "email": "john@example.com", "password": "pass1234", "age": 15, "acceptedTerms": True}
        }
    ]
    
    for example in invalid_examples:
        print(f"\n{example['name']}:")
        print(f"  Data: {json.dumps(example['data'])}")
        result = processor.validate_data(example['data'])
        print(f"  Valid: {result.is_valid}")
        if not result.is_valid:
            for issue in result.issues[:2]:
                print(f"  Issue: {issue.path} - {issue.message}")


# =============================================================================
# EXAMPLE 16: SCHEMA VALIDATOR
# =============================================================================

def demo_schema_validator():
    """Demonstrate schema validation."""
    print_header("EXAMPLE 16: SCHEMA VALIDATION")
    
    print_subheader("Valid Schema")
    valid_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0}
        }
    }
    print_json(valid_schema)
    
    validator = SchemaValidator()
    result = validator.validate_schema(valid_schema)
    print(f"Schema valid: {result.is_valid}")
    
    print_subheader("Schema with Warnings")
    warning_schema = {
        "type": "object",
        "properties": {
            "data": {}  # Empty schema - warning
        }
    }
    print_json(warning_schema)
    
    result = validator.validate_schema(warning_schema)
    print(f"Schema valid: {result.is_valid}")
    print(f"Warnings: {len(result.warnings)}")
    for warning in result.warnings:
        print(f"  - {warning.path}: {warning.message}")
    
    print_subheader("Invalid Schema")
    invalid_schema = {
        "type": "invalid_type",  # Invalid type
        "properties": "not_an_object"  # Should be object
    }
    print_json(invalid_schema)
    
    result = validator.validate_schema(invalid_schema)
    print(f"Schema valid: {result.is_valid}")
    print(f"Errors: {len(result.errors)}")
    for error in result.errors:
        print(f"  - {error.path}: {error.message}")


# =============================================================================
# EXAMPLE 17: TYPE MAPPER
# =============================================================================

def demo_type_mapper():
    """Demonstrate type mapping from JSON Schema to Python."""
    print_header("EXAMPLE 17: TYPE MAPPING")
    
    type_mapper = TypeMapper()
    
    test_schemas = [
        {"type": "string"},
        {"type": "string", "format": "uuid"},
        {"type": "string", "format": "date-time"},
        {"type": "string", "format": "email"},
        {"type": "integer"},
        {"type": "number"},
        {"type": "boolean"},
        {"type": "array", "items": {"type": "string"}},
        {"type": "array", "items": {"type": "integer"}},
        {"type": "object"},
        {"type": "object", "additionalProperties": {"type": "string"}},
        {"type": ["string", "null"]},
        {"type": ["integer", "string"]},
        {"enum": ["a", "b", "c"]},
        {"const": "fixed_value"},
    ]
    
    print_subheader("JSON Schema to Python Type Mapping")
    print(f"{'JSON Schema':<50} {'Python Type':<30}")
    print("-" * 80)
    
    for schema in test_schemas:
        mapping = type_mapper.map_schema(schema)
        schema_str = json.dumps(schema)
        if len(schema_str) > 48:
            schema_str = schema_str[:45] + "..."
        print(f"{schema_str:<50} {mapping.python_type:<30}")


# =============================================================================
# EXAMPLE 18: CODE GENERATOR OPTIONS
# =============================================================================

def demo_code_generator_options():
    """Demonstrate different code generation options."""
    print_header("EXAMPLE 18: CODE GENERATOR OPTIONS")
    
    schema = {
        "type": "object",
        "title": "Config",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "integer"},
            "enabled": {"type": "boolean", "default": True}
        }
    }
    
    print_subheader("Default Dataclass Style")
    generator = CodeGenerator(schema, root_class_name="Config", style="dataclass")
    code = generator.generate()
    print_code(code, 40)
    
    print_subheader("Without Validators")
    generator = CodeGenerator(schema, root_class_name="Config", include_validators=False)
    code = generator.generate()
    print_code(code, 30)


# =============================================================================
# EXAMPLE 19: SAMPLE GENERATOR OPTIONS
# =============================================================================

def demo_sample_generator_options():
    """Demonstrate sample generation options."""
    print_header("EXAMPLE 19: SAMPLE GENERATOR OPTIONS")
    
    schema = {
        "type": "object",
        "title": "Person",
        "properties": {
            "firstName": {"type": "string"},
            "lastName": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 18, "maximum": 80},
            "salary": {"type": "number", "minimum": 30000, "maximum": 200000}
        }
    }
    
    print_subheader("With Faker (Realistic Data)")
    processor = SchemaProcessor(schema)
    samples = processor.generate_samples(count=3, use_faker=True)
    for i, sample in enumerate(samples, 1):
        print(f"Sample {i}: {json.dumps(sample, default=str)}")
    
    print_subheader("Without Faker (Random Data)")
    samples = processor.generate_samples(count=3, use_faker=False)
    for i, sample in enumerate(samples, 1):
        print(f"Sample {i}: {json.dumps(sample, default=str)}")


# =============================================================================
# EXAMPLE 20: MODULE GENERATION
# =============================================================================

def demo_module_generation():
    """Demonstrate module generation from schema folder."""
    print_header("EXAMPLE 20: MODULE GENERATION")
    
    examples_dir = Path(__file__).parent / "examples" / "schemas"
    output_dir = Path(__file__).parent / "demo_output"
    
    if not examples_dir.exists():
        print(f"Examples directory not found: {examples_dir}")
        print("Skipping module generation demo.")
        return
    
    # Clean up previous demo output
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    print_subheader("Generating Module from Schema Folder")
    print(f"Schema directory: {examples_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Module name: demo_models")
    
    try:
        result = generate_module(
            schema_dir=str(examples_dir),
            output_dir=str(output_dir),
            module_name="demo_models",
        )
        
        print(f"\n[OK] Module generation complete!")
        print(f"  Module name: {result['module_name']}")
        print(f"  Module path: {result['module_path']}")
        print(f"  Schemas processed: {result['schemas_processed']}")
        print(f"  Classes generated: {len(result['classes_generated'])}")
        print(f"  Files created: {len(result['files_created'])}")
        
        print("\n  Generated classes:")
        for class_name in sorted(result['classes_generated']):
            print(f"    - {class_name}")
        
        if result['errors']:
            print("\n  Errors:")
            for error in result['errors']:
                print(f"    - {error}")
        
        print("\n  Generated files structure:")
        module_path = Path(result['module_path'])
        for f in sorted(module_path.rglob("*.py"))[:20]:
            rel_path = f.relative_to(output_dir)
            print(f"    {rel_path}")
        
        print("\n  Usage:")
        print(f"    import sys")
        print(f"    sys.path.insert(0, '{output_dir}')")
        print(f"    from demo_models import User, load_json, to_json")
        print()
        print(f"  CLI:")
        print(f"    python -m demo_models list")
        print(f"    python -m demo_models sample User -o sample.json")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# EXAMPLE 21: WORKING WITH EXTERNAL SCHEMAS
# =============================================================================

def demo_external_schemas():
    """Demonstrate loading schemas from files."""
    print_header("EXAMPLE 21: LOADING EXTERNAL SCHEMAS")
    
    examples_dir = Path(__file__).parent / "examples" / "schemas"
    
    if not examples_dir.exists():
        print(f"Examples directory not found: {examples_dir}")
        return
    
    # List available schemas
    print_subheader("Available Example Schemas")
    schemas = sorted(examples_dir.glob("*.json"))
    for schema_path in schemas[:15]:
        print(f"  - {schema_path.name}")
    if len(schemas) > 15:
        print(f"  ... and {len(schemas) - 15} more")
    
    # Load and process a specific schema
    user_schema_path = examples_dir / "01_user.json"
    if user_schema_path.exists():
        print_subheader("Loading User Schema")
        schema = load_schema(user_schema_path)
        print(f"Schema: {schema.get('title', 'Untitled')}")
        print(f"Description: {schema.get('description', 'N/A')}")
        
        processor = SchemaProcessor(schema, root_class_name="User")
        
        print_subheader("Generated User Class")
        code = processor.generate_code()
        print_code(code, 50)
        
        print_subheader("Sample User Data")
        samples = processor.generate_samples(count=2)
        for i, sample in enumerate(samples, 1):
            print(f"Sample {i}:")
            print_json(sample, 20)


# =============================================================================
# EXAMPLE 22: RECURSIVE SCHEMAS
# =============================================================================

def demo_recursive_schemas():
    """Demonstrate handling of recursive schemas."""
    print_header("EXAMPLE 22: RECURSIVE SCHEMAS")
    
    # Tree structure
    schema = {
        "type": "object",
        "title": "TreeNode",
        "properties": {
            "id": {"type": "string"},
            "value": {"type": "string"},
            "children": {
                "type": "array",
                "items": {"$ref": "#"}
            }
        },
        "required": ["id", "value"]
    }
    
    print_subheader("Recursive Tree Schema")
    print_json(schema)
    
    processor = SchemaProcessor(schema, root_class_name="TreeNode")
    
    print_subheader("Generated Code")
    code = processor.generate_code()
    print_code(code, 40)
    
    # Linked list
    schema2 = {
        "type": "object",
        "title": "LinkedListNode",
        "properties": {
            "value": {"type": "integer"},
            "next": {
                "oneOf": [
                    {"$ref": "#"},
                    {"type": "null"}
                ]
            }
        },
        "required": ["value"]
    }
    
    print_subheader("Recursive Linked List Schema")
    print_json(schema2)


# =============================================================================
# EXAMPLE 23: COMPLEX NESTED STRUCTURES
# =============================================================================

def demo_complex_nested():
    """Demonstrate deeply nested structures."""
    print_header("EXAMPLE 23: COMPLEX NESTED STRUCTURES")
    
    schema = {
        "type": "object",
        "title": "Organization",
        "properties": {
            "name": {"type": "string"},
            "divisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "title": "Division",
                    "properties": {
                        "name": {"type": "string"},
                        "departments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "title": "Department",
                                "properties": {
                                    "name": {"type": "string"},
                                    "teams": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "title": "Team",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "lead": {"type": "string"},
                                                "members": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "title": "Member",
                                                        "properties": {
                                                            "id": {"type": "string"},
                                                            "name": {"type": "string"},
                                                            "role": {"type": "string"},
                                                            "skills": {
                                                                "type": "array",
                                                                "items": {"type": "string"}
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    print_subheader("Deeply Nested Organization Schema")
    print_json(schema, 60)
    
    processor = SchemaProcessor(schema, root_class_name="Organization")
    
    print_subheader("Generated Classes (Multiple Levels)")
    code = processor.generate_code()
    print_code(code, 80)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run all demonstrations."""
    print("=" * 78)
    print("  JsonSchemaCodeGen v{} - Comprehensive Demonstration".format(__version__))
    print("=" * 78)
    print("\nCopyright (C) 2025-2030, Ashutosh Sinha. All Rights Reserved.")
    print("This software is proprietary and confidential.\n")
    
    demos = [
        ("Basic Schema Processing", demo_basic_schema),
        ("Nested Objects", demo_nested_objects),
        ("Arrays and Collections", demo_arrays),
        ("String Formats and Patterns", demo_string_formats),
        ("Enums and Constants", demo_enums),
        ("Numeric Constraints", demo_numeric_constraints),
        ("AllOf (Composition)", demo_allof),
        ("OneOf (Union Types)", demo_oneof),
        ("AnyOf (Flexible Types)", demo_anyof),
        ("Definitions and References", demo_definitions),
        ("Additional Properties", demo_additional_properties),
        ("Conditional Schemas", demo_conditional),
        ("Complex E-Commerce Schema", demo_ecommerce),
        ("API Response Patterns", demo_api_response),
        ("Validation", demo_validation),
        ("Schema Validator", demo_schema_validator),
        ("Type Mapping", demo_type_mapper),
        ("Code Generator Options", demo_code_generator_options),
        ("Sample Generator Options", demo_sample_generator_options),
        ("Module Generation", demo_module_generation),
        ("External Schemas", demo_external_schemas),
        ("Recursive Schemas", demo_recursive_schemas),
        ("Complex Nested Structures", demo_complex_nested),
    ]
    
    print(f"Running {len(demos)} demonstrations...\n")
    
    successful = 0
    failed = 0
    
    for name, demo_func in demos:
        try:
            demo_func()
            successful += 1
        except Exception as e:
            print(f"\n[ERROR] Error during '{name}': {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print_header("DEMONSTRATION COMPLETE")
    print(f"Results: {successful} successful, {failed} failed")
    print(f"\nThank you for using JsonSchemaCodeGen!")
    print("\nFor more information, see:")
    print("  - README.md")
    print("  - docs/QUICKSTART.md")
    print("  - docs/ARCHITECTURE.md")
    print("  - docs/MODULE_GENERATOR.md")
    print("  - docs/EXAMPLES.md")
    print("\nTo generate modules from your schemas:")
    print("  python generate.py -s ./your_schemas -o ./output -m your_module")


if __name__ == "__main__":
    main()
