"""
CSV to JSON Converter for SchemaMap Transformations

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Converts CSV records to JSON format for processing by the SchemaMap transformation engine.
"""

import csv
import io
from typing import Dict, List, Any, Optional, Union, Iterator
from pathlib import Path


class CSVConverter:
    """
    Converts CSV data to JSON format.
    
    Each CSV row becomes a JSON object with column headers as keys.
    Supports automatic type inference, custom delimiters, and batch processing.
    """
    
    def __init__(
        self,
        delimiter: str = ',',
        quotechar: str = '"',
        has_header: bool = True,
        skip_rows: int = 0,
        encoding: str = 'utf-8',
        null_values: Optional[List[str]] = None,
        true_values: Optional[List[str]] = None,
        false_values: Optional[List[str]] = None,
        infer_types: bool = True,
        strip_whitespace: bool = True,
        column_names: Optional[List[str]] = None
    ):
        """
        Initialize CSV converter.
        
        Args:
            delimiter: Field delimiter (default: ',')
            quotechar: Quote character (default: '"')
            has_header: Whether first row is header (default: True)
            skip_rows: Number of rows to skip at start (default: 0)
            encoding: File encoding (default: 'utf-8')
            null_values: Values to treat as null (default: ['', 'null', 'NULL', 'None', 'NA', 'N/A'])
            true_values: Values to treat as True (default: ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES', 'Y', 'y'])
            false_values: Values to treat as False (default: ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', 'N', 'n'])
            infer_types: Whether to infer numeric/boolean types (default: True)
            strip_whitespace: Whether to strip whitespace from values (default: True)
            column_names: Override column names (used when has_header=False)
        """
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.has_header = has_header
        self.skip_rows = skip_rows
        self.encoding = encoding
        self.infer_types = infer_types
        self.strip_whitespace = strip_whitespace
        self.column_names = column_names
        
        self.null_values = set(null_values or ['', 'null', 'NULL', 'None', 'NA', 'N/A', 'n/a'])
        self.true_values = set(true_values or ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES', 'Y', 'y'])
        self.false_values = set(false_values or ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', 'N', 'n'])
    
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
        if value in self.true_values:
            return True
        if value in self.false_values:
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
    
    def _row_to_dict(self, row: List[str], headers: List[str]) -> Dict[str, Any]:
        """Convert a CSV row to a dictionary."""
        result = {}
        for i, header in enumerate(headers):
            if i < len(row):
                result[header] = self._convert_value(row[i])
            else:
                result[header] = None
        return result
    
    def convert_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Convert a CSV file to a list of JSON objects.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of dictionaries (one per row)
        """
        with open(file_path, 'r', encoding=self.encoding, newline='') as f:
            return self.convert_string(f.read())
    
    def convert_string(self, csv_content: str) -> List[Dict[str, Any]]:
        """
        Convert CSV string content to a list of JSON objects.
        
        Args:
            csv_content: CSV content as string
            
        Returns:
            List of dictionaries (one per row)
        """
        return list(self.iterate_string(csv_content))
    
    def iterate_file(self, file_path: Union[str, Path]) -> Iterator[Dict[str, Any]]:
        """
        Iterate over a CSV file, yielding JSON objects.
        
        Memory-efficient for large files.
        
        Args:
            file_path: Path to CSV file
            
        Yields:
            Dictionary for each row
        """
        with open(file_path, 'r', encoding=self.encoding, newline='') as f:
            yield from self._iterate_reader(f)
    
    def iterate_string(self, csv_content: str) -> Iterator[Dict[str, Any]]:
        """
        Iterate over CSV string content, yielding JSON objects.
        
        Args:
            csv_content: CSV content as string
            
        Yields:
            Dictionary for each row
        """
        f = io.StringIO(csv_content)
        yield from self._iterate_reader(f)
    
    def _iterate_reader(self, file_obj) -> Iterator[Dict[str, Any]]:
        """Internal method to iterate over a file-like object."""
        reader = csv.reader(file_obj, delimiter=self.delimiter, quotechar=self.quotechar)
        
        # Skip rows
        for _ in range(self.skip_rows):
            try:
                next(reader)
            except StopIteration:
                return
        
        # Get headers
        if self.has_header:
            try:
                headers = next(reader)
                if self.strip_whitespace:
                    headers = [h.strip() for h in headers]
            except StopIteration:
                return
        elif self.column_names:
            headers = self.column_names
        else:
            # Auto-generate column names (col_0, col_1, ...)
            # Need to peek at first row
            try:
                first_row = next(reader)
                headers = [f"col_{i}" for i in range(len(first_row))]
                yield self._row_to_dict(first_row, headers)
            except StopIteration:
                return
        
        # Process rows
        for row in reader:
            yield self._row_to_dict(row, headers)
    
    def convert_row(self, row: List[str], headers: List[str]) -> Dict[str, Any]:
        """
        Convert a single CSV row to a dictionary.
        
        Args:
            row: List of values
            headers: List of column names
            
        Returns:
            Dictionary
        """
        return self._row_to_dict(row, headers)


def csv_to_json(
    source: Union[str, Path],
    is_file: bool = True,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Convenience function to convert CSV to JSON.
    
    Args:
        source: CSV file path or string content
        is_file: Whether source is a file path (True) or string content (False)
        **kwargs: Arguments passed to CSVConverter
        
    Returns:
        List of dictionaries
    """
    converter = CSVConverter(**kwargs)
    if is_file:
        return converter.convert_file(source)
    return converter.convert_string(source)


# Preset configurations for common CSV formats
class CSVPresets:
    """Common CSV format presets."""
    
    @staticmethod
    def excel() -> dict:
        """Microsoft Excel CSV format."""
        return {
            'delimiter': ',',
            'quotechar': '"',
            'has_header': True,
            'encoding': 'utf-8-sig'  # Handle BOM
        }
    
    @staticmethod
    def tsv() -> dict:
        """Tab-separated values format."""
        return {
            'delimiter': '\t',
            'quotechar': '"',
            'has_header': True
        }
    
    @staticmethod
    def pipe() -> dict:
        """Pipe-delimited format."""
        return {
            'delimiter': '|',
            'quotechar': '"',
            'has_header': True
        }
    
    @staticmethod
    def semicolon() -> dict:
        """Semicolon-delimited format (European)."""
        return {
            'delimiter': ';',
            'quotechar': '"',
            'has_header': True
        }
    
    @staticmethod
    def no_header() -> dict:
        """CSV without header row."""
        return {
            'delimiter': ',',
            'quotechar': '"',
            'has_header': False
        }
