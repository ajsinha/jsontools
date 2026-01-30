"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Command Line Interface for JsonSchemaCodeGen.

Usage:
    jsontools generate --schema schema.json --output models.py
    jsontools sample --schema schema.json --count 5
    jsontools validate --schema schema.json --data data.json
    jsontools generate-module --schema-dir schemas/ --output-dir output/
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .core.schema_processor import SchemaProcessor
from .core.validator import SchemaValidator
from .generators.sample_generator import SampleGenerator
from .generators.code_generator import CodeGenerator


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="jsontools",
        description="Generate Python code and sample data from JSON Schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate Python dataclasses:
    jsontools generate -s schema.json -o models.py
    
  Generate sample JSON data:
    jsontools sample -s schema.json -c 10 -o samples.json
    
  Validate a schema:
    jsontools validate -s schema.json
    
  Validate data against schema:
    jsontools validate -s schema.json -d data.json
    
  Generate module from schema folder:
    jsontools generate-module --schema-dir schemas/ --output-dir output/
    jsontools generate-module --schema-dir schemas/ --output-dir output/ --module-name mymodels
    
  Analyze schema complexity:
    jsontools info -s schema.json

Copyright (C) 2025-2030, Ashutosh Sinha. All Rights Reserved.
""",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.2.3",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Generate command
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate Python code from JSON Schema",
    )
    gen_parser.add_argument(
        "-s", "--schema",
        required=True,
        help="Path to JSON Schema file",
    )
    gen_parser.add_argument(
        "-o", "--output",
        default="generated_models.py",
        help="Output file path (default: generated_models.py)",
    )
    gen_parser.add_argument(
        "--class-name",
        default="Root",
        help="Name for the root class (default: Root)",
    )
    gen_parser.add_argument(
        "--no-validators",
        action="store_true",
        help="Don't include validation methods",
    )
    
    # Generate Module command
    mod_parser = subparsers.add_parser(
        "generate-module",
        help="Generate a Python module from a folder of JSON schemas",
    )
    mod_parser.add_argument(
        "--schema-dir",
        required=True,
        help="Path to directory containing JSON Schema files",
    )
    mod_parser.add_argument(
        "--output-dir",
        required=True,
        help="Path where the module will be created",
    )
    mod_parser.add_argument(
        "--module-name",
        default=None,
        help="Name for the module (default: mymodule)",
    )
    mod_parser.add_argument(
        "--overwrite",
        action="store_true",
        default=True,
        help="Overwrite existing files (default: True)",
    )
    
    # Sample command
    sample_parser = subparsers.add_parser(
        "sample",
        help="Generate sample JSON data from schema",
    )
    sample_parser.add_argument(
        "-s", "--schema",
        required=True,
        help="Path to JSON Schema file",
    )
    sample_parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)",
    )
    sample_parser.add_argument(
        "-c", "--count",
        type=int,
        default=1,
        help="Number of samples to generate (default: 1)",
    )
    sample_parser.add_argument(
        "--no-faker",
        action="store_true",
        help="Don't use Faker for realistic data",
    )
    sample_parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility",
    )
    
    # Validate command
    val_parser = subparsers.add_parser(
        "validate",
        help="Validate schema or data against schema",
    )
    val_parser.add_argument(
        "-s", "--schema",
        required=True,
        help="Path to JSON Schema file",
    )
    val_parser.add_argument(
        "-d", "--data",
        help="Path to data file to validate (optional)",
    )
    val_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show schema information and complexity",
    )
    info_parser.add_argument(
        "-s", "--schema",
        required=True,
        help="Path to JSON Schema file",
    )
    info_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    # Convert command
    conv_parser = subparsers.add_parser(
        "convert",
        help="Convert between schema formats",
    )
    conv_parser.add_argument(
        "-s", "--schema",
        required=True,
        help="Path to JSON Schema file",
    )
    conv_parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output file path",
    )
    conv_parser.add_argument(
        "--format",
        choices=["json", "yaml"],
        default="json",
        help="Output format (default: json)",
    )
    
    return parser


def cmd_generate(args) -> int:
    """Handle generate command."""
    try:
        # Load schema
        with open(args.schema, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        # Generate code
        generator = CodeGenerator(
            schema,
            root_class_name=args.class_name,
            include_validators=not args.no_validators,
        )
        
        code = generator.generate()
        
        # Write output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        print(f"[OK] Generated code written to {args.output}")
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        return 1


def cmd_generate_module(args) -> int:
    """Handle generate-module command."""
    try:
        from .module_generator import ModuleGenerator
        
        generator = ModuleGenerator(
            schema_dir=args.schema_dir,
            output_dir=args.output_dir,
            module_name=args.module_name,
            overwrite=args.overwrite,
        )
        
        result = generator.generate()
        
        print(f"[OK] Module generation complete!")
        print(f"  Module name: {result['module_name']}")
        print(f"  Module path: {result['module_path']}")
        print(f"  Schemas processed: {result['schemas_processed']}")
        print(f"  Classes generated: {len(result['classes_generated'])}")
        print(f"  Files created: {len(result['files_created'])}")
        
        if result['classes_generated']:
            print(f"\n  Generated classes:")
            for class_name in sorted(result['classes_generated'])[:10]:
                print(f"    - {class_name}")
            if len(result['classes_generated']) > 10:
                print(f"    ... and {len(result['classes_generated']) - 10} more")
        
        if result['errors']:
            print(f"\n  Errors:")
            for error in result['errors']:
                print(f"    [ERROR] {error}")
        
        print(f"\n  Usage:")
        print(f"    from {result['module_name']} import User, load_json, to_json")
        print(f"    python -m {result['module_name']} --help")
        
        return 0 if not result['errors'] else 1
        
    except Exception as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        return 1


def cmd_sample(args) -> int:
    """Handle sample command."""
    try:
        # Load schema
        with open(args.schema, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        # Create processor and generate samples
        processor = SchemaProcessor(schema)
        samples = processor.generate_samples(
            count=args.count,
            use_faker=not args.no_faker,
        )
        
        # Format output
        output = json.dumps(samples, indent=2, default=str)
        
        # Write output
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"[OK] Generated {args.count} sample(s) to {args.output}")
        else:
            print(output)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        return 1


def cmd_validate(args) -> int:
    """Handle validate command."""
    try:
        # Load schema
        with open(args.schema, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        validator = SchemaValidator(strict_mode=args.strict)
        
        # Validate schema itself
        schema_result = validator.validate_schema(schema)
        
        print("Schema Validation:")
        if schema_result.is_valid:
            print("  [OK] Schema is valid")
        else:
            print("  [ERROR] Schema has errors:")
            for issue in schema_result.errors:
                print(f"    - {issue.path}: {issue.message}")
        
        for warning in schema_result.warnings:
            print(f"  [WARN] Warning at {warning.path}: {warning.message}")
        
        # Validate data if provided
        if args.data:
            with open(args.data, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            data_result = validator.validate_data(data, schema)
            
            print("\nData Validation:")
            if data_result.is_valid:
                print("  [OK] Data is valid")
            else:
                print("  [ERROR] Data has errors:")
                for issue in data_result.errors:
                    print(f"    - {issue.path}: {issue.message}")
            
            return 0 if data_result.is_valid else 1
        
        return 0 if schema_result.is_valid else 1
        
    except Exception as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        return 1


def cmd_info(args) -> int:
    """Handle info command."""
    try:
        # Load schema
        with open(args.schema, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        from .utils.json_utils import get_schema_complexity, extract_definitions, find_all_refs
        
        metrics = get_schema_complexity(schema)
        definitions = extract_definitions(schema)
        refs = find_all_refs(schema)
        
        info = {
            "title": schema.get("title", "Untitled"),
            "description": schema.get("description", "No description"),
            "type": schema.get("type", "unknown"),
            "complexity": metrics,
            "definitions": list(definitions.keys()),
            "references": list(refs),
        }
        
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print(f"Schema: {info['title']}")
            print(f"Description: {info['description']}")
            print(f"Type: {info['type']}")
            print()
            print("Complexity Metrics:")
            for key, value in metrics.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            print()
            if definitions:
                print(f"Definitions ({len(definitions)}):")
                for name in definitions:
                    print(f"  - {name}")
            print()
            if refs:
                print(f"References ({len(refs)}):")
                for ref in refs:
                    print(f"  - {ref}")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        return 1


def cmd_convert(args) -> int:
    """Handle convert command."""
    try:
        # Load schema
        with open(args.schema, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        output_path = Path(args.output)
        
        if args.format == "yaml":
            try:
                import yaml
                with open(output_path, "w", encoding="utf-8") as f:
                    yaml.dump(schema, f, default_flow_style=False, sort_keys=False)
            except ImportError:
                print("[ERROR] Error: PyYAML is required for YAML output", file=sys.stderr)
                print("  Install with: pip install pyyaml", file=sys.stderr)
                return 1
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(schema, f, indent=2)
        
        print(f"[OK] Converted schema written to {args.output}")
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        return 1


def main(argv: Optional[list] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    commands = {
        "generate": cmd_generate,
        "generate-module": cmd_generate_module,
        "sample": cmd_sample,
        "validate": cmd_validate,
        "info": cmd_info,
        "convert": cmd_convert,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
