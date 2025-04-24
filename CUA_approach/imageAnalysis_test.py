from openai import OpenAI
import os
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path):
    """Encode an image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_product_image(local_image_path):
    # Encode the image to base64
    base64_image = encode_image(local_image_path)

    print("\nAnalyzing form screenshot for submission status...")
    
    # Create chat completion with the image and stream the response
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an image judge system which checks if a form has been submitted correctly based on the screenshot provided."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this form screenshot and check if the form shows code ASTEROID_1 or ASTEROID_0.\nASTEROID_1 is the code for correct submission. ASTEROID_0 is the code for incorrect submission.\nAlso, if there is none of these two, then reply that the form has probably not been submitted."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.2,
        stream=True
    )

    # Process the streaming response
    full_response = ""
    print("\nAnalysis results:")
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="")
            full_response += content
    
    print("\n")
    return full_response

# Example usage
image_path = "/Users/gauravbindra/Desktop/Asteroid/nova-act_approach/screenshots/easy_form_final_20250415_212654.png"
analysis = analyze_product_image(image_path)
print("\nFull analysis:", analysis)