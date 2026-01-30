"""
SchemaMap - JSON Schema Transformation DSL

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

A domain-specific language for transforming JSON documents between schemas.
Supports external Python functions for custom transformation logic.
Supports JSON, CSV, XML, and Fixed Length Records (FLR) as input formats.

Example usage:
    from jsonchamp.transformation import transform, load_mapping
    
    # Basic transformation (dict/JSON)
    result = transform(source_data, "mapping.smap")
    
    # With custom functions
    transformer = load_mapping("mapping.smap")
    transformer.register_function("calculate_tax", lambda x, r: x * r)
    result = transformer.transform(data)
    
    # CSV transformation
    from jsonchamp.transformation import transform_csv
    results = transform_csv("data.csv", "mapping.smap")
    
    # XML transformation
    from jsonchamp.transformation import transform_xml
    result = transform_xml("data.xml", "mapping.smap")
    
    # Fixed Length Record transformation
    from jsonchamp.transformation import transform_flr
    results = transform_flr("data.dat", "mapping.smap", "layout.json")
    
    # Compiled transformer (5-10x faster)
    from jsonchamp.transformation import compile_and_transform
    result = compile_and_transform(data, "mapping.smap")
"""

__version__ = "1.7.0"

from .engine.transformer import SchemaMapTransformer, TransformError
from .engine.evaluator import ExpressionEvaluator, ExternalFunctionError
from .engine.functions import BuiltinFunctions
from .engine.function_registry import (
    FunctionRegistry,
    FunctionRegistryError,
    get_global_registry,
    register_function,
    call_function
)
from .parser.lexer import SchemaMapLexer, Token, TokenType, LexerError
from .parser.parser import (
    SchemaMapParser, ParserError, MappingFile, Mapping, 
    SourcePath, TargetPath, Transform, TransformChain,
    FunctionDefinition
)
from .compiler.python_gen import PythonCodeGenerator
from .utils.validation import validate_json_schema, ValidationError

# Converters for CSV, XML, and FLR support
from .converters import (
    CSVConverter, CSVPresets, csv_to_json,
    XMLConverter, XMLPresets, xml_to_json, xml_to_json_records,
    FLRConverter, FLRPresets, RecordLayout, FieldDefinition, flr_to_json
)

__all__ = [
    # Version
    "__version__",
    # Main classes
    "SchemaMapTransformer",
    "TransformError",
    "ExpressionEvaluator",
    "ExternalFunctionError",
    "BuiltinFunctions",
    # Function registry
    "FunctionRegistry",
    "FunctionRegistryError",
    "get_global_registry",
    "register_function",
    "call_function",
    # Parser
    "SchemaMapLexer",
    "SchemaMapParser",
    "LexerError",
    "ParserError",
    # AST nodes
    "MappingFile",
    "Mapping",
    "SourcePath",
    "TargetPath",
    "Transform",
    "TransformChain",
    "FunctionDefinition",
    "Token",
    "TokenType",
    # Compiler
    "PythonCodeGenerator",
    # Validation
    "validate_json_schema",
    "ValidationError",
    # CSV Converters
    "CSVConverter",
    "CSVPresets",
    "csv_to_json",
    # XML Converters
    "XMLConverter",
    "XMLPresets",
    "xml_to_json",
    "xml_to_json_records",
    # FLR Converters
    "FLRConverter",
    "FLRPresets",
    "RecordLayout",
    "FieldDefinition",
    "flr_to_json",
    # Transform Functions
    "transform",
    "load_mapping",
    "compile_mapping",
    "transform_csv",
    "transform_xml",
    "transform_flr",
    "compile_and_transform",
    "create_compiled_transformer",
]


def transform(source_data: dict, mapping_file: str, validate_schema: str = None,
              functions: dict = None) -> dict:
    """
    Transform source JSON data using a SchemaMap DSL file.
    
    Args:
        source_data: The source JSON data as a dictionary
        mapping_file: Path to the .smap mapping file
        validate_schema: Optional path to JSON Schema to validate output
        functions: Optional dictionary of external functions to register
        
    Returns:
        Transformed JSON data as a dictionary
        
    Example:
        # With custom functions
        result = transform(
            source_data, 
            "mapping.smap",
            functions={
                "calculate_tax": lambda x, r: round(x * r, 2),
                "format_name": lambda f, l: f"{f} {l}".title()
            }
        )
    """
    transformer = SchemaMapTransformer.from_file(mapping_file)
    
    if functions:
        transformer.register_functions(functions)
    
    result = transformer.transform(source_data)
    
    if validate_schema:
        validate_json_schema(result, validate_schema)
    
    return result


def load_mapping(mapping_file: str) -> SchemaMapTransformer:
    """
    Load a SchemaMap mapping file and return a transformer.
    
    Args:
        mapping_file: Path to the .smap mapping file
        
    Returns:
        SchemaMapTransformer instance ready for transformations
    """
    return SchemaMapTransformer.from_file(mapping_file)


def compile_mapping(mapping_file: str, output_format: str = "python", 
                    class_name: str = "GeneratedTransformer") -> str:
    """
    Compile a SchemaMap mapping file to executable code.
    
    Args:
        mapping_file: Path to the .smap mapping file
        output_format: Target format ("python" supported)
        class_name: Name for the generated class
        
    Returns:
        Generated code as a string
    """
    parser = SchemaMapParser()
    with open(mapping_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ast = parser.parse(content, filename=mapping_file)
    
    if output_format == "python":
        generator = PythonCodeGenerator(class_name=class_name)
        return generator.generate(ast)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def transform_csv(csv_file: str, mapping_file: str, 
                  csv_options: dict = None, functions: dict = None) -> list:
    """
    Transform CSV data using a SchemaMap DSL file.
    
    Each CSV row is converted to JSON and transformed individually.
    
    Args:
        csv_file: Path to the CSV file
        mapping_file: Path to the .smap mapping file
        csv_options: Optional dict of CSVConverter options
        functions: Optional dictionary of external functions
        
    Returns:
        List of transformed dictionaries (one per row)
        
    Example:
        results = transform_csv(
            "customers.csv",
            "customer_mapping.smap",
            csv_options={'delimiter': ';', 'encoding': 'utf-8'},
            functions={'format_phone': format_phone}
        )
    """
    csv_opts = csv_options or {}
    converter = CSVConverter(**csv_opts)
    records = converter.convert_file(csv_file)
    
    transformer = SchemaMapTransformer.from_file(mapping_file)
    if functions:
        transformer.register_functions(functions)
    
    return [transformer.transform(record) for record in records]


def transform_xml(xml_file: str, mapping_file: str,
                  xml_options: dict = None, element_path: str = None,
                  functions: dict = None) -> list:
    """
    Transform XML data using a SchemaMap DSL file.
    
    Args:
        xml_file: Path to the XML file
        mapping_file: Path to the .smap mapping file
        xml_options: Optional dict of XMLConverter options
        element_path: Optional path to record elements for batch processing
        functions: Optional dictionary of external functions
        
    Returns:
        Single transformed dict, or list of dicts if element_path specified
        
    Example:
        # Single document transformation
        result = transform_xml("order.xml", "order_mapping.smap")
        
        # Multiple records from XML
        results = transform_xml(
            "orders.xml",
            "order_mapping.smap",
            element_path="orders/order"
        )
    """
    xml_opts = xml_options or {}
    converter = XMLConverter(**xml_opts)
    
    transformer = SchemaMapTransformer.from_file(mapping_file)
    if functions:
        transformer.register_functions(functions)
    
    if element_path:
        # Multiple records
        records = converter.convert_file_elements(xml_file, element_path)
        return [transformer.transform(record) for record in records]
    else:
        # Single document
        data = converter.convert_file(xml_file)
        return transformer.transform(data)


def transform_flr(flr_file: str, mapping_file: str, layout: any,
                  flr_options: dict = None, functions: dict = None) -> list:
    """
    Transform Fixed Length Record (FLR) data using a SchemaMap DSL file.
    
    Args:
        flr_file: Path to the FLR data file
        mapping_file: Path to the .smap mapping file
        layout: RecordLayout object, path to layout JSON/text file, or dict
        flr_options: Optional dict of FLRConverter options
        functions: Optional dictionary of external functions
        
    Returns:
        List of transformed dictionaries (one per record)
        
    Example:
        # With JSON layout file
        results = transform_flr(
            "customers.dat",
            "customer_mapping.smap",
            "customer_layout.json"
        )
        
        # With layout dict
        layout = {
            "fields": [
                {"name": "id", "start": 1, "length": 10, "data_type": "integer"},
                {"name": "name", "start": 11, "length": 30}
            ]
        }
        results = transform_flr("data.dat", "mapping.smap", layout)
        
        # With RecordLayout object
        from jsonchamp.transformation import RecordLayout
        layout = RecordLayout()
        layout.add_field("id", 1, 10, data_type="integer")
        layout.add_field("name", 11, 30)
        results = transform_flr("data.dat", "mapping.smap", layout)
    """
    from pathlib import Path
    
    # Handle layout
    if isinstance(layout, RecordLayout):
        record_layout = layout
    elif isinstance(layout, dict):
        record_layout = RecordLayout.from_dict(layout)
    elif isinstance(layout, (str, Path)):
        layout_path = Path(layout)
        if layout_path.suffix.lower() == '.json':
            record_layout = RecordLayout.from_json_file(layout)
        else:
            record_layout = RecordLayout.from_simple_format(layout)
    else:
        raise ValueError(f"Invalid layout type: {type(layout)}")
    
    flr_opts = flr_options or {}
    converter = FLRConverter(layout=record_layout, **flr_opts)
    records = converter.convert_file(flr_file)
    
    transformer = SchemaMapTransformer.from_file(mapping_file)
    if functions:
        transformer.register_functions(functions)
    
    return [transformer.transform(record) for record in records]


def create_compiled_transformer(mapping_file: str, class_name: str = "CompiledTransformer"):
    """
    Create a compiled transformer from a mapping file.
    
    Compiled transformers are 5-10x faster than interpreted transformers.
    They can be used with any input format (dict, CSV, XML, FLR).
    
    Args:
        mapping_file: Path to the .smap mapping file
        class_name: Name for the generated transformer class
        
    Returns:
        Compiled transformer instance
        
    Example:
        # Create compiled transformer
        transformer = create_compiled_transformer("mapping.smap")
        
        # Transform dict
        result = transformer.transform({"name": "John", "age": 30})
        
        # Transform batch
        results = transformer.transform_batch([data1, data2, data3])
        
        # Register external functions
        transformer.register_function("calc_tax", lambda x, r: x * r)
        
        # Use with CSV data
        from jsonchamp.transformation import csv_to_json
        records = csv_to_json("data.csv")
        results = [transformer.transform(r) for r in records]
    """
    with open(mapping_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parser = SchemaMapParser()
    mapping = parser.parse(content, filename=mapping_file)
    
    generator = PythonCodeGenerator(class_name=class_name)
    code = generator.generate(mapping)
    
    # Execute compiled code
    exec_globals = {}
    exec(code, exec_globals)
    
    TransformerClass = exec_globals[class_name]
    return TransformerClass()


def compile_and_transform(source_data: any, mapping_file: str, 
                          functions: dict = None, validate_schema: str = None):
    """
    Transform data using a compiled transformer (faster).
    
    This is a convenience function that compiles the mapping and transforms
    the data in one step. For repeated transformations, use 
    create_compiled_transformer() instead to avoid recompilation.
    
    Args:
        source_data: Dictionary or list of dictionaries to transform
        mapping_file: Path to the .smap mapping file
        functions: Optional dictionary of external functions
        validate_schema: Optional path to JSON Schema for validation
        
    Returns:
        Transformed dictionary or list of dictionaries
        
    Example:
        # Single record
        result = compile_and_transform(
            {"name": "John", "age": 30},
            "mapping.smap"
        )
        
        # Batch records
        results = compile_and_transform(
            [data1, data2, data3],
            "mapping.smap"
        )
    """
    transformer = create_compiled_transformer(mapping_file)
    
    if functions:
        for name, func in functions.items():
            transformer.register_function(name, func)
    
    if isinstance(source_data, list):
        if hasattr(transformer, 'transform_batch'):
            results = transformer.transform_batch(source_data)
        else:
            results = [transformer.transform(item) for item in source_data]
    else:
        results = transformer.transform(source_data)
    
    if validate_schema:
        if isinstance(results, list):
            for result in results:
                validate_json_schema(result, validate_schema)
        else:
            validate_json_schema(results, validate_schema)
    
    return results
