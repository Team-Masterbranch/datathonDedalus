# tests/test_data_manager.py

import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),  # Get API key from environment
        base_url="https://litellm.dccp.pbu.dedalus.com"
    )
    
    response = client.chat.completions.create(
        model="bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",
        messages=[
            {
                "role": "user",
                "content": "this is a test request, write a short poem"
            }
        ]
    )
    
    # Print the response
    print(response.choices[0].message.content)
    
except Exception as e:
    print(f"An error occurred: {e}")
