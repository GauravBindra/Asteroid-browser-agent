#!/usr/bin/env python3
"""
Configuration settings for Nova-ACT form automation.

This module contains configurable parameters for field detection
and other settings used across the form automation components.
"""

# Field detection settings
MAX_FIELD_DETECTION_SCROLLS = 3  # Maximum scrolls when looking for a field

# Scroll settings
SCROLL_AMOUNT_SMALL = "a small amount"  # Minimal scroll
SCROLL_AMOUNT_MEDIUM = "about half a page"  # Medium scroll
SCROLL_AMOUNT_LARGE = "to the bottom of the page"  # Large scroll

# Step limits
MAX_STEPS_PER_DETECTION = 20  # Maximum steps for field detection operations

# URLs
HARD_FORM_URL = "https://asteroid.ai/form"
EASY_FORM_URL = "https://asteroid.ai/form2"