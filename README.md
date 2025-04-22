# Asteroid Form Challenge

This repository contains a solution for the Asteroid Form Challenge, which aims to automate the filling and submission of web forms using Nova-ACT, a powerful browser automation framework.

## Project Overview

The project uses Nova-ACT's natural language capabilities to interact with web forms in a more human-like way. The current implementation focuses on reliable form filling with extensive verification and error handling.

### Key Features
- Natural language-based field detection and interaction
- Robust field verification and retry mechanisms
- Comprehensive error handling and logging
- Support for both easy and hard form variants
- Command-line interface for flexible usage

## Prerequisites

1. **Python Environment**
   - Python 3.8 or higher
   - Virtual environment recommended

2. **Nova-ACT API Key**
   - Required for using Nova-ACT
   - Get your API key from [Nova-ACT](https://nova-act.com)
   - Add to `.env` file:
     ```
     NOVA_ACT_API_KEY=your_api_key_here
     ```

3. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

- `nova-act2/`: Main implementation directory
  - `main_form_automation3.py`: Core automation script
  - `easy_form_automation.py`: Easy form specific implementation
  - `fill_fields.py`: Field filling utilities
  - `field_detection.py`: Field detection logic
  - `navigation.py`: Page navigation utilities
  - `verify.py`: Field verification functions
  - `error_handler.py`: Error handling utilities
  - `date_helpers.py`: Date field handling
  - Handlers for specific form sections (contact, business, etc.)

## Usage

1. **Run Hard Form Automation**
   ```bash
   python3 nova-act2/main_form_automation3.py \
     --json=/path/to/hard_form_data.json \
     --form-url=https://asteroid.ai/form
   ```

2. **Run Easy Form Automation**
   ```bash
   python3 nova-act2/easy_form_automation.py
   ```

### Command Line Arguments
- `--json`: Path to JSON file containing form data
- `--form-url`: URL of the form to automate

## Implementation Approach

1. **Field Detection**
   - Uses natural language queries to find fields
   - Handles various field types (text, dropdown, checkbox, date)
   - Implements smart scrolling for better field discovery

2. **Field Filling**
   - Verifies field existence before attempting to fill
   - Uses natural language commands for interaction
   - Validates input after filling
   - Implements retry logic for failed attempts

3. **Error Handling**
   - Comprehensive logging of all operations
   - Multiple retry attempts with different strategies
   - Detailed error reporting for debugging

4. **Verification**
   - Verifies each field after filling
   - Supports different verification strategies per field type
   - Allows for section-level verification

## Logging

Logs are stored in `nova-act2/logs/` with timestamps for easy tracking. Each run creates a new log file with detailed information about:
- Field detection attempts
- Fill operations
- Verification results
- Errors and retries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
