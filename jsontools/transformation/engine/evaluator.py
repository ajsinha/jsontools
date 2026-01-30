"""
SchemaMap Expression Evaluator

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Evaluates expressions and transforms within SchemaMap DSL.
Supports calling external Python functions for custom transformations.
"""

from __future__ import annotations
import re
import operator
import importlib
import importlib.util
from typing import Any, Callable, Dict, List, Optional, Union
from pathlib import Path
from .functions import BuiltinFunctions


class ExternalFunctionError(Exception):
    """Exception raised when external function call fails."""
    pass


class ExpressionEvaluator:
    """
    Evaluates expressions in SchemaMap transformations.
    
    Supports:
    - Built-in transform functions
    - Alias references
    - Lookup tables
    - External Python functions via @compute
    """
    
    def __init__(self, context: Dict[str, Any] = None, lookups: Dict[str, Dict] = None,
                 aliases: Dict[str, Any] = None, external_functions: Dict[str, Callable] = None):
        """
        Initialize the evaluator.
        
        Args:
            context: The source data context
            lookups: Lookup tables for value mapping
            aliases: Alias definitions for reusable transforms
            external_functions: Dictionary of external Python functions
        """
        self.context = context or {}
        self.lookups = lookups or {}
        self.aliases = aliases or {}
        self.external_functions = external_functions or {}
        self._when_state = {}
        self._modules = {}  # Cache for loaded modules
    
    def register_function(self, name: str, func: Callable) -> None:
        """
        Register an external function for use in @compute expressions.
        
        Args:
            name: Function name to use in expressions
            func: Python callable
            
        Example:
            def calculate_tax(amount, rate):
                return amount * rate
            
            evaluator.register_function("calculate_tax", calculate_tax)
        """
        if not callable(func):
            raise ValueError(f"'{name}' must be callable")
        self.external_functions[name] = func
    
    def register_functions_from_dict(self, functions: Dict[str, Callable]) -> None:
        """
        Register multiple external functions from a dictionary.
        
        Args:
            functions: Dictionary mapping names to callables
        """
        for name, func in functions.items():
            self.register_function(name, func)
    
    def register_functions_from_module(self, module_path: str, 
                                        function_names: List[str] = None) -> None:
        """
        Register functions from a Python module file.
        
        Args:
            module_path: Path to Python module file
            function_names: Optional list of function names to import.
                          If None, imports all public functions.
        
        Example:
            evaluator.register_functions_from_module(
                "custom_transforms.py",
                ["calculate_tax", "format_currency"]
            )
        """
        path = Path(module_path)
        if not path.exists():
            raise FileNotFoundError(f"Module not found: {module_path}")
        
        # Load module dynamically
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Cache the module
        self._modules[path.stem] = module
        
        # Get functions to register
        if function_names is None:
            # Import all public functions
            function_names = [
                name for name in dir(module)
                if not name.startswith('_') and callable(getattr(module, name))
            ]
        
        for name in function_names:
            if hasattr(module, name):
                func = getattr(module, name)
                if callable(func):
                    self.external_functions[name] = func
    
    def register_functions_from_class(self, cls: type, instance: Any = None) -> None:
        """
        Register methods from a class as external functions.
        
        Args:
            cls: Class containing methods to register
            instance: Optional instance for bound methods
        """
        for name in dir(cls):
            if not name.startswith('_'):
                method = getattr(cls, name)
                if callable(method):
                    if instance:
                        self.external_functions[name] = getattr(instance, name)
                    else:
                        self.external_functions[name] = method
    
    def get_value(self, path: str, data: Dict[str, Any] = None) -> Any:
        """Get a value from the data using a dotted path with array support."""
        if data is None:
            data = self.context
        
        if not path:
            return data
        
        if path.startswith("."):
            path = path[1:]
        
        # Handle array wildcard paths like items[*].name
        if "[*]" in path:
            return self._get_array_values(path, data)
        
        segments = self._parse_path(path)
        current = data
        
        for segment in segments:
            if current is None:
                return None
            
            if isinstance(segment, int):
                if isinstance(current, list):
                    if -len(current) <= segment < len(current):
                        current = current[segment]
                    else:
                        return None
                else:
                    return None
            elif segment == "*":
                if isinstance(current, list):
                    return current
                return None
            else:
                # Check for embedded array index like items[0]
                match = re.match(r'^([^\[]+)\[(\d+)\]$', str(segment))
                if match:
                    base = match.group(1)
                    idx = int(match.group(2))
                    if isinstance(current, dict):
                        current = current.get(base)
                        if isinstance(current, list) and -len(current) <= idx < len(current):
                            current = current[idx]
                        else:
                            return None
                    else:
                        return None
                elif isinstance(current, dict):
                    current = current.get(segment)
                else:
                    return None
        
        return current
    
    def _get_array_values(self, path: str, data: Dict[str, Any]) -> List[Any]:
        """Get values from array using wildcard notation like items[*].name."""
        # Split at [*]
        parts = path.split("[*]", 1)
        array_path = parts[0]
        suffix = parts[1].lstrip(".") if len(parts) > 1 and parts[1] else ""
        
        # Get the array
        array = self.get_value(array_path, data)
        if not isinstance(array, list):
            return []
        
        # If no suffix, return the array as is
        if not suffix:
            return array
        
        # Extract values from each item
        result = []
        for item in array:
            if isinstance(item, dict):
                val = self.get_value(suffix, item)
                result.append(val)
            else:
                result.append(item)
        
        return result
    
    def set_value(self, path: str, value: Any, data: Dict[str, Any]) -> None:
        """Set a value in the data using a dotted path, handling array wildcards."""
        segments = self._parse_path(path)
        
        # Check if this is an array wildcard mapping
        if "*" in segments:
            self._set_array_value(segments, value, data)
            return
        
        current = data
        for i, segment in enumerate(segments[:-1]):
            if isinstance(segment, int):
                while len(current) <= segment:
                    current.append({})
                if current[segment] is None:
                    current[segment] = {}
                current = current[segment]
            else:
                if segment not in current or current[segment] is None:
                    next_seg = segments[i + 1] if i + 1 < len(segments) else None
                    if isinstance(next_seg, int):
                        current[segment] = []
                    else:
                        current[segment] = {}
                current = current[segment]
        
        final_segment = segments[-1]
        if isinstance(final_segment, int):
            while len(current) <= final_segment:
                current.append(None)
            current[final_segment] = value
        else:
            current[final_segment] = value
    
    def _set_array_value(self, segments: List[Any], value: Any, data: Dict[str, Any]) -> None:
        """Handle setting values with array wildcards like items[*].name."""
        # Find the wildcard position
        star_idx = segments.index("*")
        
        # Segments before the wildcard (e.g., ['items'])
        before = segments[:star_idx]
        # Segments after the wildcard (e.g., ['name'])
        after = segments[star_idx + 1:]
        
        # Navigate to the array container
        current = data
        for segment in before:
            if segment not in current:
                current[segment] = []
            current = current[segment]
        
        # Ensure we have a list
        if not isinstance(current, list):
            return
        
        # If value is a list, map each value to array elements
        if isinstance(value, list):
            # Extend the array if needed
            while len(current) < len(value):
                current.append({})
            
            # Set each value
            for i, val in enumerate(value):
                if after:
                    # Navigate nested path and set value
                    target = current[i]
                    if not isinstance(target, dict):
                        current[i] = {}
                        target = current[i]
                    
                    for j, seg in enumerate(after[:-1]):
                        if seg not in target:
                            target[seg] = {}
                        target = target[seg]
                    
                    target[after[-1]] = val
                else:
                    current[i] = val
        else:
            # Single value - append or set
            if after:
                new_item = {}
                target = new_item
                for j, seg in enumerate(after[:-1]):
                    target[seg] = {}
                    target = target[seg]
                target[after[-1]] = value
                current.append(new_item)
            else:
                current.append(value)
    
    def _parse_path(self, path: str) -> List[Any]:
        """Parse a path string into segments."""
        segments = []
        current = ""
        i = 0
        
        while i < len(path):
            char = path[i]
            
            if char == ".":
                if current:
                    segments.append(current)
                current = ""
            elif char == "[":
                if current:
                    segments.append(current)
                current = ""
                j = path.index("]", i)
                index_str = path[i+1:j]
                if index_str == "*":
                    segments.append("*")
                else:
                    try:
                        segments.append(int(index_str))
                    except ValueError:
                        segments.append(index_str)
                i = j
            else:
                current += char
            
            i += 1
        
        if current:
            segments.append(current)
        
        return segments
    
    def apply_transform(self, value: Any, transform_name: str, args: List[Any],
                       is_alias: bool = False) -> Any:
        """Apply a transformation function to a value."""
        if is_alias:
            alias_def = self.aliases.get(transform_name)
            if alias_def:
                for t in alias_def.transforms.transforms:
                    value = self.apply_transform(value, t.name, t.args, t.is_alias)
                return value
            return value
        
        # Handle lookup
        if transform_name == "lookup":
            if args:
                lookup_ref = args[0]
                if isinstance(lookup_ref, str) and lookup_ref.startswith("@"):
                    lookup_name = lookup_ref[1:]
                else:
                    lookup_name = str(lookup_ref)
                
                lookup_table = self.lookups.get(lookup_name, {})
                
                if isinstance(lookup_table, dict):
                    if value in lookup_table:
                        return lookup_table[value]
                
            return value
        
        # Handle when/else
        if transform_name == "when":
            if len(args) >= 2:
                match_value = args[0]
                result_value = args[1]
                if value == match_value:
                    self._when_state["matched"] = True
                    return result_value
                return value
            return value
        
        if transform_name == "else":
            if not self._when_state.get("matched"):
                return args[0] if args else value
            self._when_state["matched"] = False
            return value
        
        # Check external functions first
        if transform_name in self.external_functions:
            try:
                func = self.external_functions[transform_name]
                if args:
                    return func(value, *args)
                return func(value)
            except Exception as e:
                raise ExternalFunctionError(
                    f"Error calling external function '{transform_name}': {e}"
                )
        
        # Get built-in function
        func = BuiltinFunctions.get_function(transform_name)
        if func:
            try:
                if args:
                    return func(value, *args)
                return func(value)
            except Exception:
                return value
        
        return value
    
    def evaluate_expression(self, expr: str, data: Dict[str, Any] = None) -> Any:
        """
        Evaluate an expression, including external function calls.
        
        Supports:
        - Simple paths: "user.name"
        - Aggregations: sum(items[*].price), count(items)
        - External functions: my_func(field1, field2)
        - Arithmetic: field1 + field2
        """
        if data is None:
            data = self.context
        
        expr = expr.strip()
        
        # Check for function call pattern: func_name(args)
        match = re.match(r"(\w+)\((.+)\)", expr)
        if match:
            func_name = match.group(1)
            args_str = match.group(2).strip()
            
            # Built-in aggregations
            if func_name in ("sum", "count", "avg", "min", "max"):
                return self._evaluate_aggregation(func_name, args_str, data)
            
            # Check for external function
            if func_name in self.external_functions:
                return self._call_external_function(func_name, args_str, data)
        
        # Handle arithmetic
        for op_str, op_func in [("*", operator.mul), ("/", operator.truediv),
                                 ("+", operator.add), ("-", operator.sub)]:
            if op_str in expr:
                parts = expr.split(op_str, 1)
                if len(parts) == 2:
                    left = self.evaluate_expression(parts[0].strip(), data)
                    right = self.evaluate_expression(parts[1].strip(), data)
                    if left is not None and right is not None:
                        try:
                            return op_func(float(left), float(right))
                        except (ValueError, TypeError):
                            pass
        
        # Try as path
        return self.get_value(expr, data)
    
    def _evaluate_aggregation(self, func_name: str, args_str: str, 
                              data: Dict[str, Any]) -> Any:
        """Evaluate built-in aggregation functions."""
        values = self.get_value(args_str, data)
        
        if func_name == "sum":
            if isinstance(values, list):
                return sum(float(v) for v in values if v is not None)
            return float(values) if values else 0
        
        if func_name == "count":
            if isinstance(values, list):
                return len(values)
            return 1 if values is not None else 0
        
        if func_name == "avg":
            if isinstance(values, list) and values:
                return sum(float(v) for v in values if v is not None) / len(values)
            return 0
        
        if func_name == "min":
            if isinstance(values, list) and values:
                return min(v for v in values if v is not None)
            return values
        
        if func_name == "max":
            if isinstance(values, list) and values:
                return max(v for v in values if v is not None)
            return values
        
        return None
    
    def _call_external_function(self, func_name: str, args_str: str,
                                data: Dict[str, Any]) -> Any:
        """
        Call an external function with parsed arguments.
        
        Args can be:
        - Field paths: user.name
        - Literals: "string", 123, true
        - Nested function calls: other_func(x)
        """
        func = self.external_functions[func_name]
        
        # Parse arguments
        args = self._parse_function_args(args_str, data)
        
        try:
            return func(*args)
        except Exception as e:
            raise ExternalFunctionError(
                f"Error calling '{func_name}' with args {args}: {e}"
            )
    
    def _parse_function_args(self, args_str: str, data: Dict[str, Any]) -> List[Any]:
        """Parse function arguments from string."""
        args = []
        current_arg = ""
        paren_depth = 0
        in_string = False
        string_char = None
        
        for char in args_str + ",":
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
                current_arg += char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
                current_arg += char
            elif char == "(" and not in_string:
                paren_depth += 1
                current_arg += char
            elif char == ")" and not in_string:
                paren_depth -= 1
                current_arg += char
            elif char == "," and paren_depth == 0 and not in_string:
                # End of argument
                arg = current_arg.strip()
                if arg:
                    args.append(self._evaluate_arg(arg, data))
                current_arg = ""
            else:
                current_arg += char
        
        return args
    
    def _evaluate_arg(self, arg: str, data: Dict[str, Any]) -> Any:
        """Evaluate a single function argument."""
        arg = arg.strip()
        
        # String literal
        if (arg.startswith('"') and arg.endswith('"')) or \
           (arg.startswith("'") and arg.endswith("'")):
            return arg[1:-1]
        
        # Number literal
        try:
            if "." in arg:
                return float(arg)
            return int(arg)
        except ValueError:
            pass
        
        # Boolean literals
        if arg.lower() == "true":
            return True
        if arg.lower() == "false":
            return False
        if arg.lower() == "null" or arg.lower() == "none":
            return None
        
        # Nested function call
        if "(" in arg:
            return self.evaluate_expression(arg, data)
        
        # Field path
        return self.get_value(arg, data)
    
    def evaluate_condition(self, condition: Any, data: Dict[str, Any]) -> bool:
        """Evaluate a conditional expression."""
        if condition is None:
            return True
        
        field_value = self.get_value(condition.field, data)
        target_value = condition.value
        
        op = condition.operator
        if op == "==":
            return field_value == target_value
        elif op == "!=":
            return field_value != target_value
        elif op == ">":
            return field_value > target_value
        elif op == "<":
            return field_value < target_value
        elif op == ">=":
            return field_value >= target_value
        elif op == "<=":
            return field_value <= target_value
        
        return False
