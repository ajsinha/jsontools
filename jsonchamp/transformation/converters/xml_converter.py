"""
XML to JSON Converter for SchemaMap Transformations

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Converts XML documents to JSON format for processing by the SchemaMap transformation engine.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from collections import defaultdict


class XMLConverter:
    """
    Converts XML data to JSON format.
    
    Features:
    - Elements become JSON objects
    - Attributes can be prefixed (e.g., @attr)
    - Text content stored in special key (e.g., #text)
    - Repeated elements become arrays
    - Namespace handling
    """
    
    def __init__(
        self,
        attr_prefix: str = '@',
        text_key: str = '#text',
        cdata_key: str = '#cdata',
        always_array: Optional[List[str]] = None,
        strip_whitespace: bool = True,
        strip_namespaces: bool = False,
        force_list: bool = False,
        infer_types: bool = True,
        null_values: Optional[List[str]] = None,
        preserve_root: bool = True,
        encoding: str = 'utf-8'
    ):
        """
        Initialize XML converter.
        
        Args:
            attr_prefix: Prefix for attributes (default: '@')
            text_key: Key for text content (default: '#text')
            cdata_key: Key for CDATA content (default: '#cdata')
            always_array: Element names that should always be arrays
            strip_whitespace: Strip whitespace from text content (default: True)
            strip_namespaces: Remove namespace prefixes from tag names (default: False)
            force_list: Force all repeated elements to be arrays (default: False)
            infer_types: Infer numeric/boolean types from text (default: True)
            null_values: Values to treat as null
            preserve_root: Keep root element in output (default: True)
            encoding: File encoding (default: 'utf-8')
        """
        self.attr_prefix = attr_prefix
        self.text_key = text_key
        self.cdata_key = cdata_key
        self.always_array = set(always_array or [])
        self.strip_whitespace = strip_whitespace
        self.strip_namespaces = strip_namespaces
        self.force_list = force_list
        self.infer_types = infer_types
        self.preserve_root = preserve_root
        self.encoding = encoding
        
        self.null_values = set(null_values or ['', 'null', 'NULL', 'None', 'nil'])
    
    def _strip_namespace(self, tag: str) -> str:
        """Remove namespace from tag name."""
        if self.strip_namespaces and '}' in tag:
            return tag.split('}', 1)[1]
        return tag
    
    def _convert_value(self, value: str) -> Any:
        """Convert a string value to appropriate type."""
        if self.strip_whitespace:
            value = value.strip()
        
        # Check for null
        if value in self.null_values:
            return None
        
        if not self.infer_types:
            return value
        
        # Check for boolean
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        
        # Try integer
        try:
            if '.' not in value and 'e' not in value.lower():
                return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        return value
    
    def _element_to_dict(self, element: ET.Element) -> Any:
        """Convert an XML element to a dictionary."""
        tag = self._strip_namespace(element.tag)
        result = {}
        
        # Add attributes
        for attr, value in element.attrib.items():
            attr_name = self._strip_namespace(attr)
            result[self.attr_prefix + attr_name] = self._convert_value(value)
        
        # Process child elements
        children = list(element)
        if children:
            # Group children by tag name
            child_groups = defaultdict(list)
            for child in children:
                child_tag = self._strip_namespace(child.tag)
                child_groups[child_tag].append(self._element_to_dict(child))
            
            # Add children to result
            for child_tag, child_list in child_groups.items():
                if len(child_list) == 1 and child_tag not in self.always_array and not self.force_list:
                    result[child_tag] = child_list[0]
                else:
                    result[child_tag] = child_list
        
        # Handle text content
        text = element.text
        if text:
            if self.strip_whitespace:
                text = text.strip()
            if text:  # Still has content after stripping
                text_value = self._convert_value(text)
                if result:  # Has attributes or children
                    result[self.text_key] = text_value
                else:
                    return text_value  # Just return the text value
        
        # Handle tail text (text after closing tag)
        # This is usually just whitespace and can be ignored
        
        return result if result else None
    
    def convert_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Convert an XML file to JSON.
        
        Args:
            file_path: Path to XML file
            
        Returns:
            Dictionary representation of XML
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        return self._convert_root(root)
    
    def convert_string(self, xml_content: str) -> Dict[str, Any]:
        """
        Convert XML string content to JSON.
        
        Args:
            xml_content: XML content as string
            
        Returns:
            Dictionary representation of XML
        """
        root = ET.fromstring(xml_content)
        return self._convert_root(root)
    
    def _convert_root(self, root: ET.Element) -> Dict[str, Any]:
        """Convert root element to dictionary."""
        tag = self._strip_namespace(root.tag)
        content = self._element_to_dict(root)
        
        if self.preserve_root:
            return {tag: content}
        return content
    
    def convert_elements(self, xml_content: str, element_path: str) -> List[Dict[str, Any]]:
        """
        Extract and convert multiple elements from XML.
        
        Useful for XML with repeated record elements.
        
        Args:
            xml_content: XML content as string
            element_path: XPath-like path to elements (e.g., 'records/record')
            
        Returns:
            List of dictionaries (one per matching element)
        """
        root = ET.fromstring(xml_content)
        
        # Simple path parsing (support basic XPath-like syntax)
        elements = root.findall('.//' + element_path.replace('/', '/'))
        if not elements:
            # Try direct path
            elements = root.findall(element_path)
        
        return [self._element_to_dict(elem) for elem in elements]
    
    def convert_file_elements(self, file_path: Union[str, Path], element_path: str) -> List[Dict[str, Any]]:
        """
        Extract and convert multiple elements from an XML file.
        
        Args:
            file_path: Path to XML file
            element_path: XPath-like path to elements
            
        Returns:
            List of dictionaries
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        elements = root.findall('.//' + element_path.replace('/', '/'))
        if not elements:
            elements = root.findall(element_path)
        
        return [self._element_to_dict(elem) for elem in elements]


def xml_to_json(
    source: Union[str, Path],
    is_file: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to convert XML to JSON.
    
    Args:
        source: XML file path or string content
        is_file: Whether source is a file path (True) or string content (False)
        **kwargs: Arguments passed to XMLConverter
        
    Returns:
        Dictionary representation of XML
    """
    converter = XMLConverter(**kwargs)
    if is_file:
        return converter.convert_file(source)
    return converter.convert_string(source)


def xml_to_json_records(
    source: Union[str, Path],
    element_path: str,
    is_file: bool = True,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Convert XML elements to a list of JSON records.
    
    Useful for XML files with repeated record structures.
    
    Args:
        source: XML file path or string content
        element_path: Path to record elements (e.g., 'orders/order')
        is_file: Whether source is a file path (True) or string content (False)
        **kwargs: Arguments passed to XMLConverter
        
    Returns:
        List of dictionaries
    """
    converter = XMLConverter(**kwargs)
    if is_file:
        return converter.convert_file_elements(source, element_path)
    return converter.convert_elements(source, element_path)


# Preset configurations for common XML formats
class XMLPresets:
    """Common XML format presets."""
    
    @staticmethod
    def standard() -> dict:
        """Standard XML to JSON conversion."""
        return {
            'attr_prefix': '@',
            'text_key': '#text',
            'preserve_root': True,
            'infer_types': True
        }
    
    @staticmethod
    def no_attrs() -> dict:
        """Ignore attributes, focus on elements only."""
        return {
            'attr_prefix': '_',  # Prefix with underscore
            'preserve_root': False,
            'infer_types': True
        }
    
    @staticmethod
    def soap() -> dict:
        """SOAP/Web service XML format."""
        return {
            'strip_namespaces': True,
            'preserve_root': False,
            'infer_types': True
        }
    
    @staticmethod
    def data_records(record_element: str) -> dict:
        """Configuration for data-oriented XML with record elements."""
        return {
            'always_array': [record_element],
            'preserve_root': False,
            'infer_types': True,
            'strip_whitespace': True
        }
    
    @staticmethod
    def preserve_all() -> dict:
        """Preserve all structure including namespaces."""
        return {
            'strip_namespaces': False,
            'preserve_root': True,
            'infer_types': False,
            'strip_whitespace': False
        }
