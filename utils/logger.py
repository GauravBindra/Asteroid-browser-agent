#!/usr/bin/env python3
"""
Logger Module for Asteroid Form Challenge

This module provides logging functionality that can be used by both DOM-based and CUA-based
form automation approaches. It implements the minimal logging strategy defined in the project
requirements while remaining agnostic to the specific implementation details.
"""

import os
import json
import logging
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union, List, Tuple


class FormLogger:
    """
    A modular logger for form automation that works with both DOM-based and CUA-based approaches.
    
    This logger captures field filling actions, form submissions, errors, and artifacts
    according to the minimal logging strategy for the Asteroid Form Challenge.
    """
    
    def __init__(self, 
                 log_dir: str = "logs", 
                 form_name: str = "unknown_form",
                 log_level: int = logging.INFO,
                 enable_console_output: bool = True):
        """
        Initialize the form logger.
        
        Args:
            log_dir: Directory where logs and artifacts will be stored
            form_name: Name of the form being automated (e.g., "easy_form" or "hard_form")
            log_level: Logging level (default: logging.INFO)
            enable_console_output: Whether to output logs to console (default: True)
        """
        # Create timestamp for this session
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"{form_name}_{self.timestamp}"
        
        # Create log directory structure
        self.log_dir = Path(log_dir) / self.session_id
        self.screenshots_dir = self.log_dir / "screenshots"
        self.html_dir = self.log_dir / "html"
        self.trace_dir = self.log_dir / "trace"
        
        # Create directories if they don't exist
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.html_dir, exist_ok=True)
        os.makedirs(self.trace_dir, exist_ok=True)
        
        # Set up logger
        self.logger = logging.getLogger(f"form_logger_{self.session_id}")
        self.logger.setLevel(log_level)
        
        # Clear any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create file handler - Convert Path to string for broader compatibility
        file_handler = logging.FileHandler(str(self.log_dir / "form_automation.log"))
        file_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        self.logger.addHandler(file_handler)
        
        # Add console handler if enabled
        if enable_console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Dictionary to track field values for validation
        self.field_values: Dict[str, Any] = {}
        
        # Initialize session start
        self.logger.info(f"Started form automation session for {form_name}")
    
    def log_field_fill(self, field_name: str, value: Any) -> None:
        """
        Log a field filling action.
        
        Args:
            field_name: Name of the field being filled
            value: Value being entered into the field
        """
        # Store the field value for potential validation later
        self.field_values[field_name] = value
        
        # Log the action
        if isinstance(value, bool):
            action = "Checked" if value else "Unchecked"
            self.logger.info(f"{action} {field_name}")
        else:
            # For privacy/security, don't log the actual value for sensitive fields
            if any(sensitive in field_name.lower() for sensitive in ["password", "secret", "token", "key"]):
                self.logger.info(f"Filled {field_name} with [REDACTED]")
            else:
                self.logger.info(f"Filled {field_name} with '{value}'")
    
    def log_form_submission(self, status_code: Optional[int] = None, response_text: Optional[str] = None) -> None:
        """
        Log a form submission event.
        
        Args:
            status_code: HTTP status code of the response (if available)
            response_text: Response text or message (if available)
        """
        message = "Submitted form"
        if status_code:
            message += f", received status code: {status_code}"
        
        self.logger.info(message)
        
        # If there's a response text, save it to a file
        if response_text:
            response_file = self.log_dir / "form_response.txt"
            with open(str(response_file), "w") as f:
                f.write(response_text)
            self.logger.info(f"Response saved to {response_file}")
    
    def log_error(self, error_message: str, error_type: Optional[str] = None) -> None:
        """
        Log an error or discrepancy.
        
        Args:
            error_message: Description of the error
            error_type: Type of error (e.g., "validation", "network", "element_not_found")
        """
        if error_type:
            self.logger.error(f"{error_type.upper()}: {error_message}")
        else:
            self.logger.error(error_message)
    
    def log_discrepancy(self, field_name: str, expected_value: Any, actual_value: Any) -> None:
        """
        Log a discrepancy between expected and actual values.
        
        Args:
            field_name: Name of the field with the discrepancy
            expected_value: Value that was expected
            actual_value: Actual value found
        """
        self.logger.warning(
            f"Discrepancy in {field_name}: Expected '{expected_value}', got '{actual_value}'"
        )
    
    async def save_screenshot(self, page: Any, name: str = "screenshot") -> str:
        """
        Capture and save a screenshot.
        
        Args:
            page: Playwright page or CUA browser object
            name: Name for the screenshot file (without extension)
            
        Returns:
            Path to the saved screenshot as a string
        """
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        # Handle both Playwright and CUA approaches
        try:
            # For Playwright
            if hasattr(page, "screenshot"):
                await page.screenshot(path=str(filepath), full_page=True)
            # For CUA
            elif hasattr(page, "take_screenshot"):
                await page.take_screenshot(output_path=str(filepath))
            else:
                self.logger.warning(f"Could not take screenshot: Unsupported page object")
                return ""
                
            self.logger.info(f"Screenshot saved to {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"Failed to save screenshot: {str(e)}")
            return ""
    
    async def save_html(self, page: Any, name: str = "page_content") -> str:
        """
        Save the HTML content of the page.
        
        Args:
            page: Playwright page or CUA browser object
            name: Name for the HTML file (without extension)
            
        Returns:
            Path to the saved HTML file as a string
        """
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        filename = f"{name}_{timestamp}.html"
        filepath = self.html_dir / filename
        
        try:
            # For Playwright
            if hasattr(page, "content"):
                html_content = await page.content()
                with open(str(filepath), "w", encoding="utf-8") as f:
                    f.write(html_content)
            # For CUA
            elif hasattr(page, "get_page_source"):
                html_content = await page.get_page_source()
                with open(str(filepath), "w", encoding="utf-8") as f:
                    f.write(html_content)
            else:
                self.logger.warning(f"Could not save HTML: Unsupported page object")
                return ""
                
            self.logger.info(f"HTML content saved to {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"Failed to save HTML content: {str(e)}")
            return ""
    
    def start_tracing(self, context: Any) -> None:
        """
        Start Playwright tracing.
        
        Args:
            context: Playwright browser context
        """
        try:
            # Note: trace_path is defined here for clarity but used in stop_tracing
            if hasattr(context, "tracing"):
                context.tracing.start(
                    screenshots=True,
                    snapshots=True,
                    sources=True
                )
                self.logger.info("Started Playwright tracing")
            else:
                self.logger.warning("Tracing not supported for this browser context")
        except Exception as e:
            self.logger.error(f"Failed to start tracing: {str(e)}")
    
    def stop_tracing(self, context: Any) -> None:
        """
        Stop Playwright tracing and save the trace file.
        
        Args:
            context: Playwright browser context
        """
        try:
            trace_path = self.trace_dir / "trace.zip"
            if hasattr(context, "tracing"):
                context.tracing.stop(path=str(trace_path))
                self.logger.info(f"Saved Playwright trace to {trace_path}")
            else:
                self.logger.warning("Tracing not supported for this browser context")
        except Exception as e:
            self.logger.error(f"Failed to stop tracing: {str(e)}")
    
    def log_session_summary(self, success: bool, result_code: Optional[str] = None) -> None:
        """
        Log a summary of the form automation session.
        
        Args:
            success: Whether the form submission was successful
            result_code: Result code from the form submission (e.g., "ASTEROID_1")
        """
        if success:
            status = "SUCCESS"
            if result_code:
                status += f" with code: {result_code}"
        else:
            status = "FAILURE"
            
        self.logger.info(f"Form automation session completed: {status}")
        
        # Save field values for reference
        values_file = self.log_dir / "field_values.json"
        with open(str(values_file), "w") as f:
            json.dump(self.field_values, f, indent=2, default=str)
        
        self.logger.info(f"Field values saved to {values_file}")


# Example usage:
"""
async def run_form_automation():
    # Initialize the logger
    logger = FormLogger(form_name="easy_form")
    
    # Initialize Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        
        # Start tracing
        logger.start_tracing(context)
        
        page = await context.new_page()
        await page.goto("https://asteroid.ai/form2")
        
        # Log field filling
        await page.fill("#firstName", "John")
        logger.log_field_fill("First Name", "John")
        
        # Take screenshot before submission
        await logger.save_screenshot(page, "before_submission")
        
        # Submit form
        await page.click("button[type='submit']")
        logger.log_form_submission()
        
        # Save HTML after submission
        await logger.save_html(page, "after_submission")
        
        # Check for success
        if "ASTEROID_1" in await page.content():
            logger.log_session_summary(True, "ASTEROID_1")
        else:
            logger.log_error("Form submission did not return expected code")
            logger.log_session_summary(False)
        
        # Stop tracing
        logger.stop_tracing(context)
        
        await browser.close()
"""
