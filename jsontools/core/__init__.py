"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Core module - Schema parsing, reference resolution, and type mapping.
"""

from .schema_parser import SchemaParser
from .reference_resolver import ReferenceResolver
from .type_mapper import TypeMapper
from .validator import SchemaValidator
from .schema_processor import SchemaProcessor

__all__ = [
    "SchemaParser",
    "ReferenceResolver",
    "TypeMapper", 
    "SchemaValidator",
    "SchemaProcessor",
]
