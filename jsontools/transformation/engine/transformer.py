"""
SchemaMap Transformer

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Main transformation engine for executing SchemaMap DSL mappings.
Supports external Python functions for custom transformation logic.
"""

from __future__ import annotations
import json
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from pathlib import Path

from ..parser.parser import (
    SchemaMapParser, MappingFile, Mapping, NestedBlock, ConditionalBlock,
    SourcePath, TargetPath, MergeExpression, ComputeExpression, ConstantValue,
    SkipTarget, TransformChain
)
from .evaluator import ExpressionEvaluator
from .functions import BuiltinFunctions
from .function_registry import FunctionRegistry, FunctionRegistryError


class TransformError(Exception):
    """Exception raised during transformation."""
    def __init__(self, message: str, mapping: Optional[Mapping] = None):
        self.message = message
        self.mapping = mapping
        if mapping:
            super().__init__(f"Line {mapping.line_number}: {message}")
        else:
            super().__init__(message)


class SchemaMapTransformer:
    """
    Main transformer class for executing SchemaMap transformations.
    
    This class takes a parsed MappingFile (AST) and applies the mappings
    to transform source JSON data into target JSON data.
    
    Supports:
    - Field mappings with transform chains
    - Aliases for reusable transforms
    - Lookup tables for value mapping
    - Computed fields with expressions
    - External Python functions for custom logic
    
    Example:
        transformer = SchemaMapTransformer.from_file("mapping.smap")
        
        # Register custom function
        transformer.register_function("calculate_tax", lambda x, r: x * r)
        
        result = transformer.transform(source_data)
    """
    
    def __init__(self, mapping_file: MappingFile):
        """
        Initialize the transformer with a parsed mapping file.
        
        Args:
            mapping_file: Parsed MappingFile AST
        """
        self.mapping_file = mapping_file
        self.config = mapping_file.config
        self.aliases = mapping_file.aliases
        self.lookups = self._load_lookups(mapping_file.lookups)
        
        # Initialize function registry
        self.function_registry = FunctionRegistry()
        
        # Load functions from config if specified
        self._load_configured_functions()
        
        # Initialize evaluator with registry
        self.evaluator = ExpressionEvaluator(
            lookups=self.lookups,
            aliases=self.aliases,
            external_functions=self.function_registry._functions
        )
    
    @classmethod
    def from_file(cls, filepath: str) -> "SchemaMapTransformer":
        """
        Create a transformer from a .smap file.
        
        Args:
            filepath: Path to the .smap mapping file
            
        Returns:
            SchemaMapTransformer instance
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Mapping file not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = SchemaMapParser()
        mapping_file = parser.parse(content, filename=str(path))
        
        return cls(mapping_file)
    
    @classmethod
    def from_string(cls, content: str) -> "SchemaMapTransformer":
        """
        Create a transformer from a mapping string.
        
        Args:
            content: SchemaMap DSL content as string
            
        Returns:
            SchemaMapTransformer instance
        """
        parser = SchemaMapParser()
        mapping_file = parser.parse(content)
        return cls(mapping_file)
    
    def _load_lookups(self, lookup_defs: Dict) -> Dict[str, Dict]:
        """Load lookup tables from definitions."""
        lookups = {}
        for name, lookup_def in lookup_defs.items():
            if isinstance(lookup_def.source, str):
                # Load from file
                try:
                    with open(lookup_def.source, 'r', encoding='utf-8') as f:
                        lookups[name] = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    lookups[name] = {}
            else:
                # Inline dictionary
                lookups[name] = lookup_def.source
        return lookups
    
    def _load_configured_functions(self) -> None:
        """Load external functions specified in @config."""
        # Check for functions_module config
        functions_module = self.config.get('functions_module')
        if functions_module:
            try:
                self.function_registry.register_module(functions_module)
            except FunctionRegistryError as e:
                pass  # Module not available, continue without it
        
        # Check for functions_file config
        functions_file = self.config.get('functions_file')
        if functions_file:
            try:
                self.function_registry.register_file(functions_file)
            except FunctionRegistryError as e:
                pass  # File not available, continue without it
        
        # Check for individual function specs
        functions_specs = self.config.get('functions', [])
        if isinstance(functions_specs, list):
            for spec in functions_specs:
                try:
                    self.function_registry.register_from_spec(spec)
                except FunctionRegistryError:
                    pass  # Skip failed registrations
    
    # =========================================================================
    # External Function Registration
    # =========================================================================
    
    def register_function(self, name: str, func: Callable, 
                         description: str = None) -> "SchemaMapTransformer":
        """
        Register an external Python function for use in @compute expressions.
        
        Args:
            name: Function name to use in expressions
            func: Python callable
            description: Optional description
            
        Returns:
            self for method chaining
            
        Example:
            transformer.register_function(
                "calculate_tax",
                lambda amount, rate: round(amount * rate, 2)
            )
            
            # Then in .smap file:
            # @compute(calculate_tax(order.subtotal, 0.08)) : order.tax
        """
        self.function_registry.register(name, func, description=description)
        # Update evaluator's function reference
        self.evaluator.external_functions = self.function_registry._functions
        return self
    
    def register_functions(self, functions: Dict[str, Callable]) -> "SchemaMapTransformer":
        """
        Register multiple external functions at once.
        
        Args:
            functions: Dictionary mapping names to callables
            
        Returns:
            self for method chaining
        """
        for name, func in functions.items():
            self.register_function(name, func)
        return self
    
    def register_module(self, module_name: str, 
                       function_names: List[str] = None,
                       prefix: str = None) -> "SchemaMapTransformer":
        """
        Register functions from a Python module.
        
        Args:
            module_name: Module to import (e.g., "my_package.transforms")
            function_names: Optional list of specific functions
            prefix: Optional prefix for function names
            
        Returns:
            self for method chaining
        """
        self.function_registry.register_module(module_name, function_names, prefix)
        self.evaluator.external_functions = self.function_registry._functions
        return self
    
    def register_file(self, file_path: str,
                     function_names: List[str] = None,
                     prefix: str = None) -> "SchemaMapTransformer":
        """
        Register functions from a Python file.
        
        Args:
            file_path: Path to Python file
            function_names: Optional list of specific functions
            prefix: Optional prefix for function names
            
        Returns:
            self for method chaining
        """
        self.function_registry.register_file(file_path, function_names, prefix)
        self.evaluator.external_functions = self.function_registry._functions
        return self
    
    def list_functions(self) -> List[str]:
        """Get list of all registered external functions."""
        return self.function_registry.list_functions()
    
    # =========================================================================
    # Transformation
    # =========================================================================
    
    def transform(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform source data according to the mapping rules.
        
        Args:
            source_data: Source JSON data as dictionary
            
        Returns:
            Transformed JSON data as dictionary
        """
        self.evaluator.context = source_data
        target_data = {}
        
        for mapping_item in self.mapping_file.mappings:
            self._apply_mapping_item(mapping_item, source_data, target_data)
        
        # Apply post-processing based on config
        if self.config.get("null_handling") == "omit":
            target_data = self._remove_nulls(target_data)
        
        return target_data
    
    def _apply_mapping_item(self, item: Union[Mapping, ConditionalBlock, NestedBlock],
                           source_data: Dict, target_data: Dict) -> None:
        """Apply a single mapping item."""
        if isinstance(item, Mapping):
            self._apply_mapping(item, source_data, target_data)
        elif isinstance(item, ConditionalBlock):
            self._apply_conditional(item, source_data, target_data)
        elif isinstance(item, NestedBlock):
            self._apply_nested_block(item, source_data, target_data)
    
    def _apply_mapping(self, mapping: Mapping, source_data: Dict, target_data: Dict) -> None:
        """Apply a single mapping rule."""
        # Skip mappings
        if isinstance(mapping.target, SkipTarget):
            return
        
        # Get source value
        value = self._get_source_value(mapping.source, source_data)
        
        # Check if source is optional and value is None
        if value is None:
            if isinstance(mapping.source, SourcePath) and mapping.source.is_optional:
                return
            if self.config.get("missing_fields") == "skip":
                return
        
        # Apply transforms
        value = self._apply_transforms(value, mapping.transforms)
        
        # Set target value
        self._set_target_value(mapping.target, value, target_data)
    
    def _get_source_value(self, source: Union[SourcePath, MergeExpression, 
                                              ComputeExpression, ConstantValue],
                         source_data: Dict) -> Any:
        """Get value from the source expression."""
        if isinstance(source, ConstantValue):
            return source.value
        
        if isinstance(source, ComputeExpression):
            return self._evaluate_compute(source, source_data)
        
        if isinstance(source, MergeExpression):
            return self._evaluate_merge(source, source_data)
        
        if isinstance(source, SourcePath):
            path = str(source)
            return self.evaluator.get_value(path, source_data)
        
        return None
    
    def _evaluate_compute(self, expr: ComputeExpression, source_data: Dict) -> Any:
        """
        Evaluate a compute expression.
        
        Supports:
        - @now - Current timestamp
        - @uuid - Generate UUID
        - @compute(expression) - Evaluate expression with external functions
        - @call(func_name, args...) - Explicit function call
        """
        if expr.type == "now":
            return datetime.now().isoformat() + "Z"
        
        if expr.type == "uuid":
            return str(uuid.uuid4())
        
        if expr.type == "call":
            # Direct function call: @call(func_name, arg1, arg2)
            return self._evaluate_function_call(expr.expression, source_data)
        
        # Standard compute expression
        return self.evaluator.evaluate_expression(expr.expression, source_data)
    
    def _evaluate_function_call(self, expr: str, source_data: Dict) -> Any:
        """Evaluate a direct function call expression."""
        # Parse: func_name, arg1, arg2, ...
        parts = expr.split(",", 1)
        func_name = parts[0].strip()
        
        if not self.function_registry.has_function(func_name):
            raise TransformError(f"Unknown function: {func_name}")
        
        args = []
        if len(parts) > 1:
            args = self.evaluator._parse_function_args(parts[1], source_data)
        
        return self.function_registry.call(func_name, *args)
    
    def _evaluate_merge(self, merge: MergeExpression, source_data: Dict) -> Any:
        """Evaluate a merge expression."""
        if merge.operator == "+":
            # Concatenation
            parts = []
            for part in merge.parts:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, SourcePath):
                    val = self.evaluator.get_value(str(part), source_data)
                    if val is not None:
                        parts.append(str(val))
            return "".join(parts)
        
        elif merge.operator == "??":
            # Coalesce
            for part in merge.parts:
                if isinstance(part, SourcePath):
                    val = self.evaluator.get_value(str(part), source_data)
                    if val is not None:
                        return val
                elif isinstance(part, str):
                    return part
            return None
        
        return None
    
    def _apply_transforms(self, value: Any, transforms: TransformChain) -> Any:
        """Apply a chain of transformations to a value, handling arrays."""
        if not transforms.transforms:
            return value
        
        # If value is a list, apply transforms to each element
        if isinstance(value, list):
            return [self._apply_transforms_single(v, transforms) for v in value]
        
        return self._apply_transforms_single(value, transforms)
    
    def _apply_transforms_single(self, value: Any, transforms: TransformChain) -> Any:
        """Apply transforms to a single value."""
        for transform in transforms.transforms:
            value = self.evaluator.apply_transform(
                value, transform.name, transform.args, transform.is_alias
            )
        return value
    
    def _set_target_value(self, target: TargetPath, value: Any, target_data: Dict) -> None:
        """Set a value in the target data."""
        path = str(target)
        self.evaluator.set_value(path, value, target_data)
    
    def _apply_conditional(self, conditional: ConditionalBlock, 
                          source_data: Dict, target_data: Dict) -> None:
        """Apply a conditional block."""
        if conditional.condition is None:
            # This is an @else block
            for mapping in conditional.mappings:
                self._apply_mapping_item(mapping, source_data, target_data)
        else:
            # Check condition
            if self.evaluator.evaluate_condition(conditional.condition, source_data):
                for mapping in conditional.mappings:
                    self._apply_mapping_item(mapping, source_data, target_data)
    
    def _apply_nested_block(self, block: NestedBlock, 
                           source_data: Dict, target_data: Dict) -> None:
        """Apply a nested block of mappings."""
        for mapping in block.mappings:
            self._apply_mapping_item(mapping, source_data, target_data)
    
    def _remove_nulls(self, data: Any) -> Any:
        """Recursively remove null values from data."""
        if isinstance(data, dict):
            return {k: self._remove_nulls(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [self._remove_nulls(v) for v in data if v is not None]
        return data
    
    def transform_batch(self, items: List[Dict]) -> List[Dict]:
        """
        Transform a batch of items.
        
        Args:
            items: List of source JSON objects
            
        Returns:
            List of transformed JSON objects
        """
        return [self.transform(item) for item in items]
