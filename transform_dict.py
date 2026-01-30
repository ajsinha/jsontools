#!/usr/bin/env python3
"""
Dictionary/JSON Transformation Runner with Compiled Support

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Transform JSON data using SchemaMap DSL - supports both interpreted and compiled modes.
This script provides a unified interface for transforming dictionaries/JSON data.

Usage:
    # Interpreted mode (flexible, good for development)
    python transform_dict.py mapping.smap input.json
    
    # Compiled mode (5-10x faster, good for production)
    python transform_dict.py mapping.smap input.json --compiled
    
    # Transform inline JSON
    python transform_dict.py mapping.smap --data '{"name": "John", "age": 30}'
    
    # Batch transformation
    python transform_dict.py mapping.smap batch_input.json --batch
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Union

sys.path.insert(0, str(Path(__file__).parent))

from jsonchamp.transformation import (
    load_mapping, validate_json_schema,
    SchemaMapParser, TransformError
)
from jsonchamp.transformation.compiler.python_gen import PythonCodeGenerator
from jsonchamp import __version__


class CompiledTransformerWrapper:
    """
    Wrapper for compiled transformers that provides a consistent interface.
    """
    
    def __init__(self, mapping_path: str, class_name: str = "CompiledTransformer"):
        """
        Initialize compiled transformer.
        
        Args:
            mapping_path: Path to .smap mapping file
            class_name: Name for generated class
        """
        self.mapping_path = mapping_path
        self.class_name = class_name
        self._transformer = None
        self._external_functions = {}
        self._compile()
    
    def _compile(self):
        """Compile the mapping to Python code and execute it."""
        with open(self.mapping_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = SchemaMapParser()
        mapping_file = parser.parse(content, filename=self.mapping_path)
        
        generator = PythonCodeGenerator(class_name=self.class_name)
        code = generator.generate(mapping_file)
        
        # Execute compiled code
        exec_globals = {}
        exec(code, exec_globals)
        
        TransformerClass = exec_globals[self.class_name]
        self._transformer = TransformerClass()
        
        # Register any pre-registered functions
        for name, func in self._external_functions.items():
            self._transformer.register_function(name, func)
    
    def register_function(self, name: str, func):
        """Register an external function."""
        self._external_functions[name] = func
        if self._transformer:
            self._transformer.register_function(name, func)
    
    def register_functions(self, functions: Dict[str, callable]):
        """Register multiple external functions."""
        for name, func in functions.items():
            self.register_function(name, func)
    
    def register_file(self, file_path: str):
        """Register functions from a Python file."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("custom_functions", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Register all public functions
        for name in dir(module):
            if not name.startswith('_'):
                obj = getattr(module, name)
                if callable(obj):
                    self.register_function(name, obj)
    
    def transform(self, source_data: Dict) -> Dict:
        """Transform a single dictionary."""
        return self._transformer.transform(source_data)
    
    def transform_batch(self, items: List[Dict]) -> List[Dict]:
        """Transform multiple dictionaries."""
        if hasattr(self._transformer, 'transform_batch'):
            return self._transformer.transform_batch(items)
        return [self._transformer.transform(item) for item in items]


def transform_dict(
    data: Union[Dict, List[Dict]],
    mapping_path: str,
    compiled: bool = False,
    functions: Dict[str, callable] = None,
    validate_schema: str = None
) -> Union[Dict, List[Dict]]:
    """
    Transform dictionary data using SchemaMap.
    
    Args:
        data: Dictionary or list of dictionaries to transform
        mapping_path: Path to .smap mapping file
        compiled: Use compiled transformer (faster)
        functions: Dictionary of external functions
        validate_schema: Optional JSON Schema path for validation
        
    Returns:
        Transformed dictionary or list of dictionaries
    """
    # Create transformer
    if compiled:
        transformer = CompiledTransformerWrapper(mapping_path)
    else:
        transformer = load_mapping(mapping_path)
    
    # Register functions
    if functions:
        transformer.register_functions(functions)
    
    # Transform
    if isinstance(data, list):
        results = [transformer.transform(item) for item in data]
    else:
        results = transformer.transform(data)
    
    # Validate
    if validate_schema:
        if isinstance(results, list):
            for result in results:
                validate_json_schema(result, validate_schema)
        else:
            validate_json_schema(results, validate_schema)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Transform JSON/Dictionary data using SchemaMap DSL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transformation (interpreted)
  %(prog)s mapping.smap input.json
  
  # Compiled mode (5-10x faster)
  %(prog)s mapping.smap input.json --compiled
  
  # Transform inline JSON data
  %(prog)s mapping.smap --data '{"name": "John", "age": 30}'
  
  # Batch transformation (JSON array input)
  %(prog)s mapping.smap batch.json --batch
  
  # With external functions
  %(prog)s mapping.smap input.json --functions custom_funcs.py
  
  # Compare interpreted vs compiled performance
  %(prog)s mapping.smap input.json --benchmark
  
  # Output to file
  %(prog)s mapping.smap input.json --output result.json
  
  # Validate output against schema
  %(prog)s mapping.smap input.json --schema target_schema.json

Input Formats:
  - JSON file: {"field": "value", ...}
  - JSON array file (with --batch): [{"field": "value"}, ...]
  - Inline JSON (with --data): '{"field": "value"}'
        """
    )
    
    parser.add_argument("mapping", help="Path to SchemaMap DSL file (.smap)")
    parser.add_argument("input", nargs="?", help="Path to input JSON file")
    parser.add_argument("--data", "-d", help="Inline JSON data to transform")
    parser.add_argument("--output", "-o", help="Output path for JSON result")
    parser.add_argument("--functions", "-f", help="Python file with custom functions")
    parser.add_argument("--schema", "-s", help="JSON Schema for output validation")
    
    # Mode options
    mode_group = parser.add_argument_group("Mode Options")
    mode_group.add_argument("--compiled", "-c", action="store_true",
                           help="Use compiled transformer (5-10x faster)")
    mode_group.add_argument("--batch", "-b", action="store_true",
                           help="Input is array of records to transform")
    mode_group.add_argument("--benchmark", action="store_true",
                           help="Benchmark interpreted vs compiled performance")
    mode_group.add_argument("--iterations", type=int, default=1000,
                           help="Number of benchmark iterations (default: 1000)")
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--wrap-array", action="store_true",
                             help="Wrap batch output in {\"records\": [...]} object")
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
    
    # Validate mapping exists
    mapping_path = Path(args.mapping)
    if not mapping_path.exists():
        print(f"Error: Mapping file not found: {args.mapping}", file=sys.stderr)
        sys.exit(1)
    
    # Get input data
    if args.data:
        try:
            source_data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid inline JSON: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        with open(input_path, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
    else:
        print("Error: Either --data or input file required", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Benchmark mode
        if args.benchmark:
            run_benchmark(str(mapping_path), source_data, args.iterations, args.verbose)
            sys.exit(0)
        
        # Handle batch input
        if args.batch:
            if not isinstance(source_data, list):
                print("Error: --batch requires JSON array input", file=sys.stderr)
                sys.exit(1)
            records = source_data
        else:
            records = [source_data] if not isinstance(source_data, list) else source_data
            if len(records) == 1:
                records = records[0]  # Single record mode
        
        # Create transformer
        if args.compiled:
            if args.verbose:
                print("Using compiled transformer")
            transformer = CompiledTransformerWrapper(str(mapping_path))
        else:
            if args.verbose:
                print("Using interpreted transformer")
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
        
        # Transform
        if args.verbose:
            print("Transforming...")
        
        if isinstance(records, list):
            results = [transformer.transform(r) for r in records]
            if args.wrap_array:
                results = {"records": results, "count": len(results)}
        else:
            results = transformer.transform(records)
        
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
                if isinstance(results, list):
                    print(f"✓ Transformed {len(results)} record(s) to: {args.output}")
                else:
                    print(f"✓ Transformed to: {args.output}")
        else:
            print(json_output)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_benchmark(mapping_path: str, source_data: Any, iterations: int, verbose: bool):
    """Run benchmark comparing interpreted vs compiled transformers."""
    print("=" * 60)
    print("  Dictionary Transformation Benchmark")
    print("  Interpreted vs Compiled")
    print("=" * 60)
    
    # Handle batch data
    if isinstance(source_data, list):
        test_data = source_data[0] if source_data else {}
        print(f"\nUsing first record from batch of {len(source_data)}")
    else:
        test_data = source_data
    
    print(f"Mapping: {mapping_path}")
    print(f"Iterations: {iterations:,}")
    
    # Create interprested transformer
    print("\n[1] Loading interpreted transformer...")
    interpreted = load_mapping(mapping_path)
    
    # Create compiled transformer
    print("[2] Creating compiled transformer...")
    compiled = CompiledTransformerWrapper(mapping_path)
    
    # Verify outputs match
    print("[3] Verifying outputs match...")
    result_i = interpreted.transform(test_data)
    result_c = compiled.transform(test_data)
    
    def normalize(d):
        if isinstance(d, dict):
            return {k: normalize(v) for k, v in d.items() 
                   if k not in ('transformedAt', 'transformationId', 'transformId', 'processedAt', 'recordId')}
        elif isinstance(d, list):
            return [normalize(v) for v in d]
        return d
    
    if normalize(result_i) == normalize(result_c):
        print("    ✓ Outputs match!")
    else:
        print("    ⚠ Outputs differ (dynamic fields excluded)")
        if verbose:
            print(f"\n  Interpreted: {json.dumps(result_i, default=str)[:200]}...")
            print(f"  Compiled: {json.dumps(result_c, default=str)[:200]}...")
    
    # Warmup
    print("\n[4] Warming up (100 iterations each)...")
    for _ in range(100):
        interpreted.transform(test_data)
        compiled.transform(test_data)
    
    # Benchmark interpreted
    print(f"\n[5] Benchmarking interpreted ({iterations:,} iterations)...")
    start = time.perf_counter()
    for _ in range(iterations):
        interpreted.transform(test_data)
    interpreted_time = time.perf_counter() - start
    
    # Benchmark compiled
    print(f"[6] Benchmarking compiled ({iterations:,} iterations)...")
    start = time.perf_counter()
    for _ in range(iterations):
        compiled.transform(test_data)
    compiled_time = time.perf_counter() - start
    
    # Results
    speedup = interpreted_time / compiled_time if compiled_time > 0 else 0
    
    print("\n" + "=" * 60)
    print("  BENCHMARK RESULTS")
    print("=" * 60)
    
    print(f"\n  Interpreted Transformer:")
    print(f"    Total time:     {interpreted_time:.4f} seconds")
    print(f"    Ops/second:     {iterations/interpreted_time:,.0f}")
    print(f"    μs/operation:   {(interpreted_time/iterations)*1_000_000:.2f}")
    
    print(f"\n  Compiled Transformer:")
    print(f"    Total time:     {compiled_time:.4f} seconds")
    print(f"    Ops/second:     {iterations/compiled_time:,.0f}")
    print(f"    μs/operation:   {(compiled_time/iterations)*1_000_000:.2f}")
    
    print(f"\n  " + "-" * 56)
    print(f"  SPEEDUP: {speedup:.1f}x faster with compiled code!")
    print("=" * 60)


if __name__ == "__main__":
    main()
