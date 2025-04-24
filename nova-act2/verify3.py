#!/usr/bin/env python3
"""
Improved verification utility for the Asteroid Form Challenge.
Provides enhanced functions to verify if fields have been filled correctly.
"""

import logging
from typing import Dict, List, Any, Tuple
from nova_act import NovaAct, BOOL_SCHEMA
from config import FIELD_TYPES, SECTION_MAPPING, FIELD_DEPENDENCIES
from field_detection import get_form_label as centralized_get_form_label

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

def verify_field_filled(nova: NovaAct, label: str, expected_value, field_type: str = "text", section_name: str = None) -> bool:
    """
    Specialized verification for fields that were previously filled but failed verification.
    Uses more robust approaches to locate and verify the field.
    
    Args:
        nova: NovaAct instance
        label: The label of the field to verify
        expected_value: The expected value in the field
        field_type: The type of field ("text", "dropdown", "checkbox", "date")
        section_name: Optional section name for context
        
    Returns:
        bool: True if the field contains the expected value, False otherwise
    """
    # Convert expected_value to string unless it's a boolean (for checkboxes)
    if not isinstance(expected_value, bool):
        expected_value = str(expected_value)
    
    logger.info(f"Using specialized verification for previously filled field '{label}'")
    
    # First, try to make sure we can see the field (more aggressive scrolling)
    try:
        find_command = (
            f"Find the {field_type} field labeled '{label}'. "
            f"Scroll carefully to ensure it's fully visible in the center of the screen. "
            f"Take your time to locate it precisely."
        )
        if section_name:
            find_command = f"In the {section_name} section, {find_command.lower()}"
            
        nova.act(find_command, max_steps=5)
        logger.info(f"Focused on field '{label}' for specialized verification")
    except Exception as e:
        logger.warning(f"Couldn't focus on field '{label}': {e}")
        # Continue anyway - we'll try to verify even if focusing failed
    
    # Construct specialized queries based on field type
    if field_type == "checkbox":
        state = "checked" if expected_value else "unchecked"
        logger.info(f"Verifying checkbox '{label}' is {state} (specialized)")
        
        # Try multiple query variants for checkboxes
        queries = [
            f"Is the checkbox labeled '{label}' {state}? Answer true or false.",
            f"Check if the checkbox with label '{label}' is {state}. Answer true or false.",
            f"Find the checkbox '{label}' and tell me if it's {state}. Answer true or false."
        ]
        
    elif field_type == "dropdown":
        logger.info(f"Verifying dropdown '{label}' has '{expected_value}' selected (specialized)")
        
        # Try multiple query variants for dropdowns
        queries = [
            f"Does the dropdown field labeled '{label}' have the option '{expected_value}' selected? Answer true or false.",
            f"Is '{expected_value}' selected in the dropdown '{label}'? Answer true or false.",
            f"Look at the dropdown field '{label}'. Is the value '{expected_value}' selected? Answer true or false."
        ]
        
    elif field_type == "date":
        logger.info(f"Verifying date field '{label}' contains '{expected_value}' (specialized)")
        
        # Try multiple query variants for date fields
        queries = [
            f"Does the date field labeled '{label}' contain the date '{expected_value}'? Answer true or false.",
            f"Is '{expected_value}' present in the date field '{label}'? Answer true or false.",
            f"Check the date input with label '{label}'. Does it show '{expected_value}'? Answer true or false."
        ]
        
    else:  # Default text field
        logger.info(f"Verifying text field '{label}' contains '{expected_value}' (specialized)")
        
        # Try multiple query variants for text fields
        queries = [
            f"Does the field labeled '{label}' contain the value '{expected_value}'? Answer true or false.",
            f"Is the text '{expected_value}' present in the field '{label}'? Answer true or false.",
            f"Find the input field '{label}'. Does it have the value '{expected_value}'? Answer true or false."
        ]
    
    # Try each query until one succeeds
    for i, query in enumerate(queries):
        try:
            logger.info(f"Trying verification query variant {i+1}/{len(queries)}")
            result = nova.act(query, schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                logger.info(f"✅ Specialized verification successful: Field '{label}' contains expected value")
                return True
            
            # If this query failed but we have more to try, continue
            if i < len(queries) - 1:
                logger.info(f"Query variant {i+1} failed, trying next variant")
                continue
                
            # If all queries failed, return failure
            logger.warning(f"❌ All specialized verification queries failed for field '{label}'")
            return False
            
        except Exception as e:
            logger.warning(f"Error with verification query variant {i+1}: {e}")
            # Continue to next query if there are more to try
            if i < len(queries) - 1:
                continue
            
            # If this was the last query, fail
            logger.exception(f"All specialized verification attempts failed for field '{label}'")
            return False
    
    # Shouldn't reach here, but just in case
    return False

def get_form_label(key: str, section_name: str = None) -> str:
    """
    Convert a JSON field key to a likely form label.
    
    Now redirects to the centralized get_form_label function to ensure consistency.
    
    Args:
        key: JSON field key in camelCase
        section_name: Optional section name for context-aware conversions
        
    Returns:
        str: Converted form label in Title Case with spaces
    """
    # Use the centralized function for consistency
    return centralized_get_form_label(key, section_name)

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

def verify_section(nova: NovaAct, section_name: str, form_data: Dict[str, Any], 
               subsection_name: str = None, specific_fields: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Verify if fields in a section or specific subsection have been filled correctly.
    
    This improved version uses find_field to ensure fields are located
    before verification is attempted. When subsection_name is provided,
    only verifies fields within that specific subsection. When specific_fields
    is provided, only verifies those specific fields.
    
    Args:
        nova: NovaAct instance
        section_name: Name of the current form section
        form_data: Complete form data dictionary
        subsection_name: Optional subsection name to verify only that subsection
        specific_fields: Optional list of specific fields to verify (instead of all fields)
                         Each item should be a dict with keys: key, json_section, value, field_type
        
    Returns:
        List[Dict[str, Any]]: List of fields that failed verification with details
    """
    # Handle targeted verification of specific fields
    if specific_fields:
        logger.info(f"Performing targeted verification of {len(specific_fields)} specific fields in section '{section_name}'")
        return verify_specific_fields(nova, specific_fields)
    
    # Handle regular section/subsection verification
    if subsection_name:
        logger.info(f"Verifying fields in subsection '{subsection_name}' of section '{section_name}'")
    else:
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
            # If subsection_name is specified, only verify that subsection
            if subsection_name:
                if subsection_name in section_data and isinstance(section_data[subsection_name], dict):
                    logger.info(f"Verifying specified subsection '{subsection_name}' in premises")
                    subsection_data = section_data[subsection_name]
                    failed = verify_subsection_fields(nova, section_name, json_section, 
                                                    subsection_name, subsection_data)
                    failed_fields.extend(failed)
                else:
                    logger.warning(f"Subsection '{subsection_name}' not found in premises data")
            else:
                # No subsection specified, verify all subsections
                for sub_name, subsection_data in section_data.items():
                    if isinstance(subsection_data, dict):
                        logger.info(f"Verifying subsection '{sub_name}' in premises")
                        failed = verify_subsection_fields(nova, section_name, json_section, 
                                                        sub_name, subsection_data)
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
                
                # Get field label and type with section context
                label = get_form_label(key, section_name)
                
                # Skip if field type is unknown
                if key not in FIELD_TYPES:
                    logger.warning(f"Field '{key}' not found in FIELD_TYPES configuration, skipping verification")
                    continue
                
                field_type = FIELD_TYPES[key]
                
                # First find the field using the new find_field function
                logger.info(f"Locating field '{label}' for verification")
                from field_detection import find_field
                if find_field(nova, label, section_name, field_type):
                    # Now perform verification on the found field
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
                else:
                    # If field can't be found, mark it as failed
                    logger.warning(f"Field '{label}' could not be found, marking as verification failed")
                    failed_fields.append({
                        "section": section_name,
                        "json_section": json_section,
                        "key": key,
                        "label": label,
                        "expected_value": value,
                        "field_type": field_type,
                        "reason": "field_not_found"
                    })
    
    if failed_fields:
        logger.warning(f"Found {len(failed_fields)} fields that failed verification in section '{section_name}'")
    else:
        logger.info(f"All fields in section '{section_name}' verified successfully")
    
    return failed_fields

def verify_specific_fields(nova: NovaAct, specific_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Verify only specific fields that were previously unverified or failed.
    Uses the specialized verify_field_filled function for more robust verification.
    
    Args:
        nova: NovaAct instance
        specific_fields: List of field information dictionaries
        
    Returns:
        List[Dict[str, Any]]: List of fields that still failed verification
    """
    logger.info(f"Performing targeted verification of {len(specific_fields)} specific fields")
    still_failed = []
    
    for field_info in specific_fields:
        section_name = field_info.get("section")
        key = field_info.get("key")
        label = field_info.get("label")
        value = field_info.get("expected_value")
        field_type = field_info.get("field_type")
        
        # Skip if missing essential information
        if not all([section_name, key, label, field_type]):
            logger.warning(f"Skipping field with incomplete information: {field_info}")
            continue
            
        logger.info(f"Performing specialized verification for field '{label}' ({field_type})")
        
        # Use the specialized verification function for filled fields
        verification_success = verify_field_filled(
            nova, 
            label, 
            value, 
            field_type, 
            section_name
        )
        
        if verification_success:
            logger.info(f"✅ Field '{label}' now verified successfully with specialized verification")
        else:
            logger.warning(f"❌ Field '{label}' still fails verification with specialized approach")
            # Keep the original field info in the failed list
            still_failed.append(field_info)
    
    if still_failed:
        logger.warning(f"{len(still_failed)} fields still failed verification after specialized verification")
    else:
        logger.info("All targeted fields now verify successfully with specialized verification")
        
    return still_failed

def verify_subsection_fields(nova: NovaAct, section_name: str, json_section: str, 
                             subsection_name: str, subsection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Verify fields in a subsection using the new find_field function.
    
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
    
    # First navigate to the subsection
    from field_detection import navigate_to_subsection
    nav_result = navigate_to_subsection(nova, section_name, subsection_name)
    if not nav_result:
        logger.warning(f"Failed to navigate to subsection '{subsection_name}', verification may be incomplete")
    
    for key, value in subsection_data.items():
        # Handle nested address in subsection
        if key == "address" and isinstance(value, dict):
            address_failed = verify_address_fields(nova, section_name, value)
            failed_fields.extend(address_failed)
            continue
        
        # Get field label and type with section context
        label = get_form_label(key, section_name)
        
        # Skip if field type is unknown
        if key not in FIELD_TYPES:
            logger.warning(f"Field '{key}' not found in FIELD_TYPES configuration, skipping verification")
            continue
        
        field_type = FIELD_TYPES[key]
        
        # Use the new find_field function
        from field_detection import find_field
        logger.info(f"Locating field '{label}' in subsection '{subsection_name}' for verification")
        if find_field(nova, label, section_name, field_type):
            # Now perform verification
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
        else:
            # If field can't be found, mark it as failed
            logger.warning(f"Field '{label}' in subsection '{subsection_name}' could not be found")
            failed_fields.append({
                "section": section_name,
                "json_section": json_section,
                "subsection": subsection_name,
                "key": key,
                "label": label,
                "expected_value": value,
                "field_type": field_type,
                "reason": "field_not_found"
            })
    
    return failed_fields

def verify_address_fields(nova: NovaAct, section_name: str, address_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Verify all fields in an address block by directly checking for values.
    
    Args:
        nova: NovaAct instance
        section_name: Section containing the address fields
        address_data: Dictionary containing address components
        
    Returns:
        List[Dict[str, Any]]: List of address fields that failed verification
    """
    failed_fields = []
    
    # Define position descriptions for error messages
    position_descriptions = {
        "addressLine1": "first line",
        "addressLine2": "second line", 
        "addressLine3": "third line",
        "city": "city field",
        "postcode": "postcode field"
    }
    
    # First focus on the address section in general
    logger.info(f"Focusing on the address section in {section_name}")
    
    # Try a few different approaches to focus on the address section
    address_focus_attempts = [
        f"Look at the address fields in the {section_name} section",
        f"Find the address section of the {section_name} form",
        f"Look for address information in the {section_name} section"
    ]
    
    focus_success = False
    for focus_attempt in address_focus_attempts:
        try:
            nova.act(focus_attempt, max_steps=3)
            focus_success = True
            logger.info("Successfully focused on the address section")
            break
        except Exception as e:
            logger.warning(f"Failed to focus with prompt: '{focus_attempt}': {e}")
    
    if not focus_success:
        logger.warning("Could not focus on address section, verification may be less reliable")
    
    # Verify each address value directly
    for key, value in address_data.items():
        if not value:  # Skip empty values
            continue
            
        position_desc = position_descriptions.get(key, key)
        
        # Direct verification without trying to find the field first
        logger.info(f"Directly verifying if '{value}' is present in the {position_desc}")
        
        # Create a simple query that asks if the value is visible
        query = f"Is the text '{value}' visible in the address section of the form? Answer true or false."
        
        try:
            result = nova.act(query, schema=BOOL_SCHEMA)
            if result.matches_schema and result.parsed_response:
                logger.info(f"✅ Value '{value}' found in the address section")
            else:
                logger.warning(f"❌ Value '{value}' not found in the address section")
                
                # Try a more specific query as a fallback
                specific_query = f"Is the value '{value}' present in the {position_desc} of the address? Answer true or false."
                specific_result = nova.act(specific_query, schema=BOOL_SCHEMA)
                
                if specific_result.matches_schema and specific_result.parsed_response:
                    logger.info(f"✅ Value '{value}' found in the {position_desc} on second attempt")
                else:
                    # If still not found, add to failed fields
                    logger.warning(f"❌ Value '{value}' not found in the address section on multiple attempts")
                    failed_fields.append({
                        "section": section_name,
                        "key": key,
                        "position": position_desc,
                        "expected_value": value,
                        "field_type": "text",
                        "is_address_field": True,
                        "reason": "value_not_found"
                    })
        except Exception as e:
            logger.exception(f"Error verifying address value '{value}': {e}")
            failed_fields.append({
                "section": section_name,
                "key": key,
                "position": position_desc,
                "expected_value": value,
                "field_type": "text",
                "is_address_field": True,
                "reason": "verification_error"
            })
    
    return failed_fields