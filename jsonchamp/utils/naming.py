"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Naming Utilities - Convert names between different conventions.
"""

import re
from typing import Set

# Python reserved keywords
PYTHON_KEYWORDS: Set[str] = {
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else", "except",
    "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
    "while", "with", "yield",
}

# Python built-in names to avoid
PYTHON_BUILTINS: Set[str] = {
    "id", "type", "list", "dict", "set", "str", "int", "float", "bool",
    "tuple", "object", "input", "print", "open", "file", "format",
    "hash", "help", "len", "max", "min", "next", "range", "sum",
}


def to_snake_case(name: str) -> str:
    """
    Convert a name to snake_case.
    
    Args:
        name: Input name (any format)
        
    Returns:
        Name in snake_case
        
    Examples:
        >>> to_snake_case("MyClassName")
        'my_class_name'
        >>> to_snake_case("my-property-name")
        'my_property_name'
    """
    # Handle already snake_case
    if "_" in name and name.islower():
        return name
    
    # Replace hyphens and spaces with underscores
    name = name.replace("-", "_").replace(" ", "_")
    
    # Insert underscore before uppercase letters
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove consecutive underscores
    name = re.sub(r"_+", "_", name)
    
    # Remove leading/trailing underscores
    name = name.strip("_")
    
    return name


def to_pascal_case(name: str) -> str:
    """
    Convert a name to PascalCase.
    
    Args:
        name: Input name (any format)
        
    Returns:
        Name in PascalCase
        
    Examples:
        >>> to_pascal_case("my_class_name")
        'MyClassName'
        >>> to_pascal_case("my-property-name")
        'MyPropertyName'
    """
    # Split on separators
    words = re.split(r"[-_\s]+", name)
    
    # Handle already PascalCase
    if not words or (len(words) == 1 and name[0].isupper()):
        # Still need to handle cases like "XMLParser"
        words = re.findall(r"[A-Z][a-z]*|[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+", name)
    
    # Capitalize each word
    return "".join(word.capitalize() for word in words if word)


def to_camel_case(name: str) -> str:
    """
    Convert a name to camelCase.
    
    Args:
        name: Input name (any format)
        
    Returns:
        Name in camelCase
        
    Examples:
        >>> to_camel_case("my_class_name")
        'myClassName'
    """
    pascal = to_pascal_case(name)
    if pascal:
        return pascal[0].lower() + pascal[1:]
    return ""


def to_safe_identifier(name: str, style: str = "snake") -> str:
    """
    Convert a name to a safe Python identifier.
    
    Args:
        name: Input name
        style: Output style ("snake", "pascal", "camel")
        
    Returns:
        Safe Python identifier
        
    Examples:
        >>> to_safe_identifier("class")
        'class_'
        >>> to_safe_identifier("123abc")
        '_123abc'
    """
    # Convert to requested style
    if style == "pascal":
        name = to_pascal_case(name)
    elif style == "camel":
        name = to_camel_case(name)
    else:
        name = to_snake_case(name)
    
    # Replace invalid characters
    name = re.sub(r"[^\w]", "_", name)
    
    # Ensure doesn't start with digit
    if name and name[0].isdigit():
        name = "_" + name
    
    # Handle empty name
    if not name:
        name = "_unnamed"
    
    # Handle Python keywords
    if name in PYTHON_KEYWORDS:
        name = name + "_"
    
    # Optionally handle built-ins
    if name in PYTHON_BUILTINS:
        name = name + "_"
    
    return name


def pluralize(name: str) -> str:
    """
    Simple pluralization of a name.
    
    Args:
        name: Singular name
        
    Returns:
        Pluralized name
    """
    if name.endswith("s") or name.endswith("x") or name.endswith("z"):
        return name + "es"
    elif name.endswith("y") and len(name) > 1 and name[-2] not in "aeiou":
        return name[:-1] + "ies"
    else:
        return name + "s"


def singularize(name: str) -> str:
    """
    Simple singularization of a name.
    
    Args:
        name: Plural name
        
    Returns:
        Singularized name
    """
    if name.endswith("ies"):
        return name[:-3] + "y"
    elif name.endswith("es"):
        return name[:-2]
    elif name.endswith("s") and not name.endswith("ss"):
        return name[:-1]
    return name
