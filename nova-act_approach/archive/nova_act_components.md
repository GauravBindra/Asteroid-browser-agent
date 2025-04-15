# Nova-ACT Implementation Components

## Core Implementation Files (`impl` folder)

1. `playwright.py` - Core implementation for browser automation using Playwright. Manages browser instances, context, pages, video recording, and browser configuration.

2. `backend.py` - Handles communication with Nova-ACT's backend services.

3. `common.py` - Contains utility functions and common code used across the implementation.

4. `extension.py` - Manages Chrome extension functionality used for enhanced browser interactions.

5. `inputs.py` - Handles user input processing and validation for Nova-ACT commands.

6. `keyboard_event_watcher.py` - Monitors and processes keyboard events during browser automation.

7. `message_encrypter.py` - Provides encryption for secure communication between Nova-ACT and browser extensions.

8. `protocol.py` - Defines the communication protocol between Nova-ACT components.

9. `run_info_compiler.py` - Compiles and manages information about automation runs.

10. `window_messages.py` - Handles communication with browser windows through message passing.

## Sample Applications

The samples directory shows practical examples of using Nova-ACT, such as:

- `order_a_coffee_maker.py` - Demonstrates how to automate a simple e-commerce workflow using high-level natural language commands.
- `order_salad.py` - Example of food ordering automation.
- `apartments_caltrain.py` - Example of apartment search automation.
- `setup_chrome_user_data_dir.py` - Utility for setting up Chrome user data directory.

## Key Features

- Browser automation through natural language commands
- Support for video recording of automation sessions
- Customizable browser configurations
- Secure communication with browser extensions
- Parallel browser session support