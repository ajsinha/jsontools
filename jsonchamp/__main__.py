#!/usr/bin/env python3
"""
JsonSchemaCodeGen - Main Entry Point and CLI

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder. This software
is provided "as is" without warranty of any kind.

Patent Pending: Certain architectural patterns and implementations
described herein may be subject to patent applications.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from jsonchamp import (
    SchemaProcessor,
    generate_classes,
    generate_samples,
    generate_code,
    generate_module,
    __version__,
)
from jsonchamp.core import SchemaValidator
from jsonchamp.utils import load_schema, save_code


def print_banner():
    """Print the application banner."""
    banner = f"""
+==================================================================+
|                     JsonSchemaCodeGen v{__version__}                      |
|                                                                  |
|  Commercial Grade JSON Schema to Python Code Generator           |
|                                                                  |
|  Copyright (C) 2025-2030, All Rights Reserved                      |
|  Ashutosh Sinha (ajsinha@gmail.com)                              |
+==================================================================+
"""
    print(banner)


def cmd_generate_classes(args):
    """Generate Python classes from schema."""
    schema = load_schema(args.schema)
    processor = SchemaProcessor(schema, root_class_name=args.class_name)
    
    code = processor.generate_code(style="dataclass")
    
    if args.output:
        save_code(code, args.output)
        print(f"[OK] Generated code saved to: {args.output}")
    else:
        print(code)


def cmd_generate_module(args):
    """Generate Python module from schema folder."""
    result = generate_module(
        schema_dir=args.schema_dir,
        output_dir=args.output_dir,
        module_name=args.module_name,
        overwrite=True,
    )
    
    print(f"[OK] Module generation complete!")
    print(f"  Schemas processed: {result['schemas_processed']}")
    print(f"  Classes generated: {len(result['classes_generated'])}")
    
    if result['classes_generated']:
        print(f"\n  Generated classes:")
        for name in sorted(result['classes_generated'])[:10]:
            print(f"    - {name}")
        if len(result['classes_generated']) > 10:
            print(f"    ... and {len(result['classes_generated']) - 10} more")
    
    if result['errors']:
        print(f"\n  Errors:")
        for err in result['errors']:
            print(f"    [ERROR] {err}")


def cmd_generate_samples(args):
    """Generate sample JSON data from schema."""
    schema = load_schema(args.schema)
    processor = SchemaProcessor(schema)
    
    samples = processor.generate_samples(
        count=args.count,
        use_faker=not args.no_faker,
    )
    
    output = json.dumps(samples, indent=2, default=str)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"[OK] Generated {args.count} sample(s) saved to: {args.output}")
    else:
        print(output)


def cmd_validate(args):
    """Validate a schema or data against a schema."""
    schema = load_schema(args.schema)
    
    if args.data:
        with open(args.data, "r") as f:
            data = json.load(f)
        
        processor = SchemaProcessor(schema)
        result = processor.validate_data(data)
    else:
        validator = SchemaValidator()
        result = validator.validate_schema(schema)
    
    if result.is_valid:
        print("[OK] Validation passed!")
    else:
        print("[ERROR] Validation failed:")
        for issue in result.issues:
            print(f"  - [{issue.severity.value}] {issue.path}: {issue.message}")
    
    return 0 if result.is_valid else 1


def cmd_info(args):
    """Display information about a schema."""
    schema = load_schema(args.schema)
    processor = SchemaProcessor(schema)
    info = processor.parse()
    
    print(f"\nSchema Information:")
    print(f"  Title: {info.title or 'N/A'}")
    print(f"  Description: {info.description or 'N/A'}")
    print(f"  Type(s): {', '.join(t.value for t in info.types) or 'N/A'}")
    
    print(f"\n  Properties ({len(info.properties)}):")
    for name, prop in info.properties.items():
        req = "*" if prop.required else ""
        types = ", ".join(t.value for t in prop.types) or "any"
        print(f"    - {name}{req}: {types}")
    
    print(f"\n  Definitions ({len(info.definitions)}):")
    for name in info.definitions:
        print(f"    - {name}")


def cmd_interactive(args):
    """Start interactive mode."""
    print_banner()
    print("Interactive mode - type 'help' for commands, 'exit' to quit\n")
    
    processor = None
    
    while True:
        try:
            cmd = input("jsonchamp> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not cmd:
            continue
        
        parts = cmd.split()
        action = parts[0].lower()
        
        if action in ("exit", "quit"):
            print("Goodbye!")
            break
        
        elif action == "help":
            print("""
Available commands:
  load <schema.json>     - Load a JSON schema
  classes                - Generate Python classes
  samples [count]        - Generate sample data
  validate <data.json>   - Validate data against loaded schema
  info                   - Show schema information
  exit                   - Exit interactive mode
""")
        
        elif action == "load":
            if len(parts) < 2:
                print("Usage: load <schema.json>")
                continue
            try:
                schema = load_schema(parts[1])
                processor = SchemaProcessor(schema)
                print(f"[OK] Loaded schema from {parts[1]}")
            except Exception as e:
                print(f"[ERROR] Error loading schema: {e}")
        
        elif action == "classes":
            if processor is None:
                print("[ERROR] No schema loaded. Use 'load <schema.json>' first.")
                continue
            print(processor.generate_code())
        
        elif action == "samples":
            if processor is None:
                print("[ERROR] No schema loaded. Use 'load <schema.json>' first.")
                continue
            count = int(parts[1]) if len(parts) > 1 else 1
            samples = processor.generate_samples(count=count)
            print(json.dumps(samples, indent=2, default=str))
        
        elif action == "info":
            if processor is None:
                print("[ERROR] No schema loaded. Use 'load <schema.json>' first.")
                continue
            info = processor.parse()
            print(f"Title: {info.title}")
            print(f"Properties: {len(info.properties)}")
            print(f"Definitions: {len(info.definitions)}")
        
        elif action == "validate":
            if processor is None:
                print("[ERROR] No schema loaded. Use 'load <schema.json>' first.")
                continue
            if len(parts) < 2:
                print("Usage: validate <data.json>")
                continue
            try:
                with open(parts[1], "r") as f:
                    data = json.load(f)
                result = processor.validate_data(data)
                if result.is_valid:
                    print("[OK] Validation passed!")
                else:
                    print("[ERROR] Validation failed:")
                    for issue in result.issues:
                        print(f"  - {issue.path}: {issue.message}")
            except Exception as e:
                print(f"[ERROR] Error: {e}")
        
        else:
            print(f"Unknown command: {action}. Type 'help' for available commands.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="jsonchamp",
        description="JsonSchemaCodeGen - Generate Python code from JSON Schema",
        epilog="Copyright (C) 2025-2030 Ashutosh Sinha. All Rights Reserved.",
    )
    
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate classes command
    gen_parser = subparsers.add_parser(
        "generate",
        aliases=["gen"],
        help="Generate Python classes from schema",
    )
    gen_parser.add_argument("schema", help="Path to JSON Schema file")
    gen_parser.add_argument(
        "-o", "--output",
        help="Output file path (prints to stdout if not specified)",
    )
    gen_parser.add_argument(
        "-c", "--class-name",
        default="Root",
        help="Name for the root class (default: Root)",
    )
    gen_parser.set_defaults(func=cmd_generate_classes)
    
    # Generate module command
    mod_parser = subparsers.add_parser(
        "generate-module",
        aliases=["genmod"],
        help="Generate Python module from schema folder",
    )
    mod_parser.add_argument(
        "--schema-dir",
        required=True,
        help="Path to directory containing JSON Schema files",
    )
    mod_parser.add_argument(
        "--output-dir",
        required=True,
        help="Path where the Python module will be created",
    )
    mod_parser.add_argument(
        "--module-name",
        help="Name for the module (defaults to output-dir basename)",
    )
    mod_parser.set_defaults(func=cmd_generate_module)
    
    # Generate samples command
    sample_parser = subparsers.add_parser(
        "samples",
        help="Generate sample JSON data from schema",
    )
    sample_parser.add_argument("schema", help="Path to JSON Schema file")
    sample_parser.add_argument(
        "-n", "--count",
        type=int,
        default=1,
        help="Number of samples to generate (default: 1)",
    )
    sample_parser.add_argument(
        "-o", "--output",
        help="Output file path (prints to stdout if not specified)",
    )
    sample_parser.add_argument(
        "--no-faker",
        action="store_true",
        help="Disable Faker for realistic data",
    )
    sample_parser.set_defaults(func=cmd_generate_samples)
    
    # Validate command
    val_parser = subparsers.add_parser(
        "validate",
        help="Validate schema or data",
    )
    val_parser.add_argument("schema", help="Path to JSON Schema file")
    val_parser.add_argument(
        "-d", "--data",
        help="Path to JSON data file to validate",
    )
    val_parser.set_defaults(func=cmd_validate)
    
    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Display schema information",
    )
    info_parser.add_argument("schema", help="Path to JSON Schema file")
    info_parser.set_defaults(func=cmd_info)
    
    # Interactive command
    inter_parser = subparsers.add_parser(
        "interactive",
        aliases=["i"],
        help="Start interactive mode",
    )
    inter_parser.set_defaults(func=cmd_interactive)
    
    args = parser.parse_args()
    
    if args.command is None:
        print_banner()
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
