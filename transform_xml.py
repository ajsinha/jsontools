#!/usr/bin/env python3
"""
XML to JSON Transformation Runner

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Transform XML data using SchemaMap DSL.
XML is converted to JSON and then transformed using the mapping file.

Usage:
    python transform_xml.py mapping.smap input.xml
    python transform_xml.py mapping.smap input.xml --output result.json
    python transform_xml.py mapping.smap input.xml --records "orders/order"
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from jsonchamp.transformation import load_mapping, validate_json_schema
from jsonchamp.transformation.converters import XMLConverter, XMLPresets
from jsonchamp import __version__


def main():
    parser = argparse.ArgumentParser(
        description="Transform XML data using SchemaMap DSL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic XML transformation (entire document)
  %(prog)s mapping.smap order.xml
  
  # With output file
  %(prog)s mapping.smap order.xml --output transformed.json
  
  # Process multiple records from XML
  %(prog)s mapping.smap orders.xml --records "order"
  %(prog)s mapping.smap data.xml --records "root/items/item"
  
  # Strip XML namespaces
  %(prog)s mapping.smap soap_response.xml --strip-namespaces
  
  # Don't preserve root element
  %(prog)s mapping.smap data.xml --no-root
  
  # Custom attribute prefix
  %(prog)s mapping.smap data.xml --attr-prefix "_"
  
  # Use preset format
  %(prog)s mapping.smap data.xml --preset soap
  %(prog)s mapping.smap data.xml --preset standard
  
  # Force elements to always be arrays
  %(prog)s mapping.smap data.xml --always-array "item,option"
  
  # With external functions
  %(prog)s mapping.smap data.xml --functions custom_funcs.py
        """
    )
    
    parser.add_argument("mapping", help="Path to SchemaMap DSL file (.smap)")
    parser.add_argument("input", help="Path to input XML file")
    parser.add_argument("--output", "-o", help="Output path for JSON result")
    parser.add_argument("--functions", "-f", help="Python file with custom functions")
    parser.add_argument("--schema", "-s", help="JSON Schema for output validation")
    
    # XML options
    xml_group = parser.add_argument_group("XML Options")
    xml_group.add_argument("--records", "-r",
                          help="XPath-like path to record elements for batch processing")
    xml_group.add_argument("--attr-prefix", default="@",
                          help="Prefix for attributes (default: '@')")
    xml_group.add_argument("--text-key", default="#text",
                          help="Key for text content (default: '#text')")
    xml_group.add_argument("--strip-namespaces", action="store_true",
                          help="Remove namespace prefixes from tag names")
    xml_group.add_argument("--no-root", action="store_true",
                          help="Don't preserve root element in output")
    xml_group.add_argument("--no-infer-types", action="store_true",
                          help="Keep all values as strings (don't infer types)")
    xml_group.add_argument("--no-strip", action="store_true",
                          help="Don't strip whitespace from text content")
    xml_group.add_argument("--always-array",
                          help="Elements that should always be arrays (comma-separated)")
    xml_group.add_argument("--force-list", action="store_true",
                          help="Force all repeated elements to be arrays")
    xml_group.add_argument("--encoding", default="utf-8",
                          help="File encoding (default: utf-8)")
    xml_group.add_argument("--preset", choices=["standard", "soap", "no_attrs", "preserve_all"],
                          help="Use preset XML format")
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--wrap-array", action="store_true",
                             help="Wrap output in {\"records\": [...]} object (with --records)")
    output_group.add_argument("--pretty", action="store_true", default=True,
                             help="Pretty-print JSON output (default)")
    output_group.add_argument("--compact", action="store_true",
                             help="Compact JSON output (no indentation)")
    output_group.add_argument("--show-xml-json", action="store_true",
                             help="Show intermediate XML-to-JSON conversion")
    
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
        # Build XML options
        if args.preset:
            preset_func = getattr(XMLPresets, args.preset)
            xml_options = preset_func()
        else:
            xml_options = {}
        
        # Override with explicit options
        xml_options['attr_prefix'] = args.attr_prefix
        xml_options['text_key'] = args.text_key
        xml_options['strip_namespaces'] = args.strip_namespaces
        xml_options['preserve_root'] = not args.no_root
        xml_options['infer_types'] = not args.no_infer_types
        xml_options['strip_whitespace'] = not args.no_strip
        xml_options['force_list'] = args.force_list
        xml_options['encoding'] = args.encoding
        
        if args.always_array:
            xml_options['always_array'] = [a.strip() for a in args.always_array.split(',')]
        
        # Convert XML to JSON
        if args.verbose:
            print(f"Reading XML: {args.input}")
            print(f"  Preserve root: {xml_options['preserve_root']}")
            print(f"  Strip namespaces: {xml_options['strip_namespaces']}")
        
        converter = XMLConverter(**xml_options)
        
        if args.records:
            # Multiple records mode
            if args.verbose:
                print(f"  Record path: {args.records}")
            records = converter.convert_file_elements(input_path, args.records)
            if args.verbose:
                print(f"  Records found: {len(records)}")
        else:
            # Single document mode
            records = [converter.convert_file(input_path)]
            if args.verbose:
                print(f"  Single document mode")
        
        if not records:
            print("Warning: No records found in XML file", file=sys.stderr)
            sys.exit(0)
        
        # Show intermediate JSON if requested
        if args.show_xml_json:
            print("\n=== XML to JSON Conversion ===")
            print(json.dumps(records[0] if len(records) == 1 else records, 
                           indent=2, default=str))
            print("==============================\n")
        
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
        
        if args.records:
            # Multiple records
            results = [transformer.transform(record) for record in records]
            
            # Wrap in object if requested
            if args.wrap_array:
                results = {"records": results, "count": len(results)}
        else:
            # Single document
            results = transformer.transform(records[0])
        
        # Validate if schema provided
        if args.schema:
            schema_path = Path(args.schema)
            if schema_path.exists():
                if isinstance(results, list):
                    for result in results:
                        validate_json_schema(result, str(schema_path))
                elif isinstance(results, dict) and 'records' in results:
                    for result in results['records']:
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
                if args.records:
                    count = results.get('count', len(results)) if isinstance(results, dict) else len(results)
                    print(f"✓ Transformed {count} record(s) to: {args.output}")
                else:
                    print(f"✓ Transformed XML to: {args.output}")
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
