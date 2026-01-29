"""

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder.

Patent Pending: Certain implementations may be subject to patent applications.

Reference Resolver - Handles $ref resolution for JSON Schema.

Supports:
- Local references (#/definitions/..., #/$defs/...)
- Relative file references (./other-schema.json)
- Absolute file references (/path/to/schema.json)
- Remote HTTP/HTTPS references (http://example.com/schema.json)
- Recursive reference detection and handling
- Circular reference detection
"""

import json
import os
import re
import copy
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urljoin, urlparse
from pathlib import Path
import hashlib

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class ReferenceError(Exception):
    """Exception raised for reference resolution errors."""
    pass


class CircularReferenceError(ReferenceError):
    """Exception raised when a circular reference is detected."""
    pass


class ReferenceResolver:
    """
    Resolves $ref references in JSON Schema documents.
    
    Handles local, file-based, and remote references with caching
    and circular reference detection.
    """
    
    def __init__(
        self,
        schema: Dict[str, Any],
        base_uri: Optional[str] = None,
        schema_store: Optional[Dict[str, Dict[str, Any]]] = None,
        allow_remote: bool = True,
        cache_remote: bool = True,
    ):
        """
        Initialize the reference resolver.
        
        Args:
            schema: The root schema document
            base_uri: Base URI for resolving relative references
            schema_store: Pre-loaded schemas keyed by URI
            allow_remote: Whether to fetch remote schemas
            cache_remote: Whether to cache fetched remote schemas
        """
        self.root_schema = schema
        self.base_uri = base_uri or ""
        self.schema_store: Dict[str, Dict[str, Any]] = schema_store or {}
        self.allow_remote = allow_remote
        self.cache_remote = cache_remote
        
        # Cache for resolved references
        self._resolution_cache: Dict[str, Any] = {}
        
        # Track resolution stack for circular reference detection
        self._resolution_stack: List[str] = []
        
        # Extract definitions from root schema
        self._definitions = self._extract_definitions(schema)
        
        # Register root schema
        if base_uri:
            self.schema_store[base_uri] = schema
    
    def _extract_definitions(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all definitions from a schema."""
        definitions = {}
        
        # JSON Schema Draft-07 uses "definitions"
        if "definitions" in schema:
            definitions.update(schema["definitions"])
        
        # JSON Schema Draft 2019-09+ uses "$defs"
        if "$defs" in schema:
            definitions.update(schema["$defs"])
        
        return definitions
    
    def resolve_all(self, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Resolve all $ref in the schema, returning a fully dereferenced schema.
        
        Args:
            schema: Schema to resolve (uses root if not provided)
            
        Returns:
            Fully resolved schema with all $ref replaced
        """
        schema = schema or self.root_schema
        return self._resolve_recursive(copy.deepcopy(schema), set())
    
    def _resolve_recursive(
        self, 
        obj: Any, 
        seen_refs: Set[str],
        current_path: str = "#"
    ) -> Any:
        """Recursively resolve all references in an object."""
        if isinstance(obj, dict):
            # Check for $ref
            if "$ref" in obj:
                ref = obj["$ref"]
                
                # Handle circular references
                if ref in seen_refs:
                    # Return a reference marker for circular refs
                    return {"$circular_ref": ref}
                
                # Resolve the reference
                resolved = self.resolve_ref(ref)
                
                # Merge any additional properties from the referring schema
                # (JSON Schema allows siblings to $ref in some cases)
                extra_props = {k: v for k, v in obj.items() if k != "$ref"}
                if extra_props and isinstance(resolved, dict):
                    resolved = {**resolved, **extra_props}
                
                # Continue resolving the resolved schema
                new_seen = seen_refs | {ref}
                return self._resolve_recursive(resolved, new_seen, ref)
            
            # Resolve nested objects
            return {
                k: self._resolve_recursive(v, seen_refs, f"{current_path}/{k}")
                for k, v in obj.items()
            }
        
        elif isinstance(obj, list):
            return [
                self._resolve_recursive(item, seen_refs, f"{current_path}[{i}]")
                for i, item in enumerate(obj)
            ]
        
        return obj
    
    def resolve_ref(self, ref: str) -> Dict[str, Any]:
        """
        Resolve a single $ref and return the referenced schema.
        
        Args:
            ref: The reference string (e.g., "#/definitions/User")
            
        Returns:
            The resolved schema
            
        Raises:
            ReferenceError: If the reference cannot be resolved
            CircularReferenceError: If a circular reference is detected
        """
        # Check cache
        cache_key = self._get_cache_key(ref)
        if cache_key in self._resolution_cache:
            return copy.deepcopy(self._resolution_cache[cache_key])
        
        # Check for circular reference
        if ref in self._resolution_stack:
            raise CircularReferenceError(
                f"Circular reference detected: {' -> '.join(self._resolution_stack)} -> {ref}"
            )
        
        self._resolution_stack.append(ref)
        
        try:
            resolved = self._do_resolve(ref)
            
            # Cache the result
            if self.cache_remote:
                self._resolution_cache[cache_key] = resolved
            
            return copy.deepcopy(resolved)
        finally:
            self._resolution_stack.pop()
    
    def _do_resolve(self, ref: str) -> Dict[str, Any]:
        """Internal method to perform reference resolution."""
        # Parse the reference
        uri, fragment = self._parse_ref(ref)
        
        # Get the schema document
        if uri:
            schema_doc = self._get_schema_document(uri)
        else:
            schema_doc = self.root_schema
        
        # Navigate to the fragment
        if fragment:
            return self._resolve_fragment(schema_doc, fragment)
        
        return schema_doc
    
    def _parse_ref(self, ref: str) -> Tuple[str, str]:
        """
        Parse a $ref into URI and fragment parts.
        
        Args:
            ref: The reference string
            
        Returns:
            Tuple of (uri, fragment)
        """
        if "#" in ref:
            uri, fragment = ref.split("#", 1)
            return uri, fragment
        return ref, ""
    
    def _get_schema_document(self, uri: str) -> Dict[str, Any]:
        """
        Get a schema document by URI.
        
        Args:
            uri: The URI of the schema
            
        Returns:
            The schema document
        """
        # Resolve relative URIs
        if self.base_uri and not self._is_absolute_uri(uri):
            uri = urljoin(self.base_uri, uri)
        
        # Check schema store
        if uri in self.schema_store:
            return self.schema_store[uri]
        
        # Try to load the schema
        if self._is_remote_uri(uri):
            if not self.allow_remote:
                raise ReferenceError(f"Remote references not allowed: {uri}")
            schema = self._fetch_remote_schema(uri)
        else:
            schema = self._load_local_schema(uri)
        
        # Cache in schema store
        self.schema_store[uri] = schema
        
        return schema
    
    def _is_absolute_uri(self, uri: str) -> bool:
        """Check if a URI is absolute."""
        parsed = urlparse(uri)
        return bool(parsed.scheme) or uri.startswith("/")
    
    def _is_remote_uri(self, uri: str) -> bool:
        """Check if a URI is a remote HTTP(S) URI."""
        parsed = urlparse(uri)
        return parsed.scheme in ("http", "https")
    
    def _fetch_remote_schema(self, uri: str) -> Dict[str, Any]:
        """Fetch a remote schema via HTTP(S)."""
        if not HAS_REQUESTS:
            raise ReferenceError(
                f"Cannot fetch remote schema {uri}: 'requests' library not installed"
            )
        
        try:
            response = requests.get(uri, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ReferenceError(f"Failed to fetch remote schema {uri}: {e}")
        except json.JSONDecodeError as e:
            raise ReferenceError(f"Invalid JSON in remote schema {uri}: {e}")
    
    def _load_local_schema(self, uri: str) -> Dict[str, Any]:
        """Load a schema from the local filesystem."""
        # Handle file:// URIs
        if uri.startswith("file://"):
            uri = uri[7:]
        
        # Resolve relative to base URI if needed
        if self.base_uri and not os.path.isabs(uri):
            # Handle base_uri as file path or URI
            base_path = self.base_uri
            if base_path.startswith("file://"):
                base_path = base_path[7:]
            
            # If base_uri looks like a URL, extract path
            parsed = urlparse(base_path)
            if parsed.scheme and parsed.scheme != "file":
                base_path = parsed.path
            
            # If base_path is a file, get its directory
            if os.path.isfile(base_path):
                base_path = os.path.dirname(base_path)
            
            uri = os.path.join(base_path, uri)
        
        # Normalize the path
        uri = os.path.normpath(uri)
        
        try:
            with open(uri, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ReferenceError(f"Schema file not found: {uri}")
        except json.JSONDecodeError as e:
            raise ReferenceError(f"Invalid JSON in schema file {uri}: {e}")
    
    def _resolve_fragment(self, schema: Dict[str, Any], fragment: str) -> Dict[str, Any]:
        """
        Resolve a JSON Pointer fragment within a schema.
        
        Args:
            schema: The schema document
            fragment: The fragment path (e.g., "/definitions/User")
            
        Returns:
            The schema at the fragment location
        """
        if not fragment or fragment == "/":
            return schema
        
        # Parse JSON Pointer
        parts = fragment.split("/")
        if parts[0] == "":
            parts = parts[1:]  # Remove empty string from leading /
        
        current = schema
        for part in parts:
            # Unescape JSON Pointer encoding
            part = part.replace("~1", "/").replace("~0", "~")
            
            if isinstance(current, dict):
                if part not in current:
                    raise ReferenceError(
                        f"Cannot resolve fragment '{fragment}': key '{part}' not found"
                    )
                current = current[part]
            elif isinstance(current, list):
                try:
                    index = int(part)
                    current = current[index]
                except (ValueError, IndexError):
                    raise ReferenceError(
                        f"Cannot resolve fragment '{fragment}': invalid array index '{part}'"
                    )
            else:
                raise ReferenceError(
                    f"Cannot resolve fragment '{fragment}': cannot traverse {type(current)}"
                )
        
        return current
    
    def _get_cache_key(self, ref: str) -> str:
        """Generate a cache key for a reference."""
        return hashlib.md5(f"{self.base_uri}:{ref}".encode()).hexdigest()
    
    def get_all_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all definitions from the schema and any referenced schemas.
        
        Returns:
            Dictionary mapping definition names to their schemas
        """
        all_defs = dict(self._definitions)
        
        # Also collect from schema store
        for uri, schema in self.schema_store.items():
            defs = self._extract_definitions(schema)
            for name, def_schema in defs.items():
                key = f"{uri}#{name}" if uri else name
                all_defs[key] = def_schema
        
        return all_defs
    
    def register_schema(self, uri: str, schema: Dict[str, Any]) -> None:
        """
        Register a schema in the schema store.
        
        Args:
            uri: The URI to register the schema under
            schema: The schema document
        """
        self.schema_store[uri] = schema
        
        # Extract and merge definitions
        defs = self._extract_definitions(schema)
        self._definitions.update(defs)


class SchemaRegistry:
    """
    A registry for managing multiple related schemas.
    
    Useful when working with a collection of schemas that reference each other.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the schema registry.
        
        Args:
            base_path: Base path for loading schemas from files
        """
        self.base_path = base_path
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self._resolvers: Dict[str, ReferenceResolver] = {}
    
    def register(self, uri: str, schema: Dict[str, Any]) -> None:
        """Register a schema with the given URI."""
        self.schemas[uri] = schema
    
    def register_from_file(self, filepath: str, uri: Optional[str] = None) -> str:
        """
        Register a schema from a file.
        
        Args:
            filepath: Path to the schema file
            uri: Optional URI to register under (defaults to filepath)
            
        Returns:
            The URI the schema was registered under
        """
        if self.base_path and not os.path.isabs(filepath):
            filepath = os.path.join(self.base_path, filepath)
        
        with open(filepath, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        uri = uri or filepath
        self.register(uri, schema)
        
        return uri
    
    def register_directory(self, directory: str, pattern: str = "*.json") -> List[str]:
        """
        Register all schemas from a directory.
        
        Args:
            directory: Path to the directory
            pattern: Glob pattern for schema files
            
        Returns:
            List of registered URIs
        """
        import glob
        
        if self.base_path and not os.path.isabs(directory):
            directory = os.path.join(self.base_path, directory)
        
        uris = []
        for filepath in glob.glob(os.path.join(directory, pattern)):
            uri = self.register_from_file(filepath)
            uris.append(uri)
        
        return uris
    
    def get_resolver(self, uri: str) -> ReferenceResolver:
        """
        Get a resolver for a registered schema.
        
        Args:
            uri: The URI of the schema
            
        Returns:
            A ReferenceResolver configured for the schema
        """
        if uri not in self.schemas:
            raise ValueError(f"Schema not registered: {uri}")
        
        if uri not in self._resolvers:
            self._resolvers[uri] = ReferenceResolver(
                schema=self.schemas[uri],
                base_uri=uri,
                schema_store=self.schemas.copy(),
            )
        
        return self._resolvers[uri]
    
    def resolve_all(self, uri: str) -> Dict[str, Any]:
        """
        Fully resolve all references in a schema.
        
        Args:
            uri: The URI of the schema
            
        Returns:
            The fully resolved schema
        """
        resolver = self.get_resolver(uri)
        return resolver.resolve_all()
