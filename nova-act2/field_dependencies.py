#!/usr/bin/env python3
"""
Field dependencies module for form automation.

This module defines utility functions for handling conditional fields in form automation,
using configuration from the config module.
"""

import logging
from config import FIELD_DEPENDENCIES

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def should_process_field(data, field_name, current_section=None):
    """
    Determine if a field should be processed based on its dependencies.
    
    Args:
        data: Complete form data dictionary
        field_name: Name of the field to check
        current_section: The section from which this check is being made (optional)
        
    Returns:
        bool: True if field should be processed, False if it should be skipped
    """
    # If field has no dependencies, always process it
    if field_name not in FIELD_DEPENDENCIES:
        return True
        
    dependency = FIELD_DEPENDENCIES[field_name]
    prereq_field = dependency["prerequisite_field"]
    prereq_value = dependency["prerequisite_value"]
    dependency_section = dependency["section"]
    
    # If current_section is provided, check if it matches the dependency section
    if current_section and dependency_section != current_section:
        logger.info(f"Skipping field '{field_name}' - field is in section '{dependency_section}', not in current section '{current_section}'")
        # If we're processing a different section, we should skip this field
        return False
    
    # Check if prerequisite field exists in the data
    if prereq_field not in data:
        logger.info(f"Skipping field '{field_name}' - prerequisite '{prereq_field}' not in data")
        return False
        
    # Check if prerequisite field has the required value
    if data[prereq_field] != prereq_value:
        logger.info(f"Skipping field '{field_name}' - prerequisite '{prereq_field}' value is {data[prereq_field]}, not {prereq_value}")
        return False
        
    # All dependency checks passed
    return True

# def get_dependent_fields(data, section=None):
#     """
#     Filter a data dictionary to return only fields that should be processed
#     based on dependencies.
    
#     Args:
#         data: Dictionary containing all form data
#         section: Optional section name to filter by
        
#     Returns:
#         dict: Filtered dictionary with only processable fields
#     """
#     filtered_data = {}
    
#     for field_name, value in data.items():
#         # If section is specified, check dependencies only for that section
#         if section:
#             # Skip if field is dependent and in specified section but should not be processed
#             if (field_name in FIELD_DEPENDENCIES and 
#                 FIELD_DEPENDENCIES[field_name]["section"] == section and 
#                 not should_process_field(data, field_name, section)):
#                 logger.info(f"Filtering out dependent field '{field_name}' in section '{section}'")
#                 continue
#         # No section specified, check all dependencies
#         elif not should_process_field(data, field_name):
#             logger.info(f"Filtering out dependent field '{field_name}'")
#             continue
            
#         # Field passes dependency check, include it
#         filtered_data[field_name] = value
        
#     return filtered_data
