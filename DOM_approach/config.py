#!/usr/bin/env python3
"""
Configuration settings for Asteroid Form Challenge

This module contains constants and configuration settings for the form automation.
These include URLs, timeouts, retry parameters, and file paths.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any

# Form URLs
FORM_URLS = {
    "easy": "https://asteroid.ai/form2",
    "hard": "https://asteroid.ai/form"
}

# Demo data file paths - can be overridden via command line arguments
DEMO_DATA_FILES = {
    "easy": "easy_form_demo_data.txt",
    "hard": "hard_form_demo_data.txt"
}

# Browser configuration
BROWSER_CONFIG = {
    "browser_type": "chromium",      # Options: chromium, firefox, webkit
    "headless": False,               # Set to True for production/CI environments
    "slow_mo": 50,                   # Slow down operations by 50ms for stability/visibility
    "viewport_width": 1280,
    "viewport_height": 1024,
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "locale": "en-US",
    "timezone_id": "America/New_York"
}

# Timeouts (in milliseconds)
TIMEOUTS = {
    "navigation": 30000,             # Page navigation timeout
    "element_visibility": 5000,      # Wait for element to be visible
    "element_enabled": 2000,         # Wait for element to be enabled
    "conditional_field": 2000,       # Wait for conditional field to appear
    "form_submission": 10000,        # Wait for form submission response
    "section_transition": 5000       # Wait for section transition (hard form)
}

# Retry configuration
RETRY_CONFIG = {
    "max_fill_attempts": 3,          # Maximum attempts to fill a field
    "max_navigation_attempts": 2,    # Maximum attempts to navigate between sections
    "retry_delay": 500,              # Delay between retries (ms)
    "verify_inputs": True            # Verify input values after filling
}

# Logging configuration (works with utils/logger.py)
LOGGING_CONFIG = {
    "log_dir": "logs",
    "log_level": logging.INFO,
    "enable_console_output": True,
    "take_screenshots": True,
    "save_html": True,
    "save_traces": True
}

# Output file paths
PATHS = {
    "screenshots_dir": "screenshots",
    "traces_dir": "traces",
    "reports_dir": "reports"
}

# Field type mapping - maps field types to appropriate interaction methods
FIELD_TYPE_MAPPING = {
    "text": "fill",
    "email": "fill",
    "tel": "fill", 
    "number": "fill",
    "date": "fill",
    "password": "fill",
    "textarea": "fill",
    "select": "select_option",
    "checkbox": "set_checked",
    "radio": "check"
}

# Success indicators
SUCCESS_CODES = {
    "success": "ASTEROID_1",
    "data_error": "ASTEROID_0"
}

# Project root directory (for consistent file path references)
PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))

def get_abs_path(relative_path: str) -> str:
    """Convert a relative path to an absolute path based on project root"""
    return str(PROJECT_ROOT / relative_path)

def get_form_config(form_type: str) -> Dict[str, Any]:
    """Get configuration specific to a form type"""
    if form_type not in ["easy", "hard"]:
        raise ValueError(f"Invalid form type: {form_type}. Must be 'easy' or 'hard'")
        
    return {
        "url": FORM_URLS[form_type],
        "demo_data_file": get_abs_path(DEMO_DATA_FILES[form_type]),
        "is_multi_section": form_type == "hard"
    }


# This file provides:

#   1. Form URLs and Data Files: Configuration for both easy and hard forms
#   2. Browser Settings: Detailed Playwright browser configuration
#   3. Timeouts: Various timeouts for different operations
#   4. Retry Configuration: Settings for retry mechanisms
#   5. Logging Configuration: Compatible with your existing logger.py
#   6. Path Definitions: Organized file paths for outputs
#   7. Field Type Mapping: Maps form field types to interaction methods
#   8. Helper Functions: Utilities for path resolution and form-specific configs

#   The configuration is designed to be:
#   - Centralized: All settings in one place
#   - Flexible: Easy to adjust parameters
#   - Comprehensive: Covers all aspects of the automation
#   - Compatible: Works with your logger.py module

