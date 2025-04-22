#!/usr/bin/env python3
"""
Verification utility for the Asteroid Form Challenge.
Provides functions to verify if fields have been filled correctly.
"""

import logging
from typing import Dict, List, Any, Tuple
from nova_act import NovaAct, BOOL_SCHEMA
from config import FIELD_TYPES, SECTION_MAPPING, FIELD_DEPENDENCIES

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def verify_field(nova: NovaAct, label: str, expected_value, field_type: str = "text") -> bool:
    """
    Verify if a field contains the expected value.
    
    Args:
        nova: NovaAct instance
        label: The label of the field to verify
        expected_value: The expected value in the field
        field_type: The type of field ("text", "dropdown", "checkbox", "date")
        
    Returns:
        bool: True if the field contains the expected value, False otherwise
    """
    # Convert expected_value to string unless it's a boolean (for checkboxes)
    if not isinstance(expected_value, bool):
        expected_value = str(expected_value)
    
    # Construct query based on field type
    if field_type == "checkbox":
        state = "checked" if expected_value else "unchecked"
        logger.info(f"Verifying checkbox '{label}' is {state}")
        query = f"Is the checkbox labeled '{label}' {state}? Answer true or false."
    elif field_type == "dropdown":
        logger.info(f"Verifying dropdown '{label}' has '{expected_value}' selected")
        query = f"Does the dropdown field labeled '{label}' have the option '{expected_value}' selected? Answer true or false."
    elif field_type == "date":
        logger.info(f"Verifying date field '{label}' contains '{expected_value}'")
        query = f"Does the date field labeled '{label}' contain the date '{expected_value}'? Answer true or false."
    else:  # Default text field
        logger.info(f"Verifying text field '{label}' contains '{expected_value}'")
        query = f"Does the field labeled '{label}' contain the value '{expected_value}'? Answer true or false."
    
    try:
        result = nova.act(query, schema=BOOL_SCHEMA)
        
        if result.matches_schema and result.parsed_response:
            logger.info(f"✅ Verification successful: Field '{label}' contains expected value")
            return True
        else:
            logger.warning(f"❌ Verification failed: Field '{label}' does not contain expected value")
            return False
    except Exception as e:
        logger.exception(f"Error verifying field '{label}': {e}")
        return False

def get_form_label(key: str) -> str:
    """
    Convert a JSON field key to a likely form label.
    
    Args:
        key: JSON field key in camelCase
        
    Returns:
        str: Converted form label in Title Case with spaces
    """
    # Special case handling for known fields
    special_cases = {
        "name": "Business Name",
        "type": "Business Type", 
        "address": "Address"
    }
    
    if key in special_cases:
        return special_cases[key]
    
    # Convert camelCase to Title Case with spaces
    label_words = []
    current_word = ""
    
    for char in key:
        if char.isupper():
            if current_word:
                label_words.append(current_word)
            current_word = char
        else:
            current_word += char
    
    if current_word:
        label_words.append(current_word)
    
    return " ".join(word.capitalize() for word in label_words)

def should_process_field(data: Dict[str, Any], key: str, section_name: str) -> bool:
    """
    Check if a field should be processed based on dependencies.
    
    Args:
        data: Section data containing all fields
        key: Field key to check
        section_name: Name of the current form section
        
    Returns:
        bool: True if field should be processed, False otherwise
    """
    if key not in FIELD_DEPENDENCIES:
        return True  # No dependencies, always process
        
    dependency = FIELD_DEPENDENCIES[key]
    
    # Skip if field is in a different section
    if dependency["section"] != section_name:
        return True
        
    prerequisite_field = dependency["prerequisite_field"]
    prerequisite_value = dependency["prerequisite_value"]
    
    # Check if prerequisite field exists and has the expected value
    if prerequisite_field in data:
        actual_value = data[prerequisite_field]
        return actual_value == prerequisite_value
        
    return False  # Prerequisite field not found, skip to be safe

def verify_section(nova: NovaAct, section_name: str, form_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Verify if all fields in a section have been filled correctly.
    
    Args:
        nova: NovaAct instance
        section_name: Name of the current form section
        form_data: Complete form data dictionary
        
    Returns:
        List[Dict[str, Any]]: List of fields that failed verification with details
    """
    logger.info(f"Verifying all fields in section: {section_name}")
    failed_fields = []
    
    # Find the JSON section names that correspond to this form section
    json_sections = []
    for json_section, form_section in SECTION_MAPPING.items():
        if form_section == section_name and json_section in form_data:
            json_sections.append(json_section)
    
    if not json_sections:
        logger.warning(f"No data found for section '{section_name}' in form data")
        return failed_fields
    
    # Process each JSON section
    for json_section in json_sections:
        section_data = form_data[json_section]
        logger.info(f"Verifying fields from data section '{json_section}'")
        
        # Handle special case for nested sections like premises
        if json_section == "premises" and isinstance(section_data, dict):
            for subsection_name, subsection_data in section_data.items():
                if isinstance(subsection_data, dict):
                    logger.info(f"Verifying subsection '{subsection_name}' in premises")
                    failed = verify_subsection_fields(nova, section_name, json_section, 
                                                      subsection_name, subsection_data)
                    failed_fields.extend(failed)
        else:
            # Process regular section fields
            for key, value in section_data.items():
                # Skip address fields as they're handled specially
                if key == "address" and isinstance(value, dict):
                    address_failed = verify_address_fields(nova, section_name, value)
                    failed_fields.extend(address_failed)
                    continue
                
                # Skip fields that shouldn't be processed due to dependencies
                if not should_process_field(section_data, key, section_name):
                    logger.info(f"Skipping verification of field '{key}' due to dependencies")
                    continue
                
                # Get field label and type
                label = get_form_label(key)
                
                # Skip if field type is unknown
                if key not in FIELD_TYPES:
                    logger.warning(f"Field '{key}' not found in FIELD_TYPES configuration, skipping verification")
                    continue
                
                field_type = FIELD_TYPES[key]
                
                # First, scroll to ensure the field is visible
                try:
                    logger.info(f"Scrolling to field '{label}' before verification")
                    find_command = f"Find the field labeled '{label}' and ensure it's visible. Scroll if necessary."
                    nova.act(find_command, max_steps=5)
                    # Small delay to ensure UI is stable after scrolling
                    import time
                    time.sleep(0.5)
                except Exception as e:
                    logger.warning(f"Error while scrolling to field '{label}': {e}")
                    # Continue anyway, as field may still be visible
                
                # Perform verification
                logger.info(f"Verifying field '{label}' (type: {field_type}, expected value: {value})")
                verification_success = verify_field(nova, label, value, field_type)
                
                if not verification_success:
                    failed_fields.append({
                        "section": section_name,
                        "json_section": json_section,
                        "key": key,
                        "label": label,
                        "expected_value": value,
                        "field_type": field_type
                    })
    
    if failed_fields:
        logger.warning(f"Found {len(failed_fields)} fields that failed verification in section '{section_name}'")
    else:
        logger.info(f"All fields in section '{section_name}' verified successfully")
    
    return failed_fields

def verify_subsection_fields(nova: NovaAct, section_name: str, json_section: str, 
                             subsection_name: str, subsection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Verify fields in a subsection (e.g., premises.identity or premises.construction).
    
    Args:
        nova: NovaAct instance
        section_name: Main section name
        json_section: JSON section name
        subsection_name: Subsection name
        subsection_data: Subsection data dictionary
        
    Returns:
        List[Dict[str, Any]]: List of fields that failed verification
    """
    failed_fields = []
    
    for key, value in subsection_data.items():
        # Handle nested address in subsection
        if key == "address" and isinstance(value, dict):
            address_failed = verify_address_fields(nova, section_name, value)
            failed_fields.extend(address_failed)
            continue
        
        # Get field label and type
        label = get_form_label(key)
        
        # Skip if field type is unknown
        if key not in FIELD_TYPES:
            logger.warning(f"Field '{key}' not found in FIELD_TYPES configuration, skipping verification")
            continue
        
        field_type = FIELD_TYPES[key]
        
        # Perform verification
        logger.info(f"Verifying field '{label}' in subsection '{subsection_name}' (type: {field_type}, expected value: {value})")
        verification_success = verify_field(nova, label, value, field_type)
        
        if not verification_success:
            failed_fields.append({
                "section": section_name,
                "json_section": json_section,
                "subsection": subsection_name,
                "key": key,
                "label": label,
                "expected_value": value,
                "field_type": field_type
            })
    
    return failed_fields

def verify_address_fields(nova: NovaAct, section_name: str, address_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Verify all fields in an address block.
    
    Args:
        nova: NovaAct instance
        section_name: Section containing the address fields
        address_data: Dictionary containing address components
        
    Returns:
        List[Dict[str, Any]]: List of address fields that failed verification
    """
    failed_fields = []
    
    # Define field mappings (JSON keys to form labels)
    field_mappings = {
        "addressLine1": "Address Line 1",
        "addressLine2": "Address Line 2",
        "addressLine3": "Address Line 3",
        "city": "City",
        "postcode": "Postcode"
    }
    
    # Verify each address field
    for key, form_label in field_mappings.items():
        if key not in address_data or not address_data[key]:
            continue
            
        value = address_data[key]
        
        # Verify this field
        verification_success = verify_field(nova, form_label, value, "text")
        
        if not verification_success:
            failed_fields.append({
                "section": section_name,
                "key": key,
                "label": form_label,
                "expected_value": value,
                "field_type": "text",
                "is_address_field": True
            })
    
    return failed_fields