"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Base Models - Base classes for generated models.

Provides common functionality for serialization, deserialization,
and validation that can be used by generated classes.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from datetime import datetime, date
from dataclasses import dataclass, asdict, fields

T = TypeVar("T", bound="JsonSerializable")


class JsonSerializable(ABC):
    """
    Abstract base class for JSON-serializable objects.
    
    Provides a common interface for serialization and deserialization.
    """
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        pass
    
    def to_json(self, indent: int = 2, **kwargs) -> str:
        """
        Serialize to JSON string.
        
        Args:
            indent: JSON indentation level
            **kwargs: Additional arguments for json.dumps
            
        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=indent, default=str, **kwargs)
    
    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create instance from dictionary."""
        pass
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """
        Create instance from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            Instance of the class
        """
        return cls.from_dict(json.loads(json_str))


@dataclass
class BaseModel(JsonSerializable):
    """
    Base dataclass with JSON serialization support.
    
    This class can be used as a base for manually created models
    or as a mixin for generated classes.
    """
    
    # Property name mapping (override in subclasses)
    _property_mapping: Dict[str, str] = None
    
    def __post_init__(self):
        """Post-initialization hook for validation."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary with proper JSON property names.
        
        Returns:
            Dictionary representation
        """
        result = {}
        mapping = getattr(self, "_property_mapping", None) or {}
        
        for fld in fields(self):
            if fld.name.startswith("_"):
                continue
            
            value = getattr(self, fld.name)
            
            # Get JSON property name
            json_name = mapping.get(fld.name, fld.name)
            
            # Skip None values
            if value is None:
                continue
            
            # Serialize the value
            result[json_name] = self._serialize_value(value)
        
        return result
    
    def _serialize_value(self, value: Any) -> Any:
        """
        Serialize a single value for JSON output.
        
        Args:
            value: Value to serialize
            
        Returns:
            JSON-compatible value
        """
        if hasattr(value, "to_dict"):
            return value.to_dict()
        
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        
        if isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        
        return value
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """
        Create instance from dictionary.
        
        Args:
            data: Dictionary with property values
            
        Returns:
            Instance of the class
        """
        mapping = getattr(cls, "_property_mapping", None) or {}
        reverse_mapping = {v: k for k, v in mapping.items()}
        
        # Get field names
        field_names = {f.name for f in fields(cls)}
        
        kwargs = {}
        for json_name, value in data.items():
            py_name = reverse_mapping.get(json_name, json_name)
            if py_name in field_names:
                kwargs[py_name] = value
        
        return cls(**kwargs)
    
    def update(self, **kwargs) -> "BaseModel":
        """
        Create a new instance with updated values.
        
        Args:
            **kwargs: Values to update
            
        Returns:
            New instance with updated values
        """
        data = self.to_dict()
        data.update(kwargs)
        return self.from_dict(data)
    
    def validate(self) -> List[str]:
        """
        Validate the model.
        
        Override in subclasses to add custom validation.
        
        Returns:
            List of validation error messages
        """
        return []
    
    def is_valid(self) -> bool:
        """
        Check if the model is valid.
        
        Returns:
            True if valid, False otherwise
        """
        return len(self.validate()) == 0


class ModelRegistry:
    """
    Registry for managing generated model classes.
    
    Useful for looking up models by name and for handling
    references between models.
    """
    
    def __init__(self):
        """Initialize the registry."""
        self._models: Dict[str, Type[JsonSerializable]] = {}
    
    def register(self, name: str, model_class: Type[JsonSerializable]) -> None:
        """
        Register a model class.
        
        Args:
            name: Model name
            model_class: The model class
        """
        self._models[name] = model_class
    
    def get(self, name: str) -> Optional[Type[JsonSerializable]]:
        """
        Get a model class by name.
        
        Args:
            name: Model name
            
        Returns:
            The model class or None
        """
        return self._models.get(name)
    
    def list_models(self) -> List[str]:
        """
        List all registered model names.
        
        Returns:
            List of model names
        """
        return list(self._models.keys())
    
    def create_instance(self, name: str, data: Dict[str, Any]) -> JsonSerializable:
        """
        Create an instance of a registered model.
        
        Args:
            name: Model name
            data: Dictionary with property values
            
        Returns:
            Model instance
            
        Raises:
            ValueError: If model is not registered
        """
        model_class = self.get(name)
        if model_class is None:
            raise ValueError(f"Model not registered: {name}")
        
        return model_class.from_dict(data)


# Global registry
_global_registry = ModelRegistry()


def register_model(name: str, model_class: Type[JsonSerializable]) -> None:
    """Register a model in the global registry."""
    _global_registry.register(name, model_class)


def get_model(name: str) -> Optional[Type[JsonSerializable]]:
    """Get a model from the global registry."""
    return _global_registry.get(name)


def create_instance(name: str, data: Dict[str, Any]) -> JsonSerializable:
    """Create an instance from the global registry."""
    return _global_registry.create_instance(name, data)
