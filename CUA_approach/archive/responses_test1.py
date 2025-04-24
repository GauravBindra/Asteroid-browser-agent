from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_product_description(product_name, features, target_audience):
   response = client.responses.create(
       model="gpt-4o",
       instructions="You are a professional copywriter specialized in creating concise, compelling product descriptions. Focus on benefits rather than just features.",
       input=f"""
       Create a product description for {product_name}.
       Key features:
       - {features[0]}
       - {features[1]}
       - {features[2]}
       Target audience: {target_audience}
       Keep it under 150 words.
       """,
       temperature=0.7,
       max_output_tokens=200
   )
  
   return response.output_text

# Example usage
headphones_desc = generate_product_description(
   "NoiseGuard Pro Headphones",
   ["Active noise cancellation", "40-hour battery life", "Memory foam ear cushions"],
   "Business travelers and remote workers"
)

print(headphones_desc)