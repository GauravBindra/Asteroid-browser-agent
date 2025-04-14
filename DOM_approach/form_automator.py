#!/usr/bin/env python3
"""
Form Automator for Asteroid Form Challenge

This module provides the core form automation functionality, including browser
initialization, form navigation, and field filling for both easy and hard forms.
It includes robust handlers with advanced validation, recovery strategies, and
form-specific optimizations.
"""

import asyncio
import json
import time
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, Locator

import sys
import os
# Add the parent directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import FormLogger
from DOM_approach import config
from DOM_approach import element_utils
from DOM_approach import data_mapper
from DOM_approach import form_schemas


class FormAutomationError(Exception):
    """Exception raised when there's an error in form automation."""
    pass


class FormAutomator:
    """
    Base class for form automation that handles browser initialization,
    form navigation, and field filling for both easy and hard forms.
    """
    
    def __init__(
        self,
        form_type: str,
        headless: bool = config.BROWSER_CONFIG["headless"],
        browser_type: str = config.BROWSER_CONFIG["browser_type"],
        logger: Optional[FormLogger] = None
    ):
        """
        Initialize the form automator.
        
        Args:
            form_type: Type of form to automate ("easy" or "hard")
            headless: Whether to run the browser in headless mode
            browser_type: Type of browser to use ("chromium", "firefox", or "webkit")
            logger: Optional logger instance
        """
        self.form_type = form_type
        self.headless = headless
        self.browser_type = browser_type
        self.form_config = config.get_form_config(form_type)
        self.form_url = self.form_config["url"]
        self.schema = form_schemas.get_form_schema(form_type)
        
        # Set up logger if not provided
        if logger:
            self.logger = logger
        else:
            self.logger = FormLogger(
                log_dir=config.LOGGING_CONFIG["log_dir"],
                form_name=f"{form_type}_dom",
                log_level=config.LOGGING_CONFIG["log_level"],
                enable_console_output=config.LOGGING_CONFIG["enable_console_output"]
            )
        
        # These will be initialized later
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    async def initialize(self) -> None:
        """Initialize Playwright and browser."""
        try:
            self.playwright = await async_playwright().start()
            browser_launcher = getattr(self.playwright, self.browser_type)
            
            self.browser = await browser_launcher.launch(
                headless=self.headless,
                slow_mo=config.BROWSER_CONFIG["slow_mo"]
            )
            
            self.context = await self.browser.new_context(
                viewport={
                    "width": config.BROWSER_CONFIG["viewport_width"],
                    "height": config.BROWSER_CONFIG["viewport_height"]
                },
                user_agent=config.BROWSER_CONFIG["user_agent"],
                locale=config.BROWSER_CONFIG["locale"],
                timezone_id=config.BROWSER_CONFIG["timezone_id"]
            )
            
            if config.LOGGING_CONFIG["save_traces"]:
                await self.context.tracing.start(screenshots=True, snapshots=True)
                
            self.page = await self.context.new_page()
            
            # Set up event handlers
            self.page.on("dialog", self._handle_dialog)
            self.page.on("console", self._handle_console_message)
            
            self.logger.info(f"Initialized {self.browser_type} browser for {self.form_type} form")
            return self
            
        except Exception as e:
            error_msg = f"Failed to initialize browser: {str(e)}"
            self.logger.log_error(error_msg)
            raise FormAutomationError(error_msg)
    
    async def _handle_dialog(self, dialog) -> None:
        """
        Handle dialogs that may appear during form interaction.
        
        Args:
            dialog: Playwright dialog object
        """
        self.logger.info(f"Dialog appeared: {dialog.type} - {dialog.message}")
        await dialog.accept()
    
    async def _handle_console_message(self, message) -> None:
        """
        Handle console messages from the page.
        
        Args:
            message: Playwright console message object
        """
        if message.type == "error":
            self.logger.log_error(f"Console error: {message.text}")
        elif message.type == "warning":
            self.logger.info(f"Console warning: {message.text}")
    
    async def navigate_to_form(self) -> None:
        """Navigate to the form URL."""
        try:
            self.logger.info(f"Navigating to {self.form_url}")
            
            # Navigate to the form with appropriate timeout and wait until
            await self.page.goto(
                self.form_url,
                timeout=config.TIMEOUTS["navigation"],
                wait_until="networkidle"
            )
            
            # Take a screenshot after navigation
            if config.LOGGING_CONFIG["take_screenshots"]:
                await self.logger.save_screenshot(self.page, "form_loaded")
                
            self.logger.info("Form loaded successfully")
            
        except Exception as e:
            error_msg = f"Failed to navigate to form: {str(e)}"
            self.logger.log_error(error_msg)
            
            # Take error screenshot
            if config.LOGGING_CONFIG["take_screenshots"]:
                await self.logger.save_screenshot(self.page, "navigation_error")
                
            raise FormAutomationError(error_msg)
    
    async def fill_field(
        self,
        field_name: str,
        field_info: Dict[str, Any],
        value: Any
    ) -> bool:
        """
        Fill a form field with the provided value.
        
        Args:
            field_name: Name of the field
            field_info: Dictionary containing field information
            value: Value to fill into the field
            
        Returns:
            True if the field was successfully filled, False otherwise
        """
        if field_info.get("type") == "button":
            # Skip button fields
            return True
            
        try:
            # Special handling for conditional fields
            if field_info.get("conditional", False):
                # Skip filling if the field depends on a trigger that's not set
                trigger_name = field_info.get("depends_on", "")
                if not trigger_name:
                    self.logger.log_error(f"Conditional field {field_name} has no trigger defined")
                    return False
                    
                # Assume trigger value based on conditional field's visibility condition
                trigger_value = field_info.get("visible_when", True)
                
                # Get the trigger field info
                trigger_info = None
                if "sections" in self.schema:
                    # Search in all sections for hard form
                    for section in self.schema["sections"].values():
                        if trigger_name in section:
                            trigger_info = section[trigger_name]
                            break
                else:
                    # Direct lookup for easy form
                    trigger_info = self.schema.get(trigger_name)
                
                if not trigger_info:
                    self.logger.log_error(f"Trigger field {trigger_name} not found in schema")
                    return False
                
                # Handle the conditional field with its trigger
                return await element_utils.handle_conditional_field(
                    self.page,
                    trigger_info,
                    field_info,
                    value,
                    trigger_value,
                    self.logger,
                    config.RETRY_CONFIG["max_fill_attempts"]
                )
            
            # Regular field filling
            return await element_utils.fill_field_with_retry(
                self.page,
                field_info,
                value,
                self.logger,
                config.RETRY_CONFIG["max_fill_attempts"],
                config.RETRY_CONFIG["retry_delay"]
            )
            
        except Exception as e:
            self.logger.log_error(f"Error filling field {field_name}: {str(e)}")
            return False
    
    async def verify_field_value(self, field_name: str, field_info: Dict[str, Any], expected_value: Any) -> bool:
        """
        Verify that a field was filled with the expected value.
        
        Args:
            field_name: Name of the field to verify
            field_info: Field information dictionary
            expected_value: Expected value for the field
            
        Returns:
            True if the field value matches the expected value, False otherwise
        """
        try:
            # Find the field element
            locator = await element_utils.find_element_smart(self.page, field_info, self.logger)
            
            field_type = field_info.get("type")
            
            # Verify based on field type
            if field_type == "checkbox":
                actual_value = await locator.is_checked()
                expected_bool = bool(expected_value)
                if actual_value != expected_bool:
                    self.logger.log_discrepancy(field_name, expected_bool, actual_value)
                    return False
            elif field_type in ["text", "email", "tel", "textarea", "date", "number"]:
                actual_value = await locator.input_value()
                expected_str = str(expected_value)
                if actual_value != expected_str:
                    self.logger.log_discrepancy(field_name, expected_str, actual_value)
                    return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error verifying field {field_name}: {str(e)}")
            return False
    
    async def fill_field_with_recovery(
        self, 
        field_name: str, 
        field_info: Dict[str, Any], 
        value: Any,
        attempt: int = 1
    ) -> bool:
        """
        Fill a field with enhanced recovery strategies.
        
        Args:
            field_name: Name of the field to fill
            field_info: Field information dictionary
            value: Value to fill into the field
            attempt: Current attempt number (for retry logic)
            
        Returns:
            True if the field was successfully filled, False otherwise
        """
        self.logger.info(f"Filling field {field_name} (attempt {attempt})")
        
        # Try standard field filling first
        success = await self.fill_field(field_name, field_info, value)
        if success:
            # Verify that the field was properly filled
            if await self.verify_field_value(field_name, field_info, value):
                return True
        
        # If we've already tried multiple times, try alternative strategies
        if attempt >= 2:
            self.logger.info(f"Using recovery strategies for {field_name}")
            
            try:
                # Strategy 1: Try clicking the field first to ensure focus
                locator = await element_utils.find_element_smart(self.page, field_info, self.logger)
                await locator.click()
                await self.page.wait_for_timeout(500)
                
                # Strategy 2: Clear the field explicitly
                if field_info.get("type") in ["text", "email", "tel", "textarea", "date", "number"]:
                    await locator.fill("")
                    await self.page.wait_for_timeout(300)
                    
                    # Strategy 3: Use type() instead of fill() for text fields
                    if field_info.get("type") in ["text", "email", "tel", "textarea"]:
                        await locator.type(str(value), delay=50)
                    else:
                        await locator.fill(str(value))
                
                # Strategy 4: For checkboxes, explicitly set to desired state
                elif field_info.get("type") == "checkbox":
                    current_state = await locator.is_checked()
                    desired_state = bool(value)
                    
                    if current_state != desired_state:
                        await locator.set_checked(desired_state)
                
                # Verify the field value again
                return await self.verify_field_value(field_name, field_info, value)
                
            except Exception as e:
                self.logger.log_error(f"Recovery failed for {field_name}: {str(e)}")
                return False
        
        # If we're on the first attempt, recursively try again
        if attempt < config.RETRY_CONFIG["max_fill_attempts"]:
            await self.page.wait_for_timeout(config.RETRY_CONFIG["retry_delay"])
            return await self.fill_field_with_recovery(field_name, field_info, value, attempt + 1)
            
        return success
    
    async def _get_validation_errors(self) -> List[Dict[str, str]]:
        """
        Get validation errors from the form.
        
        Returns:
            List of validation errors with field name and error message
        """
        return await element_utils.detect_validation_errors(self.page)
    
    async def submit_form(self) -> bool:
        """
        Submit the form.
        
        Returns:
            True if the form was successfully submitted, False otherwise
        """
        try:
            self.logger.info("Submitting form")
            
            # Find the submit button
            button_selector = "button[type='submit']"
            submit_button = None
            
            # Try multiple strategies to find the submit button
            try:
                # Try role-based selector first
                submit_button = await element_utils.find_by_role(
                    self.page, "button", name="Submit"
                )
            except element_utils.ElementNotFoundError:
                try:
                    # Try text-based selector
                    submit_button = await element_utils.find_by_text(
                        self.page, "Submit", exact=True
                    )
                except element_utils.ElementNotFoundError:
                    # Fallback to CSS selector
                    submit_button = await element_utils.find_by_selector(
                        self.page, button_selector
                    )
            
            if not submit_button:
                raise element_utils.ElementNotFoundError("Could not find submit button")
            
            # Take screenshot before submission
            if config.LOGGING_CONFIG["take_screenshots"]:
                await self.logger.save_screenshot(self.page, "before_submission")
            
            # Click the submit button and wait for navigation
            try:
                await submit_button.click()
                await self.page.wait_for_load_state("networkidle", timeout=config.TIMEOUTS["form_submission"])
            except Exception as e:
                self.logger.log_error(f"Error during form submission: {str(e)}")
                
                # Check for validation errors
                validation_errors = await self._get_validation_errors()
                if validation_errors:
                    for error in validation_errors:
                        self.logger.log_error(f"Validation error for {error['field']}: {error['message']}")
                
                return False
            
            # Take screenshot after submission
            if config.LOGGING_CONFIG["take_screenshots"]:
                await self.logger.save_screenshot(self.page, "after_submission")
            
            self.logger.info("Form submitted successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to submit form: {str(e)}"
            self.logger.log_error(error_msg)
            
            # Take error screenshot
            if config.LOGGING_CONFIG["take_screenshots"]:
                await self.logger.save_screenshot(self.page, "submission_error")
            
            return False
    
    async def check_result(self) -> str:
        """
        Check the result of the form submission.
        
        Returns:
            Result code if found, empty string otherwise
        """
        try:
            # Wait for result code to appear
            result_selectors = [
                ".result-code",
                "[data-testid='result-code']",
                "#result-code",
                "div.result",
                "p.code",
                "code",
                ".success-message",
                ".error-message"
            ]
            
            result_text = ""
            
            # Try each selector to find the result
            for selector in result_selectors:
                try:
                    element = await element_utils.find_by_selector(self.page, selector)
                    result_text = await element.inner_text()
                    if "ASTEROID" in result_text:
                        break
                except:
                    continue
            
            # If we didn't find a result with any selector, try getting all text
            if not result_text or "ASTEROID" not in result_text:
                # Look for text containing ASTEROID anywhere on the page
                try:
                    all_text = await self.page.evaluate("() => document.body.innerText")
                    import re
                    match = re.search(r"ASTEROID_[01]", all_text)
                    if match:
                        result_text = match.group(0)
                except:
                    pass
            
            # Check result
            if result_text:
                if "ASTEROID_1" in result_text:
                    self.logger.info("Form submission successful: ASTEROID_1")
                    success = True
                elif "ASTEROID_0" in result_text:
                    self.logger.info("Form submission had data errors: ASTEROID_0")
                    success = False
                else:
                    self.logger.info(f"Unknown result: {result_text}")
                    success = False
                
                self.logger.log_session_summary(success, result_text)
                return result_text
            
            self.logger.log_error("Could not find result code")
            self.logger.log_session_summary(False)
            return ""
            
        except Exception as e:
            error_msg = f"Error checking result: {str(e)}"
            self.logger.log_error(error_msg)
            self.logger.log_session_summary(False)
            return ""
    
    async def close(self) -> None:
        """Close browser and clean up resources."""
        try:
            # Save trace if enabled
            if self.context and config.LOGGING_CONFIG["save_traces"]:
                trace_path = str(self.logger.trace_dir / "trace.zip")
                await self.context.tracing.stop(path=trace_path)
                self.logger.info(f"Trace saved to {trace_path}")
            
            # Close browser
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.logger.info("Browser closed")
            
            # Stop Playwright
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
                
        except Exception as e:
            self.logger.log_error(f"Error closing browser: {str(e)}")


class EasyFormHandler(FormAutomator):
    """
    Handler for the easy form with optimized form filling strategies.
    Includes pre-validation, field optimization, and enhanced recovery mechanisms.
    """
    
    def __init__(self, **kwargs):
        """Initialize the easy form handler."""
        super().__init__(form_type="easy", **kwargs)
        self.field_fill_attempts = {}
        self.validation_errors = {}
    
    async def validate_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate form data before filling the form.
        
        Args:
            data: Data to be used for form filling
            
        Returns:
            Dictionary mapping field names to validation error messages
        """
        validation_errors = {}
        schema = self.schema
        
        # Check required fields
        for field_name, field_info in schema.items():
            if field_info.get("required", False) and field_info.get("type") != "button":
                data_path = field_info.get("data_path")
                if data_path:
                    value = data_mapper.resolve_data_path(data, data_path)
                    if value is None or value == "":
                        validation_errors[field_name] = f"Missing required field: {field_name}"
        
        # Validate specific field formats
        mapped_data = data_mapper.map_data_for_form("easy", data, self.schema)
        
        # Email validation
        if "email" in mapped_data:
            email = mapped_data["email"]
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, str(email)):
                validation_errors["email"] = f"Invalid email format: {email}"
        
        # Phone number validation
        if "phoneNumber" in mapped_data:
            phone = mapped_data["phoneNumber"]
            # Simple check for reasonable phone number length
            if not re.match(r'^\+?[\d\s\(\)\-]{7,20}$', str(phone)):
                validation_errors["phoneNumber"] = f"Invalid phone number format: {phone}"
        
        # Date of birth validation
        if "dateOfBirth" in mapped_data:
            dob = mapped_data["dateOfBirth"]
            # Make sure it's in one of the expected formats
            if not any(re.match(pattern, str(dob)) for pattern in [
                r'^\d{2}-\d{2}-\d{4}$',  # dd-mm-yyyy
                r'^\d{2}/\d{2}/\d{4}$',  # dd/mm/yyyy
                r'^\d{4}-\d{2}-\d{2}$',  # yyyy-mm-dd
                r'^\d{4}/\d{2}/\d{2}$',  # yyyy/mm/dd
            ]):
                validation_errors["dateOfBirth"] = f"Invalid date format: {dob}"
        
        # Store validation errors for reference
        self.validation_errors = validation_errors
        
        if validation_errors:
            self.logger.log_error(f"Data validation found {len(validation_errors)} errors")
            for field, error in validation_errors.items():
                self.logger.log_error(f"Validation error: {field} - {error}")
        
        return validation_errors
    
    async def optimize_field_order(self, data: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any], Any]]:
        """
        Optimize the field filling order based on field dependencies and types.
        
        Args:
            data: Data to fill into the form
            
        Returns:
            List of tuples (field_name, field_info, value) in optimized order
        """
        self.logger.info("Optimizing field filling order")
        mapped_data = data_mapper.map_data_for_form("easy", data, self.schema)
        
        # Create a list of all fields to fill
        fields_to_fill = []
        for field_name, field_info in self.schema.items():
            if field_name in mapped_data and field_info.get("type") != "button":
                fields_to_fill.append((field_name, field_info, mapped_data[field_name]))
        
        # Sort fields based on priority
        # 1. Non-checkbox fields first (text inputs, etc.)
        # 2. Checkbox fields last (since they can trigger conditional fields)
        # 3. Within each group, prioritize required fields
        
        def get_field_priority(field_tuple):
            field_name, field_info, _ = field_tuple
            
            # Factor 1: Field type
            type_priority = 1 if field_info.get("type") == "checkbox" else 0
            
            # Factor 2: Required status
            required_priority = 0 if field_info.get("required", False) else 1
            
            # Factor 3: Field name priority (certain fields filled first)
            name_priority_map = {
                "firstName": 0,
                "lastName": 1,
                "email": 2,
                "phoneNumber": 3,
                "dateOfBirth": 4
            }
            name_priority = name_priority_map.get(field_name, 10)
            
            return (type_priority, required_priority, name_priority)
        
        # Sort fields based on priority
        fields_to_fill.sort(key=get_field_priority)
        
        self.logger.info(f"Optimized field order: {[f[0] for f in fields_to_fill]}")
        return fields_to_fill
    
    async def fill_form(self, data: Dict[str, Any]) -> bool:
        """
        Fill the easy form with the provided data.
        
        Args:
            data: Data to fill into the form
            
        Returns:
            True if the form was successfully filled, False otherwise
        """
        try:
            self.logger.info("Starting to fill easy form")
            
            # Validate data before filling
            validation_errors = await self.validate_data(data)
            if validation_errors:
                self.logger.log_error("Validation errors found, but proceeding with filling")
            
            # Optimize field filling order
            optimized_fields = await self.optimize_field_order(data)
            
            # Fill each field in optimized order
            for field_name, field_info, value in optimized_fields:
                success = await self.fill_field_with_recovery(field_name, field_info, value)
                if not success and field_info.get("required", False):
                    self.logger.log_error(f"Failed to fill required field {field_name}")
                    
                    # Take a screenshot of the failure
                    if config.LOGGING_CONFIG["take_screenshots"]:
                        await self.logger.save_screenshot(self.page, f"field_error_{field_name}")
            
            # Final check for any unfilled required fields
            unfilled_fields = []
            for field_name, field_info in self.schema.items():
                if field_info.get("required", False) and field_info.get("type") != "button":
                    data_value = data_mapper.map_data_for_form("easy", data, self.schema).get(field_name)
                    if not await self.verify_field_value(field_name, field_info, data_value):
                        unfilled_fields.append(field_name)
            
            if unfilled_fields:
                self.logger.log_error(f"Found {len(unfilled_fields)} unfilled required fields: {unfilled_fields}")
                return False
            
            self.logger.info("Easy form filled successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to fill easy form: {str(e)}"
            self.logger.log_error(error_msg)
            return False
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the form filling process with enhanced validation and recovery.
        
        Args:
            data: Data to fill into the form
            
        Returns:
            Dictionary with automation results
        """
        try:
            # Initialize the browser
            await self.initialize()
            
            # Navigate to the form
            await self.navigate_to_form()
            
            # Fill the form
            fill_success = await self.fill_form(data)
            if not fill_success:
                return {
                    "success": False,
                    "message": "Failed to fill form",
                    "result_code": ""
                }
            
            # Submit the form
            submit_success = await self.submit_form()
            if not submit_success:
                return {
                    "success": False,
                    "message": "Failed to submit form",
                    "result_code": ""
                }
            
            # Check the result
            result_code = await self.check_result()
            success = "ASTEROID_1" in result_code
            
            # Record the complete session outcome
            self.logger.log_session_summary(success, result_code)
            
            return {
                "success": success,
                "message": "Form automation completed",
                "result_code": result_code
            }
            
        except Exception as e:
            error_msg = f"Error automating easy form: {str(e)}"
            self.logger.log_error(error_msg)
            
            # Take screenshot of error state
            if config.LOGGING_CONFIG["take_screenshots"] and self.page:
                await self.logger.save_screenshot(self.page, "error_state")
            
            return {
                "success": False,
                "message": error_msg,
                "result_code": ""
            }
            
        finally:
            # Clean up resources
            await self.close()


class HardFormHandler(FormAutomator):
    """
    Handler for the hard form with advanced multi-section navigation and validation.
    Includes section validation, recovery strategies, and conditional field handling.
    """
    
    def __init__(self, **kwargs):
        """Initialize the hard form handler."""
        super().__init__(form_type="hard", **kwargs)
        self.current_section = None
        self.completed_sections = set()
        self.section_validation_results = {}
        self.section_attempts = {}
        self.problematic_fields = set()
    
    async def validate_section_data(self, section_name: str, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate data for a specific section.
        
        Args:
            section_name: Name of the section to validate
            data: Data to validate
            
        Returns:
            Dictionary mapping field names to validation error messages
        """
        if section_name not in self.schema["sections"]:
            return {}
            
        validation_errors = {}
        section_schema = self.schema["sections"][section_name]
        
        # Map data for validation
        mapped_data = data_mapper.map_data_for_form("hard", data, {"sections": {section_name: section_schema}})
        
        # Check required fields
        for field_name, field_info in section_schema.items():
            if field_info.get("required", False) and field_info.get("type") != "button":
                # Skip conditional fields if their dependency isn't set
                if field_info.get("conditional", False):
                    depends_on = field_info.get("depends_on", "")
                    visible_when = field_info.get("visible_when", True)
                    
                    # Find the trigger field in any section
                    trigger_value = None
                    for section in self.schema["sections"].values():
                        if depends_on in section:
                            trigger_data_path = section[depends_on].get("data_path")
                            if trigger_data_path:
                                trigger_value = data_mapper.resolve_data_path(data, trigger_data_path)
                                break
                    
                    # Skip if the condition isn't met
                    if trigger_value != visible_when:
                        continue
                
                # Check if field has a value
                if field_name not in mapped_data or mapped_data[field_name] in [None, ""]:
                    data_path = field_info.get("data_path", "")
                    validation_errors[field_name] = f"Missing required field {field_name} (data path: {data_path})"
        
        # Section-specific validations
        if section_name == "contactDetails":
            # Validate email if present
            if "email" in mapped_data:
                email = mapped_data["email"]
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(email)):
                    validation_errors["email"] = f"Invalid email format: {email}"
        
        if validation_errors:
            self.logger.log_error(f"Validation for section {section_name} found {len(validation_errors)} errors")
            for field, error in validation_errors.items():
                self.logger.log_error(f"Validation error: {field} - {error}")
        
        return validation_errors
    
    async def navigate_to_section(self, section_name: str) -> bool:
        """
        Navigate to a specific section of the form.
        
        Args:
            section_name: Name of the section to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        if section_name == self.current_section:
            return True
            
        try:
            self.logger.info(f"Navigating to section: {section_name}")
            
            # Get section info from schema
            section_info = self.schema["navigation"].get(section_name)
            if not section_info:
                raise FormAutomationError(f"Section {section_name} not found in schema")
            
            section_title = section_info["title"]
            
            # Try clicking the section tab
            try:
                # Try by text first
                section_tab = await element_utils.find_by_text(
                    self.page, section_title, exact=True
                )
                await section_tab.click()
            except element_utils.ElementNotFoundError:
                # Try by role
                try:
                    section_tab = await element_utils.find_by_role(
                        self.page, "tab", name=section_title
                    )
                    await section_tab.click()
                except element_utils.ElementNotFoundError:
                    # Try various selectors
                    selectors = [
                        f"[data-section='{section_name}']",
                        f"[data-tab='{section_name}']",
                        f".{section_name}-tab",
                        f"#{section_name}-tab",
                        f"button:has-text('{section_title}')",
                        f"li:has-text('{section_title}')"
                    ]
                    
                    for selector in selectors:
                        try:
                            section_tab = await element_utils.find_by_selector(
                                self.page, selector
                            )
                            await section_tab.click()
                            break
                        except element_utils.ElementNotFoundError:
                            continue
                    else:
                        # If all selectors failed, try a more general approach
                        self.logger.log_error(f"Could not find tab for section {section_name}")
                        return False
            
            # Wait for section content to load
            await self.page.wait_for_timeout(config.TIMEOUTS["section_transition"])
            
            # Update current section
            self.current_section = section_name
            self.logger.info(f"Navigated to section: {section_name}")
            return True
            
        except Exception as e:
            error_msg = f"Error navigating to section {section_name}: {str(e)}"
            self.logger.log_error(error_msg)
            return False
    
    async def navigate_to_next_section(self) -> bool:
        """
        Navigate to the next section using the Next button.
        
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            self.logger.info("Navigating to next section")
            
            # Find the Next button
            next_button = None
            
            # Try multiple strategies to find the Next button
            try:
                # Try role-based selector first
                next_button = await element_utils.find_by_role(
                    self.page, "button", name="Next"
                )
            except element_utils.ElementNotFoundError:
                try:
                    # Try text-based selector
                    next_button = await element_utils.find_by_text(
                        self.page, "Next", exact=True
                    )
                except element_utils.ElementNotFoundError:
                    # Try various selectors
                    selectors = [
                        "button:has-text('Next')",
                        "button:has-text('Continue')",
                        ".next-button",
                        ".btn-next",
                        "[data-action='next']"
                    ]
                    
                    for selector in selectors:
                        try:
                            next_button = await element_utils.find_by_selector(
                                self.page, selector
                            )
                            break
                        except element_utils.ElementNotFoundError:
                            continue
            
            if not next_button:
                self.logger.log_error("Could not find Next button")
                return False
            
            # Get current section
            if not self.current_section:
                self.logger.log_error("Current section is unknown")
                return False
            
            # Get next section from schema
            section_info = self.schema["navigation"].get(self.current_section)
            if not section_info or not section_info.get("next"):
                self.logger.log_error(f"No next section defined for {self.current_section}")
                return False
            
            next_section = section_info["next"]
            
            # Click the Next button
            await next_button.click()
            
            # Wait for next section to load
            await self.page.wait_for_timeout(config.TIMEOUTS["section_transition"])
            
            # Update current section
            self.current_section = next_section
            self.logger.info(f"Navigated to next section: {next_section}")
            return True
            
        except Exception as e:
            error_msg = f"Error navigating to next section: {str(e)}"
            self.logger.log_error(error_msg)
            return False
    
    async def verify_section_completion(self, section_name: str) -> bool:
        """
        Verify that a section is completely and correctly filled.
        
        Args:
            section_name: Name of the section to verify
            
        Returns:
            True if the section is completely filled, False otherwise
        """
        self.logger.info(f"Verifying completion of section: {section_name}")
        
        # Check for any visible validation errors
        validation_errors = await element_utils.detect_validation_errors(self.page)
        if validation_errors:
            self.logger.log_error(f"Found {len(validation_errors)} validation errors in section {section_name}")
            self.section_validation_results[section_name] = validation_errors
            return False
        
        # Check for required fields that are empty
        section_schema = self.schema["sections"].get(section_name, {})
        required_fields_empty = []
        
        for field_name, field_info in section_schema.items():
            if field_info.get("required", False) and field_info.get("type") != "button":
                # Skip conditional fields that aren't visible
                if field_info.get("conditional", False):
                    try:
                        # Try to find the field to see if it's visible
                        locator = await element_utils.find_element_smart(self.page, field_info, self.logger)
                        if not await locator.is_visible():
                            continue
                    except:
                        # If we can't find the field, assume it's not visible
                        continue
                
                try:
                    # Try to find the field
                    locator = await element_utils.find_element_smart(self.page, field_info, self.logger)
                    
                    # Check if it's empty
                    if field_info.get("type") in ["text", "email", "tel", "number", "date", "textarea"]:
                        value = await locator.input_value()
                        if not value:
                            required_fields_empty.append(field_name)
                    elif field_info.get("type") == "checkbox" and field_info.get("required", False):
                        is_checked = await locator.is_checked()
                        if not is_checked:
                            required_fields_empty.append(field_name)
                    elif field_info.get("type") == "select":
                        value = await locator.evaluate("el => el.value")
                        if not value:
                            required_fields_empty.append(field_name)
                except:
                    # If we can't find the field, assume it's an issue
                    required_fields_empty.append(field_name)
        
        if required_fields_empty:
            self.logger.log_error(f"Found {len(required_fields_empty)} empty required fields in section {section_name}")
            self.section_validation_results[section_name] = {
                "empty_required_fields": required_fields_empty
            }
            return False
        
        # If no errors found, section is complete
        self.logger.info(f"Section {section_name} is complete and valid")
        self.section_validation_results[section_name] = {"status": "valid"}
        return True
    
    async def recover_section(self, section_name: str, data: Dict[str, Any]) -> bool:
        """
        Attempt to recover from errors in a section.
        
        Args:
            section_name: Name of the section to recover
            data: Data to fill into the section
            
        Returns:
            True if recovery was successful, False otherwise
        """
        self.logger.info(f"Attempting to recover section: {section_name}")
        
        # Track attempts for this section
        self.section_attempts[section_name] = self.section_attempts.get(section_name, 0) + 1
        attempt = self.section_attempts[section_name]
        
        # If we've already tried too many times, give up
        if attempt > 3:
            self.logger.log_error(f"Too many recovery attempts for section {section_name}")
            return False
        
        # Get validation results for this section
        validation_results = self.section_validation_results.get(section_name, {})
        problematic_fields = set()
        
        # Handle empty required fields
        if "empty_required_fields" in validation_results:
            problematic_fields.update(validation_results["empty_required_fields"])
        
        # Handle validation errors
        if isinstance(validation_results, list):
            for error in validation_results:
                if "field" in error:
                    problematic_fields.add(error["field"])
        
        # Add any previously problematic fields
        problematic_fields.update(self.problematic_fields)
        
        # If we have problematic fields, focus on those
        if problematic_fields:
            self.logger.info(f"Focusing on problematic fields: {problematic_fields}")
            section_schema = self.schema["sections"].get(section_name, {})
            mapped_data = data_mapper.map_data_for_form("hard", data, self.schema)
            
            # Make sure we're on the right section
            if not await self.navigate_to_section(section_name):
                return False
            
            # Try some recovery strategies
            for field_name in problematic_fields:
                if field_name in section_schema and field_name in mapped_data:
                    field_info = section_schema[field_name]
                    value = mapped_data[field_name]
                    
                    try:
                        # Find the field element
                        locator = await element_utils.find_element_smart(self.page, field_info, self.logger)
                        
                        # Clear any existing value
                        if field_info.get("type") in ["text", "email", "tel", "textarea", "date", "number"]:
                            await locator.fill("")
                            await self.page.wait_for_timeout(300)
                        
                        # Try a different filling strategy - type character by character
                        if field_info.get("type") in ["text", "email", "tel", "textarea"]:
                            await locator.type(str(value), delay=50)
                        elif field_info.get("type") == "checkbox":
                            # Explicitly set checkbox state
                            await locator.set_checked(bool(value))
                        elif field_info.get("type") == "select":
                            # Try selecting by value and label
                            try:
                                await locator.select_option(value=str(value))
                            except:
                                try:
                                    await locator.select_option(label=str(value))
                                except:
                                    # If all else fails, try to select the first option
                                    await locator.select_option(index=0)
                        else:
                            # Use standard fill for other types
                            await locator.fill(str(value))
                            
                    except Exception as e:
                        self.logger.log_error(f"Recovery for field {field_name} failed: {str(e)}")
            
            # Verify section completion after recovery
            return await self.verify_section_completion(section_name)
        
        # If no specific problems found, try refilling the whole section
        return await self.fill_section(section_name, self.schema["sections"].get(section_name, {}),
                                     data_mapper.map_data_for_form("hard", data, self.schema))
    
    async def handle_captive_fields(self) -> bool:
        """
        Handle fields that can 'capture' focus or require special interaction.
        
        Returns:
            True if successfully handled all captive fields, False otherwise
        """
        # Close any open overlays by clicking elsewhere and pressing escape
        try:
            await self.page.mouse.click(10, 10)
            await self.page.keyboard.press("Escape")
            await self.page.wait_for_timeout(500)
            return True
        except Exception as e:
            self.logger.log_error(f"Error handling captive fields: {str(e)}")
            return False
    
    async def fill_section(
        self,
        section_name: str,
        section_schema: Dict[str, Dict[str, Any]],
        mapped_data: Dict[str, Any]
    ) -> bool:
        """
        Fill a specific section of the form.
        
        Args:
            section_name: Name of the section to fill
            section_schema: Schema for the section
            mapped_data: Mapped data to fill into the section
            
        Returns:
            True if the section was successfully filled, False otherwise
        """
        try:
            self.logger.info(f"Filling section: {section_name}")
            
            # Navigate to the section
            if not await self.navigate_to_section(section_name):
                return False
            
            # Fill each field in the section
            for field_name, field_info in section_schema.items():
                if field_name in mapped_data:
                    value = mapped_data[field_name]
                    success = await self.fill_field_with_recovery(field_name, field_info, value)
                    if not success:
                        self.logger.log_error(f"Failed to fill field {field_name} in section {section_name}")
                        # Add to problematic fields for recovery later
                        self.problematic_fields.add(field_name)
            
            # Handle any fields that might be capturing focus
            await self.handle_captive_fields()
            
            # Mark section as completed
            self.completed_sections.add(section_name)
            self.logger.info(f"Section {section_name} filled successfully")
            
            # Take screenshot after filling section
            if config.LOGGING_CONFIG["take_screenshots"]:
                await self.logger.save_screenshot(self.page, f"{section_name}_filled")
            
            return True
            
        except Exception as e:
            error_msg = f"Error filling section {section_name}: {str(e)}"
            self.logger.log_error(error_msg)
            return False
    
    async def fill_form(self, data: Dict[str, Any]) -> bool:
        """
        Fill the hard form with the provided data.
        
        Args:
            data: Data to fill into the form
            
        Returns:
            True if the form was successfully filled, False otherwise
        """
        try:
            self.logger.info("Starting to fill hard form")
            
            # Map data to form fields
            mapped_data = data_mapper.map_data_for_form("hard", data, self.schema)
            
            # Fill each section in order
            for section_name, section_schema in self.schema["sections"].items():
                # Validate section data before filling
                validation_errors = await self.validate_section_data(section_name, data)
                if validation_errors:
                    self.logger.log_error(f"Section {section_name} data validation failed, but proceeding")
                
                # Fill the current section
                success = await self.fill_section(section_name, section_schema, mapped_data)
                
                if not success:
                    self.logger.log_error(f"Failed to fill section {section_name}")
                    
                    # Try to recover
                    recovery_success = await self.recover_section(section_name, data)
                    if not recovery_success:
                        self.logger.log_error(f"Failed to recover section {section_name}")
                        return False
                
                # Verify section completion
                if not await self.verify_section_completion(section_name):
                    # Try recovery
                    recovery_success = await self.recover_section(section_name, data)
                    if not recovery_success:
                        self.logger.log_error(f"Section {section_name} verification failed even after recovery")
                        return False
                
                # Navigate to the next section if not the last one
                next_section = self.schema["navigation"][section_name].get("next")
                if next_section:
                    success = await self.navigate_to_next_section()
                    
                    # If that fails, try direct tab navigation
                    if not success:
                        success = await self.navigate_to_section(next_section)
                    
                    if not success:
                        self.logger.log_error(f"Failed to navigate from {section_name} to {next_section}")
                        return False
            
            self.logger.info("Hard form filled successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to fill hard form: {str(e)}"
            self.logger.log_error(error_msg)
            return False
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete form filling process with enhanced section handling.
        
        Args:
            data: Data to fill into the form
            
        Returns:
            Dictionary with automation results
        """
        try:
            # Initialize the browser
            await self.initialize()
            
            # Navigate to the form
            await self.navigate_to_form()
            
            # Fill the form with all sections
            fill_success = await self.fill_form(data)
            if not fill_success:
                return {
                    "success": False,
                    "message": "Failed to fill form",
                    "result_code": ""
                }
            
            # Submit the form
            submit_success = await self.submit_form()
            if not submit_success:
                return {
                    "success": False,
                    "message": "Failed to submit form",
                    "result_code": ""
                }
            
            # Check the result
            result_code = await self.check_result()
            success = "ASTEROID_1" in result_code
            
            # Record the complete session outcome
            self.logger.log_session_summary(success, result_code)
            
            return {
                "success": success,
                "message": "Form automation completed",
                "result_code": result_code
            }
            
        except Exception as e:
            error_msg = f"Error automating hard form: {str(e)}"
            self.logger.log_error(error_msg)
            
            # Take screenshot of error state
            if config.LOGGING_CONFIG["take_screenshots"] and self.page:
                await self.logger.save_screenshot(self.page, "error_state")
            
            return {
                "success": False,
                "message": error_msg,
                "result_code": ""
            }
            
        finally:
            # Clean up resources
            await self.close()


async def automate_form(
    form_type: str,
    data_file: str,
    headless: bool = config.BROWSER_CONFIG["headless"],
    browser_type: str = config.BROWSER_CONFIG["browser_type"]
) -> Dict[str, Any]:
    """
    Automate filling and submitting a form with advanced handlers.
    
    Args:
        form_type: Type of form ("easy" or "hard")
        data_file: Path to the data file
        headless: Whether to run the browser in headless mode
        browser_type: Type of browser to use
        
    Returns:
        Dictionary with automation results
    """
    # Create appropriate handler based on form type
    handler_class = EasyFormHandler if form_type == "easy" else HardFormHandler
    handler = handler_class(
        headless=headless,
        browser_type=browser_type
    )
    
    try:
        # Load data from file
        data = data_mapper.load_data_from_file(data_file)
        
        # Execute the handler
        return await handler.execute(data)
        
    except Exception as e:
        error_msg = f"Error automating form: {str(e)}"
        handler.logger.log_error(error_msg)
        
        return {
            "success": False,
            "message": error_msg,
            "result_code": ""
        }
        
    finally:
        # Clean up resources
        if handler:
            await handler.close()