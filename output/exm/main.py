"""
Main Module - Utility Functions for JSON/Class Operations

Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
Generated at: 2026-01-29T13:36:20.833353

This module provides high-level utility functions for:
- Loading JSON files and parsing into class instances
- Creating class instances and saving to JSON
- Generating sample data
- Converting between formats

Usage:
    from exm.main import load_and_parse, create_and_save, generate_sample
    
    # Load JSON file into a class instance
    user = load_and_parse("user.json", "User")
    
    # Create instance and save to JSON
    create_and_save("User", "output.json", name="John", email="john@example.com")
    
    # Generate sample data
    sample = generate_sample("User")
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import fields, is_dataclass
import random
import string
from datetime import datetime, date
from uuid import uuid4

from .driver import (
    load_json,
    load_json_file,
    load_dict,
    to_json,
    to_json_file,
    to_json_string,
    to_dict,
    list_classes,
    get_class_info,
    create_instance,
    validate_data,
)
from .generated import CLASS_REGISTRY, get_class


# ============================================================================
# HIGH-LEVEL UTILITY FUNCTIONS
# ============================================================================

def load_and_parse(
    file_path: Union[str, Path],
    class_name: str,
    verbose: bool = False,
) -> Any:
    """
    Load a JSON file and parse it into a class instance.
    
    Args:
        file_path: Path to the JSON file
        class_name: Name of the target class
        verbose: Print progress information
        
    Returns:
        Instance of the specified class
        
    Example:
        user = load_and_parse("data/user.json", "User")
        print(user.name)
    """
    if verbose:
        print(f"Loading {file_path} as {class_name}...")
    
    instance = load_json(file_path, class_name)
    
    if verbose:
        print(f"Successfully loaded {class_name} instance")
    
    return instance


def create_and_save(
    class_name: str,
    output_path: Union[str, Path],
    indent: int = 2,
    verbose: bool = False,
    **kwargs,
) -> Any:
    """
    Create a class instance and save it to a JSON file.
    
    Args:
        class_name: Name of the class to instantiate
        output_path: Path for the output JSON file
        indent: JSON indentation
        verbose: Print progress information
        **kwargs: Field values for the instance
        
    Returns:
        The created instance
        
    Example:
        user = create_and_save(
            "User",
            "output/user.json",
            name="John Doe",
            email="john@example.com"
        )
    """
    if verbose:
        print(f"Creating {class_name} instance...")
    
    instance = create_instance(class_name, **kwargs)
    
    if verbose:
        print(f"Saving to {output_path}...")
    
    to_json_file(instance, output_path, indent=indent)
    
    if verbose:
        print(f"Successfully saved {class_name} to {output_path}")
    
    return instance


def generate_sample(
    class_name: str,
    seed: Optional[int] = None,
) -> Any:
    """
    Generate a sample instance of a class with random data.
    
    Args:
        class_name: Name of the class
        seed: Random seed for reproducibility
        
    Returns:
        Instance with sample data
        
    Example:
        sample_user = generate_sample("User")
        print(sample_user.name)
    """
    if seed is not None:
        random.seed(seed)
    
    target_class = get_class(class_name)
    if target_class is None:
        raise ValueError(f"Unknown class: {class_name}. Available: {list_classes()}")
    
    if not is_dataclass(target_class):
        raise TypeError(f"{class_name} is not a dataclass")
    
    sample_data = {}
    for field in fields(target_class):
        sample_data[field.name] = _generate_sample_value(field.type, field.name)
    
    return target_class(**sample_data)


def _generate_sample_value(field_type: Any, field_name: str) -> Any:
    """Generate a sample value for a field."""
    origin = getattr(field_type, '__origin__', None)
    
    # Handle Optional
    if origin is Union:
        args = field_type.__args__
        non_none = [t for t in args if t is not type(None)]
        if non_none:
            field_type = non_none[0]
            origin = getattr(field_type, '__origin__', None)
        else:
            return None
    
    # Handle List
    if origin is list:
        item_type = field_type.__args__[0] if field_type.__args__ else str
        return [_generate_sample_value(item_type, field_name) for _ in range(random.randint(1, 3))]
    
    # Handle Dict
    if origin is dict:
        return {"key": "value"}
    
    # Handle basic types
    name_lower = field_name.lower()
    
    if field_type is str or field_type == 'str':
        if 'email' in name_lower:
            return f"user{random.randint(1, 999)}@example.com"
        elif 'name' in name_lower:
            return random.choice(["John", "Jane", "Bob", "Alice", "Charlie", "Diana"])
        elif 'id' in name_lower or 'uuid' in name_lower:
            return str(uuid4())
        elif 'url' in name_lower or 'uri' in name_lower:
            return "https://example.com/resource"
        elif 'phone' in name_lower:
            return f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        elif 'address' in name_lower:
            return f"{random.randint(1, 999)} Main Street"
        elif 'city' in name_lower:
            return random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"])
        elif 'country' in name_lower:
            return random.choice(["US", "UK", "CA", "AU", "DE", "FR"])
        elif 'title' in name_lower:
            return f"Sample Title {random.randint(1, 100)}"
        elif 'description' in name_lower:
            return "This is a sample description for testing purposes."
        else:
            return ''.join(random.choices(string.ascii_letters, k=10))
    
    if field_type is int or field_type == 'int':
        if 'age' in name_lower:
            return random.randint(18, 80)
        elif 'year' in name_lower:
            return random.randint(2020, 2025)
        elif 'count' in name_lower or 'quantity' in name_lower:
            return random.randint(1, 100)
        elif 'price' in name_lower or 'amount' in name_lower:
            return random.randint(1, 10000)
        else:
            return random.randint(1, 1000)
    
    if field_type is float or field_type == 'float':
        if 'price' in name_lower or 'amount' in name_lower:
            return round(random.uniform(1.0, 1000.0), 2)
        elif 'rate' in name_lower or 'percentage' in name_lower:
            return round(random.uniform(0.0, 100.0), 2)
        else:
            return round(random.uniform(0.0, 100.0), 2)
    
    if field_type is bool or field_type == 'bool':
        return random.choice([True, False])
    
    if field_type is datetime:
        return datetime.now()
    
    if field_type is date:
        return date.today()
    
    # Handle nested dataclass
    if is_dataclass(field_type):
        nested_data = {}
        for f in fields(field_type):
            nested_data[f.name] = _generate_sample_value(f.type, f.name)
        return field_type(**nested_data)
    
    # Default
    return None


def convert_json(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    class_name: str,
    indent: int = 2,
    verbose: bool = False,
) -> Any:
    """
    Load JSON, parse to class, and save back (useful for validation/normalization).
    
    Args:
        input_path: Input JSON file path
        output_path: Output JSON file path
        class_name: Name of the class
        indent: JSON indentation
        verbose: Print progress
        
    Returns:
        The parsed instance
        
    Example:
        # Validate and normalize JSON through the class
        user = convert_json("input.json", "output.json", "User")
    """
    if verbose:
        print(f"Loading {input_path}...")
    
    instance = load_json(input_path, class_name)
    
    if verbose:
        print(f"Saving to {output_path}...")
    
    to_json_file(instance, output_path, indent=indent)
    
    if verbose:
        print(f"Successfully converted {class_name}")
    
    return instance


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def run_cli(args: Optional[List[str]] = None) -> int:
    """
    Run the command-line interface.
    
    Args:
        args: Command-line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(
        prog="exm",
        description="Generated Data Models - Load, create, and manipulate JSON data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  List available classes:
    python -m exm list
    
  Show class info:
    python -m exm info User
    
  Load and display JSON:
    python -m exm load user.json User
    
  Generate sample data:
    python -m exm sample User
    python -m exm sample User -o sample_user.json
    
  Validate JSON against class:
    python -m exm validate user.json User

Copyright © 2025-2030, Ashutosh Sinha. All Rights Reserved.
""",
    )
    
    parser.add_argument("--version", action="version", version="1.0.0")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available classes")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show class information")
    info_parser.add_argument("class_name", help="Name of the class")
    
    # Load command
    load_parser = subparsers.add_parser("load", help="Load and display JSON file")
    load_parser.add_argument("file", help="JSON file to load")
    load_parser.add_argument("class_name", help="Name of the class")
    load_parser.add_argument("-o", "--output", help="Output file (optional)")
    
    # Sample command
    sample_parser = subparsers.add_parser("sample", help="Generate sample data")
    sample_parser.add_argument("class_name", help="Name of the class")
    sample_parser.add_argument("-o", "--output", help="Output file (optional)")
    sample_parser.add_argument("-n", "--count", type=int, default=1, help="Number of samples")
    sample_parser.add_argument("--seed", type=int, help="Random seed")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate JSON against class")
    validate_parser.add_argument("file", help="JSON file to validate")
    validate_parser.add_argument("class_name", help="Name of the class")
    
    parsed = parser.parse_args(args)
    
    if parsed.command is None:
        parser.print_help()
        return 0
    
    try:
        if parsed.command == "list":
            print("Available classes:")
            for name in sorted(list_classes()):
                print(f"  - {name}")
            return 0
        
        elif parsed.command == "info":
            info = get_class_info(parsed.class_name)
            if info is None:
                print(f"Unknown class: {parsed.class_name}")
                return 1
            print(f"Class: {info['name']}")
            print(f"Docstring: {info['docstring'] or 'N/A'}")
            print("Fields:")
            for f in info['fields']:
                req = " (required)" if f.get('required') else ""
                print(f"  - {f['name']}: {f['type']}{req}")
            return 0
        
        elif parsed.command == "load":
            instance = load_and_parse(parsed.file, parsed.class_name, verbose=True)
            json_str = to_json_string(instance)
            if parsed.output:
                with open(parsed.output, "w") as f:
                    f.write(json_str)
                print(f"Saved to {parsed.output}")
            else:
                print(json_str)
            return 0
        
        elif parsed.command == "sample":
            samples = []
            for i in range(parsed.count):
                seed = parsed.seed + i if parsed.seed else None
                samples.append(generate_sample(parsed.class_name, seed=seed))
            
            if parsed.count == 1:
                json_str = to_json_string(samples[0])
            else:
                json_str = json.dumps([to_dict(s) for s in samples], indent=2, default=str)
            
            if parsed.output:
                with open(parsed.output, "w") as f:
                    f.write(json_str)
                print(f"Generated {parsed.count} sample(s) to {parsed.output}")
            else:
                print(json_str)
            return 0
        
        elif parsed.command == "validate":
            with open(parsed.file, "r") as f:
                data = json.load(f)
            result = validate_data(data, parsed.class_name)
            if result["valid"]:
                print(f"✓ {parsed.file} is valid for {parsed.class_name}")
            else:
                print(f"✗ {parsed.file} has errors:")
                for err in result["errors"]:
                    print(f"  - {err}")
            return 0 if result["valid"] else 1
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
