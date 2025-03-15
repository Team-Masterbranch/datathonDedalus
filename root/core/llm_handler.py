# core/llm_handler.py
from typing import Optional, Dict, Any
from utils.config import (
    LLM_API_KEY,
    LLM_DEFAULT_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_TOP_P,
    LLM_FREQUENCY_PENALTY,
    LLM_PRESENCE_PENALTY
)
from utils.logger import logger
from utils.logger import setup_logger
logger = setup_logger(__name__)

class LLMHandler:
    """
    Handles interactions with the LLM service.
    Currently supports basic query processing with configurable parameters.
    """

    def __init__(self):
        logger.info("Initializing LLM Handler")
        self.api_key = LLM_API_KEY
        if not self.api_key:
            logger.error("LLM API key not found in config")
            raise ValueError("LLM API key not configured")
        
        # Configure LLM parameters
        params = {
            "temperature": LLM_DEFAULT_TEMPERATURE,
            "max_tokens": LLM_MAX_TOKENS,
            "top_p": LLM_TOP_P,
            "frequency_penalty": LLM_FREQUENCY_PENALTY,
             "presence_penalty": LLM_PRESENCE_PENALTY
        }

    async def process_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a query through the LLM.
        
        Args:
            query: The query string to process
            params: Optional parameters to override defaults
            
        Returns:
            str: LLM response
        """
        logger.info(f"Processing query through LLM: {query[:50]}...")  # Log first 50 chars
        
        # Merge default params with any provided params
        query_params = self.default_params.copy()
        if params:
            query_params.update(params)

        try:
            response = await self._send_to_llm(query, query_params)
            logger.info("Successfully received LLM response")
            return response
        except Exception as e:
            logger.error(f"Error processing LLM query: {e}")
            raise

    async def _send_to_llm(self, query: str, params: Dict[str, Any]) -> str:
        """
        Send query to LLM service and get response.
        Stub method - replace with actual LLM API calls.
        """
        logger.info("Sending query to LLM service")
        # TODO: Implement actual LLM API call
        # For now, return mock response
        return f"LLM MOCK RESPONSE: Processed query '{query[:30]}...'"

    def update_default_params(self, params: Dict[str, Any]) -> None:
        """
        Update default parameters for LLM queries.
        
        Args:
            params: Dictionary of parameters to update
        """
        logger.info(f"Updating default LLM parameters: {params}")
        self.default_params.update(params)

    @staticmethod
    def format_prompt(query: str) -> str:
        """
        Format a query into a proper prompt for the LLM.
        
        Args:
            query: Raw query string
            
        Returns:
            str: Formatted prompt
        """
        # TODO: Implement proper prompt formatting
        return f"Convert the following healthcare query into structured criteria: {query}"
