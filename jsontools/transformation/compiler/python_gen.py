"""
SchemaMap Python Code Generator

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Compiles SchemaMap DSL to optimized, standalone Python code.
Generated code runs 10-100x faster than interpreted transformations.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from textwrap import dedent

from ..parser.parser import (
    MappingFile, Mapping, ConditionalBlock, NestedBlock,
    SourcePath, TargetPath, MergeExpression, ComputeExpression,
    ConstantValue, SkipTarget, TransformChain, Transform,
    AliasDefinition, LookupDefinition, FunctionDefinition
)


class PythonCodeGenerator:
    """
    Generates optimized Python code from SchemaMap AST.
    
    The generated code is:
    - Standalone (no SchemaMap runtime dependency)
    - Optimized (transforms inlined, no function lookups)
    - Type-hinted (for IDE support)
    - Fast (10-100x faster than interpretation)
    
    Example:
        generator = PythonCodeGenerator(class_name="CustomerTransformer")
        code = generator.generate(mapping_file)
        
        # Save and use
        with open("customer_transformer.py", "w") as f:
            f.write(code)
        
        from customer_transformer import CustomerTransformer
        transformer = CustomerTransformer()
        result = transformer.transform(source_data)
    """
    
    def __init__(self, class_name: str = "GeneratedTransformer",
                 include_benchmarks: bool = False,
                 include_type_hints: bool = True):
        self.class_name = class_name
        self.include_benchmarks = include_benchmarks
        self.include_type_hints = include_type_hints
        self._lookups: Dict[str, Any] = {}
        self._aliases: Dict[str, AliasDefinition] = {}
    
    def generate(self, mapping_file: MappingFile) -> str:
        """Generate Python code from a MappingFile AST."""
        self._lookups = {}
        self._aliases = mapping_file.aliases
        
        # Load lookups
        for name, lookup_def in mapping_file.lookups.items():
            if isinstance(lookup_def.source, dict):
                self._lookups[name] = lookup_def.source
        
        # Get config
        config = mapping_file.config
        null_handling = config.get("null_handling", "keep")
        
        # Generate lookup dict literal
        lookup_code = self._generate_lookup_dict()
        
        # Generate mapping code
        mapping_code = self._generate_mappings(mapping_file.mappings)
        
        source_file = mapping_file.source_file or "unknown"
        timestamp = datetime.now().isoformat()
        
        code = f'''"""
Generated Transformer Code

Auto-generated from: {source_file}
Generated at: {timestamp}
Generator: JsonTools SchemaMap Compiler v1.4.0

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

DO NOT EDIT - This file is auto-generated.
Regenerate from source .smap file if changes are needed.
"""

from __future__ import annotations
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable


class {self.class_name}:
    """
    Compiled SchemaMap Transformer
    
    This class was auto-generated from a SchemaMap DSL file.
    It provides optimized JSON transformation without runtime parsing.
    """

    def __init__(self):
        """Initialize the transformer."""
        self._lookups = {lookup_code}
        self._external_functions: Dict[str, Callable] = {{}}
        self._null_handling = "{null_handling}"

    def register_function(self, name: str, func: Callable) -> "{self.class_name}":
        """Register an external function for use in transformations."""
        self._external_functions[name] = func
        return self

    def transform(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform source data to target format.
        
        Args:
            source: Source JSON data as dictionary
        
        Returns:
            Transformed JSON data as dictionary
        """
        target: Dict[str, Any] = {{}}
        
{mapping_code}
        
        # Post-processing
        if self._null_handling == "omit":
            target = self._remove_nulls(target)
        
        return target

    def transform_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform a batch of items."""
        return [self.transform(item) for item in items]

    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _get_value(self, data: Any, path: str) -> Any:
        """Get a value from nested dict using dot notation."""
        if not path or data is None:
            return data
        
        current = data
        for segment in path.replace("?", "").split("."):
            if current is None:
                return None
            
            # Handle array access like items[0] or items[*]
            if "[" in segment:
                key = segment[:segment.index("[")]
                idx_str = segment[segment.index("[")+1:segment.index("]")]
                
                if key:
                    current = current.get(key) if isinstance(current, dict) else None
                
                if current is None:
                    return None
                
                if isinstance(current, list):
                    if idx_str == "*":
                        return current
                    try:
                        idx = int(idx_str)
                        current = current[idx] if -len(current) <= idx < len(current) else None
                    except (ValueError, IndexError):
                        return None
            else:
                current = current.get(segment) if isinstance(current, dict) else None
        
        return current

    def _set_value(self, data: Dict, path: str, value: Any) -> None:
        """Set a value in nested dict using dot notation."""
        segments = path.split(".")
        current = data
        
        for segment in segments[:-1]:
            if "[" in segment:
                key = segment[:segment.index("[")]
                if key not in current:
                    current[key] = []
                current = current[key]
            else:
                if segment not in current:
                    current[segment] = {{}}
                current = current[segment]
        
        final = segments[-1]
        if "[" in final:
            key = final[:final.index("[")]
            if key not in current:
                current[key] = []
            if isinstance(value, list):
                current[key] = value
            else:
                current[key].append(value)
        else:
            current[final] = value

    def _get_array_values(self, data: Dict, path: str) -> List[Any]:
        """Get values from array elements using [*] notation."""
        if "[*]" not in path:
            return self._get_value(data, path)
        
        parts = path.split("[*]")
        array_path = parts[0]
        suffix = parts[1].lstrip(".") if len(parts) > 1 else ""
        
        array = self._get_value(data, array_path)
        if not isinstance(array, list):
            return []
        
        if not suffix:
            return array
        
        return [self._get_value(item, suffix) for item in array]

    def _remove_nulls(self, data: Any) -> Any:
        """Recursively remove null values from data."""
        if isinstance(data, dict):
            return {{k: self._remove_nulls(v) for k, v in data.items() if v is not None}}
        elif isinstance(data, list):
            return [self._remove_nulls(v) for v in data if v is not None]
        return data

    def _coalesce(self, *values) -> Any:
        """Return first non-None value."""
        for v in values:
            if v is not None:
                return v
        return None

    def _lookup(self, table_name: str, value: Any) -> Any:
        """Look up a value in a lookup table."""
        table = self._lookups.get(table_name, {{}})
        return table.get(value, value)

    def _call_function(self, func_name: str, *args) -> Any:
        """Call a registered external function."""
        func = self._external_functions.get(func_name)
        if func:
            return func(*args)
        return None

    def _evaluate_expr(self, expr: str, source: Dict) -> Any:
        """Evaluate a compute expression."""
        # Handle aggregations: sum(), count(), avg()
        import re as _re
        match = _re.match(r"(\\w+)\\((.+)\\)", expr)
        if match:
            func_name = match.group(1)
            inner = match.group(2)
            values = self._get_value(source, inner)
            
            if func_name == "sum" and isinstance(values, list):
                return sum(float(v) for v in values if v is not None)
            elif func_name == "count":
                return len(values) if isinstance(values, list) else (1 if values else 0)
            elif func_name == "avg" and isinstance(values, list) and values:
                nums = [float(v) for v in values if v is not None]
                return sum(nums) / len(nums) if nums else 0
            elif func_name in self._external_functions:
                # Parse args and call external function
                args = self._parse_args(inner, source)
                return self._external_functions[func_name](*args)
        
        return self._get_value(source, expr)

    def _parse_args(self, args_str: str, source: Dict) -> List[Any]:
        """Parse function arguments from string."""
        args = []
        for arg in args_str.split(","):
            arg = arg.strip()
            # Try as number
            try:
                args.append(float(arg) if "." in arg else int(arg))
                continue
            except ValueError:
                pass
            # Try as string literal
            if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                args.append(arg[1:-1])
                continue
            # Try as path
            args.append(self._get_value(source, arg))
        return args


if __name__ == "__main__":
    import json
    import sys
    
    transformer = {self.class_name}()
    
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            source_data = json.load(f)
    else:
        source_data = {{"example": "data"}}
    
    result = transformer.transform(source_data)
    print(json.dumps(result, indent=2, default=str))
'''
        return code
    
    def _generate_lookup_dict(self) -> str:
        """Generate Python dict literal for lookups."""
        if not self._lookups:
            return "{}"
        
        parts = ["{"]
        for name, table in self._lookups.items():
            parts.append(f'            "{name}": {{')
            for k, v in table.items():
                parts.append(f'                "{k}": "{v}",')
            parts.append("            },")
        parts.append("        }")
        return "\n".join(parts)
    
    def _generate_mappings(self, mappings: List, indent: int = 8) -> str:
        """Generate code for all mappings."""
        lines = []
        ind = " " * indent
        
        for item in mappings:
            if isinstance(item, Mapping):
                lines.extend(self._generate_mapping(item, indent))
            elif isinstance(item, ConditionalBlock):
                lines.extend(self._generate_conditional(item, indent))
        
        return "\n".join(lines)
    
    def _generate_mapping(self, mapping: Mapping, indent: int) -> List[str]:
        """Generate code for a single mapping."""
        ind = " " * indent
        lines = []
        
        if isinstance(mapping.target, SkipTarget):
            return lines
        
        target_path = str(mapping.target)
        source_expr = self._source_to_code(mapping.source, indent)
        
        # Check if optional
        is_optional = isinstance(mapping.source, SourcePath) and mapping.source.is_optional
        
        if is_optional:
            lines.append(f"{ind}try:")
            ind2 = " " * (indent + 4)
        else:
            ind2 = ind
        
        lines.append(f"{ind2}_v = {source_expr}")
        
        # Apply transforms
        for transform in mapping.transforms.transforms:
            transform_code = self._transform_to_code(transform)
            lines.append(f"{ind2}_v = {transform_code}")
        
        lines.append(f'{ind2}self._set_value(target, "{target_path}", _v)')
        
        if is_optional:
            lines.append(f"{ind}except (KeyError, TypeError, IndexError):")
            lines.append(f"{ind}    pass")
        
        lines.append("")
        return lines
    
    def _source_to_code(self, source, indent: int) -> str:
        """Convert source expression to Python code."""
        if isinstance(source, ConstantValue):
            return repr(source.value)
        
        if isinstance(source, ComputeExpression):
            if source.type == "now":
                return 'datetime.now().isoformat() + "Z"'
            elif source.type == "uuid":
                return "str(uuid.uuid4())"
            elif source.type == "call":
                # Parse function call: func_name, arg1, arg2
                parts = source.expression.split(",", 1)
                func_name = parts[0].strip()
                if len(parts) > 1:
                    args = parts[1].strip()
                    return f'self._call_function("{func_name}", *self._parse_args("{args}", source))'
                return f'self._call_function("{func_name}")'
            else:
                return f'self._evaluate_expr("{source.expression}", source)'
        
        if isinstance(source, MergeExpression):
            if source.operator == "+":
                parts = []
                for part in source.parts:
                    if isinstance(part, str):
                        parts.append(repr(part))
                    elif isinstance(part, SourcePath):
                        path = str(part)
                        parts.append(f'str(self._get_value(source, "{path}") or "")')
                return "(" + " + ".join(parts) + ")"
            elif source.operator == "??":
                parts = []
                for part in source.parts:
                    if isinstance(part, str):
                        parts.append(repr(part))
                    elif isinstance(part, SourcePath):
                        path = str(part)
                        parts.append(f'self._get_value(source, "{path}")')
                return f"self._coalesce({', '.join(parts)})"
        
        if isinstance(source, SourcePath):
            path = str(source)
            if "[*]" in path:
                return f'self._get_array_values(source, "{path}")'
            return f'self._get_value(source, "{path}")'
        
        return "None"
    
    def _transform_to_code(self, transform: Transform) -> str:
        """Convert transform to inline Python code."""
        name = transform.name
        args = transform.args
        
        # Handle aliases - expand inline
        if transform.is_alias:
            alias_def = self._aliases.get(name)
            if alias_def:
                code = "_v"
                for t in alias_def.transforms.transforms:
                    inner = self._transform_to_code(t)
                    code = inner.replace("_v", code)
                return code
            return "_v"
        
        # Inline common transforms for speed
        if name == "trim":
            return "str(_v).strip() if _v is not None else None"
        elif name == "lowercase":
            return "str(_v).lower() if _v is not None else None"
        elif name == "uppercase":
            return "str(_v).upper() if _v is not None else None"
        elif name == "titlecase":
            return "str(_v).title() if _v is not None else None"
        elif name == "capitalize":
            return "str(_v).capitalize() if _v is not None else None"
        elif name == "to_int":
            return "int(float(_v)) if _v is not None else None"
        elif name == "to_float":
            return "float(_v) if _v is not None else None"
        elif name == "to_string":
            return "str(_v) if _v is not None else None"
        elif name == "to_bool":
            return "bool(_v) if _v is not None else None"
        elif name == "round":
            decimals = args[0] if args else 2
            return f"round(float(_v), {decimals}) if _v is not None else None"
        elif name == "abs":
            return "abs(float(_v)) if _v is not None else None"
        elif name == "floor":
            return "int(float(_v)) if _v is not None else None"
        elif name == "ceil":
            return "int(float(_v)) + (1 if float(_v) % 1 else 0) if _v is not None else None"
        elif name == "default":
            default_val = repr(args[0]) if args else "None"
            return f"_v if _v is not None else {default_val}"
        elif name == "replace":
            old = repr(args[0]) if args else "''"
            new = repr(args[1]) if len(args) > 1 else "''"
            return f"str(_v).replace({old}, {new}) if _v is not None else None"
        elif name == "regex_replace":
            pattern = repr(args[0]) if args else "''"
            repl = repr(args[1]) if len(args) > 1 else "''"
            return f"re.sub({pattern}, {repl}, str(_v)) if _v is not None else None"
        elif name == "prefix":
            prefix = repr(args[0]) if args else "''"
            return f"{prefix} + str(_v) if _v is not None else None"
        elif name == "suffix":
            suffix = repr(args[0]) if args else "''"
            return f"str(_v) + {suffix} if _v is not None else None"
        elif name == "max_length":
            length = args[0] if args else 255
            return f"str(_v)[:{length}] if _v is not None else None"
        elif name == "split":
            delim = repr(args[0]) if args else "','"
            return f"str(_v).split({delim}) if _v is not None else None"
        elif name == "join":
            delim = repr(args[0]) if args else "','"
            return f"{delim}.join(_v) if isinstance(_v, list) else _v"
        elif name == "collapse_spaces":
            return "re.sub(r'\\\\s+', ' ', str(_v)).strip() if _v is not None else None"
        elif name == "first":
            return "_v[0] if _v and isinstance(_v, list) else _v"
        elif name == "last":
            return "_v[-1] if _v and isinstance(_v, list) else _v"
        elif name == "count":
            return "len(_v) if isinstance(_v, list) else (1 if _v else 0)"
        elif name == "lookup":
            if args:
                lookup_ref = args[0]
                if isinstance(lookup_ref, str) and lookup_ref.startswith("@"):
                    lookup_name = lookup_ref[1:]
                else:
                    lookup_name = str(lookup_ref)
                return f'self._lookup("{lookup_name}", _v)'
            return "_v"
        elif name == "when":
            if len(args) >= 2:
                match_val = repr(args[0])
                result_val = repr(args[1])
                return f"{result_val} if _v == {match_val} else _v"
            return "_v"
        elif name == "constant":
            return "_v"
        else:
            # Unknown - pass through
            return "_v"
    
    def _generate_conditional(self, cond: ConditionalBlock, indent: int) -> List[str]:
        """Generate code for conditional block."""
        ind = " " * indent
        lines = []
        
        if cond.condition:
            field = cond.condition.field
            op = cond.condition.operator
            value = repr(cond.condition.value)
            py_op = {"==": "==", "!=": "!=", ">": ">", "<": "<", ">=": ">=", "<=": "<="}.get(op, "==")
            
            lines.append(f'{ind}if self._get_value(source, "{field}") {py_op} {value}:')
            
            for m in cond.mappings:
                if isinstance(m, Mapping):
                    lines.extend(self._generate_mapping(m, indent + 4))
        else:
            for m in cond.mappings:
                if isinstance(m, Mapping):
                    lines.extend(self._generate_mapping(m, indent))
        
        return lines
