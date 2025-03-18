# core/llm_handler.py
import os
from pathlib import Path
from typing import Any, Dict, List
from openai import OpenAI
from core.data_manager import DataManager
from utils import logger
from utils.config import DATA_DIR
from datetime import datetime
from utils.config import LLM_LOG_DIR, LLM_LOG_FILE, LLM_LOG_SEPARATOR

logger = logger.setup_logger(__name__)


class LLMHandler:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://litellm.dccp.pbu.dedalus.com"
        )
        self.data_manager = DataManager(DATA_DIR)
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self._clear_llm_log()

    def _load_prompt(self, filename: str) -> str:
        """Load prompt from file"""
        with open(self.prompts_dir / filename, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def _format_schema(self, schema: dict) -> str:
        """Format schema into a readable string"""
        return '\n'.join([f"{col}: {dtype}" for col, dtype in schema.items()])

    def single_string_request(self, request: str) -> Dict[str, Any]:
        try:
            # Get current schema
            schema = self.data_manager.get_current_schema()
            formatted_schema = self._format_schema(schema)
            
            # Load static prompts
            intentions_prompt = self._load_prompt("system_intentions.txt")
            examples_prompt = self._load_prompt("system_examples.txt")
            schema_description = self._load_prompt("schema_description.txt")
            
            # Combine schema description with actual schema
            schema_prompt = f"{schema_description}\n{formatted_schema}"

            # Create system messages
            system_messages = [
                {
                    "role": "system",
                    "content": intentions_prompt
                },
                {
                    "role": "system",
                    "content": schema_prompt
                },
                {
                    "role": "system",
                    "content": examples_prompt
                }
            ]

            messages = system_messages + [
                {
                    "role": "user",
                    "content": request
                }
            ]
            
            response = self.client.chat.completions.create(
                model="bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",
                messages=messages
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error in LLM test: {e}")
            raise

    def single_message_request(self, message: Dict[str, str]) -> str:
        """
        Process a single input message through LLM.
        
        Args:
            message: Dictionary containing message with format {"role": str, "content": str}
            
        Returns:
            str: LLM response text
            
        Raises:
            ValueError: If message format is invalid
        """
        try:
            # Validate message format
            if not isinstance(message, dict) or "role" not in message or "content" not in message:
                raise ValueError("Invalid message format. Expected {'role': str, 'content': str}")

            # Get current schema
            schema = self.data_manager.get_current_schema()
            formatted_schema = self._format_schema(schema)
            
            # Load static prompts
            intentions_prompt = self._load_prompt("system_intentions.txt")
            examples_prompt = self._load_prompt("system_examples.txt")
            schema_description = self._load_prompt("schema_description.txt")
            
            # Combine schema description with actual schema
            schema_prompt = f"{schema_description}\n{formatted_schema}"

            # Create system messages
            system_messages = [
                {
                    "role": "system",
                    "content": intentions_prompt
                },
                {
                    "role": "system",
                    "content": schema_prompt
                },
                {
                    "role": "system",
                    "content": examples_prompt
                }
            ]

            # Combine system messages with user message
            messages = system_messages + [message]
            
            response = self.client.chat.completions.create(
                model="bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",
                messages=messages
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error in LLM request: {e}")
            raise


    def send_chat_request(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0"
    ) -> str:
        """
        Send a generic chat completion request to LLM.
        
        Args:
            messages: List of message dictionaries with format [{"role": str, "content": str}, ...]
            model: Model identifier to use for the request
            
        Returns:
            str: LLM response text
            
        Raises:
            Exception: If LLM request fails
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            self._add_llm_log_entry(messages, response.choices[0].message.content)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in chat request: {e}")
            raise
        



    def _add_llm_log_entry(self, messages: List[Dict[str, str]], response: str) -> None:
        """
        Log LLM interaction to dedicated log file.
        
        Args:
            messages: List of messages sent to LLM
            response: Response received from LLM
        """
        try:
            # Ensure log directory exists
            LLM_LOG_DIR.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(LLM_LOG_FILE, 'a', encoding='utf-8') as f:
                # Write timestamp
                f.write(f"\nTimestamp: {timestamp}")
                f.write(LLM_LOG_SEPARATOR)
                
                # Write messages sent to LLM
                f.write("Messages sent to LLM:\n")
                for msg in messages:
                    f.write(f"\nRole: {msg['role']}\n")
                    f.write(f"Content: {msg['content']}\n")
                
                # Write LLM response
                f.write("\nLLM Response:\n")
                f.write(f"{response}\n")
                
                # Write separator for next entry
                f.write(LLM_LOG_SEPARATOR)
                
            logger.debug(f"LLM interaction logged to {LLM_LOG_FILE}")
                
        except Exception as e:
            logger.error(f"Failed to log LLM interaction: {e}")
            # Don't raise - logging failure shouldn't break main functionality

    def _clear_llm_log(self) -> None:
        """
        Clear the LLM interaction log file.
        Creates empty file if it doesn't exist.
        """
        try:
            # Ensure log directory exists
            LLM_LOG_DIR.mkdir(parents=True, exist_ok=True)
            
            # Create or clear file
            with open(LLM_LOG_FILE, 'w', encoding='utf-8') as f:
                f.write(f"LLM Interaction Log\nCreated: {datetime.now()}\n")
                
            logger.info(f"LLM log cleared: {LLM_LOG_FILE}")
                
        except Exception as e:
            logger.error(f"Failed to clear LLM log: {e}")
            raise
