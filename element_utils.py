#!/usr/bin/env python3
"""
Element Utilities for Asteroid Form Challenge

This module provides robust element finding and interaction utilities for form automation.
It includes functions for locating elements using various strategies, interacting with
different element types, and handling conditional fields.
"""

import time
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from playwright.sync_api import Page, Locator, ElementHandle
import config


class ElementNotFoundError(Exception):
    """Exception raised when an element cannot be found."""
    pass


class ElementInteractionError(Exception):
    """Exception raised when interaction with an element fails."""
    pass


def find_by_label(page: Page, label_text: str, exact: bool = False) -> Locator:
    """
    Find an element by its associated label text.
    This is the most reliable method for locating form elements.
    
    Args:
        page: Playwright page object
        label_text: Text of the label associated with the element
        exact: Whether to match the label text exactly
        
    Returns:
        Locator for the element
        
    Raises:
        ElementNotFoundError: If the element cannot be found
    """
    try:
        # Most reliable: getByLabel which matches <label for="..."> or wrapping <label>
        locator = page.get_by_label(label_text, exact=exact)
        if locator.count() > 0:
            return locator
        
        # Try more permissive search if exact matching fails
        if exact:
            locator = page.get_by_label(label_text, exact=False)
            if locator.count() > 0:
                return locator
                
        # If still not found, raise exception
        raise ElementNotFoundError(f"Element with label '{label_text}' not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with label '{label_text}': {str(e)}")


def find_by_role(page: Page, role: str, name: Optional[str] = None) -> Locator:
    """
    Find an element by its ARIA role and optional accessible name.
    
    Args:
        page: Playwright page object
        role: ARIA role of the element (button, checkbox, etc.)
        name: Accessible name of the element (optional)
        
    Returns:
        Locator for the element
        
    Raises:
        ElementNotFoundError: If the element cannot be found
    """
    try:
        if name:
            locator = page.get_by_role(role, name=name)
        else:
            locator = page.get_by_role(role)
            
        if locator.count() > 0:
            return locator
            
        raise ElementNotFoundError(f"Element with role '{role}'{' and name ' + name if name else ''} not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with role '{role}': {str(e)}")


def find_by_placeholder(page: Page, placeholder_text: str, exact: bool = False) -> Locator:
    """
    Find an element by its placeholder text.
    
    Args:
        page: Playwright page object
        placeholder_text: Placeholder text of the element
        exact: Whether to match the placeholder text exactly
        
    Returns:
        Locator for the element
        
    Raises:
        ElementNotFoundError: If the element cannot be found
    """
    try:
        locator = page.get_by_placeholder(placeholder_text, exact=exact)
        if locator.count() > 0:
            return locator
            
        raise ElementNotFoundError(f"Element with placeholder '{placeholder_text}' not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with placeholder '{placeholder_text}': {str(e)}")


def find_by_text(page: Page, text: str, exact: bool = False) -> Locator:
    """
    Find an element by its text content.
    Useful for buttons and links without specific roles.
    
    Args:
        page: Playwright page object
        text: Text content of the element
        exact: Whether to match the text exactly
        
    Returns:
        Locator for the element
        
    Raises:
        ElementNotFoundError: If the element cannot be found
    """
    try:
        locator = page.get_by_text(text, exact=exact)
        if locator.count() > 0:
            return locator
            
        raise ElementNotFoundError(f"Element with text '{text}' not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with text '{text}': {str(e)}")


def find_by_test_id(page: Page, test_id: str) -> Locator:
    """
    Find an element by its data-testid attribute.
    
    Args:
        page: Playwright page object
        test_id: Test ID of the element
        
    Returns:
        Locator for the element
        
    Raises:
        ElementNotFoundError: If the element cannot be found
    """
    try:
        locator = page.get_by_test_id(test_id)
        if locator.count() > 0:
            return locator
            
        raise ElementNotFoundError(f"Element with test ID '{test_id}' not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with test ID '{test_id}': {str(e)}")


def find_by_selector(page: Page, selector: str) -> Locator:
    """
    Find an element by CSS selector.
    This is a fallback method when other methods fail.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        
    Returns:
        Locator for the element
        
    Raises:
        ElementNotFoundError: If the element cannot be found
    """
    try:
        locator = page.locator(selector)
        if locator.count() > 0:
            return locator
            
        raise ElementNotFoundError(f"Element with selector '{selector}' not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with selector '{selector}': {str(e)}")


def find_element_smart(
    page: Page, 
    field_info: Dict[str, Any],
    logger: Optional[Any] = None
) -> Locator:
    """
    Smart element finder that tries multiple strategies to find an element.
    
    Args:
        page: Playwright page object
        field_info: Dictionary containing field information (label, placeholder, etc.)
        logger: Optional logger to record the search process
        
    Returns:
        Locator for the element
        
    Raises:
        ElementNotFoundError: If the element cannot be found using any strategy
    """
    errors = []
    
    # Try label-based search first (most reliable)
    if 'label' in field_info and field_info['label']:
        try:
            locator = find_by_label(page, field_info['label'])
            if logger:
                logger.info(f"Found element by label: {field_info['label']}")
            return locator
        except ElementNotFoundError as e:
            errors.append(str(e))
    
    # Try role-based search
    if 'role' in field_info and field_info['role']:
        try:
            name = field_info.get('name') if 'name' in field_info else None
            locator = find_by_role(page, field_info['role'], name)
            if logger:
                logger.info(f"Found element by role: {field_info['role']}")
            return locator
        except ElementNotFoundError as e:
            errors.append(str(e))
    
    # Try placeholder-based search
    if 'placeholder' in field_info and field_info['placeholder'] and field_info['placeholder'] != 'none':
        try:
            locator = find_by_placeholder(page, field_info['placeholder'])
            if logger:
                logger.info(f"Found element by placeholder: {field_info['placeholder']}")
            return locator
        except ElementNotFoundError as e:
            errors.append(str(e))
    
    # Try selector-based search as fallback
    if 'selector' in field_info and field_info['selector']:
        try:
            locator = find_by_selector(page, field_info['selector'])
            if logger:
                logger.info(f"Found element by selector: {field_info['selector']}")
            return locator
        except ElementNotFoundError as e:
            errors.append(str(e))
    
    # If ID is available, try direct ID selector
    if 'id' in field_info and field_info['id'] and field_info['id'] != 'none':
        try:
            locator = find_by_selector(page, f"#{field_info['id']}")
            if logger:
                logger.info(f"Found element by ID: {field_info['id']}")
            return locator
        except ElementNotFoundError as e:
            errors.append(str(e))
    
    # If name attribute is available, try name selector
    if 'name' in field_info and field_info['name'] and field_info['name'] != 'none':
        try:
            locator = find_by_selector(page, f"[name='{field_info['name']}']")
            if logger:
                logger.info(f"Found element by name attribute: {field_info['name']}")
            return locator
        except ElementNotFoundError as e:
            errors.append(str(e))
    
    # If all strategies fail, raise exception with all errors
    raise ElementNotFoundError(f"Could not find element using any strategy. Errors: {'; '.join(errors)}")


async def fill_field_with_retry(
    page: Page,
    field_info: Dict[str, Any],
    value: Any,
    logger: Optional[Any] = None,
    max_retries: int = config.RETRY_CONFIG['max_fill_attempts'],
    retry_delay: int = config.RETRY_CONFIG['retry_delay']
) -> bool:
    """
    Fill a form field with automatic retries on failure.
    
    Args:
        page: Playwright page object
        field_info: Dictionary containing field information
        value: Value to fill into the field
        logger: Optional logger to record the fill process
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in milliseconds
        
    Returns:
        True if the field was successfully filled, False otherwise
    """
    field_name = field_info.get('label', field_info.get('name', 'unknown field'))
    
    for attempt in range(max_retries):
        try:
            # Find the element
            locator = find_element_smart(page, field_info, logger)
            
            # Wait for the element to be visible and enabled
            await locator.wait_for(
                state="visible", 
                timeout=config.TIMEOUTS['element_visibility']
            )
            
            # Fill the field based on its type
            field_type = field_info.get('type', 'text')
            input_type = field_info.get('inputType', field_type)
            
            if input_type == 'checkbox' or input_type == 'radio':
                # Convert value to boolean for checkboxes
                bool_value = bool(value)
                await locator.set_checked(bool_value)
                if logger:
                    action = "Checked" if bool_value else "Unchecked"
                    logger.log_field_fill(field_name, bool_value)
            elif input_type == 'select' or field_type == 'select':
                # Select an option from a dropdown
                await locator.select_option(value)
                if logger:
                    logger.log_field_fill(field_name, value)
            else:
                # For regular text input fields
                # First clear the field to ensure clean state
                await locator.fill("")
                # Then fill with the value
                await locator.fill(str(value))
                if logger:
                    logger.log_field_fill(field_name, value)
            
            # Verify the value if appropriate and possible
            if config.RETRY_CONFIG['verify_inputs'] and input_type not in ['file', 'image']:
                if input_type == 'checkbox' or input_type == 'radio':
                    is_checked = await locator.is_checked()
                    if is_checked != bool_value:
                        raise ElementInteractionError(
                            f"Checkbox verification failed. Expected: {bool_value}, Got: {is_checked}"
                        )
                elif input_type != 'select' and field_type != 'select':
                    input_value = await locator.input_value()
                    if input_value != str(value):
                        raise ElementInteractionError(
                            f"Input verification failed. Expected: {value}, Got: {input_value}"
                        )
            
            return True
            
        except Exception as e:
            if logger:
                logger.log_error(f"Attempt {attempt+1} failed for {field_name}: {str(e)}")
            
            # Last attempt failed
            if attempt == max_retries - 1:
                if logger:
                    logger.log_error(f"Failed to fill {field_name} after {max_retries} attempts")
                return False
            
            # Wait before retrying
            if retry_delay > 0:
                time.sleep(retry_delay / 1000)  # Convert ms to seconds
    
    return False


async def handle_conditional_field(
    page: Page,
    trigger_field: Dict[str, Any],
    dependent_field: Dict[str, Any],
    value: Any,
    trigger_value: bool = True,
    logger: Optional[Any] = None,
    max_retries: int = config.RETRY_CONFIG['max_fill_attempts']
) -> bool:
    """
    Handle a conditional field that appears based on a trigger field's state.
    
    Args:
        page: Playwright page object
        trigger_field: Dictionary containing trigger field information
        dependent_field: Dictionary containing dependent field information
        value: Value to fill into the dependent field
        trigger_value: Value to set the trigger field to (usually True to reveal the dependent field)
        logger: Optional logger to record the process
        max_retries: Maximum number of retry attempts
        
    Returns:
        True if the conditional field was successfully handled, False otherwise
    """
    trigger_name = trigger_field.get('label', trigger_field.get('name', 'unknown trigger'))
    dependent_name = dependent_field.get('label', dependent_field.get('name', 'unknown dependent field'))
    
    try:
        # First set the trigger field to the desired state
        trigger_locator = find_element_smart(page, trigger_field, logger)
        
        if logger:
            logger.info(f"Setting trigger field '{trigger_name}' to {trigger_value}")
        
        # For checkbox triggers, we use set_checked to ensure correct state
        await trigger_locator.set_checked(trigger_value)
        if logger:
            logger.log_field_fill(trigger_name, trigger_value)
        
        # Wait for a moment to allow the dependent field to appear
        page.wait_for_timeout(config.TIMEOUTS['conditional_field'])
        
        # Now try to fill the dependent field
        success = await fill_field_with_retry(
            page, dependent_field, value, logger, max_retries
        )
        
        if not success and logger:
            logger.log_error(f"Failed to fill conditional field '{dependent_name}'")
        
        return success
    
    except Exception as e:
        if logger:
            logger.log_error(f"Error handling conditional field '{dependent_name}': {str(e)}")
        return False


async def wait_for_navigation(
    page: Page,
    timeout: int = config.TIMEOUTS['navigation'],
    logger: Optional[Any] = None
) -> bool:
    """
    Wait for navigation to complete.
    
    Args:
        page: Playwright page object
        timeout: Timeout in milliseconds
        logger: Optional logger to record the process
        
    Returns:
        True if navigation completed successfully, False otherwise
    """
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout)
        return True
    except Exception as e:
        if logger:
            logger.log_error(f"Navigation wait failed: {str(e)}")
        return False


async def extract_form_elements(page: Page) -> List[Dict[str, Any]]:
    """
    Extract all form elements from the current page.
    This is adapted from the explore_forms.py script.
    
    Args:
        page: Playwright page object
        
    Returns:
        List of dictionaries containing form element information
    """
    # This uses the same extraction logic from explore_forms.py
    return await page.evaluate("""() => {
        // Find all input elements, selects, textareas, and submit buttons
        const elements = Array.from(document.querySelectorAll(
            'input, select, textarea, button[type="submit"], .form-control, .input-field, [role="combobox"], .checkbox, .radio, .toggle'
        ));
        
        return elements.map(el => {
            // Try to find associated label
            let labelText = 'none';
            
            // Check for label with 'for' attribute
            if (el.id) {
                const label = document.querySelector(`label[for="${el.id}"]`);
                if (label) {
                    labelText = label.textContent.trim();
                }
            }
            
            // Check for parent label
            if (labelText === 'none') {
                const parentLabel = el.closest('label');
                if (parentLabel) {
                    // Get text content excluding the text of the input itself
                    const clone = parentLabel.cloneNode(true);
                    const inputs = clone.querySelectorAll('input, select, textarea');
                    inputs.forEach(input => input.remove());
                    labelText = clone.textContent.trim();
                }
            }
            
            // Check for nearby label or text
            if (labelText === 'none') {
                // Look for preceding element that might be a label
                const prevSibling = el.previousElementSibling;
                if (prevSibling && prevSibling.tagName !== 'INPUT' && prevSibling.tagName !== 'SELECT' && prevSibling.tagName !== 'TEXTAREA') {
                    labelText = prevSibling.textContent.trim();
                }
                
                // For form groups, look for label within the same parent
                const formGroup = el.closest('.form-group, .input-group, .field-container');
                if (formGroup) {
                    const groupLabel = formGroup.querySelector('label, .label, .form-label');
                    if (groupLabel) {
                        labelText = groupLabel.textContent.trim();
                    }
                }
            }
            
            // For checkboxes and radios, look for text nodes next to them
            if ((el.type === 'checkbox' || el.type === 'radio') && labelText === 'none') {
                const parent = el.parentElement;
                if (parent) {
                    const textContent = parent.textContent.trim();
                    if (textContent) {
                        labelText = textContent;
                    }
                }
            }
            
            // Get options for select elements
            let options = [];
            if (el.tagName.toLowerCase() === 'select') {
                options = Array.from(el.options).map(opt => ({
                    value: opt.value,
                    text: opt.textContent.trim()
                }));
            }
            
            return {
                type: el.tagName.toLowerCase(),
                inputType: el.type || 'none',
                id: el.id || 'none',
                name: el.name || 'none',
                placeholder: el.placeholder || 'none',
                label: labelText,
                value: el.value || 'none',
                checked: el.checked || false,
                required: el.required || false,
                options: options,
                isVisible: el.offsetParent !== null,
                isDisabled: el.disabled || el.readOnly
            };
        });
    }""")


async def detect_form_sections(page: Page) -> List[Dict[str, Any]]:
    """
    Detect form sections in a multi-section form.
    
    Args:
        page: Playwright page object
        
    Returns:
        List of dictionaries containing section information
    """
    sections = []
    
    # Try to find tabs or section navigation elements
    # Similar to explore_forms.py approach
    tab_selectors = [
        'button[role="tab"]', 
        '.nav-item', 
        '.tab', 
        '.section-tab',
        'ul.nav li',
        '.form-section',
        '.step-indicator'
    ]
    
    for selector in tab_selectors:
        try:
            tabs = page.query_selector_all(selector)
            if tabs and len(tabs) > 0:
                for i, tab in enumerate(tabs):
                    text = await tab.inner_text()
                    section_name = text.strip() or f"Section {i+1}"
                    sections.append({
                        "name": section_name,
                        "index": i,
                        "element": tab
                    })
                return sections
        except:
            continue
    
    # Check for Next buttons if no tabs found
    try:
        next_buttons = page.query_selector_all('button:has-text("Next"), button:has-text("Continue"), .next-button, .btn-next')
        if next_buttons and len(next_buttons) > 0:
            # This is likely a sequential form with Next buttons
            sections.append({
                "name": "Section 1",
                "index": 0,
                "is_sequential": True
            })
    except:
        pass
    
    # If no sections detected, assume it's a single-page form
    if not sections:
        sections.append({
            "name": "Single Page Form",
            "index": 0,
            "is_single_page": True
        })
    
    return sections


async def detect_validation_errors(page: Page) -> List[Dict[str, str]]:
    """
    Detect validation errors on the form.
    
    Args:
        page: Playwright page object
        
    Returns:
        List of dictionaries containing error information
    """
    # Common selectors for error messages
    error_selectors = [
        '.error', '.invalid-feedback', '[aria-invalid="true"]',
        '.form-error', '.validation-error', '.error-message',
        '.alert-danger', '.field-error'
    ]
    
    errors = []
    
    for selector in error_selectors:
        try:
            error_elements = page.query_selector_all(selector)
            for error_elem in error_elements:
                if await error_elem.is_visible():
                    error_text = await error_elem.inner_text()
                    
                    # Try to find the associated field
                    field_name = "Unknown field"
                    
                    # Check if error is within a form group
                    form_group = error_elem.query_selector('xpath=./ancestor::div[contains(@class, "form-group")]')
                    if form_group:
                        label = form_group.query_selector('label')
                        if label:
                            field_name = await label.inner_text()
                    
                    errors.append({
                        "field": field_name,
                        "message": error_text.strip()
                    })
        except:
            continue
    
    return errors