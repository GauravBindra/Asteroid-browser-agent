#!/usr/bin/env python3
"""
Utility functions for Nova-ACT form automation.
"""

import json
import logging

def load_json_data(file_path):
    """
    Load and parse JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        raise

# Test function
if __name__ == "__main__":
    # Test with the provided data file
    import os
    
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             "easy_form_data.json")
    
    print(f"Testing with file: {file_path}")
    
    if os.path.exists(file_path):
        data = load_json_data(file_path)
        print(f"Successfully loaded data: {data}")
    else:
        print(f"Test file not found: {file_path}")

#   1. Defines a load_json_data function that:
#     - Takes a file path as input
#     - Opens and reads the JSON file
#     - Returns the parsed JSON data
#     - Handles basic error cases (file not found, invalid JSON)
#   2. Includes a simple test at the bottom that:
#     - Runs when the file is executed directly
#     - Attempts to load the easy_form_data.json file
#     - Prints the loaded data for verification