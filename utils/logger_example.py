#!/usr/bin/env python3
"""
Example usage of the FormLogger for both DOM-based and CUA-based approaches.

This script demonstrates how to use the FormLogger utility in both scenarios.
"""

import asyncio
from typing import Any, Optional
from playwright.async_api import async_playwright
from utils.logger import FormLogger


async def dom_based_example() -> None:
    """Example of using FormLogger with a DOM-based approach using Playwright."""
    print("\n=== Running DOM-based example ===")
    
    # Initialize the logger
    logger = FormLogger(form_name="easy_form_dom")
    
    # Initialize Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Start tracing
        logger.start_tracing(context)
        
        try:
            page = await context.new_page()
            await page.goto("https://asteroid.ai/form2")
            
            # Log field filling
            await page.fill("#firstName", "John")
            logger.log_field_fill("First Name", "John")
            
            await page.fill("#lastName", "Smith")
            logger.log_field_fill("Last Name", "Smith")
            
            # Take screenshot before submission
            await logger.save_screenshot(page, "before_submission")
            
            # Save HTML before submission
            await logger.save_html(page, "before_submission")
            
            # Log a simulated form submission
            logger.log_form_submission(status_code=200)
            
            # Log session summary
            logger.log_session_summary(True, "ASTEROID_1")
            
        except Exception as e:
            logger.log_error(f"Error during form automation: {str(e)}")
            await logger.save_screenshot(page, "error_state")
            logger.log_session_summary(False)
        finally:
            # Stop tracing
            logger.stop_tracing(context)
            await browser.close()


async def cua_based_example() -> None:
    """
    Example of using FormLogger with a CUA-based approach.
    
    Note: This is a simulation since we don't have actual CUA implementation yet.
    """
    print("\n=== Running CUA-based example (simulated) ===")
    
    # Initialize the logger
    logger = FormLogger(form_name="easy_form_cua")
    
    # Simulate a CUA browser object
    class MockCUABrowser:
        async def take_screenshot(self, output_path: str) -> str:
            print(f"CUA: Taking screenshot and saving to {output_path}")
            # In a real implementation, this would actually save a screenshot
            with open(str(output_path), "w") as f:
                f.write("<mock screenshot data>")
            return output_path
            
        async def get_page_source(self) -> str:
            return "<html><body><h1>Mock CUA Page</h1></body></html>"
    
    # Create mock CUA browser
    mock_browser = MockCUABrowser()
    
    try:
        # Log field filling
        logger.log_field_fill("First Name", "Jane")
        logger.log_field_fill("Last Name", "Doe")
        
        # Take screenshot
        await logger.save_screenshot(mock_browser, "cua_screenshot")
        
        # Save HTML
        await logger.save_html(mock_browser, "cua_page_source")
        
        # Log form submission
        logger.log_form_submission()
        
        # Log session summary
        logger.log_session_summary(True, "ASTEROID_1")
        
    except Exception as e:
        logger.log_error(f"Error during CUA form automation: {str(e)}")
        logger.log_session_summary(False)


async def main() -> None:
    """Run both examples."""
    await dom_based_example()
    await cua_based_example()


if __name__ == "__main__":
    asyncio.run(main())
