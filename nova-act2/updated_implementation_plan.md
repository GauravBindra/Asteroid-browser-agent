# Nova-ACT Hard Form Implementation Plan

## Core Component Structure

This document outlines the optimized approach for implementing the Asteroid form automation challenge using a modular, section-based architecture.

### 1. Utility Modules

#### `field_detection.py` - Field Detection Operations
- **Field Exists** - Simple semantic lookup to check if fields with specific labels exist in the current tab

#### `field_utils.py` - Field Filling Operations
- **Text Field Handling** - Standard input with field types
- **Dropdown Handling** - Selection functionality
- **Date Field Handling** - Format conversion
- **Checkbox Handling** - Toggle operations

#### `form_utils.py` - Navigation
- **Tab Navigation** - Section switching
- **Button Interaction** - Next/Back/Submit actions
- **Page State Detection** - Checking if elements are loaded

#### `config.py` - Basic Configuration
- **Timeout Settings** - Basic wait durations
- **Detection Parameters** - Field lookup settings

### 2. Section Handlers

#### `base_section.py` - Common Section Functionality
- **Initialization** - Setup with Nova-ACT instance and data
- **Navigation** - Standard tab navigation methods
- **Field Filling** - Common field population logic
- **Completion** - Standard section completion

#### Individual Section Handlers
- `contact_details.py` - Contact Details section
- `business_info.py` - Business Info section
- `premises_details.py` - Premises Details section
- `security_safety.py` - Security & Safety section
- `coverage_options.py` - Coverage Options section

Each section handler focuses on:
- Field mapping for that specific section
- Section-specific field interactions
- Conditional field logic for that section
- Section completion and transition

### 3. Main Orchestrator

#### `hard_form_automator.py` - Coordination
- **Section Sequencing** - Proper ordering of sections
- **Data Preparation** - Basic data loading
- **Form Completion** - End-to-end orchestration
- **Result Extraction** - Getting final form code

## Implementation Plan

### Phase 1: Core Utilities
1. Create `config.py` with basic parameters
2. Create `field_detection.py` with field existence checking
3. Create `field_utils.py` with field filling operations
4. Build `form_utils.py` for navigation

### Phase 2: Section Framework
1. Implement `base_section.py` with common functionality
2. Create template for section handlers

### Phase 3: Section Handlers
1. Implement individual section handlers:
   - Start with `contact_details.py`
   - Move to `business_info.py` 
   - Continue with remaining sections
   - Focus on accurate field mapping and filling

### Phase 4: Integration
1. Develop `hard_form_automator.py` main orchestrator
2. Integrate section handlers in sequence
3. Test end-to-end form completion