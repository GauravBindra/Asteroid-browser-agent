#!/usr/bin/env python3
"""
Field detection utility for Nova-ACT form automation.

This module provides a simple function for detecting the presence of form fields
by their labels in the current form tab.
"""

import logging
import time
from nova_act import BOOL_SCHEMA, NovaAct

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def navigate_to_subsection(nova, section_name, subsection_name):
    """
    Navigate to a specific subsection within a section.
    
    Args:
        nova: NovaAct instance
        section_name: Main section name (e.g., "Premises Details")
        subsection_name: Subsection name to navigate to (e.g., "Construction Details")
        
    Returns:
        bool: True if successfully navigated to subsection
    """
    logger.info(f"Navigating to {subsection_name} subsection within {section_name}")
    
    # First check if the subsection header is already visible
    check_visible = nova.act(
        f"Is the '{subsection_name}' subsection header visible in the {section_name} section? "
        f"Answer true or false.", 
        schema=BOOL_SCHEMA
    )
    
    if check_visible.matches_schema and check_visible.parsed_response:
        logger.info(f"{subsection_name} subsection is already visible")
        return True
        
    # If not visible, explicitly navigate to it
    navigation_command = (
        f"In the {section_name} section, find and scroll to the '{subsection_name}' subsection header. "
        f"Make sure the subsection header is at the top portion of the screen."
    )
    
    try:
        nova.act(navigation_command, max_steps=3)
        
        # Verify we found the right subsection
        verify = nova.act(
            f"Can you see the '{subsection_name}' subsection heading now? Answer true or false.",
            schema=BOOL_SCHEMA
        )
        
        if verify.matches_schema and verify.parsed_response:
            logger.info(f"Successfully navigated to {subsection_name} subsection")
            return True
        else:
            logger.warning(f"Failed to navigate to {subsection_name} subsection")
            return False
            
    except Exception as e:
        logger.exception(f"Error navigating to {subsection_name} subsection: {e}")
        return False

def field_exists(nova: NovaAct, label: str, current_tab: str, field_type: str = None, subsection: str = None) -> bool:
    """
    Check if a field with the given label exists in the current form tab/subsection.
    
    Args:
        nova: NovaAct instance
        label: Label text to look for
        current_tab: Name of the current form tab (e.g., "Contact Details")
        field_type: Type of field to look for (e.g., "dropdown", "text", "checkbox")
        subsection: Name of the subsection within the tab (e.g., "Property Identity")
        
    Returns:
        bool: True if field exists in the current tab/subsection
    """
    if subsection:
        location = f"{subsection} subsection of {current_tab}"
        logger.info(f"Checking if '{field_type}' field labeled '{label}' exists in the {location}")
        
        # Make sure we're in the right subsection before checking for fields
        subsection_nav_success = navigate_to_subsection(nova, current_tab, subsection)
        if not subsection_nav_success:
            logger.warning(f"Could not navigate to {subsection} subsection, field detection may fail")
    else:
        location = f"{current_tab} tab"
        logger.info(f"Checking if '{field_type}' field labeled '{label}' exists {location}")
    
    try:
        # Include field type and subsection in query if provided
        if subsection and field_type:
            query = (
                f"Is there a {field_type} field labeled '{label}' in the {subsection} subsection of {current_tab}? "
                f"Answer true or false."
            )
        elif subsection:
            query = (
                f"Is there a field '{label}' in the {subsection} subsection of {current_tab}? "
                f"Answer true or false."
            )
        elif field_type:
            query = (
                f"Is there a {field_type} field labeled '{label}' in {current_tab} section? "
                f"Answer true or false."
            )
        else:
            query = (
                f"Is there a field '{label}' in {current_tab} section? "
                f"Answer true or false."
            )
        result = nova.act(query, schema=BOOL_SCHEMA)

        location = f"{subsection} subsection of {current_tab}" if subsection else f"{current_tab} tab"

        if result.parsed_response:
            logger.info(f"{field_type if field_type else 'Field'} labeled '{label}' found in {location}")
            return True
        else:
            nova.act(f"Scroll down till you see the website footer. ",max_steps=3)
            result = nova.act(query, schema=BOOL_SCHEMA)

            if result.parsed_response:
                logger.info(f"{field_type if field_type else 'Field'} labeled '{label}' found in {location}")
                return True
            else:
                logger.info(f"{field_type if field_type else 'Field'} labeled '{label}' not found in {location}")
                nova.act(f"Scroll up till you see 'Commercial Property Insurance Application'.",max_steps=3)
                result = nova.act(query, schema=BOOL_SCHEMA)

                if result.parsed_response:
                    logger.info(f"{field_type if field_type else 'Field'} labeled '{label}' found in {location}")
                    return True
                else:
                    logger.info(f"{field_type if field_type else 'Field'} labeled '{label}' not found in {location}")
                    return False

    except Exception as e:
        logger.exception(f"Error checking if field exists: {e}")
        return False


def find_field(nova: NovaAct, label: str, section_name: str, field_type: str, 
  max_attempts: int = 3) -> bool:
      """
      Find a field in the form with retry logic.
      
      Args:
          nova: NovaAct instance
          label: Field label to find
          section_name: Section containing the field
          field_type: Type of the field ("text", "dropdown", "checkbox", "date")
          max_attempts: Maximum number of retry attempts
          
      Returns:
          bool: True if the field was found, False otherwise
      """
      logger = logging.getLogger("nova_form_automation")
      logger.info(f"Finding field '{label}' ({field_type}) in {section_name} section")

      for attempt in range(max_attempts):
          if attempt > 0:
              logger.info(f"Retry attempt {attempt + 1}/{max_attempts} to find field '{label}'")

          try:
              # Check if field exists - if this returns true, the field is already visible
              # so we don't need additional checks
              if field_exists(nova, label, section_name, field_type):
                  logger.info(f"✅ Successfully found field '{label}'")
                  return True

              # Last attempt already tried with the standard label, no additional fallback needed
              elif attempt == max_attempts - 1:
                  logger.info(f"Field '{label}' not found after {max_attempts} attempts")
                  # No fallback to raw field names

          except Exception as e:
              logger.warning(f"Error during attempt {attempt + 1} to find field '{label}': {e}")
              # If last attempt, give up, otherwise continue to next attempt
              if attempt == max_attempts - 1:
                  logger.error(f"Failed to find field '{label}' after {max_attempts} attempts")
                  return False

              # Short pause before retry
              time.sleep(0.5)

      logger.error(f"Failed to find field '{label}' after {max_attempts} attempts")
      return False

# Centralized field label mapping
def get_form_label(key: str, section_name: str = None) -> str:
    """
    Get the form label for a JSON field key, taking section context into account.
    
    This centralized function handles all special cases and section-specific mappings.
    
    Args:
        key: The JSON field key (e.g., "firstName", "type")
        section_name: Optional section name for context-specific mappings
        
    Returns:
        str: The corresponding form label to use
    """
    # Section-specific mappings
    section_mappings = {
        "Contact Details": {
            "phoneNumber": "Phone Number",
            "firstName": "First Name",
            "lastName": "Last Name",
            "dateOfBirth": "Date of Birth",
            "jointInsuredPersonName": "Joint Insured Person Name",
            "jointInsured": "Joint Insured",
            "numberOfYearsAsLandlord": "Number of Years as Landlord",
        },
        "Business Info": {
            "name": "Business Name",
            "type": "Business Type",
            "yearsOfExperience": "Years of Experience",
            "descriptionOfExperience": "Description of Experience",
            "ernTaxCode": "ERN Tax Code",
            "exemptFromERNCode": "Exempt from ERN Code",
            "websiteUrl": "Website URL",
        },
        "Premises Details": {
            "type": "Property Type",
            "listed": "Listed Status",
            "numberOfFlatsInBlock": "Number of Flats in Block",
            "numberOfFlatsToBeInsured": "Number of Flats to be Insured",
            "rebuildingCost": "Rebuilding Cost (£)",
            "yearOfConstruction": "Year of Construction",
            "hasFlatRoof": "Has Flat Roof",
            "percentageOfFlatRoof": "Percentage of Flat Roof",
            "flatRoofLastInspected": "Flat Roof Last Inspected",
            "isBuildingPurposeBuilt": "Is Building Purpose Built",
            "isUndergoingBuildingWorks": "Is Undergoing Building Works",
        },
        "Security & Safety": {
            "cctv": "CCTV Installed",
            "cctvType": "CCTV Type",
            "cctvCoverage": "CCTV Coverage",
            "selfContained": "Self Contained",
            "doorSecurityType": "Door Security Type",
            "fittedWithSmokeAlarms": "Fitted with Smoke Alarms",
            "intruderAlarm": "Intruder Alarm",
            "intruderAlarmType": "Intruder Alarm Type",
            "requireTerrorismCover": "Require Terrorism Cover",
            "fireAlarm": "Fire Alarm",
            "flammableLiquidStored": "Flammable Liquid Stored",
            "flammableLiquids": "Flammable Liquids",
        },
        "Coverage Options": {
            "sumInsuredLossOfRent": "Sum Insured Loss of Rent",
            "periodOfIndemnityInMonths": "Period of Indemnity in Months",
            "propertyOwnersLiabilityAmount": "Property Owners Liability Amount",
            "terrorism": "Terrorism",
            "subsidence": "Subsidence",
            "accidentalDamage": "Accidental Damage",
        }
    }
    
    # General mappings (fallback if no section-specific mapping exists)
    general_mappings = {
        "name": "Name",
        "type": "Type", 
        "address": "Address",
        "city": "City",
        "postcode": "Postcode",
    }
    
    # First check section-specific mappings if section is provided
    if section_name and section_name in section_mappings and key in section_mappings[section_name]:
        return section_mappings[section_name][key]
    
    # Then check general mappings
    if key in general_mappings:
        return general_mappings[key]
    
    # Default: convert camelCase to Title Case
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