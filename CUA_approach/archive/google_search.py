"""
OpenAI Computer Use API example: Google Search
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
MAX_TURNS = 20  # Increased to allow for more interactions
USER_INSTRUCTION = "Go to google.com and search for 'Gaurav Bindra'"

def take_screenshot(page):
    """Take a screenshot of the current page and encode as base64"""
    screenshot_bytes = page.screenshot()
    return base64.b64encode(screenshot_bytes).decode('utf-8')

def handle_computer_action(page, action):
    """Execute a computer action on the page"""
    action_type = action.type
    print(f"Executing action: {action_type}")
    
    try:
        if action_type == "click":
            x, y = action.x, action.y
            button = action.button if hasattr(action, 'button') else "left"
            print(f"  Clicking at ({x}, {y}) with button '{button}'")
            page.mouse.click(x, y, button=button)
            return True
            
        elif action_type == "type":
            text = action.text
            print(f"  Typing: '{text}'")
            page.keyboard.type(text)
            return True
            
        elif action_type == "navigate":
            if hasattr(action, 'url'):
                url = action.url
                print(f"  Navigating to: {url}")
                page.goto(url)
                print(f"  Current URL: {page.url}")
                return True
            else:
                print("  Error: Navigate action missing URL")
                return False
                
        elif action_type == "keypress":
            keys = action.keys if hasattr(action, 'keys') else [action.key]
            for k in keys:
                print(f"  Pressing key: {k}")
                page.keyboard.press(k)
            return True
            
        elif action_type == "scroll":
            x, y = action.x, action.y
            scroll_x, scroll_y = action.scroll_x, action.scroll_y
            print(f"  Scrolling at ({x}, {y}) with offsets ({scroll_x}, {scroll_y})")
            page.mouse.move(x, y)
            page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")
            return True
            
        elif action_type == "wait":
            duration = 2  # Default wait time in seconds
            if hasattr(action, 'duration'):
                duration = action.duration
            print(f"  Waiting for {duration} seconds")
            time.sleep(duration)
            return True
            
        elif action_type == "screenshot":
            print("  Taking screenshot (no action needed)")
            return True
            
        else:
            print(f"  Unsupported action type: {action_type}")
            return False
            
    except Exception as e:
        print(f"  Error executing {action_type}: {e}")
        return False

def computer_use_loop(page):
    """Run the main CUA loop"""
    # Navigate to blank page and take initial screenshot
    page.goto('about:blank')
    screenshot_base64 = take_screenshot(page)
    
    # Start the conversation with the user instruction
    print(f"Starting CUA loop with instruction: {USER_INSTRUCTION}")
    
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
                {"type": "input_text", "text": USER_INSTRUCTION},
                {"type": "input_image", "image_url": f"data:image/png;base64,{screenshot_base64}"}
            ]
        }],
        truncation="auto"
    )
    
    # Main conversation loop
    turn_count = 0
    task_complete = False
    
    while turn_count < MAX_TURNS and not task_complete:
        turn_count += 1
        print(f"\n--- Turn {turn_count} ---")
        
        # Check if we have any computer_call items
        computer_calls = [item for item in response.output if item.type == "computer_call"]
        if not computer_calls:
            print("No computer call found in response. Task may be complete.")
            break
            
        # We expect at most one computer call per response
        computer_call = computer_calls[0]
        call_id = computer_call.call_id
        action = computer_call.action
        
        # Check for safety checks
        if hasattr(computer_call, 'pending_safety_checks') and computer_call.pending_safety_checks:
            print("\n*** SAFETY CHECKS REQUIRED ***")
            for check in computer_call.pending_safety_checks:
                print(f"Safety check: {check.code} - {check.message}")
                confirm = input("Acknowledge this safety check? (y/n): ").lower() == 'y'
                if not confirm:
                    print("Safety check not acknowledged. Stopping.")
                    return
        
        # Execute the action
        action_success = handle_computer_action(page, action)
        
        # Small delay to let page react to the action
        time.sleep(1)
        
        # Get current state
        screenshot_base64 = take_screenshot(page)
        current_url = page.url
        
        # Check for completion indication in response text
        if hasattr(response, 'output_text') and response.output_text:
            text = response.output_text
            if "search complete" in text.lower() or "task complete" in text.lower():
                print(f"Task completion indicated: {text}")
                task_complete = True
        
        # Send the updated state back to the model
        try:
            response = client.responses.create(
                model="computer-use-preview",
                previous_response_id=response.id,
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": BROWSER_WIDTH,
                    "display_height": BROWSER_HEIGHT,
                    "environment": "browser"
                }],
                input=[{
                    "type": "computer_call_output",
                    "call_id": call_id,
                    "output": {
                        "type": "computer_screenshot",
                        "image_url": f"data:image/png;base64,{screenshot_base64}"
                    },
                    "current_url": current_url
                }],
                truncation="auto"
            )
            
            # Print any text output from the model
            if hasattr(response, 'output_text') and response.output_text:
                print(f"\nModel output: {response.output_text}")
                
        except Exception as e:
            print(f"Error in API call: {e}")
            break
    
    print(f"\nCompleted after {turn_count} turns")
    
    # Keep browser open for a moment to see the final result
    print("Keeping browser open for 15 seconds to view results...")
    time.sleep(15)

def main():
    """Main entry point"""
    print("Starting Google Search automation with CUA...")
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': BROWSER_WIDTH, 'height': BROWSER_HEIGHT}
        )
        page = context.new_page()
        
        try:
            computer_use_loop(page)
        except Exception as e:
            print(f"Error during automation: {e}")
        finally:
            print("Closing browser...")
            browser.close()
    
    print("Automation completed.")

if __name__ == "__main__":
    main()