"""
Simple test for OpenAI Computer Use API
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

def main():
    """Run a simple test of the Computer Use API with Playwright"""
    
    # Configuration
    BROWSER_WIDTH = 1024
    BROWSER_HEIGHT = 768
    USER_INSTRUCTION = "Go to bing.com and search for 'OpenAI news'"
    
    print("Starting Playwright browser...")
    with sync_playwright() as playwright:
        # Launch the browser
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': BROWSER_WIDTH, 'height': BROWSER_HEIGHT}
        )
        page = context.new_page()
        
        # Navigate to a blank page
        page.goto('about:blank')
        
        # Take a screenshot
        print("Taking initial screenshot...")
        screenshot_bytes = page.screenshot()
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        # Send the first request with the screenshot
        print("Sending initial request to OpenAI...")
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
        
        print("\n=== First Response ===")
        print(f"Response ID: {response.id}")
        print(f"Status: {response.status}")
        
        # Print detailed response info for debugging
        print("\nResponse structure:")
        for attr in dir(response):
            if not attr.startswith('_') and attr not in ['dict', 'json', 'model_dump', 'model_dump_json']:
                try:
                    value = getattr(response, attr)
                    if attr == 'output':
                        print(f"  {attr}: {value}")
                    elif not callable(value):
                        print(f"  {attr}: {type(value)}")
                except:
                    pass
        
        # Process the response
        if hasattr(response, 'output') and response.output:
            for item in response.output:
                print(f"\nOutput item type: {item.type}")
                
                if item.type == "computer_call":
                    print(f"Action: {item.action.type}")
                    print(f"Call ID: {item.call_id}")
                    
                    # For a screenshot action, we take a new screenshot and send it back
                    if item.action.type == "screenshot":
                        print("Taking and sending a new screenshot...")
                        
                        # Take a new screenshot
                        screenshot_bytes = page.screenshot()
                        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                        
                        # Send the screenshot back
                        second_response = client.responses.create(
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
                                "call_id": item.call_id,
                                "output": {
                                    "type": "computer_screenshot",
                                    "image_url": f"data:image/png;base64,{screenshot_base64}"
                                },
                                "current_url": page.url
                            }],
                            truncation="auto"
                        )
                        
                        print("\n=== Second Response ===")
                        print(f"Response ID: {second_response.id}")
                        print(f"Status: {second_response.status}")
                        
                        # Check for the next action
                        if hasattr(second_response, 'output') and second_response.output:
                            for second_item in second_response.output:
                                print(f"\nOutput item type: {second_item.type}")
                                
                                if second_item.type == "computer_call":
                                    print(f"Action: {second_item.action.type}")
                                    
                                    # Handle a navigate action
                                    if second_item.action.type == "navigate":
                                        # Try different ways to access the URL property
                                        if hasattr(second_item.action, 'url'):
                                            url = second_item.action.url
                                        else:
                                            print("URL property not found, printing action properties:")
                                            for attr in dir(second_item.action):
                                                if not attr.startswith('_'):
                                                    try:
                                                        value = getattr(second_item.action, attr)
                                                        print(f"  {attr}: {value}")
                                                    except:
                                                        print(f"  {attr}: <error accessing>")
                                            # Fall back to a default URL if needed
                                            url = "https://bing.com"
                                        
                                        print(f"Navigating to: {url}")
                                        page.goto(url)
                                        print(f"Current URL: {page.url}")
                        else:
                            print("No output in second response")
                else:
                    print(f"Not a computer call, type: {item.type}")
        else:
            print("No output in response")
        
        # Wait a bit to see the browser window before closing
        print("\nKeeping browser open for 10 seconds...")
        time.sleep(10)
        
        # Close browser
        print("Closing browser...")
        browser.close()
        
        print("Test completed.")

if __name__ == "__main__":
    main()