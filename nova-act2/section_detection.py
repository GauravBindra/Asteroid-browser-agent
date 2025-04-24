#!/usr/bin/env python3
"""
Section detection module for form automation.

This module provides functions to detect sections and subsections in web forms
using Nova-ACT.
"""

import logging
from nova_act import BOOL_SCHEMA

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def section_exists(nova, section_name):
    """
    Check if a section exists in the form using Nova-ACT.
    
    Args:
        nova: NovaAct instance
        section_name: Name of the section to check
        
    Returns:
        bool: True if section exists, False otherwise
    """
    logger.info(f"Checking if section '{section_name}' exists")
    # nova.act(f"Scroll up till you see 'Commercia/l Property Insurance Application'.",max_steps=3)
    query = (
            f"If you are not at the top then Scroll up till you see 'Commercial Property Insurance Application'. "
        )
    # Add try-except block around the scroll command
    try:
        nova.act(query, max_steps=5)
    except Exception as e:
        logger.warning(f"Initial scroll command failed, retrying: {e}")
        try:
            nova.act(query, max_steps=5)
        except Exception as e2:
            logger.error(f"Retry of scroll command also failed: {e2}")
            # Continue anyway - we'll try to find the section even if scrolling fails
            
    # First, let's try to find it by exact name
    query = f"Is there a section labeled '{section_name}' in this form? Answer true or false."
    
    # Add try-except block around the section check
    try:
        result = nova.act(query, schema=BOOL_SCHEMA)
    except Exception as e:
        logger.warning(f"Section check failed, retrying: {e}")
        try:
            result = nova.act(query, schema=BOOL_SCHEMA)
        except Exception as e2:
            logger.error(f"Retry of section check also failed: {e2}")
            # If we can't check if the section exists, assume it doesn't
            return False
    
    if result.parsed_response:
        logger.info(f"Section '{section_name}' found with exact name match")
        return True
    
    # If not found, let's try to see if it's visible after scrolling
    # logger.info(f"Section '{section_name}' not immediately visible, trying to scroll")
    # nova.act(f"Scroll to find '{section_name}'")
    
    # # Check again after scrolling
    # result = nova.act(query, schema=BOOL_SCHEMA)
    
    # if result.parsed_response:
    #     logger.info(f"Section '{section_name}' found after scrolling")
    #     return True
    else:
        logger.info(f"Section '{section_name}' not found")
        return False

def sub_section_exists(nova, section_name):
    """
    Check if a sub-section exists in the form using Nova-ACT.
    
    Args:
        nova: NovaAct instance
        section_name: Name of the sub-section to check
        
    Returns:
        bool: True if sub-section exists, False otherwise
    """
    logger.info(f"Checking if sub-section '{section_name}' exists")
    
    # First, let's try to find it by exact name
    query = f"Is there a sub-section labeled '{section_name}' in this form? Answer true or false."
    result = nova.act(query, schema=BOOL_SCHEMA)
    
    if result.parsed_response:
        logger.info(f"Sub-section '{section_name}' found with exact name match")
        return True
    
    # If not found, let's try to see if it's visible after scrolling
    logger.info(f"Sub-section '{section_name}' not immediately visible, trying to scroll")
    nova.act(f"Find '{section_name}'",
             f"Scroll down if you cant find '{section_name}'",
             f"Stop scrolling if you have reached the bottom of the page")
    
    # Check again after scrolling
    result = nova.act(query, schema=BOOL_SCHEMA)
    
    if result.parsed_response:
        logger.info(f"Sub-section '{section_name}' found after scrolling")
        nova.act(f"Scroll to the top",
                 f"Stop scrolling if you have reached the top of the page", max_steps=5)
        return True
    else:
        logger.info(f"Sub-section '{section_name}' not found")
        nova.act(f"Scroll to the top",
                 f"Stop scrolling if you have reached the top of the page", max_steps=5)
        return False
