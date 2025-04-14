#!/usr/bin/env python3
"""
Element Utilities for Asteroid Form Challenge

This module provides robust element finding and interaction utilities for form automation.
It includes functions for locating elements using various strategies, interacting with
different element types, and handling conditional fields.

The module uses Playwright's asynchronous API consistently throughout to maintain
compatibility with modern Playwright practices and avoid mixing sync/async approaches.
"""

import time
import logging
import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union
from playwright.async_api import Page, Locator, ElementHandle
import config


class ElementNotFoundError(Exception):
    """Exception raised when an element cannot be found."""
    pass


class ElementInteractionError(Exception):
    """Exception raised when interaction with an element fails."""
    pass


async def find_by_label(page: Page, label_text: str, exact: bool = False) -> Locator:
    """
    Find an element by its associated label text.
    This is the most reliable method for locating form elements as it matches
    how users identify fields and is less brittle than selectors.
    
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
        count = await locator.count()
        if count > 0:
            return locator
        
        # Try more permissive search if exact matching fails
        if exact:
            locator = page.get_by_label(label_text, exact=False)
            count = await locator.count()
            if count > 0:
                return locator
                
        # If still not found, raise exception
        raise ElementNotFoundError(f"Element with label '{label_text}' not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with label '{label_text}': {str(e)}")


async def find_by_role(page: Page, role: str, name: Optional[str] = None) -> Locator:
    """
    Find an element by its ARIA role and optional accessible name.
    This is particularly effective for semantic elements like buttons,
    checkboxes, and other elements with well-defined roles.
    
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
            
        count = await locator.count()
        if count > 0:
            return locator
            
        raise ElementNotFoundError(f"Element with role '{role}'{' and name ' + name if name else ''} not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with role '{role}': {str(e)}")


async def find_by_placeholder(page: Page, placeholder_text: str, exact: bool = False) -> Locator:
    """
    Find an element by its placeholder text.
    Useful for forms where inputs have distinctive placeholder text
    that can serve as a reliable identifier.
    
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
        count = await locator.count()
        if count > 0:
            return locator
            
        raise ElementNotFoundError(f"Element with placeholder '{placeholder_text}' not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with placeholder '{placeholder_text}': {str(e)}")


async def find_by_text(page: Page, text: str, exact: bool = False) -> Locator:
    """
    Find an element by its text content.
    Useful for buttons and links without specific roles, especially
    when the visible text is the most reliable way to identify an element.
    
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
        count = await locator.count()
        if count > 0:
            return locator
            
        raise ElementNotFoundError(f"Element with text '{text}' not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with text '{text}': {str(e)}")


async def find_by_test_id(page: Page, test_id: str) -> Locator:
    """
    Find an element by its data-testid attribute.
    This is useful when working with forms designed with automated testing
    in mind, where data-testid attributes have been explicitly added.
    
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
        count = await locator.count()
        if count > 0:
            return locator
            
        raise ElementNotFoundError(f"Element with test ID '{test_id}' not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with test ID '{test_id}': {str(e)}")


async def find_by_selector(page: Page, selector: str) -> Locator:
    """
    Find an element by CSS selector.
    This is a fallback method when other methods fail and should be used
    with caution as CSS selectors can be brittle during site changes.
    
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
        count = await locator.count()
        if count > 0:
            return locator
            
        raise ElementNotFoundError(f"Element with selector '{selector}' not found")
    except Exception as e:
        raise ElementNotFoundError(f"Error finding element with selector '{selector}': {str(e)}")


async def find_element_smart(
    page: Page, 
    field_info: Dict[str, Any],
    logger: Optional[Any] = None
) -> Locator:
    """
    Smart element finder that tries multiple strategies to find an element.
    
    This function attempts multiple location strategies in a specific order of reliability:
    1. Label-based - Most reliable as it matches what users see and how fields are typically identified
    2. Role-based - Good for semantic elements like buttons with clear roles
    3. Placeholder-based - Useful for inputs with distinctive placeholder text
    4. CSS Selector - Used when more specific targeting is needed
    5. ID-based - Direct but may be auto-generated or change between sessions
    6. Name-based - Similar to ID but uses the name attribute
    
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
    
    # 1. Try label-based search first (most reliable)
    # This matches how users identify fields and is typically stable across changes
    if 'label' in field_info and field_info['label']:
        try:
            locator = await find_by_label(page, field_info['label'])
            if logger:
                logger.logger.info(f"Found element by label: {field_info['label']}")
            return locator
        except ElementNotFoundError as e:
            errors.append(str(e))
    
    # 2. Try role-based search (good for semantic elements)
    # Particularly effective for buttons, checkboxes, etc. with ARIA roles
    if 'role' in field_info and field_info['role']:
        try:
            name = field_info.get('name') if 'name' in field_info else None
            locator = await find_by_role(page, field_info['role'], name)
            if logger:
                logger.logger.info(f"Found element by role: {field_info['role']}")
            return locator
        except ElementNotFoundError as e:
            errors.append(str(e))
    
    # 3. Try placeholder-based search (useful for many inputs)
    # Particularly helpful for forms where placeholders are distinct
    if 'placeholder' in field_info and field_info['placeholder'] and field_info['placeholder'] != 'none':
        try:
            locator = await find_by_placeholder(page, field_info['placeholder'])
            if logger:
                logger.logger.info(f"Found element by placeholder: {field_info['placeholder']}")
            return locator
        except ElementNotFoundError as e:
            errors.append(str(e))
    
    # 4. Try selector-based search (custom selectors for specific targeting)
    # Used when we have a specific selector known to work
    if 'selector' in field_info and field_info['selector']:
        try:
            locator = await find_by_selector(page, field_info['selector'])
            if logger:
                logger.logger.info(f"Found element by selector: {field_info['selector']}")
            return locator
        except ElementNotFoundError as e:
            errors.append(str(e))
    
    # 5. If ID is available, try direct ID selector
    # Less preferred because IDs might be auto-generated or change
    if 'id' in field_info and field_info['id'] and field_info['id'] != 'none':
        try:
            locator = await find_by_selector(page, f"#{field_info['id']}")
            if logger:
                logger.logger.info(f"Found element by ID: {field_info['id']}")
            return locator
        except ElementNotFoundError as e:
            errors.append(str(e))
    
    # 6. If name attribute is available, try name selector
    # Similar to ID but using the name attribute
    if 'name' in field_info and field_info['name'] and field_info['name'] != 'none':
        try:
            locator = await find_by_selector(page, f"[name='{field_info['name']}']")
            if logger:
                logger.logger.info(f"Found element by name attribute: {field_info['name']}")
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
            locator = await find_element_smart(page, field_info, logger)
            
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
                
                if bool_value:
                    if logger:
                        logger.logger.info(f"Checked {field_name}")
                else:
                    if logger:
                        logger.logger.info(f"Unchecked {field_name}")
                        
            elif input_type == 'select':
                # Select options from dropdown
                await locator.select_option(value=str(value))
                if logger:
                    logger.logger.info(f"Selected option '{value}' for {field_name}")
                    
            else:
                # For text inputs, clear first then fill
                await locator.fill('')
                await locator.fill(str(value))
                if logger:
                    logger.logger.info(f"Filled {field_name} with '{value}'")
            
            # Add a delay after filling to make the process more observable
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            if logger:
                logger.logger.error(f"Attempt {attempt + 1} failed for {field_name}: {str(e)}")
                
            if attempt < max_retries - 1:
                # Wait before retrying
                await asyncio.sleep(retry_delay / 1000)  # Convert ms to seconds
                
    if logger:
        logger.logger.error(f"Failed to fill {field_name} after {max_retries} attempts")
        
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
        trigger_locator = await find_element_smart(page, trigger_field, logger)
        
        if logger:
            logger.logger.info(f"Setting trigger field '{trigger_name}' to {trigger_value}")
        
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



# This file:

#   1. Builds on explore_forms.py techniques: Adapts and enhances the element finding logic from the exploration script
#   2. Implements modern Playwright selectors: Uses get_by_label(), get_by_role(), and other modern locators
#   3. Provides smart element finding: Tries multiple strategies to reliably locate elements
#   4. Handles different input types: Supports text inputs, checkboxes, dropdowns, etc.
#   5. Implements retry mechanisms: For robust interaction with elements
#   6. Handles conditional fields: Special support for fields that appear conditionally
#   7. Includes form structure detection: Functions to detect sections and validation errors
#   8. Integrates with logger.py: Compatible with your existing logging system
#   9. Uses config.py settings: For timeouts, retry counts, etc.

#   The file provides a strong foundation for the form-filling agent, with functions that can handle both the easy and hard forms. The emphasis
#   is on reliability and robustness, with multiple fallback strategies to ensure elements are found and interactions succeed.
