"""
SchemaMap Built-in Functions

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Provides built-in transformation functions for the SchemaMap DSL.
"""

from __future__ import annotations
import re
import json
import uuid
from datetime import datetime, date, timedelta
from typing import Any, Callable, Dict, List, Optional, Union
import hashlib


class BuiltinFunctions:
    """Collection of built-in transformation functions."""
    
    @staticmethod
    def get_function(name: str) -> Optional[Callable]:
        """Get a built-in function by name."""
        functions = {
            # String functions
            "trim": BuiltinFunctions.trim,
            "lowercase": BuiltinFunctions.lowercase,
            "uppercase": BuiltinFunctions.uppercase,
            "titlecase": BuiltinFunctions.titlecase,
            "capitalize": BuiltinFunctions.capitalize,
            "replace": BuiltinFunctions.replace,
            "regex_replace": BuiltinFunctions.regex_replace,
            "substring": BuiltinFunctions.substring,
            "prefix": BuiltinFunctions.prefix,
            "suffix": BuiltinFunctions.suffix,
            "max_length": BuiltinFunctions.max_length,
            "min_length": BuiltinFunctions.min_length,
            "split": BuiltinFunctions.split,
            "join": BuiltinFunctions.join,
            "pad_left": BuiltinFunctions.pad_left,
            "pad_right": BuiltinFunctions.pad_right,
            "collapse_spaces": BuiltinFunctions.collapse_spaces,
            "sentence_case": BuiltinFunctions.sentence_case,
            
            # Numeric functions
            "to_int": BuiltinFunctions.to_int,
            "to_float": BuiltinFunctions.to_float,
            "to_decimal": BuiltinFunctions.to_decimal,
            "round": BuiltinFunctions.round_num,
            "floor": BuiltinFunctions.floor,
            "ceil": BuiltinFunctions.ceil,
            "abs": BuiltinFunctions.abs_val,
            "multiply": BuiltinFunctions.multiply,
            "divide": BuiltinFunctions.divide,
            "add": BuiltinFunctions.add,
            "subtract": BuiltinFunctions.subtract,
            "min": BuiltinFunctions.min_val,
            "max": BuiltinFunctions.max_val,
            "clamp": BuiltinFunctions.clamp,
            
            # Boolean functions
            "to_bool": BuiltinFunctions.to_bool,
            "negate": BuiltinFunctions.negate,
            
            # Date functions
            "parse_date": BuiltinFunctions.parse_date,
            "format_date": BuiltinFunctions.format_date,
            "to_iso8601": BuiltinFunctions.to_iso8601,
            "to_timestamp": BuiltinFunctions.to_timestamp,
            "add_days": BuiltinFunctions.add_days,
            "add_months": BuiltinFunctions.add_months,
            "add_years": BuiltinFunctions.add_years,
            
            # Array functions
            "first": BuiltinFunctions.first,
            "last": BuiltinFunctions.last,
            "at": BuiltinFunctions.at,
            "flatten": BuiltinFunctions.flatten,
            "distinct": BuiltinFunctions.distinct,
            "sort": BuiltinFunctions.sort,
            "reverse": BuiltinFunctions.reverse,
            "take": BuiltinFunctions.take,
            "skip": BuiltinFunctions.skip,
            "count": BuiltinFunctions.count,
            "sum": BuiltinFunctions.sum_arr,
            "avg": BuiltinFunctions.avg,
            "wrap": BuiltinFunctions.wrap,
            "unwrap": BuiltinFunctions.unwrap,
            
            # Object functions
            "pick": BuiltinFunctions.pick,
            "omit": BuiltinFunctions.omit,
            
            # Conditional functions
            "default": BuiltinFunctions.default,
            "if_empty": BuiltinFunctions.if_empty,
            "if_null": BuiltinFunctions.if_null,
            "required": BuiltinFunctions.required,
            "optional": BuiltinFunctions.optional,
            "when": BuiltinFunctions.when,
            "else": BuiltinFunctions.else_val,
            
            # Lookup functions
            "lookup": BuiltinFunctions.lookup,
            
            # Validation functions
            "validate": BuiltinFunctions.validate,
            "matches": BuiltinFunctions.matches,
            "in": BuiltinFunctions.in_list,
            "not_in": BuiltinFunctions.not_in_list,
            
            # Special functions
            "constant": BuiltinFunctions.constant,
            "raw": BuiltinFunctions.raw,
            "json_parse": BuiltinFunctions.json_parse,
            "json_stringify": BuiltinFunctions.json_stringify,
            "mask": BuiltinFunctions.mask,
            "hash": BuiltinFunctions.hash_val,
            "template": BuiltinFunctions.template,
            "to_string": BuiltinFunctions.to_string,
        }
        return functions.get(name)
    
    # String functions
    @staticmethod
    def trim(value: Any) -> str:
        return str(value).strip() if value is not None else ""
    
    @staticmethod
    def lowercase(value: Any) -> str:
        return str(value).lower() if value is not None else ""
    
    @staticmethod
    def uppercase(value: Any) -> str:
        return str(value).upper() if value is not None else ""
    
    @staticmethod
    def titlecase(value: Any) -> str:
        return str(value).title() if value is not None else ""
    
    @staticmethod
    def capitalize(value: Any) -> str:
        return str(value).capitalize() if value is not None else ""
    
    @staticmethod
    def replace(value: Any, old: str, new: str) -> str:
        return str(value).replace(old, new) if value is not None else ""
    
    @staticmethod
    def regex_replace(value: Any, pattern: str, replacement: str) -> str:
        if value is None:
            return ""
        return re.sub(pattern, replacement, str(value))
    
    @staticmethod
    def substring(value: Any, start: int, end: int = None) -> str:
        if value is None:
            return ""
        s = str(value)
        if end is None:
            return s[start:]
        return s[start:end]
    
    @staticmethod
    def prefix(value: Any, pre: str) -> str:
        return f"{pre}{value}" if value is not None else pre
    
    @staticmethod
    def suffix(value: Any, suf: str) -> str:
        return f"{value}{suf}" if value is not None else suf
    
    @staticmethod
    def max_length(value: Any, length: int) -> str:
        s = str(value) if value is not None else ""
        return s[:length]
    
    @staticmethod
    def min_length(value: Any, length: int, pad: str = " ") -> str:
        s = str(value) if value is not None else ""
        return s.ljust(length, pad)
    
    @staticmethod
    def split(value: Any, delimiter: str = ",") -> List[str]:
        if value is None:
            return []
        return str(value).split(delimiter)
    
    @staticmethod
    def join(value: Any, delimiter: str = ",") -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            return delimiter.join(str(v) for v in value)
        return str(value)
    
    @staticmethod
    def pad_left(value: Any, width: int, char: str = " ") -> str:
        return str(value).rjust(width, char) if value is not None else ""
    
    @staticmethod
    def pad_right(value: Any, width: int, char: str = " ") -> str:
        return str(value).ljust(width, char) if value is not None else ""
    
    @staticmethod
    def collapse_spaces(value: Any) -> str:
        if value is None:
            return ""
        return " ".join(str(value).split())
    
    @staticmethod
    def sentence_case(value: Any) -> str:
        if value is None:
            return ""
        s = str(value).lower()
        return s[0].upper() + s[1:] if s else ""
    
    # Numeric functions
    @staticmethod
    def to_int(value: Any) -> int:
        if value is None:
            return 0
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def to_float(value: Any) -> float:
        if value is None:
            return 0.0
        try:
            return float(str(value))
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def to_decimal(value: Any, precision: int = 2) -> float:
        return round(BuiltinFunctions.to_float(value), precision)
    
    @staticmethod
    def round_num(value: Any, decimals: int = 0) -> float:
        return round(BuiltinFunctions.to_float(value), decimals)
    
    @staticmethod
    def floor(value: Any) -> int:
        import math
        return math.floor(BuiltinFunctions.to_float(value))
    
    @staticmethod
    def ceil(value: Any) -> int:
        import math
        return math.ceil(BuiltinFunctions.to_float(value))
    
    @staticmethod
    def abs_val(value: Any) -> float:
        return abs(BuiltinFunctions.to_float(value))
    
    @staticmethod
    def multiply(value: Any, factor: float) -> float:
        return BuiltinFunctions.to_float(value) * factor
    
    @staticmethod
    def divide(value: Any, divisor: float) -> float:
        if divisor == 0:
            return 0.0
        return BuiltinFunctions.to_float(value) / divisor
    
    @staticmethod
    def add(value: Any, amount: float) -> float:
        return BuiltinFunctions.to_float(value) + amount
    
    @staticmethod
    def subtract(value: Any, amount: float) -> float:
        return BuiltinFunctions.to_float(value) - amount
    
    @staticmethod
    def min_val(value: Any, minimum: float) -> float:
        return max(BuiltinFunctions.to_float(value), minimum)
    
    @staticmethod
    def max_val(value: Any, maximum: float) -> float:
        return min(BuiltinFunctions.to_float(value), maximum)
    
    @staticmethod
    def clamp(value: Any, minimum: float, maximum: float) -> float:
        return max(minimum, min(BuiltinFunctions.to_float(value), maximum))
    
    # Boolean functions
    @staticmethod
    def to_bool(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "y", "1", "on")
        return bool(value)
    
    @staticmethod
    def negate(value: Any) -> bool:
        return not BuiltinFunctions.to_bool(value)
    
    # Date functions
    @staticmethod
    def parse_date(value: Any, format_str: str = "%Y-%m-%d") -> Optional[str]:
        if value is None:
            return None
        try:
            # Convert Python format
            fmt = format_str.replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d")
            fmt = fmt.replace("HH", "%H").replace("mm", "%M").replace("ss", "%S")
            dt = datetime.strptime(str(value), fmt)
            return dt.isoformat()
        except ValueError:
            return str(value)
    
    @staticmethod
    def format_date(value: Any, format_str: str = "%Y-%m-%d") -> str:
        if value is None:
            return ""
        try:
            if isinstance(value, (datetime, date)):
                dt = value
            else:
                dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            fmt = format_str.replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d")
            return dt.strftime(fmt)
        except ValueError:
            return str(value)
    
    @staticmethod
    def to_iso8601(value: Any) -> str:
        if value is None:
            return ""
        try:
            if isinstance(value, (datetime, date)):
                return value.isoformat()
            s = str(value)
            if "T" not in s and len(s) == 10:
                return s + "T00:00:00Z"
            return s
        except ValueError:
            return str(value)
    
    @staticmethod
    def to_timestamp(value: Any) -> int:
        if value is None:
            return 0
        try:
            if isinstance(value, (datetime, date)):
                dt = value
            else:
                dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return int(dt.timestamp())
        except ValueError:
            return 0
    
    @staticmethod
    def add_days(value: Any, days: int) -> str:
        if value is None:
            return ""
        try:
            if isinstance(value, (datetime, date)):
                dt = value
            else:
                dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            result = dt + timedelta(days=days)
            return result.isoformat()
        except ValueError:
            return str(value)
    
    @staticmethod
    def add_months(value: Any, months: int) -> str:
        if value is None:
            return ""
        try:
            if isinstance(value, (datetime, date)):
                dt = value
            else:
                dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            # Simple month addition
            new_month = dt.month + months
            new_year = dt.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            result = dt.replace(year=new_year, month=new_month)
            return result.isoformat()
        except ValueError:
            return str(value)
    
    @staticmethod
    def add_years(value: Any, years: int) -> str:
        if value is None:
            return ""
        try:
            if isinstance(value, (datetime, date)):
                dt = value
            else:
                dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            result = dt.replace(year=dt.year + years)
            return result.isoformat()
        except ValueError:
            return str(value)
    
    # Array functions
    @staticmethod
    def first(value: Any) -> Any:
        if isinstance(value, list) and len(value) > 0:
            return value[0]
        return None
    
    @staticmethod
    def last(value: Any) -> Any:
        if isinstance(value, list) and len(value) > 0:
            return value[-1]
        return None
    
    @staticmethod
    def at(value: Any, index: int) -> Any:
        if isinstance(value, list) and -len(value) <= index < len(value):
            return value[index]
        return None
    
    @staticmethod
    def flatten(value: Any) -> List:
        if not isinstance(value, list):
            return [value] if value is not None else []
        result = []
        for item in value:
            if isinstance(item, list):
                result.extend(BuiltinFunctions.flatten(item))
            else:
                result.append(item)
        return result
    
    @staticmethod
    def distinct(value: Any) -> List:
        if not isinstance(value, list):
            return [value] if value is not None else []
        seen = set()
        result = []
        for item in value:
            key = json.dumps(item, sort_keys=True, default=str) if isinstance(item, (dict, list)) else item
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result
    
    @staticmethod
    def sort(value: Any, key: str = None, reverse: bool = False) -> List:
        if not isinstance(value, list):
            return [value] if value is not None else []
        if key:
            return sorted(value, key=lambda x: x.get(key) if isinstance(x, dict) else x, reverse=reverse)
        return sorted(value, reverse=reverse)
    
    @staticmethod
    def reverse(value: Any) -> List:
        if not isinstance(value, list):
            return [value] if value is not None else []
        return list(reversed(value))
    
    @staticmethod
    def take(value: Any, n: int) -> List:
        if not isinstance(value, list):
            return [value] if value is not None else []
        return value[:n]
    
    @staticmethod
    def skip(value: Any, n: int) -> List:
        if not isinstance(value, list):
            return []
        return value[n:]
    
    @staticmethod
    def count(value: Any) -> int:
        if isinstance(value, list):
            return len(value)
        return 1 if value is not None else 0
    
    @staticmethod
    def sum_arr(value: Any) -> float:
        if not isinstance(value, list):
            return BuiltinFunctions.to_float(value)
        return sum(BuiltinFunctions.to_float(v) for v in value)
    
    @staticmethod
    def avg(value: Any) -> float:
        if not isinstance(value, list) or len(value) == 0:
            return 0.0
        return sum(BuiltinFunctions.to_float(v) for v in value) / len(value)
    
    @staticmethod
    def wrap(value: Any) -> List:
        if isinstance(value, list):
            return value
        return [value] if value is not None else []
    
    @staticmethod
    def unwrap(value: Any) -> Any:
        if isinstance(value, list) and len(value) == 1:
            return value[0]
        return value
    
    # Object functions
    @staticmethod
    def pick(value: Any, *keys: str) -> Dict:
        if not isinstance(value, dict):
            return {}
        return {k: value[k] for k in keys if k in value}
    
    @staticmethod
    def omit(value: Any, *keys: str) -> Dict:
        if not isinstance(value, dict):
            return {}
        return {k: v for k, v in value.items() if k not in keys}
    
    # Conditional functions
    @staticmethod
    def default(value: Any, default_val: Any) -> Any:
        return default_val if value is None else value
    
    @staticmethod
    def if_empty(value: Any, default_val: Any) -> Any:
        if value is None:
            return default_val
        if isinstance(value, str) and value.strip() == "":
            return default_val
        if isinstance(value, (list, dict)) and len(value) == 0:
            return default_val
        return value
    
    @staticmethod
    def if_null(value: Any, default_val: Any) -> Any:
        return default_val if value is None else value
    
    @staticmethod
    def required(value: Any) -> Any:
        if value is None:
            raise ValueError("Required field is null")
        return value
    
    @staticmethod
    def optional(value: Any) -> Any:
        return value
    
    @staticmethod
    def when(value: Any, match: Any, result: Any) -> Any:
        if value == match:
            return result
        return value
    
    @staticmethod
    def else_val(value: Any, default_val: Any) -> Any:
        return default_val if value is None else value
    
    # Lookup functions
    @staticmethod
    def lookup(value: Any, lookup_table: Dict, key_field: str = None, value_field: str = None) -> Any:
        if value is None:
            return None
        if isinstance(lookup_table, dict):
            result = lookup_table.get(value)
            if result is not None and value_field:
                return result.get(value_field, result)
            return result
        return value
    
    # Validation functions
    @staticmethod
    def validate(value: Any, validation_type: str) -> Any:
        if value is None:
            return value
        
        validators = {
            "email": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
            "url": r"^https?://[^\s]+$",
            "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            "phone": r"^\+?[\d\s\-().]+$",
            "zip_us": r"^\d{5}(-\d{4})?$",
        }
        
        pattern = validators.get(validation_type)
        if pattern and not re.match(pattern, str(value), re.IGNORECASE):
            raise ValueError(f"Validation failed for {validation_type}: {value}")
        return value
    
    @staticmethod
    def matches(value: Any, pattern: str) -> bool:
        if value is None:
            return False
        return bool(re.match(pattern, str(value)))
    
    @staticmethod
    def in_list(value: Any, *items: Any) -> bool:
        return value in items
    
    @staticmethod
    def not_in_list(value: Any, *items: Any) -> bool:
        return value not in items
    
    # Special functions
    @staticmethod
    def constant(value: Any) -> Any:
        return value
    
    @staticmethod
    def raw(value: Any) -> Any:
        return value
    
    @staticmethod
    def json_parse(value: Any) -> Any:
        if value is None:
            return None
        try:
            return json.loads(str(value))
        except json.JSONDecodeError:
            return value
    
    @staticmethod
    def json_stringify(value: Any) -> str:
        return json.dumps(value, default=str)
    
    @staticmethod
    def mask(value: Any, visible_chars: int = 4) -> str:
        if value is None:
            return ""
        s = str(value)
        if len(s) <= visible_chars:
            return "*" * len(s)
        return "*" * (len(s) - visible_chars) + s[-visible_chars:]
    
    @staticmethod
    def hash_val(value: Any, algorithm: str = "sha256") -> str:
        if value is None:
            return ""
        s = str(value).encode()
        if algorithm == "md5":
            return hashlib.md5(s).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(s).hexdigest()
        else:
            return hashlib.sha256(s).hexdigest()
    
    @staticmethod
    def template(value: Any, template_str: str, *args: Any) -> str:
        try:
            return template_str.format(value, *args)
        except (KeyError, IndexError):
            return template_str
    
    @staticmethod
    def to_string(value: Any) -> str:
        if value is None:
            return ""
        return str(value)
