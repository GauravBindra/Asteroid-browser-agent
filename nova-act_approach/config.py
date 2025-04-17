#!/usr/bin/env python3
"""
Configuration settings for Nova-ACT form automation.

This module contains configurable parameters for timeouts, retry counts,
and other settings used across the form automation components.
"""

# Timeouts (in seconds)
NAVIGATION_TIMEOUT = 5  # Time to wait after tab navigation
NEXT_BUTTON_TIMEOUT = 3  # Time to wait after clicking Next button
FIELD_INTERACTION_TIMEOUT = 1  # Time to wait after field interaction

# Retry settings
MAX_FIELD_RETRIES = 3  # Maximum retries for field operations
MAX_NAVIGATION_RETRIES = 2  # Maximum retries for navigation operations

# Field detection settings
MAX_FIELD_DETECTION_SCROLLS = 3  # Maximum scrolls when looking for a field
FIELD_VERIFICATION_ENABLED = True  # Whether to verify field values after filling

# Step limits
MAX_STEPS_PER_FIELD = 40  # Maximum steps for field operations
MAX_STEPS_PER_NAVIGATION = 30  # Maximum steps for navigation operations

# Scroll settings
SCROLL_AMOUNT_SMALL = "small"  # Amount to scroll for small adjustments
SCROLL_AMOUNT_MEDIUM = "medium"  # Amount to scroll for medium adjustments
SCROLL_AMOUNT_LARGE = "large"  # Amount to scroll for large adjustments

# URLs
HARD_FORM_URL = "https://asteroid.ai/form"
EASY_FORM_URL = "https://asteroid.ai/form2"