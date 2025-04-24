from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import time

# Load environment variables from .env file (if it exists)
load_dotenv()

# Set up the OpenAI client
# You need to set OPENAI_API_KEY environment variable or create a .env file with it
# Alternatively, you can pass the API key directly: client = OpenAI(api_key="your-api-key")
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables")
    print("Please set your API key using one of these methods:")
    print("1. Export it: export OPENAI_API_KEY='your-api-key-here'")
    print("2. Create a .env file with: OPENAI_API_KEY=your-api-key-here")
    print("3. Modify this script to pass the key directly: client = OpenAI(api_key='your-key')")
    exit(1)

client = OpenAI(api_key=api_key)

print("Sending request to OpenAI Computer Use API...")

# Create the response - this initiates the interaction
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
        #     type: "input_image",
        #     image_url: f"data:image/png;base64,{screenshot_base64}"
        # }
    ],
    reasoning={
        "generate_summary": "concise",
    },
    truncation="auto"
)

# Print response structure information
print("\n=== Response Structure ===")
print(f"Response type: {type(response)}")
print(f"Available attributes: {dir(response)}")

# Print the full response object (may be large)
print("\n=== Full Response Content ===")
print(response)

# Extract important information
print("\n=== Important Response Information ===")
print(f"Response ID: {response.id if hasattr(response, 'id') else 'Not available'}")
print(f"Created timestamp: {response.created if hasattr(response, 'created') else 'Not available'}")
print(f"Model: {response.model if hasattr(response, 'model') else 'Not available'}")

# Try to access different attributes that might contain the summary or result
print("\n=== Trying to access output content ===")

if hasattr(response, 'output') and response.output is not None:
    print("Output attribute found:")
    print(response.output)
else:
    print("Output attribute not found or is None")

if hasattr(response, 'choices') and response.choices:
    print("\nChoices found:")
    for i, choice in enumerate(response.choices):
        print(f"Choice {i}:")
        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
            print(f"Message content: {choice.message.content}")

if hasattr(response, 'computer_actions'):
    print("\nComputer actions found:")
    for i, action in enumerate(response.computer_actions):
        print(f"Action {i}: {action}")

if hasattr(response, 'reasoning_summary'):
    print("\nReasoning summary found:")
    print(response.reasoning_summary)

# Try to extract tool calls which seems to be what's being returned
print("\n=== Tool Calls Information ===")
if hasattr(response, 'tool_calls') and response.tool_calls:
    print("Tool calls found:")
    for i, tool_call in enumerate(response.tool_calls):
        print(f"Tool call {i}:")
        print(tool_call)
else:
    print("No tool_calls attribute found")

if hasattr(response, 'computer_tool_calls') and response.computer_tool_calls:
    print("\nComputer tool calls found:")
    for i, tool_call in enumerate(response.computer_tool_calls):
        print(f"Computer tool call {i}:")
        print(f"  ID: {tool_call.id}")
        print(f"  Type: {tool_call.type}")
        print(f"  Status: {tool_call.status}")
        if hasattr(tool_call, 'action'):
            print(f"  Action: {tool_call.action}")
else:
    print("No computer_tool_calls attribute found")

# Wait for completion - NOTE: This is a very basic approach and may not work in all cases
# For real applications, you would typically implement a proper polling mechanism
print("\n=== Attempting to wait for completion ===")
run_id = response.id if hasattr(response, 'id') else None

if run_id:
    try:
        # Try to retrieve the run to see if there's a completion
        print(f"Checking run status for ID: {run_id}")
        # Note: This is a guess at the API - you may need to adjust based on the actual API
        run = client.responses.retrieve(run_id)
        print(f"Run status: {run.status if hasattr(run, 'status') else 'Unknown'}")
        
        # Try to get any final content
        if hasattr(run, 'output') and run.output:
            print("Final output:")
            print(run.output)
    except Exception as e:
        print(f"Error retrieving run: {e}")
else:
    print("No run ID available to check status")
