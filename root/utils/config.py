import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
LLM_API_KEY = os.getenv('LLM_API_KEY')
if not LLM_API_KEY:
    raise ValueError("LLM_API_KEY environment variable not set")