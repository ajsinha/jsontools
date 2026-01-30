# SchemaMap DSL Documentation

**Version:** 1.4.0  
**Copyright:** (C) 2025-2030, All Rights Reserved - Ashutosh Sinha

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [File Structure](#file-structure)
4. [Core Syntax](#core-syntax)
5. [Configuration](#configuration)
6. [Aliases](#aliases)
7. [Lookups](#lookups)
8. [Mappings](#mappings)
9. [Transform Functions](#transform-functions)
10. [Array Transformations](#array-transformations)
11. [Computed Fields](#computed-fields)
12. [Conditionals](#conditionals)
13. [Examples](#examples)
14. [CLI Usage](#cli-usage)
15. [Python API](#python-api)

---

## Overview

SchemaMap is a domain-specific language (DSL) for transforming JSON documents between different schemas. It provides a declarative, readable syntax for defining how fields from a source JSON structure should map to a target JSON structure.

### Key Features

- **Declarative Syntax**: Clear `source : target` mapping notation
- **Transform Chains**: Pipe-based function chaining (`| trim | lowercase`)
- **Reusable Aliases**: Define common transform patterns once
- **Lookup Tables**: Map codes to values with inline or external lookups
- **Array Support**: Transform arrays element-by-element
- **Computed Fields**: Generate values using expressions
- **Schema Validation**: Validate output against JSON Schema
- **No Code Required**: Pure configuration-driven transformations

---

## Quick Start

### 1. Create a Mapping File

```
# my_mapping.smap

@config {
    null_handling : omit
}

# Map fields
user.first_name         : firstName | trim | titlecase
user.last_name          : lastName | trim | titlecase
user.email              : contactEmail | lowercase
user.age                : age | to_int
```

### 2. Run the Transformation

```bash
python transform.py my_mapping.smap input.json --output result.json
```

### 3. Or Use Python API

```python
from jsontools.transformation import transform

result = transform(source_data, "my_mapping.smap")
```

---

## File Structure

A SchemaMap file (`.smap`) consists of these sections:

```
# Comments start with #

@config {
    # Configuration options
}

@aliases {
    # Reusable transform chains
}

@lookups {
    # Lookup tables for code mappings
}

# Mappings
source.path : target.path | transforms
```

All sections except mappings are optional.

---

## Core Syntax

### Basic Mapping

```
source_path : target_path
```

The colon (`:`) separates source from target and reads as "maps to".

### With Transforms

```
source_path : target_path | transform1 | transform2
```

Transforms are chained with the pipe operator (`|`).

### Examples

```
user.name           : fullName              # Simple mapping
user.email          : contact.email         # Nested target
user.age            : age | to_int          # With transform
user.status         : status | uppercase    # String transform
```

---

## Configuration

The `@config` block sets transformation behavior:

```
@config {
    null_handling    : omit      # omit, keep, or default
    missing_fields   : skip      # skip, error, or default
    date_format      : "ISO8601" # Date format hint
    strict_mode      : false     # Enable strict validation
}
```

### Options

| Option | Values | Description |
|--------|--------|-------------|
| `null_handling` | `omit`, `keep` | How to handle null values |
| `missing_fields` | `skip`, `error` | Handle missing source fields |
| `date_format` | String | Default date format |
| `strict_mode` | Boolean | Enable strict validation |

---

## Aliases

Aliases define reusable transform chains:

```
@aliases {
    # Simple alias
    Clean : trim | max_length(255)
    
    # Multiple transforms
    Email : trim | lowercase | validate("email")
    
    # Numeric transforms
    Money : to_float | round(2)
    
    # With parameters (future)
    Phone(country) : trim | normalize_phone(country)
}
```

### Using Aliases

Reference aliases with `@` prefix:

```
user.name           : fullName | @Clean
user.email          : contactEmail | @Email
account.balance     : balance | @Money
```

---

## Lookups

Lookups map codes to values:

### Inline Lookups

```
@lookups {
    status_codes : {
        "A" : "ACTIVE",
        "I" : "INACTIVE",
        "S" : "SUSPENDED"
    }
    
    country_names : {
        "US" : "United States",
        "UK" : "United Kingdom",
        "CA" : "Canada"
    }
}
```

### External File Lookups (Future)

```
@lookups {
    countries : "lookups/countries.json"
}
```

### Using Lookups

```
user.status         : status | lookup(@status_codes)
user.country        : countryName | lookup(@country_names)
```

---

## Mappings

### Simple Field Mapping

```
source.field : target.field
```

### Nested Paths

```
user.address.city : location.city
user.contact.email : emails.primary
```

### Optional Fields

Use `?` for optional source fields:

```
user.middle_name? : middleName
```

### Array Access

```
users[0]            : firstUser           # First element
users[-1]           : lastUser            # Last element
users[*]            : allUsers            # All elements
```

### Constants

```
"1.0"               : version | constant
42                  : magicNumber | constant
```

### Field Concatenation

```
user.first_name + " " + user.last_name : fullName
```

### Coalescing

```
user.mobile ?? user.home_phone : primaryPhone
```

---

## Transform Functions

### String Functions

| Function | Args | Description |
|----------|------|-------------|
| `trim` | - | Remove whitespace |
| `lowercase` | - | Convert to lowercase |
| `uppercase` | - | Convert to uppercase |
| `titlecase` | - | Capitalize words |
| `capitalize` | - | Capitalize first letter |
| `replace(old, new)` | 2 | Replace substring |
| `regex_replace(pattern, replacement)` | 2 | Regex replace |
| `substring(start, end)` | 1-2 | Extract substring |
| `prefix(str)` | 1 | Add prefix |
| `suffix(str)` | 1 | Add suffix |
| `max_length(n)` | 1 | Truncate to length |
| `split(delimiter)` | 1 | Split into array |
| `join(delimiter)` | 1 | Join array to string |
| `collapse_spaces` | - | Collapse multiple spaces |

### Numeric Functions

| Function | Args | Description |
|----------|------|-------------|
| `to_int` | - | Convert to integer |
| `to_float` | - | Convert to float |
| `round(decimals)` | 0-1 | Round to decimals |
| `floor` | - | Round down |
| `ceil` | - | Round up |
| `abs` | - | Absolute value |
| `multiply(n)` | 1 | Multiply by n |
| `divide(n)` | 1 | Divide by n |
| `add(n)` | 1 | Add n |
| `subtract(n)` | 1 | Subtract n |
| `clamp(min, max)` | 2 | Clamp to range |

### Boolean Functions

| Function | Args | Description |
|----------|------|-------------|
| `to_bool` | - | Convert to boolean |
| `negate` | - | Logical NOT |

### Date Functions

| Function | Args | Description |
|----------|------|-------------|
| `parse_date(format)` | 1 | Parse date string |
| `format_date(format)` | 1 | Format date |
| `to_iso8601` | - | Convert to ISO format |
| `add_days(n)` | 1 | Add days |
| `add_months(n)` | 1 | Add months |
| `add_years(n)` | 1 | Add years |

### Array Functions

| Function | Args | Description |
|----------|------|-------------|
| `first` | - | Get first element |
| `last` | - | Get last element |
| `at(index)` | 1 | Get element at index |
| `flatten` | - | Flatten nested arrays |
| `distinct` | - | Remove duplicates |
| `sort` | - | Sort array |
| `reverse` | - | Reverse array |
| `take(n)` | 1 | Take first n elements |
| `skip(n)` | 1 | Skip first n elements |
| `count` | - | Count elements |
| `sum` | - | Sum numeric values |
| `avg` | - | Average of values |
| `wrap` | - | Wrap in array |

### Conditional Functions

| Function | Args | Description |
|----------|------|-------------|
| `default(value)` | 1 | Default if null |
| `if_empty(value)` | 1 | Default if empty |
| `when(match, result)` | 2 | Map specific value |
| `else(value)` | 1 | Default for when chain |

### Special Functions

| Function | Args | Description |
|----------|------|-------------|
| `constant` | - | Mark as constant |
| `lookup(table)` | 1 | Lookup in table |
| `mask(visible)` | 0-1 | Mask sensitive data |
| `hash(algorithm)` | 0-1 | Hash value |
| `validate(type)` | 1 | Validate format |

---

## Array Transformations

### Element-by-Element Mapping

```
users[*].name       : persons[*].fullName | titlecase
users[*].age        : persons[*].age | to_int
users[*].email      : persons[*].contact | lowercase
```

### Complete Example

Source:
```json
{
  "users": [
    {"name": "JOHN", "age": "30"},
    {"name": "JANE", "age": "25"}
  ]
}
```

Mapping:
```
users[*].name : people[*].displayName | titlecase
users[*].age  : people[*].yearsOld | to_int
```

Target:
```json
{
  "people": [
    {"displayName": "John", "yearsOld": 30},
    {"displayName": "Jane", "yearsOld": 25}
  ]
}
```

---

## Computed Fields

### Using @compute

```
@compute(sum(items[*].price))           : totalPrice
@compute(count(items))                  : itemCount
@compute(items[0].price * items[0].qty) : firstLineTotal
```

### Using @now and @uuid

```
@now    : transformedAt    # Current timestamp
@uuid   : transactionId    # Generate UUID
```

---

## Conditionals

### When/Else Chains

```
status : displayStatus
    | when("A", "Active")
    | when("I", "Inactive")
    | when("S", "Suspended")
    | else("Unknown")
```

### Conditional Blocks (Future)

```
@when type == "business" {
    company_name : name
    tax_id : businessId
}
@else {
    first_name + " " + last_name : name
    ssn : personalId
}
```

---

## Examples

### Example 1: User Profile Transformation

Source:
```json
{
  "user": {
    "first_name": "JOHN",
    "last_name": "DOE",
    "email": "JOHN.DOE@EXAMPLE.COM",
    "status": "A"
  }
}
```

Mapping:
```
@config {
    null_handling : omit
}

@lookups {
    status_map : {
        "A" : "ACTIVE",
        "I" : "INACTIVE"
    }
}

user.first_name + " " + user.last_name : fullName | trim | titlecase
user.email              : contactEmail | lowercase
user.status             : status | lookup(@status_map)
@now                    : transformedAt
```

Target:
```json
{
  "fullName": "John Doe",
  "contactEmail": "john.doe@example.com",
  "status": "ACTIVE",
  "transformedAt": "2025-01-30T12:00:00Z"
}
```

### Example 2: Order Transformation

Source:
```json
{
  "order_id": "ORD-001",
  "items": [
    {"sku": "ITEM-1", "qty": 2, "price": 10.50},
    {"sku": "ITEM-2", "qty": 1, "price": 25.00}
  ],
  "customer": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

Mapping:
```
@aliases {
    Money : to_float | round(2)
}

order_id                    : orderId
items[*].sku               : lineItems[*].productCode
items[*].qty               : lineItems[*].quantity | to_int
items[*].price             : lineItems[*].unitPrice | @Money
customer.name              : buyer.fullName
customer.email             : buyer.email | lowercase
@compute(count(items))     : summary.itemCount
@compute(sum(items[*].price)) : summary.subtotal | @Money
```

---

## CLI Usage

### Basic Transformation

```bash
python transform.py mapping.smap input.json
```

### With Schema Validation

```bash
python transform.py mapping.smap input.json --schema target_schema.json
```

### Save to File

```bash
python transform.py mapping.smap input.json --output result.json
```

### Verbose Mode

```bash
python transform.py mapping.smap input.json --verbose
```

### Full Options

```bash
python transform.py mapping.smap input.json \
    --schema schema.json \
    --output result.json \
    --verbose
```

---

## Python API

### Simple Transform

```python
from jsontools.transformation import transform

source = {"user": {"name": "John", "age": "30"}}
result = transform(source, "mapping.smap")
```

### With Validation

```python
from jsontools.transformation import transform

result = transform(
    source_data,
    "mapping.smap",
    validate_schema="target_schema.json"
)
```

### Load and Reuse Transformer

```python
from jsontools.transformation import load_mapping

transformer = load_mapping("mapping.smap")

result1 = transformer.transform(data1)
result2 = transformer.transform(data2)
result3 = transformer.transform(data3)
```

### Batch Transform

```python
transformer = load_mapping("mapping.smap")

results = transformer.transform_batch([data1, data2, data3])
```

### Compile to Python Code

```python
from jsontools.transformation import compile_mapping

code = compile_mapping("mapping.smap")
with open("generated_transformer.py", "w") as f:
    f.write(code)
```

---

## Best Practices

1. **Use Aliases**: Define common transform patterns as aliases
2. **Document Mappings**: Add comments to explain complex mappings
3. **Validate Output**: Always validate against target schema
4. **Handle Optionals**: Mark optional fields with `?`
5. **Use Lookups**: Centralize code-to-value mappings
6. **Test Incrementally**: Build and test mappings step by step

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Expected ':'` | Missing colon in mapping | Add `:` between source and target |
| `Expected value` | Invalid value in config | Check syntax |
| `Lookup not found` | Unknown lookup reference | Define lookup in @lookups |
| `Validation failed` | Output doesn't match schema | Check mapping produces correct types |

---

## Version History

- **1.4.0**: Initial SchemaMap module release
  - Core DSL parser and transformer
  - 50+ built-in transform functions
  - Alias and lookup support
  - JSON Schema validation
  - CLI and Python API

---

*For more information, see the examples in `examples/transformation/`*

---

## External Python Functions (NEW in v1.4.0)

SchemaMap supports calling external Python functions for custom transformation logic that goes beyond built-in transforms.

### Registering Functions via Python API

```python
from jsontools.transformation import load_mapping

# Define custom functions
def calculate_tax(amount, rate=0.08):
    return round(float(amount) * float(rate), 2)

def format_currency(amount, symbol="$"):
    return f"{symbol}{float(amount):,.2f}"

# Load mapping and register functions
transformer = load_mapping("mapping.smap")
transformer.register_function("calculate_tax", calculate_tax)
transformer.register_function("format_currency", format_currency)

# Transform with custom functions available
result = transformer.transform(source_data)
```

### Registering Multiple Functions

```python
# Register multiple at once
transformer.register_functions({
    "calculate_tax": calculate_tax,
    "format_currency": format_currency,
    "validate_email": lambda e: "@" in e
})

# Or from a module
transformer.register_module("my_transforms")

# Or from a file
transformer.register_file("custom_functions.py")
```

### Using Functions in SchemaMap DSL

#### Using @compute

```
# Call function with field values
@compute(calculate_tax(order.subtotal, 0.08)) : order.tax

# Nested function calls
@compute(format_currency(calculate_total(subtotal, tax), "USD")) : displayTotal

# Multiple arguments from fields
@compute(format_full_name(person.firstName, person.lastName)) : person.fullName
```

#### Using @call (Explicit Syntax)

```
# Explicit function call syntax
@call(calculate_tax, order.subtotal, 0.08) : order.tax

# With field references
@call(format_phone, contact.phone, "US") : contact.formattedPhone
```

### @functions Block (Declarative Registration)

Register functions directly in the .smap file:

```
@functions {
    calc_tax    : "my_module:calculate_tax"
    fmt_phone   : "utils.formatters:format_phone"
    validate    : "validators:validate_email as check_email"
}
```

Format: `name : "module.path:function_name"`

### @config Function Loading

```
@config {
    null_handling    : omit
    functions_module : "my_transforms"
    functions_file   : "path/to/custom_functions.py"
}
```

### Creating Custom Function Files

Create a Python file with your functions:

```python
# custom_functions.py

def calculate_tax(amount, rate=0.08):
    """Calculate tax amount."""
    return round(float(amount) * float(rate), 2)

def format_currency(amount, currency="USD"):
    """Format as currency string."""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, currency + " ")
    return f"{symbol}{float(amount):,.2f}"

def calculate_age(birth_date):
    """Calculate age from birth date."""
    from datetime import datetime, date
    bd = datetime.fromisoformat(birth_date).date()
    today = date.today()
    return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

def format_phone(phone, country="US"):
    """Format phone number."""
    import re
    digits = re.sub(r'\D', '', str(phone))
    if country == "US" and len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone
```

### CLI with External Functions

```bash
# Load functions from file
python transform.py mapping.smap input.json --functions custom_functions.py

# List registered functions
python transform.py mapping.smap input.json --functions custom_functions.py --list-functions
```

### Complete Example

**custom_funcs.py:**
```python
def calculate_order_total(subtotal, tax_rate, shipping):
    tax = round(float(subtotal) * float(tax_rate), 2)
    return round(float(subtotal) + tax + float(shipping), 2)

def generate_confirmation_code(order_id):
    import hashlib
    return hashlib.md5(str(order_id).encode()).hexdigest()[:8].upper()
```

**order_mapping.smap:**
```
@config {
    null_handling : omit
}

order.id                                        : orderId
order.items[*].price                           : items[*].unitPrice | to_float

# Use custom functions
@compute(calculate_order_total(order.subtotal, 0.08, order.shipping)) : totals.grandTotal
@compute(generate_confirmation_code(order.id))  : confirmationCode

@now                                            : processedAt
```

**Python:**
```python
from jsontools.transformation import load_mapping

transformer = load_mapping("order_mapping.smap")
transformer.register_file("custom_funcs.py")

result = transformer.transform({
    "order": {
        "id": "ORD-12345",
        "subtotal": 100.00,
        "shipping": 5.99,
        "items": [{"price": "50.00"}, {"price": "50.00"}]
    }
})

print(result)
# {
#   "orderId": "ORD-12345",
#   "items": [{"unitPrice": 50.0}, {"unitPrice": 50.0}],
#   "totals": {"grandTotal": 113.99},
#   "confirmationCode": "7E3B8F2A",
#   "processedAt": "2025-01-30T12:00:00Z"
# }
```

### Best Practices for External Functions

1. **Keep functions pure** - No side effects, same input always produces same output
2. **Handle None/null** - Functions should gracefully handle missing values
3. **Type conversion** - Convert inputs to expected types (float, int, str)
4. **Return appropriate types** - Return types that serialize to JSON
5. **Error handling** - Wrap operations in try/except to avoid transformation failures
6. **Documentation** - Add docstrings describing usage and arguments

### Function Naming

Avoid these reserved names which conflict with built-ins:
- `sum`, `count`, `avg`, `min`, `max`
- `len`, `abs`, `round`, `int`, `float`, `str`, `bool`

Use descriptive names like `calculate_tax`, `format_currency`, `validate_email`.


---

## Code Compilation (NEW in v1.4.0)

SchemaMap can compile `.smap` files to optimized, standalone Python code that runs 5-10x faster than interpreted transformations.

### Why Compile?

| Aspect | Interpreted | Compiled |
|--------|-------------|----------|
| Speed | ~8,000 ops/sec | ~40,000 ops/sec |
| Startup | Fast (no compile) | Requires compile step |
| Debugging | Easy | Harder |
| Dependencies | Requires runtime | Standalone |
| Use case | Development | Production |

### Compiling SchemaMap

```bash
# Basic compilation
python transform.py --compile mapping.smap

# With custom output path and class name
python transform.py --compile mapping.smap \
    -o my_transformer.py \
    --class-name CustomerTransformer
```

### Using Compiled Code

The generated Python file is standalone and can be used directly:

```python
# Import the generated transformer
from my_transformer import CustomerTransformer

# Create instance
transformer = CustomerTransformer()

# Register external functions (if any)
transformer.register_function("calculate_tax", lambda x, r: x * r)

# Transform data
result = transformer.transform(source_data)

# Batch transformation
results = transformer.transform_batch(items)
```

### Generated Code Structure

```python
class CustomerTransformer:
    def __init__(self):
        self._lookups = {...}  # Inlined lookup tables
        self._external_functions = {}
    
    def register_function(self, name, func):
        """Register external function."""
        ...
    
    def transform(self, source: Dict) -> Dict:
        """Transform single item."""
        ...
    
    def transform_batch(self, items: List[Dict]) -> List[Dict]:
        """Transform multiple items."""
        ...
```

### Benchmarking

Compare interpreted vs compiled performance:

```bash
python transform.py --benchmark mapping.smap input.json --iterations 20000
```

Output:
```
============================================================
  BENCHMARK RESULTS
============================================================

  Interpreted Transformer:
    Total time:     2.5230 seconds
    Ops/second:     7,927
    μs/operation:   126.15

  Compiled Transformer:
    Total time:     0.4850 seconds
    Ops/second:     41,236
    μs/operation:   24.25

  --------------------------------------------------------
  SPEEDUP: 5.2x faster with compiled code!
============================================================
```

### Optimization Techniques

The compiled code is faster because:

1. **No parsing** - DSL is pre-parsed at compile time
2. **Inlined transforms** - Functions become inline expressions
3. **Inlined lookups** - Lookup tables embedded in code
4. **No runtime dispatch** - Direct Python execution
5. **Bytecode optimization** - Python compiler optimizes further

### Workflow Recommendations

**Development:**
```bash
# Use interpreted for quick iteration
python transform.py mapping.smap input.json
```

**Production:**
```bash
# Compile once, run many times
python transform.py --compile mapping.smap -o transformer.py

# Deploy transformer.py with your application
```

**CI/CD:**
```bash
# Compile during build
python transform.py --compile mappings/*.smap

# Run tests with compiled transformers
python -m pytest
```
