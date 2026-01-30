"""
SchemaMap Python Code Generator

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Compiles SchemaMap DSL to optimized, standalone Python code.
"""

from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime

from ..parser.parser import (
    MappingFile, Mapping, SourcePath, TargetPath, MergeExpression, 
    ComputeExpression, ConstantValue, SkipTarget, Transform, AliasDefinition
)


class PythonCodeGenerator:
    """Generates optimized Python code from SchemaMap AST."""
    
    def __init__(self, class_name: str = "GeneratedTransformer"):
        self.class_name = class_name
        self._lookups: Dict[str, Any] = {}
        self._aliases: Dict[str, AliasDefinition] = {}
    
    def generate(self, mapping_file: MappingFile) -> str:
        self._lookups = {}
        self._aliases = mapping_file.aliases
        
        for name, lookup_def in mapping_file.lookups.items():
            if isinstance(lookup_def.source, dict):
                self._lookups[name] = lookup_def.source
        
        config = mapping_file.config
        null_handling = config.get("null_handling", "keep")
        
        lookup_code = self._gen_lookup_dict()
        mapping_code = self._gen_mappings(mapping_file.mappings)
        
        source_file = mapping_file.source_file or "unknown"
        
        return f'''"""
Generated Transformer - {source_file}
Generated: {datetime.now().isoformat()}
JsonTools SchemaMap Compiler v1.4.0
"""

from __future__ import annotations
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Callable


class {self.class_name}:
    """Compiled SchemaMap Transformer."""

    def __init__(self):
        self._lookups = {lookup_code}
        self._external_functions: Dict[str, Callable] = {{}}
        self._null_handling = "{null_handling}"

    def register_function(self, name: str, func: Callable) -> "{self.class_name}":
        self._external_functions[name] = func
        return self

    def transform(self, source: Dict[str, Any]) -> Dict[str, Any]:
        target: Dict[str, Any] = {{}}
        
{mapping_code}
        
        if self._null_handling == "omit":
            target = self._remove_nulls(target)
        return target

    def transform_batch(self, items: List[Dict]) -> List[Dict]:
        return [self.transform(item) for item in items]

    def _get_value(self, data: Any, path: str) -> Any:
        if not path or data is None:
            return data
        if "[*]" in path:
            return self._get_array_values(data, path)
        current = data
        for seg in path.split("."):
            if current is None:
                return None
            if "[" in seg:
                key = seg[:seg.index("[")]
                idx = seg[seg.index("[")+1:seg.index("]")]
                if key:
                    current = current.get(key) if isinstance(current, dict) else None
                if current and isinstance(current, list) and idx != "*":
                    current = current[int(idx)] if -len(current) <= int(idx) < len(current) else None
            else:
                current = current.get(seg) if isinstance(current, dict) else None
        return current

    def _get_array_values(self, data: Any, path: str) -> List[Any]:
        parts = path.split("[*]")
        before = parts[0]
        after = parts[1].lstrip(".") if len(parts) > 1 else ""
        arr = self._get_value(data, before) if before else data
        if not isinstance(arr, list):
            return []
        if not after:
            return arr
        return [self._get_value(item, after) for item in arr]

    def _set_value(self, data: Dict, path: str, value: Any) -> None:
        if "[*]" in path:
            self._set_array_value(data, path, value)
            return
        segments = path.split(".")
        current = data
        for seg in segments[:-1]:
            if seg not in current:
                current[seg] = {{}}
            current = current[seg]
        current[segments[-1]] = value

    def _set_array_value(self, data: Dict, path: str, value: Any) -> None:
        parts = path.split("[*]")
        before = parts[0]
        after = parts[1].lstrip(".") if len(parts) > 1 else ""
        if before not in data:
            data[before] = []
        arr = data[before]
        if isinstance(value, list):
            while len(arr) < len(value):
                arr.append({{}})
            for i, v in enumerate(value):
                if after:
                    self._set_nested(arr[i], after, v)
                else:
                    arr[i] = v

    def _set_nested(self, data: Dict, path: str, value: Any) -> None:
        segments = path.split(".")
        current = data
        for seg in segments[:-1]:
            if seg not in current:
                current[seg] = {{}}
            current = current[seg]
        current[segments[-1]] = value

    def _remove_nulls(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {{k: self._remove_nulls(v) for k, v in data.items() if v is not None}}
        elif isinstance(data, list):
            return [self._remove_nulls(v) for v in data if v is not None]
        return data

    def _lookup(self, table: str, value: Any) -> Any:
        return self._lookups.get(table, {{}}).get(value, value)

    def _apply_transform(self, value: Any, func) -> Any:
        """Apply a transform function, handling lists element-wise."""
        if isinstance(value, list):
            return [func(v) for v in value]
        return func(value)

    def _evaluate_expr(self, expr: str, source: Dict) -> Any:
        import re as _re
        m = _re.match(r"(\\w+)\\((.*)\\)", expr)
        if m:
            fn, args = m.group(1), m.group(2)
            if fn in self._external_functions:
                parsed = self._parse_args(args, source)
                return self._external_functions[fn](*parsed)
            if fn == "sum":
                vals = self._get_value(source, args)
                return sum(float(v or 0) for v in vals) if isinstance(vals, list) else 0
            if fn == "count":
                vals = self._get_value(source, args)
                return len(vals) if isinstance(vals, list) else 0
        return self._get_value(source, expr)

    def _parse_args(self, args_str: str, source: Dict) -> List[Any]:
        args = []
        for arg in args_str.split(","):
            arg = arg.strip()
            if not arg:
                continue
            try:
                args.append(float(arg) if "." in arg else int(arg))
                continue
            except ValueError:
                pass
            if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                args.append(arg[1:-1])
                continue
            args.append(self._get_value(source, arg))
        return args


if __name__ == "__main__":
    import json, sys
    t = {self.class_name}()
    data = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {{}}
    print(json.dumps(t.transform(data), indent=2, default=str))
'''
    
    def _gen_lookup_dict(self) -> str:
        if not self._lookups:
            return "{}"
        lines = ["{"]
        for name, table in self._lookups.items():
            lines.append(f'            "{name}": {{')
            for k, v in table.items():
                lines.append(f'                "{k}": "{v}",')
            lines.append("            },")
        lines.append("        }")
        return "\n".join(lines)
    
    def _gen_mappings(self, mappings: List, indent: int = 8) -> str:
        lines = []
        ind = " " * indent
        
        for item in mappings:
            if isinstance(item, Mapping):
                lines.extend(self._gen_mapping(item, ind))
        
        return "\n".join(lines)
    
    def _gen_mapping(self, mapping: Mapping, ind: str) -> List[str]:
        if isinstance(mapping.target, SkipTarget):
            return []
        
        lines = []
        target_path = str(mapping.target)
        source_code = self._gen_source(mapping.source)
        is_array = "[*]" in str(mapping.source)
        
        lines.append(f"{ind}_v = {source_code}")
        
        # Apply transforms
        for t in mapping.transforms.transforms:
            t_code = self._gen_transform(t, is_array)
            lines.append(f"{ind}_v = {t_code}")
        
        lines.append(f'{ind}self._set_value(target, "{target_path}", _v)')
        lines.append("")
        
        return lines
    
    def _gen_source(self, source) -> str:
        if isinstance(source, ConstantValue):
            return repr(source.value)
        
        if isinstance(source, ComputeExpression):
            if source.type == "now":
                return 'datetime.now().isoformat() + "Z"'
            elif source.type == "uuid":
                return "str(uuid.uuid4())"
            else:
                expr = source.expression.replace('"', '\\"')
                return f'self._evaluate_expr("{expr}", source)'
        
        if isinstance(source, MergeExpression):
            if source.operator == "+":
                parts = []
                for p in source.parts:
                    if isinstance(p, str):
                        parts.append(repr(p))
                    elif isinstance(p, SourcePath):
                        parts.append(f'str(self._get_value(source, "{p}") or "")')
                return "(" + " + ".join(parts) + ")"
        
        if isinstance(source, SourcePath):
            return f'self._get_value(source, "{source}")'
        
        return "None"
    
    def _gen_transform(self, transform: Transform, is_array: bool = False) -> str:
        name = transform.name
        args = transform.args
        
        # Handle aliases
        if transform.is_alias:
            alias_def = self._aliases.get(name)
            if alias_def:
                transforms = alias_def.transforms.transforms
                if len(transforms) == 1:
                    return self._gen_transform(transforms[0], is_array)
                
                # Chain transforms
                result = "_v"
                for t in transforms:
                    single = self._gen_single_transform(t.name, t.args)
                    if is_array:
                        result = f"self._apply_transform({result}, lambda x: {single.replace('_v', 'x')})"
                    else:
                        result = f"(lambda _v: {single})({result})"
                return result
            return "_v"
        
        single = self._gen_single_transform(name, args)
        if is_array:
            return f"self._apply_transform(_v, lambda x: {single.replace('_v', 'x')})"
        return single
    
    def _gen_single_transform(self, name: str, args: list) -> str:
        if name == "trim":
            return "str(_v).strip() if _v is not None else None"
        elif name == "lowercase":
            return "str(_v).lower() if _v is not None else None"
        elif name == "uppercase":
            return "str(_v).upper() if _v is not None else None"
        elif name == "titlecase":
            return "str(_v).title() if _v is not None else None"
        elif name == "to_int":
            return "int(float(_v)) if _v is not None else None"
        elif name == "to_float":
            return "float(_v) if _v is not None else None"
        elif name == "to_bool":
            return "str(_v).upper() in ('Y','YES','TRUE','1','T') if _v is not None else False"
        elif name == "round":
            d = args[0] if args else 2
            return f"round(float(_v), {d}) if _v is not None else None"
        elif name == "default":
            dv = repr(args[0]) if args else "None"
            return f"_v if _v is not None else {dv}"
        elif name == "collapse_spaces":
            return "re.sub(r'\\\\s+', ' ', str(_v)).strip() if _v is not None else None"
        elif name == "lookup":
            if args:
                tbl = args[0][1:] if str(args[0]).startswith("@") else str(args[0])
                return f'self._lookup("{tbl}", _v)'
            return "_v"
        elif name == "constant":
            return "_v"
        else:
            return "_v"
