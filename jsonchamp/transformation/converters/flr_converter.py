"""
Fixed Length Record (FLR) to JSON Converter for SchemaMap Transformations

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Converts fixed-length record files to JSON format for processing by the 
SchemaMap transformation engine.

Fixed-length records are common in legacy systems (COBOL, mainframe) where
each field occupies a specific number of characters at fixed positions.
"""

import json
from typing import Dict, List, Any, Optional, Union, Iterator, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class FieldDefinition:
    """Definition of a single field in a fixed-length record."""
    name: str
    start: int          # 1-based start position (like COBOL)
    length: int         # Number of characters
    data_type: str = 'string'  # string, integer, decimal, date, boolean
    decimal_places: int = 0     # For decimal type
    date_format: str = None     # For date type (e.g., 'YYYYMMDD')
    trim: bool = True           # Whether to trim whitespace
    null_value: str = None      # Value to treat as null
    
    @property
    def end(self) -> int:
        """End position (1-based, inclusive)."""
        return self.start + self.length - 1
    
    @property
    def slice_start(self) -> int:
        """Python slice start (0-based)."""
        return self.start - 1
    
    @property
    def slice_end(self) -> int:
        """Python slice end (0-based, exclusive)."""
        return self.start - 1 + self.length


class RecordLayout:
    """
    Defines the layout of a fixed-length record.
    
    Can be loaded from:
    - JSON layout file
    - COBOL copybook-style definition
    - Programmatic definition
    """
    
    def __init__(self, fields: List[FieldDefinition] = None, record_length: int = None):
        """
        Initialize record layout.
        
        Args:
            fields: List of field definitions
            record_length: Expected record length (optional, calculated if not provided)
        """
        self.fields = fields or []
        self._record_length = record_length
    
    @property
    def record_length(self) -> int:
        """Get the record length (calculated from fields or explicit)."""
        if self._record_length:
            return self._record_length
        if not self.fields:
            return 0
        return max(f.slice_end for f in self.fields)
    
    @record_length.setter
    def record_length(self, value: int):
        self._record_length = value
    
    def add_field(self, name: str, start: int, length: int, **kwargs) -> 'RecordLayout':
        """
        Add a field definition (fluent interface).
        
        Args:
            name: Field name
            start: 1-based start position
            length: Field length
            **kwargs: Additional FieldDefinition arguments
            
        Returns:
            Self for chaining
        """
        self.fields.append(FieldDefinition(name=name, start=start, length=length, **kwargs))
        return self
    
    def get_field(self, name: str) -> Optional[FieldDefinition]:
        """Get field definition by name."""
        for field in self.fields:
            if field.name == name:
                return field
        return None
    
    @classmethod
    def from_json_file(cls, file_path: Union[str, Path]) -> 'RecordLayout':
        """
        Load layout from JSON file.
        
        JSON format:
        {
            "record_length": 100,  // optional
            "fields": [
                {"name": "id", "start": 1, "length": 10, "data_type": "integer"},
                {"name": "name", "start": 11, "length": 30},
                {"name": "amount", "start": 41, "length": 12, "data_type": "decimal", "decimal_places": 2}
            ]
        }
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_json_string(cls, json_string: str) -> 'RecordLayout':
        """Load layout from JSON string."""
        data = json.loads(json_string)
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RecordLayout':
        """Load layout from dictionary."""
        fields = []
        for field_data in data.get('fields', []):
            fields.append(FieldDefinition(
                name=field_data['name'],
                start=field_data['start'],
                length=field_data['length'],
                data_type=field_data.get('data_type', 'string'),
                decimal_places=field_data.get('decimal_places', 0),
                date_format=field_data.get('date_format'),
                trim=field_data.get('trim', True),
                null_value=field_data.get('null_value')
            ))
        
        return cls(
            fields=fields,
            record_length=data.get('record_length')
        )
    
    @classmethod
    def from_simple_format(cls, layout_file: Union[str, Path]) -> 'RecordLayout':
        """
        Load layout from simple text format.
        
        Format (tab or comma separated):
        field_name,start,length[,type[,decimal_places]]
        
        Example:
        id,1,10,integer
        name,11,30,string
        amount,41,12,decimal,2
        birth_date,53,8,date,YYYYMMDD
        """
        fields = []
        with open(layout_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Support both comma and tab
                if '\t' in line:
                    parts = line.split('\t')
                else:
                    parts = line.split(',')
                
                parts = [p.strip() for p in parts]
                
                if len(parts) < 3:
                    continue
                
                name = parts[0]
                start = int(parts[1])
                length = int(parts[2])
                data_type = parts[3] if len(parts) > 3 else 'string'
                
                kwargs = {'data_type': data_type}
                
                if data_type == 'decimal' and len(parts) > 4:
                    kwargs['decimal_places'] = int(parts[4])
                elif data_type == 'date' and len(parts) > 4:
                    kwargs['date_format'] = parts[4]
                
                fields.append(FieldDefinition(name=name, start=start, length=length, **kwargs))
        
        return cls(fields=fields)
    
    def to_dict(self) -> dict:
        """Export layout to dictionary."""
        return {
            'record_length': self.record_length,
            'fields': [
                {
                    'name': f.name,
                    'start': f.start,
                    'length': f.length,
                    'data_type': f.data_type,
                    'decimal_places': f.decimal_places,
                    'date_format': f.date_format,
                    'trim': f.trim,
                    'null_value': f.null_value
                }
                for f in self.fields
            ]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Export layout to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def validate(self) -> List[str]:
        """
        Validate layout for common issues.
        
        Returns:
            List of validation warnings/errors
        """
        issues = []
        
        if not self.fields:
            issues.append("No fields defined")
            return issues
        
        # Check for overlapping fields
        sorted_fields = sorted(self.fields, key=lambda f: f.start)
        for i, field in enumerate(sorted_fields[:-1]):
            next_field = sorted_fields[i + 1]
            if field.slice_end > next_field.slice_start:
                issues.append(
                    f"Fields overlap: '{field.name}' (ends at {field.end}) "
                    f"overlaps with '{next_field.name}' (starts at {next_field.start})"
                )
        
        # Check for gaps
        for i, field in enumerate(sorted_fields[:-1]):
            next_field = sorted_fields[i + 1]
            gap = next_field.slice_start - field.slice_end
            if gap > 0:
                issues.append(
                    f"Gap of {gap} characters between '{field.name}' and '{next_field.name}'"
                )
        
        # Check field positions
        for field in self.fields:
            if field.start < 1:
                issues.append(f"Field '{field.name}' has invalid start position: {field.start}")
            if field.length < 1:
                issues.append(f"Field '{field.name}' has invalid length: {field.length}")
        
        return issues


class FLRConverter:
    """
    Converts fixed-length record data to JSON format.
    
    Features:
    - Type conversion (string, integer, decimal, date, boolean)
    - Whitespace trimming
    - Null value handling
    - Batch processing
    - Memory-efficient iteration
    """
    
    def __init__(
        self,
        layout: RecordLayout,
        encoding: str = 'utf-8',
        skip_blank_lines: bool = True,
        strip_record: bool = False,
        line_ending: str = None,  # Auto-detect if None
        header_lines: int = 0,
        footer_lines: int = 0
    ):
        """
        Initialize FLR converter.
        
        Args:
            layout: Record layout definition
            encoding: File encoding (default: utf-8)
            skip_blank_lines: Skip empty lines (default: True)
            strip_record: Strip trailing whitespace from records (default: False)
            line_ending: Line ending character(s) (auto-detect if None)
            header_lines: Number of header lines to skip
            footer_lines: Number of footer lines to skip
        """
        self.layout = layout
        self.encoding = encoding
        self.skip_blank_lines = skip_blank_lines
        self.strip_record = strip_record
        self.line_ending = line_ending
        self.header_lines = header_lines
        self.footer_lines = footer_lines
    
    def _convert_value(self, raw_value: str, field: FieldDefinition) -> Any:
        """Convert a raw string value according to field definition."""
        if field.trim:
            value = raw_value.strip()
        else:
            value = raw_value
        
        # Check for null
        if field.null_value is not None and value == field.null_value:
            return None
        if not value:
            return None
        
        # Type conversion
        if field.data_type == 'integer':
            try:
                return int(value)
            except ValueError:
                return None
        
        elif field.data_type == 'decimal':
            try:
                # Handle implied decimal (common in COBOL)
                if field.decimal_places > 0 and '.' not in value:
                    # Insert decimal point
                    int_part = value[:-field.decimal_places] or '0'
                    dec_part = value[-field.decimal_places:].ljust(field.decimal_places, '0')
                    value = f"{int_part}.{dec_part}"
                return float(value)
            except ValueError:
                return None
        
        elif field.data_type == 'boolean':
            return value.upper() in ('Y', 'YES', 'T', 'TRUE', '1')
        
        elif field.data_type == 'date':
            # Return as string (can be transformed by SchemaMap)
            # But clean up common formats
            if field.date_format == 'YYYYMMDD' and len(value) == 8:
                return f"{value[:4]}-{value[4:6]}-{value[6:8]}"
            elif field.date_format == 'MMDDYYYY' and len(value) == 8:
                return f"{value[4:8]}-{value[:2]}-{value[2:4]}"
            elif field.date_format == 'DDMMYYYY' and len(value) == 8:
                return f"{value[4:8]}-{value[2:4]}-{value[:2]}"
            return value
        
        else:  # string
            return value
    
    def _parse_record(self, record: str) -> Dict[str, Any]:
        """Parse a single fixed-length record into a dictionary."""
        if self.strip_record:
            record = record.rstrip()
        
        result = {}
        for field in self.layout.fields:
            # Extract field value
            raw_value = record[field.slice_start:field.slice_end]
            result[field.name] = self._convert_value(raw_value, field)
        
        return result
    
    def convert_string(self, content: str) -> List[Dict[str, Any]]:
        """
        Convert FLR string content to list of JSON objects.
        
        Args:
            content: Fixed-length record content as string
            
        Returns:
            List of dictionaries (one per record)
        """
        return list(self.iterate_string(content))
    
    def convert_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Convert FLR file to list of JSON objects.
        
        Args:
            file_path: Path to FLR file
            
        Returns:
            List of dictionaries (one per record)
        """
        return list(self.iterate_file(file_path))
    
    def iterate_string(self, content: str) -> Iterator[Dict[str, Any]]:
        """
        Iterate over FLR string content, yielding JSON objects.
        
        Args:
            content: Fixed-length record content as string
            
        Yields:
            Dictionary for each record
        """
        lines = content.splitlines()
        yield from self._iterate_lines(lines)
    
    def iterate_file(self, file_path: Union[str, Path]) -> Iterator[Dict[str, Any]]:
        """
        Iterate over FLR file, yielding JSON objects.
        
        Memory-efficient for large files.
        
        Args:
            file_path: Path to FLR file
            
        Yields:
            Dictionary for each record
        """
        with open(file_path, 'r', encoding=self.encoding) as f:
            lines = f.readlines()
        
        # Remove line endings
        lines = [line.rstrip('\r\n') for line in lines]
        
        yield from self._iterate_lines(lines)
    
    def _iterate_lines(self, lines: List[str]) -> Iterator[Dict[str, Any]]:
        """Internal method to iterate over lines."""
        # Skip header lines
        start_idx = self.header_lines
        
        # Skip footer lines
        end_idx = len(lines) - self.footer_lines if self.footer_lines > 0 else len(lines)
        
        for line in lines[start_idx:end_idx]:
            if self.skip_blank_lines and not line.strip():
                continue
            yield self._parse_record(line)
    
    def convert_record(self, record: str) -> Dict[str, Any]:
        """
        Convert a single record string to dictionary.
        
        Args:
            record: Single fixed-length record string
            
        Returns:
            Dictionary
        """
        return self._parse_record(record)


def flr_to_json(
    source: Union[str, Path],
    layout: Union[RecordLayout, str, Path, dict],
    is_file: bool = True,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Convenience function to convert FLR to JSON.
    
    Args:
        source: FLR file path or string content
        layout: RecordLayout object, JSON file path, or dict
        is_file: Whether source is a file path (True) or string content (False)
        **kwargs: Arguments passed to FLRConverter
        
    Returns:
        List of dictionaries
    """
    # Handle layout
    if isinstance(layout, RecordLayout):
        record_layout = layout
    elif isinstance(layout, dict):
        record_layout = RecordLayout.from_dict(layout)
    elif isinstance(layout, (str, Path)):
        layout_path = Path(layout)
        if layout_path.suffix.lower() == '.json':
            record_layout = RecordLayout.from_json_file(layout)
        else:
            record_layout = RecordLayout.from_simple_format(layout)
    else:
        raise ValueError(f"Invalid layout type: {type(layout)}")
    
    converter = FLRConverter(layout=record_layout, **kwargs)
    
    if is_file:
        return converter.convert_file(source)
    return converter.convert_string(source)


# Preset configurations
class FLRPresets:
    """Common FLR format presets."""
    
    @staticmethod
    def cobol_defaults() -> dict:
        """COBOL-style defaults with EBCDIC considerations."""
        return {
            'encoding': 'cp037',  # EBCDIC
            'skip_blank_lines': False,
            'strip_record': False
        }
    
    @staticmethod
    def mainframe() -> dict:
        """Mainframe file defaults."""
        return {
            'encoding': 'cp037',
            'skip_blank_lines': False,
            'strip_record': False,
            'line_ending': None
        }
    
    @staticmethod
    def ascii_fixed() -> dict:
        """ASCII fixed-width file defaults."""
        return {
            'encoding': 'utf-8',
            'skip_blank_lines': True,
            'strip_record': True
        }
