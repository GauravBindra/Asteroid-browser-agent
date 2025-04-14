#!/usr/bin/env python3
"""
Form Automator for Asteroid Form Challenge

This module provides the core form automation functionality, including browser
initialization, form navigation, and field filling for both easy and hard forms.
"""

import asyncio
import json
import time
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


class EasyFormAutomator(FormAutomator):
    """
    Automator for the easy form, which is a single-page form.
    """
    
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
            self.logger.info("Starting to fill easy form")
            
            # Map data to form fields
            mapped_data = data_mapper.map_data_for_form("easy", data, self.schema)
            
            # Fill each field
            for field_name, field_info in self.schema.items():
                if field_name in mapped_data:
                    value = mapped_data[field_name]
                    success = await self.fill_field(field_name, field_info, value)
                    if not success:
                        self.logger.log_error(f"Failed to fill field {field_name}")
            
            self.logger.info("Easy form filled successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to fill easy form: {str(e)}"
            self.logger.log_error(error_msg)
            return False


class HardFormAutomator(FormAutomator):
    """
    Automator for the hard form, which is a multi-section form.
    """
    
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
                    success = await self.fill_field(field_name, field_info, value)
                    if not success:
                        self.logger.log_error(f"Failed to fill field {field_name} in section {section_name}")
            
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
                # Fill the current section
                success = await self.fill_section(section_name, section_schema, mapped_data)
                if not success:
                    self.logger.log_error(f"Failed to fill section {section_name}")
                    return False
                
                # Navigate to the next section if not the last one
                next_section = self.schema["navigation"][section_name].get("next")
                if next_section:
                    success = await self.navigate_to_next_section()
                    if not success:
                        self.logger.log_error(f"Failed to navigate from {section_name} to {next_section}")
                        return False
            
            self.logger.info("Hard form filled successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to fill hard form: {str(e)}"
            self.logger.log_error(error_msg)
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
    # Create appropriate automator based on form type
    automator_class = EasyFormAutomator if form_type == "easy" else HardFormAutomator
    automator = automator_class(headless=headless)
    
    try:
        # Initialize the automator
        await automator.initialize()
        
        # Load data from file
        data = data_mapper.load_data_from_file(data_file)
        
        # Navigate to the form
        await automator.navigate_to_form()
        
        # Fill the form
        fill_success = await automator.fill_form(data)
        if not fill_success:
            return {
                "success": False,
                "message": "Failed to fill form",
                "result_code": ""
            }
        
        # Submit the form
        submit_success = await automator.submit_form()
        if not submit_success:
            return {
                "success": False,
                "message": "Failed to submit form",
                "result_code": ""
            }
        
        # Check the result
        result_code = await automator.check_result()
        
        return {
            "success": "ASTEROID_1" in result_code,
            "message": "Form automation completed",
            "result_code": result_code
        }
        
    except Exception as e:
        error_msg = f"Error automating form: {str(e)}"
        automator.logger.log_error(error_msg)
        
        return {
            "success": False,
            "message": error_msg,
            "result_code": ""
        }
        
    finally:
        # Clean up resources
        await automator.close()


# For direct execution and testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Automate form filling")
    parser.add_argument("--form", choices=["easy", "hard"], required=True, help="Type of form to fill")
    parser.add_argument("--data", required=True, help="Path to data file")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    # Run the automation
    result = asyncio.run(automate_form(args.form, args.data, args.headless))
    
    # Print result
    print(json.dumps(result, indent=2))