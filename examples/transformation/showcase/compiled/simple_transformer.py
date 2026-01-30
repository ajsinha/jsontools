"""
Generated Transformer - examples/transformation/showcase/simple_showcase.smap
Generated: 2026-01-30T02:39:37.164563
JsonChamp SchemaMap Compiler v1.4.0
"""

from __future__ import annotations
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Callable


class SimpleShowcaseTransformer:
    """Compiled SchemaMap Transformer."""

    def __init__(self):
        self._lookups = {
            "status_map": {
                "A": "ACTIVE",
                "I": "INACTIVE",
                "P": "PENDING",
            },
            "country_names": {
                "US": "United States",
                "CA": "Canada",
                "UK": "United Kingdom",
            },
        }
        self._external_functions: Dict[str, Callable] = {}
        self._null_handling = "omit"

    def register_function(self, name: str, func: Callable) -> "SimpleShowcaseTransformer":
        self._external_functions[name] = func
        return self

    def transform(self, source: Dict[str, Any]) -> Dict[str, Any]:
        target: Dict[str, Any] = {}
        
        _v = self._get_value(source, "user.id")
        self._set_value(target, "userId", _v)

        _v = self._get_value(source, "user.status")
        _v = self._lookup("status_map", _v)
        self._set_value(target, "status", _v)

        _v = (str(self._get_value(source, "user.first_name") or "") + ' ' + str(self._get_value(source, "user.last_name") or ""))
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "fullName", _v)

        _v = self._get_value(source, "user.email")
        _v = str(_v).strip() if _v is not None else None
        _v = str(_v).lower() if _v is not None else None
        self._set_value(target, "email", _v)

        _v = self._get_value(source, "user.age")
        _v = int(float(_v)) if _v is not None else None
        self._set_value(target, "age", _v)

        _v = self._get_value(source, "order.total")
        _v = (lambda _v: round(float(_v), 2) if _v is not None else None)((lambda _v: float(_v) if _v is not None else None)(_v))
        self._set_value(target, "orderTotal", _v)

        _v = self._get_value(source, "user.address.street")
        _v = (lambda _v: re.sub(r'\\s+', ' ', str(_v)).strip() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "address.line1", _v)

        _v = self._get_value(source, "user.address.city")
        _v = (lambda _v: str(_v).title() if _v is not None else None)((lambda _v: str(_v).strip() if _v is not None else None)(_v))
        self._set_value(target, "address.city", _v)

        _v = self._get_value(source, "user.address.country")
        _v = self._lookup("country_names", _v)
        self._set_value(target, "address.country", _v)

        _v = self._get_value(source, "user.tags[*]")
        _v = self._apply_transform(_v, lambda x: str(x).lower() if x is not None else None)
        self._set_value(target, "interests[*]", _v)

        _v = None
        self._set_value(target, "primaryPhone", _v)

        _v = datetime.now().isoformat() + "Z"
        self._set_value(target, "processedAt", _v)

        _v = str(uuid.uuid4())
        self._set_value(target, "transactionId", _v)

        _v = '1.0'
        _v = _v
        self._set_value(target, "version", _v)

        
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
                current[seg] = {}
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
                arr.append({})
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
                current[seg] = {}
            current = current[seg]
        current[segments[-1]] = value

    def _remove_nulls(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: self._remove_nulls(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [self._remove_nulls(v) for v in data if v is not None]
        return data

    def _lookup(self, table: str, value: Any) -> Any:
        return self._lookups.get(table, {}).get(value, value)

    def _apply_transform(self, value: Any, func) -> Any:
        """Apply a transform function, handling lists element-wise."""
        if isinstance(value, list):
            return [func(v) for v in value]
        return func(value)

    def _evaluate_expr(self, expr: str, source: Dict) -> Any:
        import re as _re
        m = _re.match(r"(\w+)\((.*)\)", expr)
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
    t = SimpleShowcaseTransformer()
    data = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
    print(json.dumps(t.transform(data), indent=2, default=str))
