#!/usr/bin/env python3
"""
Main Entry Point for Asteroid Form Challenge

This module serves as the command-line interface and entry point for the
DOM-based form automation solution. It handles argument parsing, logging setup,
and orchestration of the form handling process.
"""

import os
import sys
import asyncio
import argparse
import logging
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add the parent directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import FormLogger
from DOM_approach import config
from DOM_approach.form_automator import automate_form


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Asteroid Form Challenge - DOM-based Form Automation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--form",
        choices=["easy", "hard"],
        required=True,
        help="Type of form to automate (easy or hard)"
    )
    
    parser.add_argument(
        "--data",
        required=True,
        help="Path to the data file for form filling"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        default=config.BROWSER_CONFIG["headless"],
        help="Run in headless mode (no visible browser)"
    )
    
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        default=config.BROWSER_CONFIG["browser_type"],
        help="Browser type to use for automation"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--screenshots",
        action="store_true",
        default=config.LOGGING_CONFIG["take_screenshots"],
        help="Enable screenshots during automation"
    )
    
    parser.add_argument(
        "--output",
        help="Path to write JSON output results"
    )
    
    return parser.parse_args()


def process_data_file_path(data_file: str) -> str:
    """
    Process the data file path to ensure it's valid and accessible.
    
    Args:
        data_file: Path to the data file (may be relative or absolute)
        
    Returns:
        Absolute path to the data file
        
    Raises:
        FileNotFoundError: If the data file does not exist
    """
    # If the path is absolute, use it directly
    if os.path.isabs(data_file):
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file not found: {data_file}")
        return data_file
    
    # Try different locations for relative paths
    
    # 1. Current directory
    if os.path.exists(data_file):
        return os.path.abspath(data_file)
    
    # 2. Relative to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_relative_path = os.path.join(script_dir, data_file)
    if os.path.exists(script_relative_path):
        return script_relative_path
    
    # 3. Relative to project root
    project_root = os.path.dirname(script_dir)
    project_relative_path = os.path.join(project_root, data_file)
    if os.path.exists(project_relative_path):
        return project_relative_path
    
    # If we've tried all locations and still can't find it, raise an error
    raise FileNotFoundError(f"Data file not found: {data_file}")


async def run_automation(args: argparse.Namespace, logger: FormLogger) -> Dict[str, Any]:
    """
    Run the form automation process.
    
    Args:
        args: Command line arguments
        logger: Logger instance for logging automation events
        
    Returns:
        Dictionary with automation results
    """
    try:
        # Update config based on arguments
        config.BROWSER_CONFIG["headless"] = args.headless
        config.BROWSER_CONFIG["browser_type"] = args.browser
        config.LOGGING_CONFIG["take_screenshots"] = args.screenshots
        
        if args.debug:
            config.LOGGING_CONFIG["log_level"] = logging.DEBUG
            config.LOGGING_CONFIG["enable_console_output"] = True
        
        # Process data file path
        try:
            data_file = process_data_file_path(args.data)
            logger.info(f"Using data from: {data_file}")
        except FileNotFoundError as e:
            logger.log_error(str(e))
            return {
                "success": False,
                "message": str(e),
                "result_code": ""
            }
        
        # Execute form automation
        result = await automate_form(
            form_type=args.form,
            data_file=data_file,
            headless=args.headless,
            browser_type=args.browser
        )
        
        # Log the result
        if result["success"]:
            logger.info(f"Form automation successful: {result['result_code']}")
        else:
            logger.log_error(f"Form automation failed: {result['message']}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error running automation: {str(e)}"
        logger.log_error(error_msg)
        
        return {
            "success": False,
            "message": error_msg,
            "result_code": ""
        }


def display_result(result: Dict[str, Any]) -> None:
    """
    Display the automation result to the console.
    
    Args:
        result: Automation result dictionary
    """
    print("\n" + "="*60)
    
    if result["success"]:
        print("✅ FORM AUTOMATION SUCCESSFUL")
        print(f"Result Code: {result['result_code']}")
    else:
        print("❌ FORM AUTOMATION FAILED")
        print(f"Error: {result['message']}")
        
        if "validation_errors" in result:
            print("\nValidation Errors:")
            for field, error in result["validation_errors"].items():
                print(f"  - {field}: {error}")
        
        if "result_code" in result and result["result_code"]:
            print(f"\nResult Code: {result['result_code']}")
    
    print("="*60)


def save_result_to_file(result: Dict[str, Any], output_path: str) -> None:
    """
    Save the automation result to a JSON file.
    
    Args:
        result: Automation result dictionary
        output_path: Path to save the result to
    """
    try:
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(os.path.abspath(output_path))
        os.makedirs(output_dir, exist_ok=True)
        
        # Add timestamp to result
        result_with_timestamp = result.copy()
        result_with_timestamp["timestamp"] = datetime.datetime.now().isoformat()
        
        # Write result to file
        with open(output_path, 'w') as f:
            json.dump(result_with_timestamp, f, indent=2, default=str)
            
        print(f"\nResult saved to: {output_path}")
        
    except Exception as e:
        print(f"\nError saving result to file: {str(e)}")


async def main() -> None:
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logger for main script
    logger = FormLogger(
        log_dir=config.LOGGING_CONFIG["log_dir"],
        form_name=f"{args.form}_dom_main",
        log_level=logging.DEBUG if args.debug else config.LOGGING_CONFIG["log_level"],
        enable_console_output=config.LOGGING_CONFIG["enable_console_output"]
    )
    
    logger.info(f"Starting form automation for {args.form} form")
    logger.info(f"Browser: {args.browser} (headless: {args.headless})")
    
    # Display startup information
    print(f"Starting form automation for {args.form} form...")
    print(f"Browser: {args.browser} (headless: {args.headless})")
    
    # Run the automation
    result = await run_automation(args, logger)
    
    # Display the result
    display_result(result)
    
    # Save result to file if requested
    if args.output:
        save_result_to_file(result, args.output)
    
    # Exit with appropriate status code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    asyncio.run(main())