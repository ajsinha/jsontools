#!/usr/bin/env python3
"""
SchemaMap Transformation Runner & Compiler

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Main entry point for running JSON transformations and compiling to Python.

Usage:
    # Transform data
    python transform.py mapping.smap input.json
    
    # Compile to Python
    python transform.py --compile mapping.smap -o transformer.py
    
    # Benchmark compiled vs interpreted
    python transform.py --benchmark mapping.smap input.json
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from jsontools.transformation import (
    transform, load_mapping, validate_json_schema,
    ValidationError, TransformError, SchemaMapParser
)
from jsontools.transformation.compiler.python_gen import PythonCodeGenerator
from jsontools import __version__


def compile_to_python(mapping_path: str, output_path: str, class_name: str, verbose: bool = False):
    """Compile SchemaMap to standalone Python code."""
    if verbose:
        print(f"Compiling: {mapping_path}")
    
    with open(mapping_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parser = SchemaMapParser()
    mapping_file = parser.parse(content, filename=mapping_path)
    
    generator = PythonCodeGenerator(class_name=class_name)
    code = generator.generate(mapping_file)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    if verbose:
        print(f"Generated: {output_path}")
        print(f"Class name: {class_name}")
        print(f"Code size: {len(code):,} bytes")
        print(f"Lines: {code.count(chr(10)):,}")


def run_benchmark(mapping_path: str, input_path: str, iterations: int = 10000, verbose: bool = False):
    """Benchmark interpreted vs compiled performance."""
    print("=" * 60)
    print("  SchemaMap Performance Benchmark")
    print("  Interpreted vs Compiled Transformer")
    print("=" * 60)
    
    # Load test data
    with open(input_path, 'r', encoding='utf-8') as f:
        source_data = json.load(f)
    
    print(f"\nMapping file: {mapping_path}")
    print(f"Input file: {input_path}")
    print(f"Input size: {len(json.dumps(source_data)):,} bytes")
    print(f"Iterations: {iterations:,}")
    
    # Create interpreted transformer
    print("\n[1] Loading interpreted transformer...")
    interpreted = load_mapping(mapping_path)
    
    # Compile to Python
    print("[2] Compiling to Python code...")
    with open(mapping_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parser = SchemaMapParser()
    mapping_file = parser.parse(content, filename=mapping_path)
    
    generator = PythonCodeGenerator(class_name="CompiledTransformer")
    compiled_code = generator.generate(mapping_file)
    
    # Execute compiled code
    exec_globals = {}
    exec(compiled_code, exec_globals)
    CompiledTransformer = exec_globals["CompiledTransformer"]
    compiled = CompiledTransformer()
    
    # Verify outputs match
    print("[3] Verifying outputs match...")
    result_i = interpreted.transform(source_data)
    result_c = compiled.transform(source_data)
    
    # Normalize for comparison (exclude dynamic fields)
    def normalize(d):
        if isinstance(d, dict):
            return {k: normalize(v) for k, v in d.items() 
                   if k not in ('transformedAt', 'transformationId', 'transformId')}
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
        interpreted.transform(source_data)
        compiled.transform(source_data)
    
    # Benchmark interpreted
    print(f"\n[5] Benchmarking interpreted ({iterations:,} iterations)...")
    start = time.perf_counter()
    for _ in range(iterations):
        interpreted.transform(source_data)
    interpreted_time = time.perf_counter() - start
    
    # Benchmark compiled
    print(f"[6] Benchmarking compiled ({iterations:,} iterations)...")
    start = time.perf_counter()
    for _ in range(iterations):
        compiled.transform(source_data)
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
    
    return {
        "interpreted_time": interpreted_time,
        "compiled_time": compiled_time,
        "speedup": speedup,
        "iterations": iterations
    }


def main():
    parser = argparse.ArgumentParser(
        description="Transform JSON data or compile SchemaMap to Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transform data
  %(prog)s mapping.smap input.json
  %(prog)s mapping.smap input.json --output result.json
  
  # Compile to Python (10-100x faster execution)
  %(prog)s --compile mapping.smap -o transformer.py
  %(prog)s --compile mapping.smap -o transformer.py --class-name MyTransformer
  
  # Benchmark interpreted vs compiled
  %(prog)s --benchmark mapping.smap input.json
  %(prog)s --benchmark mapping.smap input.json --iterations 50000
        """
    )
    
    parser.add_argument("mapping", help="Path to SchemaMap DSL file (.smap)")
    parser.add_argument("input", nargs="?", help="Path to input JSON file")
    parser.add_argument("--compile", "-c", action="store_true", help="Compile to Python code")
    parser.add_argument("--benchmark", "-b", action="store_true", help="Benchmark performance")
    parser.add_argument("--schema", "-s", help="JSON Schema for validation")
    parser.add_argument("--output", "-o", help="Output path")
    parser.add_argument("--class-name", default="GeneratedTransformer", help="Class name for compiled code")
    parser.add_argument("--functions", "-f", help="Python file with custom functions")
    parser.add_argument("--iterations", "-i", type=int, default=10000, help="Benchmark iterations")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    args = parser.parse_args()
    
    # Validate mapping exists
    mapping_path = Path(args.mapping)
    if not mapping_path.exists():
        print(f"Error: Mapping file not found: {args.mapping}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Compile mode
        if args.compile:
            output_path = args.output or mapping_path.stem + "_transformer.py"
            compile_to_python(str(mapping_path), output_path, args.class_name, args.verbose)
            if not args.quiet:
                print(f"✓ Compiled to: {output_path}")
            sys.exit(0)
        
        # Benchmark mode
        if args.benchmark:
            if not args.input:
                print("Error: Input file required for benchmark", file=sys.stderr)
                sys.exit(1)
            if not Path(args.input).exists():
                print(f"Error: Input file not found: {args.input}", file=sys.stderr)
                sys.exit(1)
            run_benchmark(str(mapping_path), str(args.input), args.iterations, args.verbose)
            sys.exit(0)
        
        # Transform mode
        if not args.input:
            print("Error: Input file required. Use --compile to generate code only.", file=sys.stderr)
            sys.exit(1)
        
        if not Path(args.input).exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        
        # Load and transform
        with open(args.input, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        
        transformer = load_mapping(str(mapping_path))
        
        if args.functions:
            if Path(args.functions).exists():
                transformer.register_file(args.functions)
        
        result = transformer.transform(source_data)
        
        # Validate if schema provided
        if args.schema:
            if Path(args.schema).exists():
                validate_json_schema(result, args.schema)
                if args.verbose:
                    print("✓ Schema validation passed")
        
        # Output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            if not args.quiet:
                print(f"✓ Output saved to: {args.output}")
        else:
            print(json.dumps(result, indent=2, default=str))
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
