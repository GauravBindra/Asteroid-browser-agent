#!/usr/bin/env python3
"""
Form automation functions for Nova-ACT.

This module contains functions for automating form filling using Nova-ACT.
"""

import logging
import time
import re
import asyncio

def wait_for_form_load(nova):
    """
    Wait for the form to fully load.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Waiting for form to load...")
    
    try:
        # Use a simple wait for now
        time.sleep(2)
        
        # Use Nova-ACT's natural language capability to wait for the form
        nova.act("wait for the form to be fully loaded and interactive")
        
        logger.info("Form loaded successfully")
        return True
        
    except Exception as e:
        logger.exception(f"Error waiting for form load: {e}")
        return False

def fill_text_field(nova, label, value):
    """
    Fill a text field in the form.
    
    Args:
        nova: NovaAct instance
        label: Field label to look for
        value: Value to enter
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Filling text field '{label}' with value '{value}'")
    
    try:
        # Use Nova-ACT's natural language capability to fill the field
        command = f"find the field labeled '{label}' and enter '{value}'"
        nova.act(command)
        
        # Brief pause to ensure the field is properly filled
        time.sleep(0.5)
        
        logger.info(f"Successfully filled '{label}' field")
        return True
        
    except Exception as e:
        logger.exception(f"Error filling '{label}' field: {e}")
        return False

def fill_easy_form_text_fields(nova, form_data):
    """
    Fill all text fields in the easy form.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        bool: True if all fields were filled successfully
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Filling text fields for easy form")
    
    # Make sure the form is loaded
    if not wait_for_form_load(nova):
        logger.error("Form failed to load properly.")
        return False
    
    # Define the text fields to fill
    text_fields = [
        {"label": "First Name", "key": "firstName"},
        {"label": "Last Name", "key": "lastName"},
        {"label": "Date of Birth", "key": "dateOfBirth"},
        {"label": "Email", "key": "email"},
        {"label": "Phone Number", "key": "phoneNumber"}
    ]
    
    # Fill each text field
    success = True
    for field in text_fields:
        label = field["label"]
        key = field["key"]
        
        if key in form_data:
            value = form_data[key]
            field_success = fill_text_field(nova, label, value)
            if not field_success:
                success = False
        else:
            logger.warning(f"Missing '{key}' in form data")
            success = False
    
    if success:
        logger.info("All text fields filled successfully")
    else:
        logger.warning("Some text fields could not be filled")
    
    return success

def handle_checkbox(nova, label, should_check):
    """
    Handle a checkbox in the form - either check it or ensure it's unchecked.
    
    Args:
        nova: NovaAct instance
        label: Checkbox label to look for
        should_check: Whether the checkbox should be checked (True) or unchecked (False)
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    
    if should_check:
        action = "check"
        logger.info(f"Checking checkbox '{label}'")
        command = f"find the checkbox labeled '{label}' and check it"
    else:
        action = "ensure it remains unchecked"
        logger.info(f"Ensuring checkbox '{label}' is unchecked")
        command = f"find the checkbox labeled '{label}' and ensure it remains unchecked"
    
    try:
        # Use Nova-ACT's natural language capability to handle the checkbox
        nova.act(command)
        
        # Brief pause to ensure the checkbox state is properly changed
        time.sleep(0.5)
        
        logger.info(f"Successfully handled checkbox '{label}'")
        return True
        
    except Exception as e:
        logger.exception(f"Error handling checkbox '{label}': {e}")
        return False

def handle_easy_form_checkboxes(nova, form_data):
    """
    Handle all checkboxes in the easy form.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        bool: True if all checkboxes were handled successfully
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Handling checkboxes for easy form")
    
    # Define the checkboxes to handle
    checkboxes = [
        {"label": "Do you currently have insurance?", "key": "hasInsurance"},
        {"label": "Would you like to receive our newsletter?", "key": "wantsNewsletter"},
        {"label": "I agree to the terms and conditions", "key": "agreeToTerms"}
    ]
    
    # Handle each checkbox
    success = True
    for checkbox in checkboxes:
        label = checkbox["label"]
        key = checkbox["key"]
        
        if key in form_data:
            should_check = form_data[key]
            checkbox_success = handle_checkbox(nova, label, should_check)
            if not checkbox_success:
                success = False
        else:
            logger.warning(f"Missing '{key}' in form data")
            success = False
    
    if success:
        logger.info("All checkboxes handled successfully")
    else:
        logger.warning("Some checkboxes could not be handled")
    
    return success

def click_button(nova, label):
    """
    Click a button on the form.
    
    Args:
        nova: NovaAct instance
        label: Button label or text
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Clicking button '{label}'")
    
    try:
        # Use Nova-ACT's natural language capability to click the button
        command = f"find and click the button labeled '{label}'"
        nova.act(command)
        
        # Wait for the action to complete
        time.sleep(1)
        
        logger.info(f"Successfully clicked '{label}' button")
        return True
        
    except Exception as e:
        logger.exception(f"Error clicking '{label}' button: {e}")
        return False

def submit_form(nova):
    """
    Navigate through the form submission process (Review and Submit).
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Navigating form submission process")
    
    try:
        # Click Review button
        logger.info("Clicking Review button")
        if not click_button(nova, "Review"):
            logger.error("Failed to click Review button")
            return False
        
        # Wait for review page to load
        logger.info("Waiting for review page to load")
        time.sleep(2)
        
        # Click Submit button
        logger.info("Clicking Submit button")
        if not click_button(nova, "Submit"):
            logger.error("Failed to click Submit button")
            return False
        
        # Wait for submission to complete
        logger.info("Waiting for submission to complete")
        time.sleep(3)
        
        logger.info("Form submitted successfully")
        return True
        
    except Exception as e:
        logger.exception(f"Error during form submission: {e}")
        return False

def extract_result_code(nova):
    """
    Extract the result code (ASTEROID_0 or ASTEROID_1) from the form.
    Uses direct DOM access via Playwright for reliable extraction.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        str: The result code or None if not found
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Extracting result code using direct DOM access")
    
    try:
        # Run the async extraction function in an event loop
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            # Create a new event loop if the current one is closed
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        result_code = loop.run_until_complete(_extract_result_code_async(nova))
        return result_code
        
    except Exception as e:
        logger.exception(f"Error in extract_result_code: {e}")
        return None

async def _extract_result_code_async(nova):
    """
    Robust extraction of ASTEROID result code using direct DOM access.
    
    Args:
        nova: NovaAct instance with access to Playwright's page object
        
    Returns:
        str: The result code or None if not found
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Extracting result code using direct DOM access")

    try:
        # Explicitly wait for the result code element to appear
        try:
            await nova.page.wait_for_selector("text=Submission Code:", timeout=5000)
        except Exception as e:
            logger.info(f"Selector wait timed out, continuing with content extraction: {e}")
        
        # Extract the text directly from the DOM element containing 'Submission Code'
        content = await nova.page.content()
        
        # Direct regex extraction from page content
        match = re.search(r'Submission Code:\s*(ASTEROID_[01])', content)
        if match:
            result_code = match.group(1)
            logger.info(f"Successfully extracted result code via DOM: {result_code}")
            return result_code

        # Alternative strategy - check for any ASTEROID code on the page
        match_alt = re.search(r'(ASTEROID_[01])', content)
        if match_alt:
            result_code = match_alt.group(1)
            logger.info(f"Found result code via fallback DOM strategy: {result_code}")
            return result_code

        logger.error("No result code found in DOM after submission.")
        return None

    except Exception as e:
        logger.exception(f"DOM-based extraction failed: {e}")
        return None

def automate_easy_form(nova, form_data):
    """
    Complete the entire easy form automation process.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        tuple: (success, result_code)
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Starting easy form automation")
    
    # Fill text fields
    if not fill_easy_form_text_fields(nova, form_data):
        logger.error("Failed to fill text fields")
        return False, None
    
    # Handle checkboxes
    if not handle_easy_form_checkboxes(nova, form_data):
        logger.error("Failed to handle checkboxes")
        return False, None
    
    # Submit the form
    if not submit_form(nova):
        logger.error("Failed to submit form")
        return False, None
    
    # Extract result code with enhanced direct DOM access
    result_code = extract_result_code(nova)
    if not result_code:
        logger.error("Failed to extract result code")
        return False, None
    
    # Check success based on result code
    if result_code == "ASTEROID_1":
        logger.info("Form automation successful! Got ASTEROID_1")
        return True, result_code
    else:
        logger.warning(f"Form automation completed but got result code: {result_code}")
        return False, result_code