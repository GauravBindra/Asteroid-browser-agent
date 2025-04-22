#!/usr/bin/env python3
"""
Element position finder for the Asteroid hard form.

This script uses Nova-ACT combined with Playwright's capabilities to locate
form elements and retrieve their positions on the page. This information
can be useful for debugging element detection issues and improving form
automation reliability.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from nova_act import NovaAct

# Import configuration
from config import HARD_FORM_URL

# Set up logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"element_positions_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("nova_form_automation")
logger.info(f"Logging to {log_file}")

def load_contact_fields():
    """Load contact fields from hard form data JSON."""
    try:
        # Find the hard_form_data.json file in the parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        data_file = os.path.join(parent_dir, "hard_form_data.json")
        
        with open(data_file, "r") as f:
            data = json.load(f)
            
        # Extract contact field names
        if "contact" in data:
            fields = list(data["contact"].keys())
            logger.info(f"Loaded {len(fields)} contact fields: {fields}")
            return fields
        else:
            logger.error("No 'contact' section found in the data")
            return []
            
    except Exception as e:
        logger.error(f"Failed to load contact fields: {e}")
        return []

def get_field_label(field_name):
    """Convert a camelCase field name to a display label."""
    # Common field mappings
    mappings = {
        "firstName": "First Name",
        "lastName": "Last Name",
        "dateOfBirth": "Date of Birth",
        "phoneNumber": "Phone Number",
        "jointInsured": "Joint Insured",
        "jointInsuredPersonName": "Joint Insured Person Name",
        "numberOfYearsAsLandlord": "Number of Years as Landlord",
        "title": "Title"
    }
    
    # Return from mappings if available
    if field_name in mappings:
        return mappings[field_name]
    
    # Otherwise do a generic conversion
    words = []
    current = ""
    for i, char in enumerate(field_name):
        if i > 0 and char.isupper():
            words.append(current)
            current = char
        else:
            current += char
    words.append(current)
    
    return " ".join(word.capitalize() for word in words)

def find_element_positions():
    """Find positions of form elements using Nova-ACT and Playwright."""
    logger.info("Starting element position finder")
    
    # Load contact fields
    contact_fields = load_contact_fields()
    if not contact_fields:
        logger.error("No contact fields to find")
        return False
    
    try:
        # Initialize NovaAct
        logger.info(f"Initializing NovaAct for form at {HARD_FORM_URL}")
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Browser started successfully")
            
            # Wait for form to load
            logger.info("Waiting for form to load")
            time.sleep(3)
            
            # Find positions for each field
            element_positions = {}
            
            # First, let's try with the display labels
            for field_name in contact_fields:
                label = get_field_label(field_name)
                
                logger.info(f"Finding position for field '{label}' (JSON key: {field_name})")
                
                try:
                    # First use Nova-ACT to find and focus on the element
                    nova.act(f"Find the field labeled '{label}'")
                    
                    # Give Nova-ACT a moment to find the element
                    time.sleep(1)
                    
                    # Try several common selector strategies
                    selectors = [
                        f"text='{label}'",
                        f"label:has-text('{label}')",
                        f"input[aria-label='{label}']",
                        f"[placeholder*='{label}']",
                        f"[name*='{field_name}']",
                        f"[id*='{field_name}']"
                    ]
                    
                    element_found = False
                    
                    for selector in selectors:
                        try:
                            # Use Playwright's locator
                            locator = nova.page.locator(selector)
                            
                            # Check if element exists
                            if locator.count() > 0:
                                # Get bounding box
                                box = locator.first.bounding_box()
                                
                                if box:
                                    x, y = box['x'], box['y']
                                    width, height = box['width'], box['height']
                                    
                                    element_positions[field_name] = {
                                        'label': label,
                                        'selector': selector,
                                        'position': {
                                            'x': x,
                                            'y': y,
                                            'width': width,
                                            'height': height
                                        }
                                    }
                                    
                                    logger.info(f"✅ Found '{label}' at position x={x}, y={y}, width={width}, height={height} using selector: {selector}")
                                    element_found = True
                                    break
                        except Exception as e:
                            logger.debug(f"Selector {selector} failed: {e}")
                    
                    if not element_found:
                        logger.warning(f"❌ Could not find element position for '{label}'")
                
                except Exception as e:
                    logger.error(f"Error finding position for '{label}': {e}")
            
            # Log summary
            found_count = len(element_positions)
            logger.info(f"Found positions for {found_count}/{len(contact_fields)} fields")
            
            # Save positions to a JSON file
            output_file = os.path.join(log_dir, f"element_positions_{timestamp}.json")
            with open(output_file, 'w') as f:
                json.dump(element_positions, f, indent=2)
            
            logger.info(f"Saved element positions to {output_file}")
            
            # Return success if we found at least some elements
            return found_count > 0
            
    except Exception as e:
        logger.exception(f"Error during element position finding: {e}")
        return False

if __name__ == "__main__":
    success = find_element_positions()
    sys.exit(0 if success else 1)