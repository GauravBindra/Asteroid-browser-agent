# Nova-ACT Hard Form Implementation Restructuring Plan

## Code Structure Reorganization

We'll reorganize the codebase for better separation of concerns with the following structure:

### 1. `field_utils.py` - Core Field Operations

This file will contain all field-filling functions and field utilities:

- `field_exists()` - Semantic field detection function
- `fill_text_field()` - Enhanced text field filling with fallbacks
- `select_dropdown_option()` - Dropdown selection function
- `fill_date_field()` - Date field handling with format conversion
- `handle_checkbox()` - Checkbox interaction logic

Benefits:
- Centralizes all field interaction logic in one place
- Makes it easier to maintain and improve field handling
- Provides a consistent API for all field operations

### 2. `navigation_utils.py` - Navigation Functions

This file will contain all navigation and transition functions:

- `navigate_to_tab()` - Tab navigation with verification
- `click_next_button()` - Next button handling
- `click_back_button()` - Back button handling
- `scroll_reset()` - Viewport reset for getting unstuck
- `is_section_loaded()` - Section load verification

Benefits:
- Separates navigation concerns from field operations
- Makes it easier to improve navigation logic in one place
- Provides clear navigation API

### 3. Section-Specific Files

Individual files for each form section:

- `contact_details_handler.py` - Contact Details section
- `business_info_handler.py` - Business Info section
- `premises_details_handler.py` - Premises Details section
- `security_safety_handler.py` - Security & Safety section
- `coverage_options_handler.py` - Coverage Options section

Each section handler will:
- Import from field_utils.py and navigation_utils.py
- Focus exclusively on the section-specific logic
- Follow a consistent pattern for filling, verification and navigation

Benefits:
- Cleaner, more focused files that are easier to test and debug
- Better separation of concerns between section handling and field operations
- Makes it easier to work on one section without affecting others

### 4. `error_handling.py` - Error Handling Utilities

This file will contain error handling utilities:

- Error recovery strategies
- Retry mechanisms
- Error classification and reporting
- Fallback functions for common failure modes

Benefits:
- Centralizes error handling logic
- Makes it easier to improve error recovery strategies
- Provides consistent error handling across the codebase

### 5. `hard_form_automator.py` - Main Automation Orchestrator

This file will:
- Import section handlers
- Coordinate the overall form filling process
- Track state and progress
- Manage the end-to-end flow

Benefits:
- Provides a clear entry point for the automation
- Separates orchestration concerns from section-specific logic
- Makes it easier to understand the overall flow

## Implementation Approach

1. **Create Core Utility Files First**
   - Implement field_utils.py with our enhanced semantic field detection
   - Implement navigation_utils.py with our improved navigation functions
   - Implement error_handling.py with standardized error recovery strategies

2. **Migrate Section Handlers**
   - Move contact_details handling to its own file
   - Move business_info handling to its own file
   - Create placeholder files for remaining sections

3. **Create Main Orchestrator**
   - Implement the hard_form_automator.py with coordinated section filling

4. **Update Test Files**
   - Create test files that align with the new structure
   - Update existing tests to use the new imports

## Benefits of Restructuring

1. **Improved Maintainability**:
   - Smaller, more focused files
   - Clear separation of concerns
   - Easier to understand individual components

2. **Better Testability**:
   - Can test field operations independently
   - Can test section handlers in isolation
   - Clearer boundaries between components

3. **Simplified Collaboration**:
   - Multiple developers can work on different sections
   - Changes to field handling don't affect section logic
   - Common utilities provide consistent behavior

4. **Easier Extensibility**:
   - Adding a new field type is isolated to field_utils.py
   - Adding a new section is as simple as creating a new section handler file
   - Improving error handling benefits the entire system