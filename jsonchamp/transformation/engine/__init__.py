"""SchemaMap Transformation Engine with External Function Support."""
from .transformer import SchemaMapTransformer, TransformError
from .evaluator import ExpressionEvaluator, ExternalFunctionError
from .functions import BuiltinFunctions
from .function_registry import (
    FunctionRegistry, 
    FunctionRegistryError,
    get_global_registry,
    register_function,
    call_function
)

__all__ = [
    "SchemaMapTransformer", 
    "TransformError",
    "ExpressionEvaluator",
    "ExternalFunctionError", 
    "BuiltinFunctions",
    "FunctionRegistry",
    "FunctionRegistryError",
    "get_global_registry",
    "register_function",
    "call_function",
]
