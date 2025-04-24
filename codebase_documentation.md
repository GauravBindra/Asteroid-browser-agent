# Nova-ACT Form Automation Codebase Documentation

This document provides a comprehensive explanation of the Nova-ACT form automation codebase. It details each file's purpose and the role of individual functions within the pipeline.

## Overview

The codebase is designed to automate filling out complex insurance forms using Nova-ACT, a browser automation framework. The architecture follows a modular approach with clear separation of concerns:

1. **Main Orchestration** - Coordinates the form filling process
2. **Section Handlers** - Process specific form sections
3. **Field Utilities** - Provide specialized functions for different field types
4. **Navigation** - Handle movement between sections
5. **Verification** - Ensure fields are filled correctly
6. **Error Handling** - Recover from failures and implement fallback strategies

## Files and Functions

### `main_form_automation3.py`

The main orchestration script that coordinates the entire form filling process.

**Key Functions:**

- `automate_form(data_file_path, form_url)`: Main entry point that:
  - Loads form data from JSON
  - Initializes Nova-ACT
  - Detects the current section
  - Calls appropriate handlers for each section
  - Uses fallback navigation if standard navigation fails
  - Verifies the final submission result

**Interactions:**
- Imports section handlers from all handler modules
- Uses navigation functions from `navigation.py`
- Uses detection functions from `section_detection.py`
- Uses data loading from `utils_final.py`
- Uses error handling from `error_handler.py`

### `config.py`

Contains configuration constants used throughout the codebase.

**Key Variables:**
- `HARD_FORM_URL`: URL of the form to automate
- `FORM_SECTIONS`: List of form sections in order
- `SECTION_MAPPING`: Maps JSON data sections to form sections
- `FIELD_TYPES`: Maps field names to their types (text, dropdown, checkbox, date)
- `FIELD_DEPENDENCIES`: Defines which fields depend on others

**Interactions:**
- Imported by most files to access configuration constants

### `field_detection.py`

Provides utilities for detecting form fields and sections.

**Key Functions:**
- `navigate_to_subsection(nova, section_name, subsection_name)`: Navigates to a specific subsection
- `field_exists(nova, label, current_tab, field_type, subsection)`: Checks if a field exists in the current section
- `find_field(nova, label, section_name, field_type, max_attempts)`: Tries to find a field with retry logic
- `get_form_label(key, section_name)`: Converts JSON field keys to form labels using context-aware mappings

**Interactions:**
- Used by all section handlers to find fields
- Used by `fill_fields.py` for field operations
- Used by `verify3.py` for field verification

### `fill_fields.py`

Contains functions for filling different types of form fields.

**Key Functions:**
- `fill_text_field(nova, label, value)`: Fills a text field
- `fill_checkbox(nova, label, should_check)`: Checks or unchecks a checkbox
- `fill_date_field(nova, label, value)`: Fills a date field with formatted date
- `select_dropdown_option(nova, label, value)`: Selects an option from a dropdown
- `fill_address_fields(nova, section_label, address_data)`: Fills a complete address block with special handling for City and Postcode fields

**Interactions:**
- Called by section handlers to fill individual fields
- Uses `get_form_label` from `field_detection.py`
- Uses verification from `verify3.py`
- Uses date formatting from `date_helpers.py`

### `verify3.py`

Provides functions for verifying if fields have been filled correctly.

**Key Functions:**
- `verify_field(nova, label, expected_value, field_type)`: Standard verification of a field
- `verify_field_filled(nova, label, expected_value, field_type, section_name)`: Specialized verification with multiple query variants for problematic fields
- `verify_section(nova, section_name, form_data, subsection_name, specific_fields)`: Verifies all or specific fields in a section
- `verify_specific_fields(nova, specific_fields)`: Targeted verification of specific fields using specialized verification
- `verify_subsection_fields(nova, section_name, json_section, subsection_name, subsection_data)`: Verifies fields in a specific subsection
- `verify_address_fields(nova, section_name, address_data)`: Specialized verification for address fields

**Interactions:**
- Called by section handlers for field verification
- Used by `fill_fields.py` to verify filled fields
- Uses field detection from `field_detection.py`

### `navigation.py`

Contains functions for navigating within the form.

**Key Functions:**
- `click_button(nova, button_text)`: Clicks a button with the given text
- `navigate_to_section(nova, section_name)`: Navigates to a specific section of the form

**Interactions:**
- Used by `main_form_automation3.py` for section navigation
- Used by all section handlers to navigate between sections
- Used by `error_handler.py` for fallback navigation

### `section_detection.py`

Contains functions for detecting form sections.

**Key Functions:**
- `section_exists(nova, section_name)`: Checks if a section exists in the form
- `sub_section_exists(nova, section_name)`: Checks if a subsection exists in the form

**Interactions:**
- Used by `main_form_automation3.py` to detect the current section
- Used by `navigation.py` to validate section navigation
- Used by section handlers to verify section navigation

### `error_handler.py`

Provides error handling and recovery mechanisms.

**Key Functions:**
- `retry_failed_fields(nova, failed_fields)`: Retries filling fields that failed initial verification
- `navigate_to_next_section(nova, current_section)`: Fallback navigation when normal navigation fails

**Interactions:**
- Used by `main_form_automation3.py` for fallback navigation
- Used by section handlers to recover from navigation failures
- Uses `verify3.py` for field verification
- Uses `navigation.py` for section navigation

### `utils_final.py`

Contains utility functions used throughout the codebase.

**Key Functions:**
- `load_json_data(file_path)`: Loads form data from a JSON file

**Interactions:**
- Used by `main_form_automation3.py` to load form data
- Used by section handlers when running standalone tests

### `date_helpers.py`

Provides functions for handling date fields.

**Key Functions:**
- `detect_order(nova, label, pattern)`: Detects the date format order in a field
- `convert_date(value)`: Converts a date from YYYY-MM-DD to appropriate format

**Interactions:**
- Used by `fill_fields.py` for date field operations

### Section Handler Files

#### `contact_details_handler3.py`

Handles the Contact Details section of the form.

**Key Functions:**
- `handle_contact_details(nova, form_data)`: Main function to process Contact Details section
  - Returns a tuple with success status and list of failed fields

**Interactions:**
- Called by `main_form_automation3.py`
- Uses `field_detection.py` to find fields
- Uses `fill_fields.py` to fill fields
- Uses `verify3.py` for verification
- Uses `navigation.py` to navigate to next section
- Uses `error_handler.py` for fallback navigation

#### `business_info_handler3.py`

Handles the Business Info section of the form.

**Key Functions:**
- `handle_business_info(nova, form_data)`: Main function to process Business Info section
  - Returns a tuple with success status and list of failed fields

**Interactions:**
- Similar to contact_details_handler3.py

#### `premises_details_handler3.py`

Handles the Premises Details section of the form.

**Key Functions:**
- `handle_premises_details(nova, form_data)`: Main function to process Premises Details section
  - Returns a tuple with success status and list of failed fields
- `process_property_identity(nova, identity_data, section_name)`: Processes Property Identity subsection
- `process_construction_details(nova, construction_data, section_name)`: Processes Construction Details subsection

**Interactions:**
- Similar to other section handlers, but with additional subsection handling

#### `security_safety_handler3.py`

Handles the Security & Safety section of the form.

**Key Functions:**
- `handle_security_safety(nova, form_data)`: Main function to process Security & Safety section
  - Returns a tuple with success status and list of failed fields
- `process_security_fields(nova, security_data, section_name)`: Processes security fields

**Interactions:**
- Similar to other section handlers

#### `submission3.py`

Handles Coverage Options section and final form submission.

**Key Functions:**
- `handle_coverage_options(nova, form_data)`: Processes Coverage Options section
- `handle_final_submission(nova)`: Handles the final submission page
- `verify_submission_result(nova)`: Verifies if ASTEROID_1 code appears after submission

**Interactions:**
- Called by `main_form_automation3.py` for final steps
- Uses `navigation.py` for button clicking
- Uses pattern similar to other section handlers

## Data Flow

1. `main_form_automation3.py` loads the form data
2. For each detected section, it calls the appropriate section handler
3. Section handlers:
   - Fill fields using functions from `fill_fields.py`
   - Verify fields using functions from `verify3.py`
   - Track failed fields during processing
   - Use specialized verification for problematic fields
   - Navigate to the next section when done
4. If standard navigation fails, `error_handler.py` provides fallback navigation
5. After all sections are processed, `submission3.py` handles final submission
6. The process verifies if the ASTEROID_1 code appears, indicating success

## Testing Scripts

The codebase includes several test scripts:

- **Section Tests**: Each handler file can be run directly to test just that section
- **Field-Specific Tests**: Tests for problematic fields like Postcode
- **Targeted Verification Tests**: Tests the specialized verification approach
- **Fallback Navigation Tests**: Tests the fallback navigation mechanism

These allow testing specific components in isolation before running the full automation.

## Improvements and Robustness Features

1. **Centralized Field Label Mapping**: `get_form_label` ensures consistent field labels
2. **Multiple Field Detection Strategies**: Enhanced detection for problematic fields (City, Postcode)
3. **Targeted Verification**: Only re-verifies fields that failed initial verification
4. **Specialized Verification**: Uses multiple query variants for problematic fields
5. **Fallback Navigation**: Alternative approaches when standard navigation fails
6. **Retry Logic**: For both field filling and verification
7. **Error Handling**: Try-except blocks throughout the codebase
8. **Field Dependency Handling**: Skips fields that shouldn't be processed based on other field values
9. **Detailed Logging**: Comprehensive logging throughout the process

These features make the automation robust against various challenges in complex form automation.