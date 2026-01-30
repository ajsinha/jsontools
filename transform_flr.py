#!/usr/bin/env python3
"""
Fixed Length Record (FLR) to JSON Transformation Runner

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Transform fixed-length record files using SchemaMap DSL.
Each record is converted to JSON based on a layout definition, then transformed.

Usage:
    python transform_flr.py mapping.smap input.dat --layout layout.json
    python transform_flr.py mapping.smap input.dat --layout layout.txt --output result.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from jsonchamp.transformation import load_mapping, validate_json_schema
from jsonchamp.transformation.converters import FLRConverter, FLRPresets, RecordLayout
from jsonchamp import __version__


def main():
    parser = argparse.ArgumentParser(
        description="Transform Fixed Length Record (FLR) data using SchemaMap DSL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic FLR transformation with JSON layout
  %(prog)s mapping.smap customers.dat --layout customer_layout.json
  
  # With output file
  %(prog)s mapping.smap data.dat --layout layout.json --output transformed.json
  
  # Using simple text layout format
  %(prog)s mapping.smap data.dat --layout layout.txt
  
  # Skip header and footer lines
  %(prog)s mapping.smap data.dat --layout layout.json --skip-header 1 --skip-footer 1
  
  # EBCDIC encoded mainframe file
  %(prog)s mapping.smap mainframe.dat --layout layout.json --encoding cp037
  
  # Use preset format
  %(prog)s mapping.smap data.dat --layout layout.json --preset mainframe
  
  # Validate layout before processing
  %(prog)s mapping.smap data.dat --layout layout.json --validate-layout
  
  # Show intermediate JSON conversion
  %(prog)s mapping.smap data.dat --layout layout.json --show-json
  
  # With external functions
  %(prog)s mapping.smap data.dat --layout layout.json --functions custom_funcs.py

Layout File Formats:
  
  JSON Layout (layout.json):
    {
      "record_length": 100,
      "fields": [
        {"name": "id", "start": 1, "length": 10, "data_type": "integer"},
        {"name": "name", "start": 11, "length": 30, "data_type": "string"},
        {"name": "amount", "start": 41, "length": 12, "data_type": "decimal", "decimal_places": 2},
        {"name": "date", "start": 53, "length": 8, "data_type": "date", "date_format": "YYYYMMDD"}
      ]
    }
  
  Simple Text Layout (layout.txt):
    # field_name,start,length,type[,decimal_places_or_date_format]
    id,1,10,integer
    name,11,30,string
    amount,41,12,decimal,2
    date,53,8,date,YYYYMMDD
        """
    )
    
    parser.add_argument("mapping", help="Path to SchemaMap DSL file (.smap)")
    parser.add_argument("input", help="Path to input FLR file")
    parser.add_argument("--layout", "-l", required=True,
                       help="Path to layout definition file (JSON or text format)")
    parser.add_argument("--output", "-o", help="Output path for JSON result")
    parser.add_argument("--functions", "-f", help="Python file with custom functions")
    parser.add_argument("--schema", "-s", help="JSON Schema for output validation")
    
    # FLR options
    flr_group = parser.add_argument_group("FLR Options")
    flr_group.add_argument("--encoding", default="utf-8",
                          help="File encoding (default: utf-8, use cp037 for EBCDIC)")
    flr_group.add_argument("--skip-header", type=int, default=0,
                          help="Number of header lines to skip")
    flr_group.add_argument("--skip-footer", type=int, default=0,
                          help="Number of footer lines to skip")
    flr_group.add_argument("--no-skip-blank", action="store_true",
                          help="Don't skip blank lines")
    flr_group.add_argument("--strip-record", action="store_true",
                          help="Strip trailing whitespace from records")
    flr_group.add_argument("--preset", choices=["mainframe", "cobol", "ascii"],
                          help="Use preset FLR format")
    flr_group.add_argument("--validate-layout", action="store_true",
                          help="Validate layout and show any issues")
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--single", action="store_true",
                             help="Output single object (first record only)")
    output_group.add_argument("--wrap-array", action="store_true",
                             help="Wrap output in {\"records\": [...]} object")
    output_group.add_argument("--pretty", action="store_true", default=True,
                             help="Pretty-print JSON output (default)")
    output_group.add_argument("--compact", action="store_true",
                             help="Compact JSON output (no indentation)")
    output_group.add_argument("--show-json", action="store_true",
                             help="Show intermediate FLR-to-JSON conversion")
    output_group.add_argument("--show-layout", action="store_true",
                             help="Show parsed layout definition")
    
    # General options
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress status messages")
    parser.add_argument("--version", action="version", 
                       version=f"%(prog)s {__version__}")
    
    args = parser.parse_args()
    
    # Validate files exist
    mapping_path = Path(args.mapping)
    if not mapping_path.exists():
        print(f"Error: Mapping file not found: {args.mapping}", file=sys.stderr)
        sys.exit(1)
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    layout_path = Path(args.layout)
    if not layout_path.exists():
        print(f"Error: Layout file not found: {args.layout}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Load layout
        if args.verbose:
            print(f"Loading layout: {args.layout}")
        
        if layout_path.suffix.lower() == '.json':
            layout = RecordLayout.from_json_file(layout_path)
        else:
            layout = RecordLayout.from_simple_format(layout_path)
        
        if args.verbose:
            print(f"  Fields defined: {len(layout.fields)}")
            print(f"  Record length: {layout.record_length}")
        
        # Show layout if requested
        if args.show_layout:
            print("\n=== Record Layout ===")
            print(f"Record Length: {layout.record_length}")
            print(f"\n{'Field':<20} {'Start':>6} {'Length':>6} {'End':>6} {'Type':<10}")
            print("-" * 60)
            for field in layout.fields:
                print(f"{field.name:<20} {field.start:>6} {field.length:>6} {field.end:>6} {field.data_type:<10}")
            print()
        
        # Validate layout if requested
        if args.validate_layout:
            issues = layout.validate()
            if issues:
                print("\n=== Layout Validation Issues ===")
                for issue in issues:
                    print(f"  ⚠ {issue}")
                print()
            else:
                print("✓ Layout validation passed")
        
        # Build FLR options
        if args.preset:
            if args.preset == 'mainframe':
                flr_options = FLRPresets.mainframe()
            elif args.preset == 'cobol':
                flr_options = FLRPresets.cobol_defaults()
            else:
                flr_options = FLRPresets.ascii_fixed()
        else:
            flr_options = {}
        
        # Override with explicit options
        flr_options['encoding'] = args.encoding
        flr_options['header_lines'] = args.skip_header
        flr_options['footer_lines'] = args.skip_footer
        flr_options['skip_blank_lines'] = not args.no_skip_blank
        flr_options['strip_record'] = args.strip_record
        
        # Convert FLR to JSON
        if args.verbose:
            print(f"Reading FLR file: {args.input}")
            print(f"  Encoding: {flr_options['encoding']}")
        
        converter = FLRConverter(layout=layout, **flr_options)
        records = list(converter.iterate_file(input_path))
        
        if args.verbose:
            print(f"  Records found: {len(records)}")
        
        if not records:
            print("Warning: No records found in FLR file", file=sys.stderr)
            sys.exit(0)
        
        # Show intermediate JSON if requested
        if args.show_json:
            print("\n=== FLR to JSON Conversion (first record) ===")
            print(json.dumps(records[0], indent=2, default=str))
            if len(records) > 1:
                print(f"\n... and {len(records) - 1} more records")
            print()
        
        # Load transformer
        if args.verbose:
            print(f"Loading mapping: {args.mapping}")
        
        transformer = load_mapping(str(mapping_path))
        
        # Register external functions
        if args.functions:
            func_path = Path(args.functions)
            if func_path.exists():
                transformer.register_file(str(func_path))
                if args.verbose:
                    print(f"Loaded functions from: {args.functions}")
            else:
                print(f"Warning: Functions file not found: {args.functions}", 
                      file=sys.stderr)
        
        # Transform records
        if args.verbose:
            print("Transforming records...")
        
        if args.single:
            results = transformer.transform(records[0])
        else:
            results = [transformer.transform(record) for record in records]
        
        # Wrap in object if requested
        if args.wrap_array and not args.single:
            results = {"records": results, "count": len(results)}
        
        # Validate if schema provided
        if args.schema:
            schema_path = Path(args.schema)
            if schema_path.exists():
                if isinstance(results, list):
                    for i, result in enumerate(results):
                        validate_json_schema(result, str(schema_path))
                else:
                    validate_json_schema(results, str(schema_path))
                if args.verbose:
                    print("✓ Schema validation passed")
        
        # Output
        indent = None if args.compact else 2
        json_output = json.dumps(results, indent=indent, default=str)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            if not args.quiet:
                count = len(results) if isinstance(results, list) else 1
                print(f"✓ Transformed {count} record(s) to: {args.output}")
        else:
            print(json_output)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
