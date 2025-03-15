from utils.config import LLM_API_KEY

def test_env():
    print(f"API Key exists: {bool(LLM_API_KEY)}")
    print(f"First few characters of API Key: {LLM_API_KEY[:8]}...")  # Only show beginning for security

if __name__ == "__main__":
    test_env()