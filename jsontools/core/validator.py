"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Schema Validator - Validates JSON Schema and data against schemas.

Provides:
- Schema validation (is the schema itself valid?)
- Data validation (does data conform to a schema?)
- Detailed error reporting
- Custom validation rules
"""

import re
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

try:
    import jsonschema
    from jsonschema import Draft7Validator, ValidationError as JsonSchemaError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class ValidationSeverity(Enum):
    """Severity level for validation errors."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    path: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    schema_path: Optional[str] = None
    value: Any = None
    expected: Any = None
    rule: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    
    @property
    def errors(self) -> List[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]
    
    def add_issue(self, issue: ValidationIssue) -> None:
        """Add an issue to the result."""
        self.issues.append(issue)
        if issue.severity == ValidationSeverity.ERROR:
            self.is_valid = False
    
    def merge(self, other: "ValidationResult") -> None:
        """Merge another validation result into this one."""
        self.issues.extend(other.issues)
        if not other.is_valid:
            self.is_valid = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [
                {
                    "path": i.path,
                    "message": i.message,
                    "severity": i.severity.value,
                    "rule": i.rule,
                }
                for i in self.issues
            ]
        }


class SchemaValidator:
    """
    Validates JSON Schema documents and data against schemas.
    """
    
    # Supported JSON Schema drafts
    SUPPORTED_DRAFTS = [
        "http://json-schema.org/draft-04/schema#",
        "http://json-schema.org/draft-06/schema#",
        "http://json-schema.org/draft-07/schema#",
        "https://json-schema.org/draft/2019-09/schema",
        "https://json-schema.org/draft/2020-12/schema",
    ]
    
    def __init__(
        self,
        strict_mode: bool = False,
        custom_validators: Optional[Dict[str, Callable]] = None,
    ):
        """
        Initialize the validator.
        
        Args:
            strict_mode: Whether to treat warnings as errors
            custom_validators: Custom validation functions by keyword
        """
        self.strict_mode = strict_mode
        self.custom_validators = custom_validators or {}
    
    def validate_schema(self, schema: Dict[str, Any]) -> ValidationResult:
        """
        Validate that a schema is a valid JSON Schema.
        
        Args:
            schema: The schema to validate
            
        Returns:
            ValidationResult with any issues found
        """
        result = ValidationResult(is_valid=True)
        
        # Check basic structure
        if not isinstance(schema, dict):
            result.add_issue(ValidationIssue(
                path="$",
                message="Schema must be an object",
                rule="schema_type",
            ))
            return result
        
        # Check $schema if present
        if "$schema" in schema:
            schema_uri = schema["$schema"]
            if schema_uri not in self.SUPPORTED_DRAFTS:
                result.add_issue(ValidationIssue(
                    path="$.$schema",
                    message=f"Unsupported schema draft: {schema_uri}",
                    severity=ValidationSeverity.WARNING,
                    rule="schema_draft",
                ))
        
        # Validate using jsonschema library if available
        if HAS_JSONSCHEMA:
            try:
                Draft7Validator.check_schema(schema)
            except jsonschema.SchemaError as e:
                result.add_issue(ValidationIssue(
                    path=self._format_path(e.absolute_path),
                    message=str(e.message),
                    rule="jsonschema",
                ))
        
        # Run custom validations
        self._validate_schema_structure(schema, result)
        
        return result
    
    def validate_data(
        self,
        data: Any,
        schema: Dict[str, Any],
        strict: Optional[bool] = None,
    ) -> ValidationResult:
        """
        Validate data against a JSON Schema.
        
        Args:
            data: The data to validate
            schema: The schema to validate against
            strict: Override strict mode for this validation
            
        Returns:
            ValidationResult with any issues found
        """
        result = ValidationResult(is_valid=True)
        strict = strict if strict is not None else self.strict_mode
        
        # Use jsonschema library if available
        if HAS_JSONSCHEMA:
            validator = Draft7Validator(schema)
            for error in validator.iter_errors(data):
                severity = ValidationSeverity.ERROR
                result.add_issue(ValidationIssue(
                    path=self._format_path(error.absolute_path),
                    message=error.message,
                    severity=severity,
                    schema_path=self._format_path(error.absolute_schema_path),
                    value=error.instance,
                    rule=error.validator,
                ))
        else:
            # Fallback to basic validation
            result = self._basic_validate(data, schema, "$")
        
        # Run custom validators
        for keyword, validator_func in self.custom_validators.items():
            if keyword in schema:
                custom_result = validator_func(data, schema[keyword], schema)
                result.merge(custom_result)
        
        return result
    
    def _validate_schema_structure(
        self,
        schema: Dict[str, Any],
        result: ValidationResult,
        path: str = "$",
    ) -> None:
        """Validate schema structure and best practices."""
        # Check for type
        if "type" not in schema and not any(
            k in schema for k in ["$ref", "allOf", "anyOf", "oneOf", "enum", "const"]
        ):
            result.add_issue(ValidationIssue(
                path=path,
                message="Schema should have a 'type' or composition keyword",
                severity=ValidationSeverity.WARNING,
                rule="has_type",
            ))
        
        # Check properties have types
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                prop_path = f"{path}.properties.{prop_name}"
                if isinstance(prop_schema, dict):
                    self._validate_schema_structure(prop_schema, result, prop_path)
        
        # Check items schema for arrays
        if schema.get("type") == "array" and "items" not in schema:
            result.add_issue(ValidationIssue(
                path=path,
                message="Array type should have 'items' schema",
                severity=ValidationSeverity.WARNING,
                rule="array_items",
            ))
        
        # Check definitions
        for def_key in ["definitions", "$defs"]:
            if def_key in schema:
                for def_name, def_schema in schema[def_key].items():
                    def_path = f"{path}.{def_key}.{def_name}"
                    if isinstance(def_schema, dict):
                        self._validate_schema_structure(def_schema, result, def_path)
    
    def _basic_validate(
        self,
        data: Any,
        schema: Dict[str, Any],
        path: str,
    ) -> ValidationResult:
        """Basic validation without jsonschema library."""
        result = ValidationResult(is_valid=True)
        
        # Handle type validation
        schema_type = schema.get("type")
        if schema_type:
            if not self._check_type(data, schema_type):
                result.add_issue(ValidationIssue(
                    path=path,
                    message=f"Expected type {schema_type}, got {type(data).__name__}",
                    value=data,
                    expected=schema_type,
                    rule="type",
                ))
                return result
        
        # Handle enum
        if "enum" in schema and data not in schema["enum"]:
            result.add_issue(ValidationIssue(
                path=path,
                message=f"Value must be one of: {schema['enum']}",
                value=data,
                expected=schema["enum"],
                rule="enum",
            ))
        
        # Handle const
        if "const" in schema and data != schema["const"]:
            result.add_issue(ValidationIssue(
                path=path,
                message=f"Value must be: {schema['const']}",
                value=data,
                expected=schema["const"],
                rule="const",
            ))
        
        # Handle required
        if schema_type == "object" and isinstance(data, dict):
            required = schema.get("required", [])
            for req_prop in required:
                if req_prop not in data:
                    result.add_issue(ValidationIssue(
                        path=f"{path}.{req_prop}",
                        message=f"Required property '{req_prop}' is missing",
                        rule="required",
                    ))
            
            # Validate properties
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    if prop_name in data:
                        prop_result = self._basic_validate(
                            data[prop_name],
                            prop_schema,
                            f"{path}.{prop_name}",
                        )
                        result.merge(prop_result)
        
        # Handle array items
        if schema_type == "array" and isinstance(data, list):
            items_schema = schema.get("items")
            if items_schema:
                for i, item in enumerate(data):
                    item_result = self._basic_validate(
                        item,
                        items_schema,
                        f"{path}[{i}]",
                    )
                    result.merge(item_result)
            
            # Check minItems/maxItems
            if "minItems" in schema and len(data) < schema["minItems"]:
                result.add_issue(ValidationIssue(
                    path=path,
                    message=f"Array must have at least {schema['minItems']} items",
                    rule="minItems",
                ))
            if "maxItems" in schema and len(data) > schema["maxItems"]:
                result.add_issue(ValidationIssue(
                    path=path,
                    message=f"Array must have at most {schema['maxItems']} items",
                    rule="maxItems",
                ))
        
        # Handle string constraints
        if isinstance(data, str):
            if "minLength" in schema and len(data) < schema["minLength"]:
                result.add_issue(ValidationIssue(
                    path=path,
                    message=f"String must be at least {schema['minLength']} characters",
                    rule="minLength",
                ))
            if "maxLength" in schema and len(data) > schema["maxLength"]:
                result.add_issue(ValidationIssue(
                    path=path,
                    message=f"String must be at most {schema['maxLength']} characters",
                    rule="maxLength",
                ))
            if "pattern" in schema:
                if not re.match(schema["pattern"], data):
                    result.add_issue(ValidationIssue(
                        path=path,
                        message=f"String must match pattern: {schema['pattern']}",
                        rule="pattern",
                    ))
        
        # Handle numeric constraints
        if isinstance(data, (int, float)) and not isinstance(data, bool):
            if "minimum" in schema and data < schema["minimum"]:
                result.add_issue(ValidationIssue(
                    path=path,
                    message=f"Value must be >= {schema['minimum']}",
                    rule="minimum",
                ))
            if "maximum" in schema and data > schema["maximum"]:
                result.add_issue(ValidationIssue(
                    path=path,
                    message=f"Value must be <= {schema['maximum']}",
                    rule="maximum",
                ))
        
        return result
    
    def _check_type(self, value: Any, expected_type: Union[str, List[str]]) -> bool:
        """Check if a value matches the expected type(s)."""
        if isinstance(expected_type, list):
            return any(self._check_type(value, t) for t in expected_type)
        
        type_checks = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "array": lambda v: isinstance(v, list),
            "object": lambda v: isinstance(v, dict),
            "null": lambda v: v is None,
        }
        
        check = type_checks.get(expected_type)
        if check:
            return check(value)
        return True
    
    def _format_path(self, path_parts) -> str:
        """Format a path from path parts."""
        if not path_parts:
            return "$"
        
        parts = ["$"]
        for part in path_parts:
            if isinstance(part, int):
                parts.append(f"[{part}]")
            else:
                parts.append(f".{part}")
        
        return "".join(parts)


def validate_schema(schema: Dict[str, Any]) -> ValidationResult:
    """
    Convenience function to validate a JSON Schema.
    
    Args:
        schema: The schema to validate
        
    Returns:
        ValidationResult with any issues found
    """
    validator = SchemaValidator()
    return validator.validate_schema(schema)


def validate_data(data: Any, schema: Dict[str, Any]) -> ValidationResult:
    """
    Convenience function to validate data against a schema.
    
    Args:
        data: The data to validate
        schema: The schema to validate against
        
    Returns:
        ValidationResult with any issues found
    """
    validator = SchemaValidator()
    return validator.validate_data(data, schema)
