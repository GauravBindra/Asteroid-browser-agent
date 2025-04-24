# OpenAI Computer Use API (CUA) Guide

## Understanding the Responses API Framework

The Computer Use API (CUA) is built on top of OpenAI's Responses API, which is a unified framework for handling various AI capabilities. This integration provides several benefits:

1. **Consistent Interface**: Uses the same client.responses.create() method for all interactions
2. **Conversation Context**: Maintains state between requests via previous_response_id
3. **Structured Output**: Provides standardized response formats with typed outputs
4. **Tool Integration**: Supports multiple tools with specialized capabilities
5. **Safety Features**: Built-in safety mechanisms like safety checks

The Responses API handles:
- Request routing to appropriate models
- Response generation and formatting
- Context management across turns
- Safety filtering and checks
- Error handling and reporting

## Core Workflow

1. **Send a request to the model**
   - Include computer tool with display size and environment
   - Optionally include initial screenshot

2. **Receive a suggested action**
   - Model returns computer_call items (click, type, scroll, etc.)
   - Includes reasoning summary explaining the action

3. **Execute the action**
   - Implement action handling for different types
   - Map model instructions to browser/environment actions

4. **Capture the updated screenshot**
   - Take a screenshot after action execution
   - Convert to base64 for the next request

5. **Repeat the loop**
   - Send screenshot as computer_call_output
   - Continue until task completion or no more actions

## Response Structure

The Responses API returns a structured response object with the following key attributes:

- **id**: Unique identifier for the response
- **created_at**: Timestamp when the response was created
- **status**: Status of the response (e.g., "completed")
- **model**: The model used to generate the response
- **output**: Array of output items, which can include:
  - `computer_call`: Actions for the computer to perform
  - `reasoning`: Explanation of what the model is doing
  - Text output or other tool call types

Each `computer_call` item contains:
- **id**: Unique identifier for the tool call
- **call_id**: ID to reference in the next request
- **action**: The specific action to perform (click, type, etc.)
- **pending_safety_checks**: Any safety warnings requiring acknowledgment
- **status**: Status of the tool call

## API Integration Details

### API Setup
```python
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

response = client.responses.create(
    model="computer-use-preview",
    tools=[{
        "type": "computer_use_preview",
        "display_width": 1024,
        "display_height": 768,
        "environment": "browser" # other possible values: "mac", "windows", "ubuntu"
    }],
    input=[
        {
            "role": "user",
            "content": "Check the latest OpenAI news on bing.com."
        }
        # Optional: include a screenshot of the initial state of the environment
        # {
        #     "type": "input_image",
        #     "image_url": f"data:image/png;base64,{screenshot_base64}"
        # }
    ],
    reasoning={
        "generate_summary": "concise",  # Options: "concise" or "detailed" 
    },
    truncation="auto",  # Required for computer_use_preview
    temperature=1.0,  # Controls randomness (0.0 to 2.0)
    top_p=1.0,  # Controls diversity of output
    # Optional user identifier for safety monitoring
    user="user-123"  
)
```

### Action Handler Implementation
```python
def handle_model_action(page, action):
    """
    Execute the corresponding operation on the Playwright page.
    """
    action_type = action.type
    
    try:
        match action_type:
            case "click":
                x, y = action.x, action.y
                button = action.button if hasattr(action, 'button') else "left"
                page.mouse.click(x, y, button=button)

            case "scroll":
                x, y = action.x, action.y
                scroll_x, scroll_y = action.scroll_x, action.scroll_y
                page.mouse.move(x, y)
                page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")

            case "keypress":
                keys = action.keys if hasattr(action, 'keys') else [action.key]
                for k in keys:
                    if k.lower() == "enter":
                        page.keyboard.press("Enter")
                    elif k.lower() == "space":
                        page.keyboard.press(" ")
                    else:
                        page.keyboard.press(k)
            
            case "type":
                text = action.text
                page.keyboard.type(text)
            
            case "wait":
                duration = 2  # Default duration
                if hasattr(action, 'duration'):
                    duration = action.duration
                time.sleep(duration)

            case "screenshot":
                # Nothing to do as screenshot is taken at each turn
                pass

            case "double_click":
                x, y = action.x, action.y
                button = action.button if hasattr(action, 'button') else "left"
                page.mouse.dblclick(x, y, button=button)
                
            case _:
                print(f"Unrecognized action: {action.type}")

    except Exception as e:
        print(f"Error handling action {action}: {e}")
```

### Screenshot Capture
```python
def get_screenshot(page):
    """
    Take a full-page screenshot using Playwright and return the image bytes.
    """
    return page.screenshot()
```

### CUA Loop Implementation
```python
def computer_use_loop(instance, response):
    """
    Run the loop that executes computer actions until no 'computer_call' is found.
    """
    while True:
        computer_calls = [item for item in response.output if item.type == "computer_call"]
        if not computer_calls:
            print("No computer call found. Output from model:")
            for item in response.output:
                print(item)
            break  # Exit when no computer calls are issued.

        # We expect at most one computer call per response.
        computer_call = computer_calls[0]
        last_call_id = computer_call.call_id
        action = computer_call.action

        # Execute the action
        handle_model_action(instance, action)
        time.sleep(1)  # Allow time for changes to take effect.

        # Take a screenshot after the action
        screenshot_bytes = get_screenshot(instance)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        # Send the screenshot back as a computer_call_output
        response = client.responses.create(
            model="computer-use-preview",
            previous_response_id=response.id,
            tools=[
                {
                    "type": "computer_use_preview",
                    "display_width": 1024,
                    "display_height": 768,
                    "environment": "browser"
                }
            ],
            input=[
                {
                    "call_id": last_call_id,
                    "type": "computer_call_output",
                    "output": {
                        "type": "computer_screenshot",
                        "image_url": f"data:image/png;base64,{screenshot_base64}"
                    }
                }
            ],
            truncation="auto"
        )

    return response
```

## Safety Mechanisms

### Safety Checks
- **malicious_instructions**: Instructions that could lead to malicious actions
- **irrelevant_domain**: Actions on domains unrelated to the task
- **sensitive_domain**: Actions on domains with sensitive content

### Acknowledging Safety Checks
```python
response = client.responses.create(
    model="computer-use-preview",
    previous_response_id="<previous_response_id>",
    tools=[{
        "type": "computer_use_preview",
        "display_width": 1024,
        "display_height": 768,
        "environment": "browser"
    }],
    input=[
        {
            "type": "computer_call_output",
            "call_id": "<call_id>",
            "acknowledged_safety_checks": [
                {
                    "id": "<safety_check_id>",
                    "code": "malicious_instructions",
                    "message": "We've detected instructions that may cause your application to perform malicious or unauthorized actions. Please acknowledge this warning if you'd like to proceed."
                }
            ],
            "output": {
                "type": "computer_screenshot",
                "image_url": "<image_url>"
            },
            "current_url": "https://example.com" # Optional but recommended
        }
    ],
    truncation="auto"
)
```

## Best Practices

1. **Human Oversight**
   - Keep humans in the loop for high-stakes tasks
   - Require user confirmation for sensitive actions

2. **Prompt Injection Protection**
   - Be cautious of untrusted instructions in screenshots
   - Use sandboxed environments

3. **Access Control**
   - Implement blocklists or allowlists for websites
   - Restrict actions to only what's necessary

4. **Error Handling**
   - Implement comprehensive try/except blocks
   - Add retry mechanisms for critical operations

5. **Performance Considerations**
   - Add small delays between actions (0.5-1s)
   - Set reasonable conversation turn limits

## Handling Common Errors

When working with the Responses API and CUA, you might encounter these common errors:

1. **Format Errors**
   - Using incorrect content types (use "input_text" and "input_image" not "text" or "image_url")
   - Using invalid structure in the input array
   - Missing required fields like "call_id" in computer_call_output

2. **Context Management**
   - Not properly maintaining conversation context with previous_response_id
   - Not handling safety checks properly
   - Attempting to send too much data (exceeding token limits)

3. **Action Implementation**
   - Not handling all action types returned by the model
   - Not properly implementing properties like double_click
   - Not validating properties with hasattr() before accessing

## Limitations

- Best suited for browser-based tasks
- 38.1% performance on OS-level tasks (according to OpenAI's system card)
- Rate limits on the computer-use-preview model
- Subject to OpenAI's data retention and usage policies
- Requires "truncation": "auto" parameter
- Actions may sometimes target browser UI elements rather than page content
- Initial actions may include multiple "wait" requests while analyzing the screen