#!/usr/bin/env python3
"""
JsonSchemaCodeGen - Module Generator

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

This script generates a complete Python module from a folder of JSON Schema files.

Usage:
    python generate.py --schema-dir ./schemas --output-dir ./output --module-name mymodels
    python generate.py -s ./schemas -o ./output -m mymodels
    python generate.py --help
"""

import argparse
import sys
from pathlib import Path

# Add package to path for direct execution
sys.path.insert(0, str(Path(__file__).parent))

from jsonschemacodegen import generate_module, __version__


def main():
    """Main entry point for module generation."""
    parser = argparse.ArgumentParser(
        prog="JsonSchemaCodeGen Module Generator",
        description="Generate Python modules from JSON Schema folders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate module with custom name:
    python generate.py -s ./schemas -o ./output -m mymodels
    
  Generate module with default name (mymodule):
    python generate.py -s ./schemas -o ./output
    
  Using long options:
    python generate.py --schema-dir ./schemas --output-dir ./output --module-name mymodels

Output Structure:
  output_dir/
  └── module_name/
      ├── __init__.py      # Main exports
      ├── __main__.py      # CLI entry point
      ├── driver.py        # JSON utilities
      ├── main.py          # High-level functions
      └── generated/
          ├── __init__.py  # Class registry
          └── *.py         # Generated dataclasses

Copyright © 2025-2030, Ashutosh Sinha. All Rights Reserved.
""",
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"JsonSchemaCodeGen v{__version__}",
    )
    
    parser.add_argument(
        "--schema-dir", "-s",
        required=True,
        help="Path to directory containing JSON Schema files",
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        required=True,
        help="Path where the module folder will be created",
    )
    
    parser.add_argument(
        "--module-name", "-m",
        default=None,
        help="Name for the generated module (default: mymodule)",
    )
    
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=True,
        help="Overwrite existing files (default: True)",
    )
    
    args = parser.parse_args()
    
    # Validate schema directory
    schema_dir = Path(args.schema_dir)
    if not schema_dir.exists():
        print(f"Error: Schema directory not found: {schema_dir}", file=sys.stderr)
        return 1
    
    # Print header
    print(f"JsonSchemaCodeGen v{__version__} - Module Generator")
    print("=" * 50)
    print(f"Schema directory: {args.schema_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Module name: {args.module_name or 'mymodule (default)'}")
    print()
    
    try:
        result = generate_module(
            schema_dir=args.schema_dir,
            output_dir=args.output_dir,
            module_name=args.module_name,
            overwrite=args.overwrite,
        )
        
        print(f"✓ Module generation complete!")
        print(f"  Module name: {result['module_name']}")
        print(f"  Module path: {result['module_path']}")
        print(f"  Schemas processed: {result['schemas_processed']}")
        print(f"  Classes generated: {len(result['classes_generated'])}")
        print(f"  Files created: {len(result['files_created'])}")
        
        if result['classes_generated']:
            print(f"\nGenerated classes:")
            for class_name in sorted(result['classes_generated']):
                print(f"  - {class_name}")
        
        if result['errors']:
            print(f"\nErrors:")
            for error in result['errors']:
                print(f"  ✗ {error}")
            return 1
        
        print(f"\nUsage:")
        print(f"  # In Python:")
        print(f"  import sys")
        print(f"  sys.path.insert(0, '{args.output_dir}')")
        print(f"  from {result['module_name']} import User, load_json, to_json")
        print()
        print(f"  # Command line:")
        print(f"  python -m {result['module_name']} list")
        print(f"  python -m {result['module_name']} sample User -o sample.json")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
