# core/query_preprocessor.py
from typing import Optional, Dict, Any
from utils.logger import logger

class QueryPreprocessor:
    """
    First stage of query processing pipeline. 
    Attempts to parse queries using cache or regex before requiring LLM processing.
    """

    def __init__(self):
        self.cache = {}  # Simple cache for now
        logger.info("Initializing QueryPreprocessor")

    def process_query(self, raw_query: str) -> tuple[str, bool]:
        """
        Process raw query and determine if it needs LLM processing.
        
        Args:
            raw_query: Raw query string from CLI
            
        Returns:
            tuple: (processed_query, needs_llm)
            - If cache/regex match: (structured_criteria, False)
            - If needs LLM: (raw_query, True)
        """
        logger.info(f"Processing query: {raw_query}")

        # Try cache first
        cached_result = self._check_cache(raw_query)
        if cached_result:
            logger.info("Cache hit - returning cached criteria")
            return cached_result, False

        # Try regex patterns
        regex_result = self._try_regex_match(raw_query)
        if regex_result:
            logger.info("Regex match - returning structured criteria")
            return regex_result, False

        # No matches found, needs LLM processing
        logger.info("Query requires LLM processing")
        return raw_query, True

    def _check_cache(self, query: str) -> Optional[str]:
        """Check if query exists in cache."""
        logger.info("Checking query cache")
        return self.cache.get(query)

    def _try_regex_match(self, query: str) -> Optional[str]:
        """Attempt to match query against regex patterns."""
        logger.info("Attempting regex matching")
        return None  # Stub for now

    def update_cache(self, query: str, structured_criteria: str) -> None:
        """
        Update cache with processed query result from LLM.
        
        Args:
            query: Original raw query
            structured_criteria: Structured criteria from LLM
        """
        logger.info(f"Updating cache for query: {query}")
        self.cache[query] = structured_criteria
