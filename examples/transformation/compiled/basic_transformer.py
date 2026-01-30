"""
Generated Transformer Code

Auto-generated from: examples/transformation/mappings/basic_test.smap
Generated at: 2026-01-30T02:12:20.185011
Generator: JsonChamp SchemaMap Compiler v1.4.0

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


class BasicTransformer:
    """
    Compiled SchemaMap Transformer
    
    This class was auto-generated from a SchemaMap DSL file.
    It provides optimized JSON transformation without runtime parsing.
    """

    def __init__(self):
        """Initialize the transformer."""
        self._lookups = {}
        self._external_functions: Dict[str, Callable] = {}
        self._null_handling = "omit"

    def register_function(self, name: str, func: Callable) -> "BasicTransformer":
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
        target: Dict[str, Any] = {}
        
        _v = self._get_value(source, "user.id")
        self._set_value(target, "userId", _v)

        _v = self._get_value(source, "user.first_name")
        _v = str(_v).strip() if _v is not None else None
        _v = str(_v).title() if _v is not None else None
        self._set_value(target, "profile.firstName", _v)

        _v = self._get_value(source, "user.last_name")
        _v = str(_v).strip() if _v is not None else None
        _v = str(_v).title() if _v is not None else None
        self._set_value(target, "profile.lastName", _v)

        _v = (str(self._get_value(source, "user.first_name") or "") + ' ' + str(self._get_value(source, "user.last_name") or ""))
        _v = str(_v).strip() if _v is not None else None
        self._set_value(target, "profile.fullName", _v)

        _v = self._get_value(source, "user.email")
        _v = str(_v).lower() if _v is not None else None
        _v = str(_v).strip() if _v is not None else None
        self._set_value(target, "contactEmail", _v)

        _v = self._get_value(source, "user.age")
        _v = int(float(_v)) if _v is not None else None
        self._set_value(target, "age", _v)

        _v = self._get_value(source, "user.street")
        self._set_value(target, "address.line1", _v)

        _v = self._get_value(source, "user.city")
        _v = str(_v).title() if _v is not None else None
        self._set_value(target, "address.city", _v)

        _v = self._get_value(source, "user.zip")
        self._set_value(target, "address.postalCode", _v)

        _v = '1.0'
        _v = _v
        self._set_value(target, "version", _v)

        _v = datetime.now().isoformat() + "Z"
        self._set_value(target, "transformedAt", _v)

        
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
                    current[segment] = {}
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
            return {k: self._remove_nulls(v) for k, v in data.items() if v is not None}
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
        table = self._lookups.get(table_name, {})
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
        match = _re.match(r"(\w+)\((.+)\)", expr)
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
    
    transformer = BasicTransformer()
    
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            source_data = json.load(f)
    else:
        source_data = {"example": "data"}
    
    result = transformer.transform(source_data)
    print(json.dumps(result, indent=2, default=str))
