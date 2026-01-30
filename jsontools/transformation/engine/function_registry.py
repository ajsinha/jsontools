"""
SchemaMap Function Registry

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Manages registration and execution of external Python functions for SchemaMap.
"""

from __future__ import annotations
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


class FunctionRegistryError(Exception):
    """Exception raised for function registry errors."""
    pass


class FunctionRegistry:
    """
    Registry for external Python functions that can be called from SchemaMap.
    
    Supports multiple ways to register functions:
    1. Direct registration via Python API
    2. Loading from a Python module
    3. Loading from a specific file path
    4. Declarative registration via @functions block in DSL
    
    Example usage:
        registry = FunctionRegistry()
        
        # Register a function directly
        registry.register("calculate_tax", lambda amount, rate: amount * rate)
        
        # Register from a module
        registry.register_module("my_transforms")
        
        # Register from a file
        registry.register_file("./custom_functions.py")
        
        # Call a function
        result = registry.call("calculate_tax", 100.0, 0.08)
    """
    
    def __init__(self):
        """Initialize an empty function registry."""
        self._functions: Dict[str, Callable] = {}
        self._modules: Dict[str, Any] = {}
        self._function_metadata: Dict[str, Dict] = {}
    
    def register(self, name: str, func: Callable, 
                 description: str = None, 
                 arg_types: List[type] = None,
                 return_type: type = None) -> None:
        """
        Register a function with the given name.
        
        Args:
            name: The name to register the function under
            func: The callable function
            description: Optional description of the function
            arg_types: Optional list of argument types for validation
            return_type: Optional return type for documentation
            
        Raises:
            FunctionRegistryError: If name is invalid or func is not callable
        """
        if not name or not isinstance(name, str):
            raise FunctionRegistryError(f"Invalid function name: {name}")
        
        if not callable(func):
            raise FunctionRegistryError(f"'{name}' is not callable")
        
        # Prevent overwriting built-in names
        reserved_names = {'sum', 'count', 'avg', 'min', 'max', 'len', 'abs', 
                         'round', 'int', 'float', 'str', 'bool', 'list', 'dict'}
        if name in reserved_names:
            raise FunctionRegistryError(
                f"Cannot register '{name}': reserved name. Use a different name like '{name}_custom'"
            )
        
        self._functions[name] = func
        self._function_metadata[name] = {
            'description': description,
            'arg_types': arg_types,
            'return_type': return_type,
            'source': 'direct'
        }
    
    def register_module(self, module_name: str, 
                       function_names: List[str] = None,
                       prefix: str = None) -> List[str]:
        """
        Register functions from a Python module.
        
        Args:
            module_name: Name of the module to import (e.g., "my_package.transforms")
            function_names: Optional list of specific function names to register.
                           If None, registers all public functions.
            prefix: Optional prefix to add to function names (e.g., "mod_")
            
        Returns:
            List of registered function names
            
        Raises:
            FunctionRegistryError: If module cannot be imported
        """
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            raise FunctionRegistryError(f"Cannot import module '{module_name}': {e}")
        
        self._modules[module_name] = module
        registered = []
        
        # Get functions to register
        if function_names:
            names_to_check = function_names
        else:
            # Get all public callables
            names_to_check = [name for name in dir(module) 
                            if not name.startswith('_') and callable(getattr(module, name))]
        
        for func_name in names_to_check:
            if not hasattr(module, func_name):
                continue
            
            func = getattr(module, func_name)
            if not callable(func):
                continue
            
            # Apply prefix if specified
            reg_name = f"{prefix}{func_name}" if prefix else func_name
            
            self._functions[reg_name] = func
            self._function_metadata[reg_name] = {
                'description': func.__doc__,
                'source': f'module:{module_name}'
            }
            registered.append(reg_name)
        
        return registered
    
    def register_file(self, file_path: str, 
                     function_names: List[str] = None,
                     prefix: str = None) -> List[str]:
        """
        Register functions from a Python file.
        
        Args:
            file_path: Path to the Python file
            function_names: Optional list of specific function names to register
            prefix: Optional prefix to add to function names
            
        Returns:
            List of registered function names
            
        Raises:
            FunctionRegistryError: If file cannot be loaded
        """
        path = Path(file_path)
        if not path.exists():
            raise FunctionRegistryError(f"File not found: {file_path}")
        
        if not path.suffix == '.py':
            raise FunctionRegistryError(f"Not a Python file: {file_path}")
        
        # Generate a unique module name
        module_name = f"_schemamap_custom_{path.stem}_{id(self)}"
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                raise FunctionRegistryError(f"Cannot load spec for: {file_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        except Exception as e:
            raise FunctionRegistryError(f"Error loading '{file_path}': {e}")
        
        self._modules[str(path)] = module
        registered = []
        
        # Get functions to register
        if function_names:
            names_to_check = function_names
        else:
            names_to_check = [name for name in dir(module) 
                            if not name.startswith('_') and callable(getattr(module, name))]
        
        for func_name in names_to_check:
            if not hasattr(module, func_name):
                continue
            
            func = getattr(module, func_name)
            if not callable(func):
                continue
            
            reg_name = f"{prefix}{func_name}" if prefix else func_name
            
            self._functions[reg_name] = func
            self._function_metadata[reg_name] = {
                'description': func.__doc__,
                'source': f'file:{file_path}'
            }
            registered.append(reg_name)
        
        return registered
    
    def register_from_spec(self, spec: str) -> str:
        """
        Register a function from a specification string.
        
        Spec format: "module.path:function_name" or "module.path:function_name as alias"
        
        Args:
            spec: Function specification string
            
        Returns:
            The name the function was registered under
            
        Examples:
            registry.register_from_spec("math:sqrt")
            registry.register_from_spec("my_module:calculate_tax as calc_tax")
            registry.register_from_spec("utils.formatting:format_name")
        """
        # Parse the spec
        alias = None
        if " as " in spec:
            spec, alias = spec.split(" as ", 1)
            alias = alias.strip()
        
        if ":" not in spec:
            raise FunctionRegistryError(
                f"Invalid spec '{spec}'. Expected format: 'module:function' or 'module:function as alias'"
            )
        
        module_path, func_name = spec.rsplit(":", 1)
        module_path = module_path.strip()
        func_name = func_name.strip()
        
        # Import the module
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise FunctionRegistryError(f"Cannot import '{module_path}': {e}")
        
        # Get the function
        if not hasattr(module, func_name):
            raise FunctionRegistryError(f"Function '{func_name}' not found in '{module_path}'")
        
        func = getattr(module, func_name)
        if not callable(func):
            raise FunctionRegistryError(f"'{func_name}' in '{module_path}' is not callable")
        
        # Register with alias or original name
        reg_name = alias if alias else func_name
        self._functions[reg_name] = func
        self._function_metadata[reg_name] = {
            'description': func.__doc__,
            'source': f'spec:{spec}'
        }
        
        return reg_name
    
    def has_function(self, name: str) -> bool:
        """Check if a function is registered."""
        return name in self._functions
    
    def get_function(self, name: str) -> Optional[Callable]:
        """Get a registered function by name."""
        return self._functions.get(name)
    
    def call(self, name: str, *args, **kwargs) -> Any:
        """
        Call a registered function.
        
        Args:
            name: Name of the function to call
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The result of the function call
            
        Raises:
            FunctionRegistryError: If function is not registered or call fails
        """
        if name not in self._functions:
            raise FunctionRegistryError(f"Function '{name}' is not registered")
        
        func = self._functions[name]
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise FunctionRegistryError(f"Error calling '{name}': {e}")
    
    def call_safe(self, name: str, *args, default: Any = None, **kwargs) -> Any:
        """
        Call a registered function with error handling.
        
        Returns the default value if the function is not registered or call fails.
        """
        try:
            return self.call(name, *args, **kwargs)
        except FunctionRegistryError:
            return default
    
    def list_functions(self) -> List[str]:
        """Get list of all registered function names."""
        return list(self._functions.keys())
    
    def get_metadata(self, name: str) -> Optional[Dict]:
        """Get metadata for a registered function."""
        return self._function_metadata.get(name)
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a function.
        
        Returns True if the function was found and removed.
        """
        if name in self._functions:
            del self._functions[name]
            self._function_metadata.pop(name, None)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all registered functions."""
        self._functions.clear()
        self._function_metadata.clear()
    
    def __contains__(self, name: str) -> bool:
        return name in self._functions
    
    def __len__(self) -> int:
        return len(self._functions)
    
    def __repr__(self) -> str:
        return f"FunctionRegistry({len(self._functions)} functions)"


# Global registry instance for convenience
_global_registry = FunctionRegistry()


def get_global_registry() -> FunctionRegistry:
    """Get the global function registry."""
    return _global_registry


def register_function(name: str, func: Callable, **kwargs) -> None:
    """Register a function in the global registry."""
    _global_registry.register(name, func, **kwargs)


def call_function(name: str, *args, **kwargs) -> Any:
    """Call a function from the global registry."""
    return _global_registry.call(name, *args, **kwargs)
