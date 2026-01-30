#!/usr/bin/env python3
"""
CSV to JSON Transformation Runner

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Transform CSV data using SchemaMap DSL.
Each CSV row is converted to JSON and then transformed using the mapping file.

Usage:
    python transform_csv.py mapping.smap input.csv
    python transform_csv.py mapping.smap input.csv --output result.json
    python transform_csv.py mapping.smap input.csv --delimiter ";" --no-header
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from jsonchamp.transformation import load_mapping, validate_json_schema
from jsonchamp.transformation.converters import CSVConverter, CSVPresets
from jsonchamp import __version__


def main():
    parser = argparse.ArgumentParser(
        description="Transform CSV data using SchemaMap DSL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic CSV transformation
  %(prog)s mapping.smap customers.csv
  
  # With output file
  %(prog)s mapping.smap customers.csv --output transformed.json
  
  # Custom delimiter (semicolon)
  %(prog)s mapping.smap data.csv --delimiter ";"
  
  # Tab-separated values
  %(prog)s mapping.smap data.tsv --delimiter "\\t"
  
  # CSV without header row
  %(prog)s mapping.smap data.csv --no-header --columns "id,name,email,age"
  
  # Use preset format
  %(prog)s mapping.smap data.csv --preset excel
  %(prog)s mapping.smap data.tsv --preset tsv
  
  # Skip header rows
  %(prog)s mapping.smap data.csv --skip-rows 2
  
  # Disable type inference (keep all values as strings)
  %(prog)s mapping.smap data.csv --no-infer-types
  
  # With external functions
  %(prog)s mapping.smap data.csv --functions custom_funcs.py
        """
    )
    
    parser.add_argument("mapping", help="Path to SchemaMap DSL file (.smap)")
    parser.add_argument("input", help="Path to input CSV file")
    parser.add_argument("--output", "-o", help="Output path for JSON result")
    parser.add_argument("--functions", "-f", help="Python file with custom functions")
    parser.add_argument("--schema", "-s", help="JSON Schema for output validation")
    
    # CSV options
    csv_group = parser.add_argument_group("CSV Options")
    csv_group.add_argument("--delimiter", "-d", default=",", 
                          help="Field delimiter (default: ',')")
    csv_group.add_argument("--quotechar", "-q", default='"',
                          help="Quote character (default: '\"')")
    csv_group.add_argument("--no-header", action="store_true",
                          help="CSV has no header row")
    csv_group.add_argument("--columns", 
                          help="Column names (comma-separated, for --no-header)")
    csv_group.add_argument("--skip-rows", type=int, default=0,
                          help="Skip N rows at start")
    csv_group.add_argument("--encoding", default="utf-8",
                          help="File encoding (default: utf-8)")
    csv_group.add_argument("--no-infer-types", action="store_true",
                          help="Keep all values as strings (don't infer types)")
    csv_group.add_argument("--no-strip", action="store_true",
                          help="Don't strip whitespace from values")
    csv_group.add_argument("--preset", choices=["excel", "tsv", "pipe", "semicolon"],
                          help="Use preset CSV format")
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--single", action="store_true",
                             help="Output single object (first row only)")
    output_group.add_argument("--wrap-array", action="store_true",
                             help="Wrap output in {\"records\": [...]} object")
    output_group.add_argument("--pretty", action="store_true", default=True,
                             help="Pretty-print JSON output (default)")
    output_group.add_argument("--compact", action="store_true",
                             help="Compact JSON output (no indentation)")
    
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
    
    try:
        # Build CSV options
        if args.preset:
            preset_func = getattr(CSVPresets, args.preset)
            csv_options = preset_func()
        else:
            csv_options = {}
        
        # Override with explicit options
        csv_options['delimiter'] = args.delimiter.encode().decode('unicode_escape')  # Handle \t
        csv_options['quotechar'] = args.quotechar
        csv_options['has_header'] = not args.no_header
        csv_options['skip_rows'] = args.skip_rows
        csv_options['encoding'] = args.encoding
        csv_options['infer_types'] = not args.no_infer_types
        csv_options['strip_whitespace'] = not args.no_strip
        
        if args.columns:
            csv_options['column_names'] = [c.strip() for c in args.columns.split(',')]
        
        # Convert CSV to JSON
        if args.verbose:
            print(f"Reading CSV: {args.input}")
            print(f"  Delimiter: {repr(csv_options['delimiter'])}")
            print(f"  Has header: {csv_options['has_header']}")
        
        converter = CSVConverter(**csv_options)
        records = list(converter.iterate_file(input_path))
        
        if args.verbose:
            print(f"  Records found: {len(records)}")
        
        if not records:
            print("Warning: No records found in CSV file", file=sys.stderr)
            sys.exit(0)
        
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
