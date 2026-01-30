"""
SchemaMap - JSON Schema Transformation DSL

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

A domain-specific language for transforming JSON documents between schemas.
Supports external Python functions for custom transformation logic.

Example usage:
    from jsonchamp.transformation import transform, load_mapping
    
    # Basic transformation
    result = transform(source_data, "mapping.smap")
    
    # With custom functions
    transformer = load_mapping("mapping.smap")
    transformer.register_function("calculate_tax", lambda x, r: x * r)
    result = transformer.transform(data)
"""

__version__ = "1.4.0"

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
    # Functions
    "transform",
    "load_mapping",
    "compile_mapping",
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
