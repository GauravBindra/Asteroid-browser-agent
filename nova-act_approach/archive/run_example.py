#!/usr/bin/env python3
"""
Simple Nova-ACT example to demonstrate basic functionality.
Adapted from the order_a_coffee_maker.py example.
"""

import os
import sys
import time
import datetime
import logging
from pathlib import Path
from nova_act import NovaAct
from dotenv import load_dotenv

load_dotenv()

def setup_logging():
    """Set up logging configuration"""
    # Create logs directory if it doesn't exist
    log_dir = Path("/Users/gauravbindra/Desktop/Asteroid/nova-act_logs")
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Create screenshots directory
    screenshots_dir = log_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    # Get current timestamp for log files
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Configure logging
    log_file = log_dir / f"run_example_{timestamp}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return {
        "timestamp": timestamp,
        "log_dir": log_dir,
        "screenshots_dir": screenshots_dir,
        "log_file": log_file
    }

def main():
    """Run a simple Nova-ACT automation example"""
    
    # Set up logging
    log_info = setup_logging()
    logger = logging.getLogger("nova-act-example")
    logger.info("Starting Nova-ACT example...")
    
    # Get current script name without extension for logging
    script_name = Path(__file__).stem
    
    # Set headless mode based on environment variable or default to False
    headless = os.environ.get("HEADLESS", "false").lower() == "true"
    logger.info(f"Headless mode: {headless}")
    
    # Set your Nova-ACT API key as an environment variable
    api_key = os.getenv("NOVA_ACT_API_KEY")
    if not api_key:
        logger.error("Missing NOVA_ACT_API_KEY environment variable.")
        raise ValueError("Missing NOVA_ACT_API_KEY environment variable.")

    os.environ["NOVA_ACT_API_KEY"] = api_key
    
    try:
        with NovaAct(
            starting_page="https://www.amazon.com",
            headless=headless,
        ) as nova:
            logger.info("Initialized Nova-ACT browser")
            
            # Perform search action
            logger.info("Searching for coffee maker...")
            nova.act("search for a coffee maker")
            
            # Take a screenshot after search
            search_screenshot = log_info["screenshots_dir"] / f"{script_name}_search_{log_info['timestamp']}.png"
            nova.page.screenshot(path=str(search_screenshot))
            logger.info(f"Saved search screenshot to {search_screenshot}")
            
            # Select first result
            logger.info("Selecting first result...")
            nova.act("select the first result")
            
            # Take a screenshot after selection
            selection_screenshot = log_info["screenshots_dir"] / f"{script_name}_selection_{log_info['timestamp']}.png"
            nova.page.screenshot(path=str(selection_screenshot))
            logger.info(f"Saved selection screenshot to {selection_screenshot}")
            
            # Add to cart
            logger.info("Adding to cart...")
            nova.act("scroll down or up until you see 'add to cart' and then click 'add to cart'")
            
            # Take a screenshot after adding to cart
            cart_screenshot = log_info["screenshots_dir"] / f"{script_name}_cart_{log_info['timestamp']}.png"
            nova.page.screenshot(path=str(cart_screenshot))
            logger.info(f"Saved cart screenshot to {cart_screenshot}")
            
            logger.info("Example completed successfully!")
            
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())