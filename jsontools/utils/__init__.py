"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Utilities module - Helper functions and classes.
"""

from .naming import to_snake_case, to_pascal_case, to_safe_identifier
from .file_utils import load_schema, save_schema, save_code
from .json_utils import deep_merge, flatten_schema

__all__ = [
    "to_snake_case",
    "to_pascal_case",
    "to_safe_identifier",
    "load_schema",
    "save_schema",
    "save_code",
    "deep_merge",
    "flatten_schema",
]
