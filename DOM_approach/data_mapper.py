#!/usr/bin/env python3
"""
Data Mapper for Asteroid Form Challenge

This module provides utilities for mapping structured data to form fields.
It handles complex nested data structures, data type conversions, and
matching between data field names and form field labels.
"""

import re
import json
import logging
import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
import config


class DataMappingError(Exception):
    """Exception raised when there's an error mapping data to form fields."""
    pass


def load_data_from_file(file_path: str) -> Dict[str, Any]:
    """
    Load structured data from a file.
    Currently supports JavaScript data format used in the demo files.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        Dictionary containing the parsed data
        
    Raises:
        DataMappingError: If the file cannot be loaded or parsed
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Handle the JavaScript-style data format used in the demo files
        if content.strip().startswith('DATA ='):
            # Extract the JSON-like part and convert JavaScript to valid JSON
            json_content = content.replace('DATA =', '').strip()
            if json_content.endswith(';'):
                json_content = json_content[:-1]  # Remove trailing semicolon
                
            # Convert JS-style object to valid JSON
            # Replace unquoted property names with quoted ones
            json_content = re.sub(r'([{,])\s*(\w+):', r'\1"\2":', json_content)
            
            # Try to parse the JSON
            try:
                return json.loads(json_content)
            except json.JSONDecodeError:
                # If direct parsing fails, use a more robust approach
                return _parse_js_object(content)
        else:
            # Assume it's already valid JSON
            return json.loads(content)
            
    except Exception as e:
        raise DataMappingError(f"Error loading data from {file_path}: {str(e)}")


def _parse_js_object(js_content: str) -> Dict[str, Any]:
    """
    Parse a JavaScript object notation into a Python dictionary.
    This is a fallback method for when the regex approach fails.
    
    Args:
        js_content: JavaScript object notation as a string
        
    Returns:
        Dictionary containing the parsed data
    """
    # Extract the actual object part
    match = re.search(r'DATA\s*=\s*({.*})\s*;?\s*$', js_content, re.DOTALL)
    if not match:
        raise DataMappingError("Could not find DATA object in the file")
        
    js_obj = match.group(1)
    
    # Handle boolean values
    js_obj = js_obj.replace('true', 'True').replace('false', 'False')
    
    # Evaluate the expression in a restricted environment
    # This is safer than using eval() directly
    try:
        # Replace JavaScript object property notation with Python dict notation
        py_obj = re.sub(r'(\w+):', r'"\1":', js_obj)
        
        # Handle trailing commas which are valid in JS but not in Python
        py_obj = re.sub(r',\s*}', '}', py_obj)
        py_obj = re.sub(r',\s*]', ']', py_obj)
        
        # Use a safer alternative to eval
        import ast
        return ast.literal_eval(py_obj)
    except Exception as e:
        raise DataMappingError(f"Error parsing JavaScript object: {str(e)}")


def resolve_data_path(data: Dict[str, Any], path: str) -> Any:
    """
    Resolve a dot-notation path in a nested data structure.
    
    Args:
        data: The nested data structure
        path: Dot-notation path (e.g., "contact.firstName")
        
    Returns:
        The value at the specified path, or None if the path doesn't exist
    """
    if not path or not isinstance(data, dict):
        return None
        
    parts = path.split('.')
    value = data
    
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return None
            
    return value


def find_best_match(field_name: str, data: Dict[str, Any]) -> Tuple[str, Any]:
    """
    Find the best matching field in data for a given field name.
    Uses a variety of matching strategies from exact match to fuzzy matching.
    
    Args:
        field_name: Name of the form field
        data: The data structure to search
        
    Returns:
        Tuple of (data_path, value) if a match is found, or (None, None) otherwise
    """
    # Try direct match first (exact field name = exact data key)
    if field_name in data:
        return field_name, data[field_name]
    
    # Normalize field name (remove spaces, underscores, hyphens, convert to lowercase)
    normalized_field = re.sub(r'[_\s-]', '', field_name.lower())
    
    # Search for matches in flattened data
    flattened_data = flatten_dict(data)
    
    # Look for exact matches with the normalized field name
    for key in flattened_data:
        normalized_key = re.sub(r'[_\s-]', '', key.lower())
        if normalized_key == normalized_field:
            return key, flattened_data[key]
    
    # Look for partial matches if no exact match is found
    for key in flattened_data:
        normalized_key = re.sub(r'[_\s-]', '', key.lower())
        if normalized_field in normalized_key or normalized_key in normalized_field:
            return key, flattened_data[key]
    
    # No match found
    return None, None


def flatten_dict(data: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
    """
    Flatten a nested dictionary into a single-level dictionary with dot-notation keys.
    
    Args:
        data: The nested dictionary to flatten
        prefix: Prefix for the keys (used in recursion)
        
    Returns:
        Flattened dictionary with dot-notation keys
    """
    result = {}
    
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            # Recursive case for nested dictionaries
            nested_dict = flatten_dict(value, full_key)
            result.update(nested_dict)
        else:
            # Base case for non-dictionary values
            result[full_key] = value
            
    return result


def format_value(value: Any, field_type: str) -> str:
    """
    Format a value for form input based on the field type.
    
    Args:
        value: The value to format
        field_type: Type of the field (e.g., "text", "date", "checkbox")
        
    Returns:
        Formatted value as a string
    """
    if value is None:
        return ""
        
    if field_type in ["checkbox", "radio"]:
        return bool(value)
        
    if field_type == "date":
        # Try to parse and format the date
        try:
            # Handle different date formats
            if isinstance(value, str):
                # Try different date formats
                formats = [
                    "%Y-%m-%d",      # 2023-04-12
                    "%d-%m-%Y",      # 12-04-2023
                    "%d/%m/%Y",      # 12/04/2023
                    "%m/%d/%Y",      # 04/12/2023
                    "%Y/%m/%d",      # 2023/04/12
                    "%d.%m.%Y",      # 12.04.2023
                    "%Y.%m.%d"       # 2023.04.12
                ]
                
                parsed_date = None
                for fmt in formats:
                    try:
                        parsed_date = datetime.datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                        
                if parsed_date:
                    # Format for HTML date input (YYYY-MM-DD)
                    return parsed_date.strftime("%Y-%m-%d")
            
            # If we couldn't parse the string, return it as is
            return str(value)
        except Exception:
            # If any error occurs, return the original value as a string
            return str(value)
            
    if field_type == "number" and not isinstance(value, str):
        return str(int(value) if isinstance(value, bool) or value == int(value) else value)
        
    # Default case: convert to string
    return str(value)


def create_field_mapping(schema: Dict[str, Dict[str, Any]], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a mapping between form fields and data values based on a schema.
    
    Args:
        schema: Dictionary mapping field names to field properties
        data: The data to map to the form fields
        
    Returns:
        Dictionary mapping field names to their values
    """
    field_values = {}
    
    for field_name, field_info in schema.items():
        # Get the data path for this field
        data_path = field_info.get("data_path")
        
        if data_path:
            # If data path is explicitly defined in the schema, use it
            value = resolve_data_path(data, data_path)
        else:
            # Otherwise, try to find the best match for the field name
            data_path, value = find_best_match(field_name, data)
            
        if value is not None:
            # Format the value according to the field type
            field_type = field_info.get("type", "text")
            formatted_value = format_value(value, field_type)
            field_values[field_name] = formatted_value
            
    return field_values


def map_data_for_form(form_type: str, data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Map data to form fields for a specific form type.
    
    Args:
        form_type: Type of form ("easy" or "hard")
        data: The data to map to the form
        schema: Schema defining the form structure
        
    Returns:
        Dictionary mapping form fields to their values
    """
    if form_type not in ["easy", "hard"]:
        raise DataMappingError(f"Invalid form type: {form_type}. Must be 'easy' or 'hard'")
        
    try:
        # Map data to fields based on the schema
        field_values = create_field_mapping(schema, data)
        
        # For hard form, handle conditional fields specifically
        if form_type == "hard" and "sections" in schema:
            for section_name, section_schema in schema["sections"].items():
                section_field_values = create_field_mapping(section_schema, data)
                field_values.update(section_field_values)
        
        return field_values
    except Exception as e:
        raise DataMappingError(f"Error mapping data for {form_type} form: {str(e)}")


if __name__ == "__main__":
    # Simple test to verify data loading functionality
    import sys
    
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
        try:
            data = load_data_from_file(data_file)
            print(f"Successfully loaded data from {data_file}:")
            print(json.dumps(data, indent=2))
            
            # Print flattened data for debugging
            print("\nFlattened data:")
            flattened = flatten_dict(data)
            for key, value in flattened.items():
                print(f"{key}: {value}")
        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        print("Please provide a data file path as an argument")