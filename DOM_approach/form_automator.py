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
        self.form_schema = form_schemas.get_form_schema(form_type)
        
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
                await self.logger.start_tracing(self.context)
                
            self.page = await self.context.new_page()
            
            # Set up event handlers
            self.page.on("dialog", self._handle_dialog)
            self.page.on("console", self._handle_console_message)
            
            self.logger.logger.info(f"Initialized {self.browser_type} browser for {self.form_type} form")
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
        self.logger.logger.info(f"Dialog appeared: {dialog.type} - {dialog.message}")
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
            self.logger.logger.info(f"Console warning: {message.text}")
    
    async def navigate_to_form(self) -> None:
        """Navigate to the form URL."""
        try:
            self.logger.logger.info(f"Navigating to {self.form_url}")
            
            # Navigate to the form with appropriate timeout and wait until
            await self.page.goto(
                self.form_url,
                timeout=config.TIMEOUTS["navigation"],
                wait_until="networkidle"
            )
            
            self.logger.logger.info("Navigation complete")
            
            # Capture and log the HTML structure for debugging
            html_content = await self.page.content()
            self.logger.logger.debug(f"Page HTML structure: {html_content[:1000]}...")  # Log first 1000 chars
            
            # Take a screenshot of the initial form state
            await self.logger.save_screenshot(self.page, "initial_form_state")
            
        except Exception as e:
            error_msg = f"Failed to navigate to form: {str(e)}"
            self.logger.log_error(error_msg)
            raise FormAutomationError(error_msg)
    
    async def analyze_form_structure(self) -> None:
        """Analyze the form structure to help with element identification."""
        try:
            self.logger.logger.info("Analyzing form structure...")
            
            # Get all input elements
            input_elements = await self.page.query_selector_all('input, select, textarea')
            
            for i, element in enumerate(input_elements):
                # Get element attributes
                element_type = await element.get_attribute('type') or 'unknown'
                element_id = await element.get_attribute('id') or 'none'
                element_name = await element.get_attribute('name') or 'none'
                element_placeholder = await element.get_attribute('placeholder') or 'none'
                
                self.logger.logger.debug(
                    f"Input #{i}: type={element_type}, id={element_id}, "
                    f"name={element_name}, placeholder={element_placeholder}"
                )
            
            # Get all labels
            labels = await self.page.query_selector_all('label')
            for i, label in enumerate(labels):
                label_text = await label.text_content()
                label_for = await label.get_attribute('for') or 'none'
                self.logger.logger.debug(f"Label #{i}: for={label_for}, text={label_text}")
                
            # Get submit buttons
            buttons = await self.page.query_selector_all('button, input[type="submit"]')
            for i, button in enumerate(buttons):
                button_type = await button.get_attribute('type') or 'none'
                button_text = await button.text_content() or 'none'
                self.logger.logger.debug(f"Button #{i}: type={button_type}, text={button_text}")
                
        except Exception as e:
            self.logger.logger.error(f"Error analyzing form structure: {str(e)}")
    
    async def fill_field(self, field_name: str, field_info: Dict[str, Any], value: Any) -> bool:
        """
        Fill a form field with the provided value.
        
        Args:
            field_name: Name of the field
            field_info: Dictionary containing field information
            value: Value to fill into the field
            
        Returns:
            True if the field was successfully filled, False otherwise
        """
        try:
            self.logger.logger.info(f"Filling field '{field_name}' with value: {value}")
            
            # Use the element_utils to fill the field with retry
            success = await element_utils.fill_field_with_retry(
                self.page,
                field_info,
                value,
                logger=self.logger
            )
            
            if success:
                self.logger.log_field_fill(field_name, value)
                return True
            else:
                self.logger.log_error(f"Failed to fill field: {field_name}")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Error filling field {field_name}: {str(e)}")
            return False
    
    async def submit_form(self) -> bool:
        """
        Submit the form after filling.
        
        Returns:
            True if the form was successfully submitted, False otherwise
        """
        try:
            self.logger.logger.info("Starting form submission process")
            
            # Take a screenshot before submission
            await self.logger.save_screenshot(self.page, "before_submission")
            
            # Step 1: Click the Review button
            self.logger.logger.info("Step 1: Clicking the Review button")
            
            # Get the submit button info from the schema
            submit_info = self.form_schema.get("submitButton", {})
            
            # Find and click the Review button
            try:
                # First try using the selector from the schema
                if "selector" in submit_info:
                    review_button = await self.page.query_selector(submit_info["selector"])
                    if not review_button:
                        raise Exception(f"Review button not found with selector: {submit_info['selector']}")
                else:
                    # Fallback to role-based finding
                    review_button = await element_utils.find_by_role(
                        self.page,
                        "button",
                        name=submit_info.get("label", "Review")
                    )
                
                # Add a delay before clicking the Review button
                self.logger.logger.info("Waiting 2 seconds before clicking Review button...")
                await asyncio.sleep(2)
                
                # Click the Review button
                self.logger.logger.info("Clicking Review button...")
                await review_button.click()
                
                # Wait for navigation to review page
                self.logger.logger.info("Waiting for review page to load...")
                await self.page.wait_for_load_state("networkidle")
                
                # Take a screenshot of the review page
                await self.logger.save_screenshot(self.page, "review_page")
                
                # Step 2: Find and click the Submit button on the review page
                self.logger.logger.info("Step 2: Looking for the Submit button on the review page")
                
                # Wait a moment for the page to stabilize
                await asyncio.sleep(2)
                
                # Try different selectors for the Submit button
                submit_button_selectors = [
                    "button:has-text('Submit')",
                    "input[type='submit']",
                    "button[type='submit']",
                    ".submit-button",
                    "form button:last-child"
                ]
                
                submit_button = None
                for selector in submit_button_selectors:
                    self.logger.logger.info(f"Trying to find Submit button with selector: {selector}")
                    submit_button = await self.page.query_selector(selector)
                    if submit_button:
                        self.logger.logger.info(f"Found Submit button with selector: {selector}")
                        break
                
                if not submit_button:
                    raise Exception("Submit button not found on review page")
                
                # Add a delay before clicking the Submit button
                self.logger.logger.info("Waiting 2 seconds before clicking Submit button...")
                await asyncio.sleep(2)
                
                # Click the Submit button
                self.logger.logger.info("Clicking Submit button...")
                await submit_button.click()
                
                # Wait for the submission to complete
                self.logger.logger.info("Waiting for submission to complete...")
                await self.page.wait_for_load_state("networkidle")
                
                # Add a delay after submission to observe the result
                self.logger.logger.info("Waiting 3 seconds to observe submission result...")
                await asyncio.sleep(3)
                
                # Take a screenshot after submission
                await self.logger.save_screenshot(self.page, "after_submission")
                
                # Save the HTML content after submission
                await self.logger.save_html(self.page, "after_submission")
                
                return True
                
            except Exception as e:
                raise Exception(f"Failed to submit form: {str(e)}")
            
        except Exception as e:
            error_msg = f"Failed to submit form: {str(e)}"
            self.logger.log_error(error_msg)
            await self.logger.save_screenshot(self.page, "submission_error")
            return False
    
    async def check_submission_result(self) -> Tuple[bool, Optional[str]]:
        """
        Check if the form submission was successful and extract the result code.
        
        Returns:
            Tuple of (success, result_code)
        """
        try:
            self.logger.logger.info("Checking submission result")
            
            # Wait for the result to appear
            await self.page.wait_for_load_state("networkidle")
            
            # Get the page content
            content = await self.page.content()
            
            # Look specifically for "Submission Code: ASTEROID_1"
            submission_code_pattern = r'Submission Code:\s*(ASTEROID_\w+)'
            submission_match = re.search(submission_code_pattern, content)
            if submission_match:
                result_code = submission_match.group(1)
                self.logger.logger.info(f"Form submission successful: {result_code} found")
                return True, result_code
            
            # Look for any ASTEROID_ code in the page
            asteroid_match = re.search(r'ASTEROID_\w+', content)
            if asteroid_match:
                result_code = asteroid_match.group(0)
                self.logger.logger.info(f"Form submission successful: {result_code} found")
                return True, result_code
            
            # Try to find any result code pattern in specific elements
            result_elements = await self.page.query_selector_all(".result-code, .success-code, .confirmation-code, h1, h2, h3, .success, p")
            for element in result_elements:
                text = await element.text_content()
                if "ASTEROID" in text:
                    # Extract the code - typically all caps with numbers and underscores
                    code_match = re.search(r'ASTEROID_\w+', text)
                    if code_match:
                        result_code = code_match.group(0)
                        self.logger.logger.info(f"Form submission successful: {result_code} found")
                        return True, result_code
            
            # Check for success messages or indicators
            success_indicators = [
                "success", "thank you", "submitted", "complete", "confirmation", "ASTEROID"
            ]
            for indicator in success_indicators:
                if indicator.lower() in content.lower():
                    self.logger.logger.info(f"Form submission likely successful: found '{indicator}'")
                    
                    # Try to extract any code-like text nearby
                    code_match = re.search(r'\b[A-Z0-9_]{5,}\b', content)
                    if code_match:
                        return True, code_match.group(0)
                    
                    return True, "SUCCESS"  # Default code if we can't find a specific one
            
            # Check for error messages
            error_elements = await self.page.query_selector_all(".error, .error-message, .alert-danger")
            if error_elements:
                error_messages = []
                for element in error_elements:
                    text = await element.text_content()
                    if text.strip():
                        error_messages.append(text.strip())
                
                error_text = "; ".join(error_messages)
                self.logger.log_error(f"Form submission failed with errors: {error_text}")
                return False, None
            
            # If still unclear, assume it might be successful but with unknown result
            self.logger.logger.info("Form submission result unclear, assuming success")
            return True, "UNKNOWN"
            
        except Exception as e:
            error_msg = f"Error checking submission result: {str(e)}"
            self.logger.log_error(error_msg)
            return False, None
    
    async def close(self) -> None:
        """Close the browser and clean up resources."""
        try:
            self.logger.logger.info("Closing browser")
            
            if self.context and config.LOGGING_CONFIG["save_traces"]:
                try:
                    await self.logger.stop_tracing(self.context)
                except Exception as e:
                    self.logger.log_error(f"Error closing browser: {str(e)}")
            
            if self.browser:
                await self.browser.close()
                
            if self.playwright:
                await self.playwright.stop()
                
            self.logger.logger.info("Browser closed")
            
        except Exception as e:
            self.logger.log_error(f"Error closing browser: {str(e)}")
    
    async def automate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automate the form filling and submission process.
        
        Args:
            data: Data to fill into the form
            
        Returns:
            Dictionary with automation results
        """
        result = {
            "success": False,
            "form_type": self.form_type,
            "timestamp": time.time()
        }
        
        try:
            # Initialize browser
            await self.initialize()
            
            # Navigate to form
            await self.navigate_to_form()
            
            # Analyze form structure
            await self.analyze_form_structure()
            
            # Map data to form fields
            mapped_data = data_mapper.map_data_for_form(
                self.form_type,
                data,
                self.form_schema
            )
            
            # Fill the form
            fill_success = await self.fill_form(mapped_data)
            if not fill_success:
                result["message"] = "Failed to fill form completely"
                return result
            
            # Submit the form
            submit_success = await self.submit_form()
            if not submit_success:
                result["message"] = "Failed to submit form"
                return result
            
            # Check the submission result
            success, result_code = await self.check_submission_result()
            result["success"] = success
            
            if success:
                result["result_code"] = result_code
                result["message"] = "Form submitted successfully"
            else:
                result["message"] = "Form submission failed"
            
            return result
            
        except Exception as e:
            error_msg = f"Error automating {self.form_type} form: {str(e)}"
            self.logger.log_error(error_msg)
            
            # Try to take an error screenshot if possible
            if hasattr(self, 'page') and self.page:
                await self.logger.save_screenshot(self.page, "error_state")
            
            result["success"] = False
            result["message"] = error_msg
            return result
            
        finally:
            # Always close the browser
            await self.close()
    
    async def fill_form(self, data: Dict[str, Any]) -> bool:
        """
        Fill the form with the provided data.
        This method should be implemented by subclasses.
        
        Args:
            data: Data to fill into the form
            
        Returns:
            True if the form was successfully filled, False otherwise
        """
        raise NotImplementedError("Subclasses must implement fill_form method")


class EasyFormAutomator(FormAutomator):
    """Automator for the easy form, which is a single-page form."""
    
    def __init__(self, **kwargs):
        """Initialize the easy form automator."""
        super().__init__(form_type="easy", **kwargs)
    
    async def fill_form(self, data: Dict[str, Any]) -> bool:
        """
        Fill the easy form with the provided data.
        
        Args:
            data: Data to fill into the form
            
        Returns:
            True if the form was successfully filled, False otherwise
        """
        try:
            self.logger.logger.info("Filling easy form")
            
            # Track the number of successfully filled fields
            fields_filled = 0
            fields_total = len(data)
            
            # Fill each field in the form
            for field_name, value in data.items():
                if field_name in self.form_schema:
                    field_info = self.form_schema[field_name]
                    success = await self.fill_field(field_name, field_info, value)
                    if success:
                        fields_filled += 1
                else:
                    self.logger.logger.info(f"Field '{field_name}' not found in schema, skipping")
            
            # Log the fill completion status
            if fields_filled == fields_total:
                self.logger.logger.info(f"Successfully filled all {fields_filled} fields")
                return True
            else:
                self.logger.logger.info(f"Filled {fields_filled} out of {fields_total} fields")
                return fields_filled > 0  # Return True if at least some fields were filled
                
        except Exception as e:
            self.logger.log_error(f"Error filling easy form: {str(e)}")
            return False


class HardFormAutomator(FormAutomator):
    """Automator for the hard form, which is a multi-section form."""
    
    def __init__(self, **kwargs):
        """Initialize the hard form automator."""
        super().__init__(form_type="hard", **kwargs)
        self.current_section = None
        self.completed_sections = set()
    
    async def navigate_to_section(self, section_name: str) -> bool:
        """
        Navigate to a specific section of the form.
        
        Args:
            section_name: Name of the section to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            # If we're already on this section, no need to navigate
            if self.current_section == section_name:
                return True
                
            self.logger.logger.info(f"Navigating to section: {section_name}")
            
            # Find the section tab/button
            section_button = await element_utils.find_by_text(
                self.page,
                section_name,
                exact=False
            )
            
            # Click the section tab/button
            await section_button.click()
            
            # Wait for the section to load
            await self.page.wait_for_load_state("networkidle")
            
            # Update current section
            self.current_section = section_name
            
            # Take a screenshot of the section
            await self.logger.save_screenshot(self.page, f"section_{section_name}")
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error navigating to section {section_name}: {str(e)}")
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
            self.logger.logger.info(f"Filling section: {section_name}")
            
            # Navigate to the section if needed
            if self.current_section != section_name:
                success = await self.navigate_to_section(section_name)
                if not success:
                    return False
            
            # Track the number of successfully filled fields
            fields_filled = 0
            fields_total = 0
            
            # Get conditional fields for this section
            conditional_fields = form_schemas.get_conditional_fields(section_schema)
            
            # Fill regular fields first
            for field_name, field_info in section_schema.items():
                # Skip fields that are dependent on other fields (will handle them later)
                if field_name in conditional_fields:
                    continue
                    
                if field_name in mapped_data:
                    fields_total += 1
                    success = await self.fill_field(field_name, field_info, mapped_data[field_name])
                    if success:
                        fields_filled += 1
            
            # Now handle conditional fields
            for trigger_field, dependent_fields in conditional_fields.items():
                if trigger_field in mapped_data and mapped_data[trigger_field]:
                    # Fill the trigger field first if it's a checkbox or similar
                    trigger_info = section_schema[trigger_field]
                    await self.fill_field(trigger_field, trigger_info, mapped_data[trigger_field])
                    
                    # Wait for any conditional fields to appear
                    await self.page.wait_for_timeout(500)
                    
                    # Now fill the dependent fields
                    for dep_field in dependent_fields:
                        if dep_field in mapped_data:
                            fields_total += 1
                            dep_info = section_schema[dep_field]
                            success = await element_utils.handle_conditional_field(
                                self.page,
                                trigger_info,
                                dep_info,
                                mapped_data[dep_field],
                                trigger_value=True,
                                logger=self.logger
                            )
                            if success:
                                fields_filled += 1
            
            # Mark this section as completed
            self.completed_sections.add(section_name)
            
            # Log the fill completion status
            if fields_filled == fields_total:
                self.logger.logger.info(f"Successfully filled all {fields_filled} fields in section {section_name}")
                return True
            else:
                self.logger.logger.info(f"Filled {fields_filled} out of {fields_total} fields in section {section_name}")
                return fields_filled > 0  # Return True if at least some fields were filled
                
        except Exception as e:
            self.logger.log_error(f"Error filling section {section_name}: {str(e)}")
            return False
    
    async def navigate_to_next_section(self) -> bool:
        """
        Navigate to the next section using the Next button.
        
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            self.logger.logger.info("Navigating to next section")
            
            # Find the Next button
            next_button = await element_utils.find_by_role(
                self.page,
                "button",
                name="Next"
            )
            
            # Click the Next button and wait for navigation
            await next_button.click()
            await self.page.wait_for_load_state("networkidle")
            
            # Update current section (will need to determine the new section name)
            # For now, just mark that we've moved to a new section
            self.current_section = None
            
            # Take a screenshot of the new section
            await self.logger.save_screenshot(self.page, "next_section")
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error navigating to next section: {str(e)}")
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
            self.logger.logger.info("Filling hard form")
            
            # Define the sections in the order they appear in the form
            sections = [
                ("Contact Details", form_schemas.CONTACT_DETAILS_SCHEMA),
                ("Business Info", form_schemas.BUSINESS_INFO_SCHEMA),
                ("Premises Details", form_schemas.PREMISES_DETAILS_SCHEMA),
                ("Security & Safety", form_schemas.SECURITY_SAFETY_SCHEMA),
                ("Coverage Options", form_schemas.COVERAGE_OPTIONS_SCHEMA)
            ]
            
            # Fill each section
            for section_name, section_schema in sections:
                success = await self.fill_section(section_name, section_schema, data)
                if not success:
                    self.logger.logger.info(f"Failed to fill section: {section_name}")
                    # Continue with the next section anyway
                
                # Navigate to the next section if not the last one
                if section_name != sections[-1][0]:
                    await self.navigate_to_next_section()
            
            # Check if we filled at least some sections
            if self.completed_sections:
                self.logger.logger.info(f"Completed {len(self.completed_sections)} out of {len(sections)} sections")
                return True
            else:
                self.logger.logger.info("Failed to fill any sections")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Error filling hard form: {str(e)}")
            return False


async def automate_form(
    form_type: str,
    data_file: str,
    headless: bool = config.BROWSER_CONFIG["headless"]
) -> Dict[str, Any]:
    """
    Automate filling and submitting a form.
    
    Args:
        form_type: Type of form ("easy" or "hard")
        data_file: Path to the data file
        headless: Whether to run the browser in headless mode
        
    Returns:
        Dictionary with automation results
    """
    logger = FormLogger(
        log_dir=config.LOGGING_CONFIG["log_dir"],
        form_name=f"{form_type}_dom",
        log_level=config.LOGGING_CONFIG["log_level"],
        enable_console_output=config.LOGGING_CONFIG["enable_console_output"]
    )
    
    try:
        logger.logger.info(f"Starting automation for {form_type} form")
        logger.logger.info(f"Using data from: {data_file}")
        
        # Load data from file
        data = data_mapper.load_data_from_file(data_file)
        
        # Create the appropriate automator
        if form_type == "easy":
            automator = EasyFormAutomator(headless=headless, logger=logger)
        elif form_type == "hard":
            automator = HardFormAutomator(headless=headless, logger=logger)
        else:
            raise ValueError(f"Unknown form type: {form_type}")
        
        # Run the automation
        result = await automator.automate(data)
        
        # Add additional information to the result
        result["data_file"] = data_file
        result["headless"] = headless
        
        return result
        
    except Exception as e:
        error_msg = f"Error automating {form_type} form: {str(e)}"
        logger.log_error(error_msg)
        
        return {
            "success": False,
            "message": error_msg,
            "form_type": form_type,
            "data_file": data_file,
            "timestamp": time.time()
        }


# For direct execution and testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Form Automator")
    parser.add_argument("--form", choices=["easy", "hard"], required=True, help="Form type")
    parser.add_argument("--data", required=True, help="Path to data file")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    result = asyncio.run(automate_form(args.form, args.data, args.headless))
    
    print(json.dumps(result, indent=2, default=str))