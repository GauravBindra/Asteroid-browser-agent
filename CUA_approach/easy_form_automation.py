"""
Easy Form Automation using OpenAI Computer Use API and Playwright
"""

import os
import json
import base64
import time
from openai import OpenAI
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from PIL import Image  # Still useful for image handling

# Load environment variables
load_dotenv()

# Set up OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
    
client = OpenAI(api_key=api_key)

# Configuration
BROWSER_WIDTH = 1280
BROWSER_HEIGHT = 800
EASY_FORM_URL = "https://asteroid.ai/form2"
MAX_TURNS = 30
SCREENSHOTS_DIR = "CUA_approach/screenshots"

# Create screenshots directory if it doesn't exist
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

class AnalysisResult:
    """Class to hold image analysis results"""
    def __init__(self, success, code=None, message=None):
        self.success = success
        self.code = code
        self.message = message
        
    def __str__(self):
        return f"Success: {self.success}, Code: {self.code}, Message: {self.message}"

def take_screenshot(page, save_path=None):
    """Take a screenshot of the current page and optionally save it to disk"""
    screenshot_bytes = page.screenshot()
    
    # If save path is provided, save the screenshot to disk
    if save_path:
        # Ensure the path is relative to screenshots directory
        if not os.path.isabs(save_path):
            save_path = os.path.join(SCREENSHOTS_DIR, save_path)
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save the screenshot
        with open(save_path, "wb") as f:
            f.write(screenshot_bytes)
            
        print(f"Screenshot saved to {save_path}")
        
    # Return base64 encoded screenshot for API
    return base64.b64encode(screenshot_bytes).decode("utf-8")

def load_form_data(file_path):
    """Load form data from JSON file"""
    print(f"Loading form data from {file_path}")
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading form data: {e}")
        raise

class ActionHandler:
    """Handles execution of CUA actions on a Playwright page"""
    
    def __init__(self, page):
        self.page = page
        
    def execute(self, action):
        """Execute a computer action on the page"""
        action_type = action.type
        print(f"Executing action: {action_type}")
        
        try:
            if action_type == "click":
                return self._handle_click(action)
            elif action_type == "type":
                return self._handle_type(action)
            elif action_type == "keypress":
                return self._handle_keypress(action)
            elif action_type == "double_click":
                return self._handle_double_click(action)
            elif action_type == "scroll":
                return self._handle_scroll(action)
            elif action_type == "wait":
                return self._handle_wait(action)
            elif action_type == "navigate":
                return self._handle_navigate(action)
            elif action_type == "screenshot":
                return True  # No action needed, we take screenshots after each action
            else:
                print(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            print(f"Error executing {action_type}: {e}")
            return False
            
    def _handle_click(self, action):
        """Handle click action"""
        x, y = action.x, action.y
        button = action.button if hasattr(action, 'button') else "left"
        print(f"  Clicking at ({x}, {y}) with button '{button}'")
        self.page.mouse.click(x, y, button=button)
        return True
        
    def _handle_double_click(self, action):
        """Handle double click action"""
        x, y = action.x, action.y
        button = action.button if hasattr(action, 'button') else "left"
        print(f"  Double-clicking at ({x}, {y}) with button '{button}'")
        self.page.mouse.dblclick(x, y, button=button)
        return True
        
    def _handle_type(self, action):
        """Handle type action"""
        text = action.text
        print(f"  Typing: '{text}'")
        self.page.keyboard.type(text)
        return True
        
    def _handle_keypress(self, action):
        """Handle keypress action"""
        keys = action.keys if hasattr(action, 'keys') else [action.key]
        for k in keys:
            print(f"  Pressing key: {k}")
            if k.lower() == "enter":
                self.page.keyboard.press("Enter")
            elif k.lower() == "space":
                self.page.keyboard.press(" ")
            else:
                self.page.keyboard.press(k)
        return True
        
    def _handle_scroll(self, action):
        """Handle scroll action"""
        x, y = action.x, action.y
        scroll_x, scroll_y = action.scroll_x, action.scroll_y
        print(f"  Scrolling at ({x}, {y}) with offsets ({scroll_x}, {scroll_y})")
        self.page.mouse.move(x, y)
        self.page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")
        return True
        
    def _handle_wait(self, action):
        """Handle wait action"""
        duration = 2  # Default duration in seconds
        if hasattr(action, 'duration'):
            duration = action.duration
        print(f"  Waiting for {duration} seconds")
        time.sleep(duration)
        return True
        
    def _handle_navigate(self, action):
        """Handle navigate action"""
        if hasattr(action, 'url'):
            url = action.url
            print(f"  Navigating to: {url}")
            self.page.goto(url)
            print(f"  Current URL: {self.page.url}")
            return True
        else:
            print("  Error: Navigate action missing URL")
            return False
            
class ImageAnalyzer:
    """Analyzes screenshots to detect completion status and result codes using OpenAI Vision"""
    
    def analyze(self, screenshot_path):
        """
        Analyze a screenshot to detect success/failure and result codes
        
        Args:
            screenshot_path: Path to the screenshot image file
            
        Returns:
            AnalysisResult: Object containing success status, code, and message
        """
        print(f"Analyzing screenshot: {screenshot_path}")
        
        try:
            # Use OpenAI Vision to analyze the image
            result = self._analyze_with_openai(screenshot_path)
            if result:
                return result
                
            # If OpenAI couldn't find a code
            return AnalysisResult(
                success=False,
                code=None,
                message="Could not determine result code"
            )
                
        except Exception as e:
            print(f"Error analyzing screenshot: {e}")
            return AnalysisResult(
                success=False,
                code=None,
                message=f"Analysis error: {str(e)}"
            )
            
    def _analyze_with_openai(self, image_path):
        """Use OpenAI Vision to analyze the image"""
        try:
            # Load the image and encode it as base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
                
            # Create a request to OpenAI vision
            response = client.chat.completions.create(
                model="gpt-4o",  # Updated to current model with vision capabilities
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": "Look at this screenshot of a form submission result. Can you see if it shows 'ASTEROID_0' or 'ASTEROID_1' code? Carefully examine the entire image for these exact codes. Only answer with the exact code you see, or 'No code found'."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]
                    }
                ],
                max_tokens=300
            )
            
            # Extract the response text
            result_text = response.choices[0].message.content
            print(f"OpenAI Vision result: {result_text}")
            
            # Check for result codes in the response
            if "ASTEROID_1" in result_text:
                return AnalysisResult(True, "ASTEROID_1", "OpenAI detected success code")
            elif "ASTEROID_0" in result_text:
                return AnalysisResult(False, "ASTEROID_0", "OpenAI detected failure code")
                
            # Try a second approach with a different prompt if no code found
            response = client.chat.completions.create(
                model="gpt-4o",  # Updated to current model with vision capabilities
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": "This is a screenshot of a form submission. Extract all text from this image and list it fully."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Extract the full text response and check for codes
            full_text = response.choices[0].message.content
            print(f"OpenAI full text extraction: {full_text[:100]}...")
            
            if "ASTEROID_1" in full_text:
                return AnalysisResult(True, "ASTEROID_1", "OpenAI detected success code in full text")
            elif "ASTEROID_0" in full_text:
                return AnalysisResult(False, "ASTEROID_0", "OpenAI detected failure code in full text")
            
            return None
            
        except Exception as e:
            print(f"OpenAI vision analysis error: {e}")
            return None
            
class CUAController:
    """Controller for the Computer Use API interactions"""
    
    def __init__(self, page):
        self.page = page
        self.action_handler = ActionHandler(page)
        self.config = {
            "display_width": BROWSER_WIDTH,
            "display_height": BROWSER_HEIGHT,
            "max_turns": MAX_TURNS,
            "environment": "browser"
        }
        
    def automate_form(self, url, form_data_path):
        """
        Automate form filling using CUA
        
        Args:
            url: The URL of the form
            form_data_path: Path to the JSON file containing form data
            
        Returns:
            str: Path to the final screenshot
        """
        # Load form data
        form_data = load_form_data(form_data_path)
        
        # Navigate to form
        print(f"Navigating to form: {url}")
        self.page.goto(url)
        time.sleep(2)  # Allow page to load
        
        # Take initial screenshot
        timestamp = int(time.time())
        initial_screenshot_path = f"initial_{timestamp}.png"
        screenshot_base64 = take_screenshot(self.page, initial_screenshot_path)
        
        # Create instruction with form data
        instruction = f"Fill out this form with the following data: {json.dumps(form_data)}. Make sure to check all required checkboxes including the Terms and Conditions checkbox. Then click the Review button at the bottom of the form, wait for the review page to load, then click the Submit button. After submitting, look for and report the submission code (ASTEROID_0 or ASTEROID_1)."
        
        # Start CUA conversation
        return self._run_cua_loop(instruction, screenshot_base64, timestamp)
        
    def _run_cua_loop(self, instruction, initial_screenshot, timestamp):
        """Run the main CUA conversation loop"""
        print(f"Starting CUA loop with instruction: {instruction}")
        
        # Initial request
        response = self._create_initial_request(instruction, initial_screenshot)
        
        # Main conversation loop
        turn_count = 0
        final_screenshot_path = None
        
        while turn_count < self.config["max_turns"]:
            turn_count += 1
            print(f"\n--- Turn {turn_count} ---")
            
            # Process computer calls
            computer_calls = [item for item in response.output if item.type == "computer_call"]
            
            if not computer_calls:
                print("No computer calls found. Checking for completion...")
                # Check if there's a message indicating completion
                if hasattr(response, 'output_text') and response.output_text:
                    print(f"Model output: {response.output_text}")
                    if any(code in response.output_text for code in ["ASTEROID_0", "ASTEROID_1"]):
                        print("Task completion indicated")
                        break
                
                # No more actions, we're done
                break
                
            # We expect at most one computer call per response
            computer_call = computer_calls[0]
            call_id = computer_call.call_id
            action = computer_call.action
            
            # Process any safety checks
            safety_checks = []
            if hasattr(computer_call, 'pending_safety_checks') and computer_call.pending_safety_checks:
                print("\n*** SAFETY CHECKS REQUIRED ***")
                for check in computer_call.pending_safety_checks:
                    print(f"Safety check: {check.code} - {check.message}")
                    # Auto-acknowledge in this demo (in a real app, you'd get user confirmation)
                    safety_checks.append({
                        "id": check.id,
                        "code": check.code,
                        "message": check.message
                    })
            
            # Execute the action
            success = self.action_handler.execute(action)
            
            # Small delay to let page update
            time.sleep(1)
            
            # Take a new screenshot
            screenshot_path = f"turn_{turn_count}_{timestamp}.png"
            screenshot_base64 = take_screenshot(self.page, screenshot_path)
            
            # Save the path to the final screenshot
            final_screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_path)
            
            # Get current URL
            current_url = self.page.url
            
            # Send continuation request
            try:
                response = self._create_continuation_request(
                    previous_id=response.id,
                    call_id=call_id,
                    screenshot=screenshot_base64,
                    current_url=current_url,
                    safety_checks=safety_checks
                )
            except Exception as e:
                print(f"Error in API call: {e}")
                break
        
        # Take a final screenshot
        final_screenshot_path = f"final_{timestamp}.png"
        take_screenshot(self.page, final_screenshot_path)
        
        print(f"\nCompleted after {turn_count} turns")
        return os.path.join(SCREENSHOTS_DIR, final_screenshot_path)
    
    def _create_initial_request(self, instruction, screenshot):
        """Create the initial request to the CUA API"""
        print("Sending initial request to OpenAI CUA...")
        
        try:
            response = client.responses.create(
                model="computer-use-preview",
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": self.config["display_width"],
                    "display_height": self.config["display_height"],
                    "environment": self.config["environment"]
                }],
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": instruction},
                        {"type": "input_image", "image_url": f"data:image/png;base64,{screenshot}"}
                    ]
                }],
                reasoning={
                    "generate_summary": "concise",
                },
                truncation="auto"
            )
            
            return response
            
        except Exception as e:
            print(f"Error creating initial request: {e}")
            raise
    
    def _create_continuation_request(self, previous_id, call_id, screenshot, current_url, safety_checks=None):
        """Create a continuation request to the CUA API"""
        print("Sending continuation request to OpenAI CUA...")
        
        try:
            # Prepare input data
            input_data = {
                "type": "computer_call_output",
                "call_id": call_id,
                "output": {
                    "type": "computer_screenshot",
                    "image_url": f"data:image/png;base64,{screenshot}"
                },
                "current_url": current_url
            }
            
            # Add acknowledged safety checks if needed
            if safety_checks:
                input_data["acknowledged_safety_checks"] = safety_checks
            
            # Create the request
            response = client.responses.create(
                model="computer-use-preview",
                previous_response_id=previous_id,
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": self.config["display_width"],
                    "display_height": self.config["display_height"],
                    "environment": self.config["environment"]
                }],
                input=[input_data],
                truncation="auto"
            )
            
            return response
            
        except Exception as e:
            print(f"Error creating continuation request: {e}")
            raise
            
def main():
    """Main function to run the form automation"""
    print("Starting Easy Form Automation with OpenAI CUA")
    
    # Paths
    form_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "easy_form_data.json")
    
    # Initialize Playwright
    with sync_playwright() as playwright:
        # Launch browser
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': BROWSER_WIDTH, 'height': BROWSER_HEIGHT}
        )
        page = context.new_page()
        
        try:
            # Initialize CUA controller
            cua = CUAController(page)
            
            # Run form automation
            final_screenshot_path = cua.automate_form(EASY_FORM_URL, form_data_path)
            
            # Analyze the result
            image_analyzer = ImageAnalyzer()
            result = image_analyzer.analyze(final_screenshot_path)
            
            # Report the outcome
            print("\n--- AUTOMATION RESULTS ---")
            print(f"Success: {result.success}")
            print(f"Result code: {result.code}")
            print(f"Message: {result.message}")
            
            # Keep browser open for a moment to view the results
            print("\nKeeping browser open for 10 seconds to view results...")
            time.sleep(10)
            
        except Exception as e:
            print(f"Error during automation: {e}")
        finally:
            print("Closing browser...")
            browser.close()
    
    print("Automation completed.")

if __name__ == "__main__":
    main()