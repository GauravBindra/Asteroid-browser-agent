"""
OpenAI Computer Use API example with Playwright browser automation
"""

import os
import base64
import time
from openai import OpenAI
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv()

# Set up the OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables")
    exit(1)

client = OpenAI(api_key=api_key)

# Configuration
BROWSER_WIDTH = 1024
BROWSER_HEIGHT = 768
MAX_TURNS = 10  # Maximum conversation turns

def take_screenshot(page):
    """Take a screenshot of the current page and encode as base64"""
    screenshot_bytes = page.screenshot()
    return base64.b64encode(screenshot_bytes).decode('utf-8')

def handle_model_action(page, action):
    """
    Execute the corresponding operation on the Playwright page.
    """
    action_type = action.type
    
    try:
        if action_type == "click":
            x, y = action.x, action.y
            button = action.button if hasattr(action, 'button') else "left"
            print(f"Action: click at ({x}, {y}) with button '{button}'")
            page.mouse.click(x, y, button=button)
        
        elif action_type == "scroll":
            x, y = action.x, action.y
            scroll_x, scroll_y = action.scroll_x, action.scroll_y
            print(f"Action: scroll at ({x}, {y}) with offsets ({scroll_x}, {scroll_y})")
            page.mouse.move(x, y)
            page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")
        
        elif action_type == "keypress":
            keys = action.keys if hasattr(action, 'keys') else [action.key]
            for k in keys:
                print(f"Action: keypress '{k}'")
                if k.lower() == "enter":
                    page.keyboard.press("Enter")
                elif k.lower() == "space":
                    page.keyboard.press(" ")
                else:
                    page.keyboard.press(k)
        
        elif action_type == "type":
            text = action.text
            print(f"Action: type text: {text}")
            page.keyboard.type(text)
        
        elif action_type == "navigate":
            url = action.url
            print(f"Action: navigate to {url}")
            page.goto(url)
        
        elif action_type == "wait":
            print(f"Action: wait")
            time.sleep(2)
        
        elif action_type == "screenshot":
            # Nothing to do as screenshot is taken at each turn
            print(f"Action: screenshot")
        
        else:
            print(f"Unrecognized action: {action_type}")

    except Exception as e:
        print(f"Error handling action {action_type}: {e}")

def computer_use_loop(page, initial_instruction):
    """
    Run the loop that executes computer actions until no 'computer_call' is found.
    """
    # Take initial screenshot
    screenshot_base64 = take_screenshot(page)
    
    # Initial request to the model
    print(f"Sending initial request with instruction: {initial_instruction}")
    response = client.responses.create(
        model="computer-use-preview",
        tools=[{
            "type": "computer_use_preview",
            "display_width": BROWSER_WIDTH,
            "display_height": BROWSER_HEIGHT,
            "environment": "browser"
        }],
        input=[{
            "role": "user",
            "content": [
                {"type": "text", "text": initial_instruction},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
            ]
        }],
        reasoning={
            "generate_summary": "concise",
        },
        truncation="auto"
    )
    
    turn_count = 0
    
    while turn_count < MAX_TURNS:
        turn_count += 1
        print(f"\n--- Turn {turn_count} ---")
        
        # Check for computer calls in response
        computer_calls = [item for item in response.output if item.type == "computer_call"]
        if not computer_calls:
            print("No computer call found. Response from model:")
            for item in response.output:
                print(item)
            break  # Exit when no computer calls are issued
        
        # Print reasoning if available
        reasoning_items = [item for item in response.output if item.type == "reasoning"]
        for item in reasoning_items:
            if hasattr(item, 'summary'):
                for summary in item.summary:
                    print(f"Reasoning: {summary.text}")
        
        # We expect at most one computer call per response
        computer_call = computer_calls[0]
        last_call_id = computer_call.call_id
        action = computer_call.action
        
        # Check for safety checks
        has_safety_checks = False
        acknowledged_checks = []
        
        if hasattr(computer_call, 'pending_safety_checks') and computer_call.pending_safety_checks:
            has_safety_checks = True
            print("\n*** SAFETY CHECKS REQUIRED ***")
            for check in computer_call.pending_safety_checks:
                print(f"Safety check {check.id}: {check.code} - {check.message}")
                
                # Ask for user confirmation (in a real app, you'd have a proper UI for this)
                confirm = input(f"Acknowledge safety check '{check.code}'? (y/n): ").lower() == 'y'
                if confirm:
                    acknowledged_checks.append({
                        "id": check.id,
                        "code": check.code,
                        "message": check.message
                    })
                else:
                    print("Safety check not acknowledged. Stopping execution.")
                    return
        
        # Execute the action
        print(f"Executing action: {action.type}")
        handle_model_action(page, action)
        time.sleep(1)  # Allow time for changes to take effect
        
        # Take a screenshot after the action
        screenshot_base64 = take_screenshot(page)
        current_url = page.url
        
        # Send the screenshot back as a computer_call_output
        print("Sending updated screenshot to OpenAI...")
        
        try:
            # Construct the input for the next request
            input_data = {
                "type": "computer_call_output",
                "call_id": last_call_id,
                "output": {
                    "type": "computer_screenshot",
                    "image_url": f"data:image/png;base64,{screenshot_base64}"
                },
                "current_url": current_url  # Include current URL for better safety checks
            }
            
            # Add acknowledged safety checks if needed
            if acknowledged_checks:
                input_data["acknowledged_safety_checks"] = acknowledged_checks
            
            response = client.responses.create(
                model="computer-use-preview",
                previous_response_id=response.id,
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": BROWSER_WIDTH,
                    "display_height": BROWSER_HEIGHT,
                    "environment": "browser"
                }],
                input=[input_data],
                truncation="auto"
            )
            
        except Exception as e:
            print(f"Error sending request to OpenAI: {e}")
            break
    
    print(f"\nCompleted after {turn_count} turns")
    return response

def main():
    """Main function to run the Computer Use API example."""
    with sync_playwright() as playwright:
        # Launch the browser
        browser = playwright.chromium.launch(headless=False)  # Set to True for headless mode
        context = browser.new_context(
            viewport={'width': BROWSER_WIDTH, 'height': BROWSER_HEIGHT}
        )
        page = context.new_page()
        
        # Start with a blank page
        page.goto('about:blank')
        
        # User instruction
        user_instruction = "Go to bing.com and search for the latest OpenAI news"
        
        try:
            # Run the computer use loop
            computer_use_loop(page, user_instruction)
        except Exception as e:
            print(f"Error during computer use loop: {e}")
        finally:
            # Ensure the browser is closed
            browser.close()

if __name__ == "__main__":
    main()