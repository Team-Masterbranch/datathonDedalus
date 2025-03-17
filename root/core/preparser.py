# core/query_preprocessor.py
from typing import Optional, Dict, Any, Tuple, Union
from core.intention import FilterTarget, Intention, IntentionType
from utils.logger import logger
from utils.logger import setup_logger
from core.query import Query
import re
logger = setup_logger(__name__)

class Preparser:
    """
    First stage of query processing pipeline. 
    Attempts to parse queries using cache or regex before requiring LLM processing.
    """

    def __init__(self):
        self.cache: Dict[str, Intention] = {}  
        logger.info("Initializing QueryPreprocessor")
        self._compile_regex_patterns()

    def _compile_regex_patterns(self):
        """Compile regex patterns for common query structures."""
        self.patterns = {
            'age_greater': re.compile(
                r'(?:edad|años?)\s*(?:mayor|más|superior|>)\s*(?:que|a|de)?\s*(\d+)',
                re.IGNORECASE
            ),
            'age_less': re.compile(
                r'(?:edad|años?)\s*(?:menor|menos|inferior|<)\s*(?:que|a|de)?\s*(\d+)',
                re.IGNORECASE
            ),
            'condition_equals': re.compile(
                r'(?:condición|condicion|enfermedad)\s+(?:es|igual a)?\s*["\']?([^"\']+)["\']?',
                re.IGNORECASE
            )
        }


    def preparse_user_input(self, user_input: str) -> Tuple[Union[Intention, str], bool]:
        """
        Process raw user input and determine if it needs LLM processing.
        
        Args:
            raw_query: Raw query string from CLI
            
        Returns:
            tuple: (processed_query, needs_llm)
            - If cache/regex match: (Query object, False)
            - If needs LLM: (raw_query string, True)
        """
        logger.info(f"Processing query: {user_input}")

        # Try cache first
        cached_result = self._check_cache(user_input)
        if cached_result:
            logger.info("Cache hit - returning cached Intention")
            return cached_result, False

        # Try regex patterns
        regex_result = self._try_regex_match(user_input)
        if regex_result:
            logger.info("Regex match - creating Query object")
            query = Query(regex_result)
            # Create Intention object with the query
            intention = Intention(
                type=IntentionType.COHORT_FILTER,
                query=query,
                target=FilterTarget.FULL_DATASET
            )
            self.update_cache(user_input, intention)
            return intention, False

        # No matches found, needs LLM processing
        logger.info("Query requires LLM processing")
        return user_input, True

    def _check_cache(self, input: str) -> Optional[Intention]:
        """
        Check if input exists in cache.
        
        Args:
            input: Raw input string
            
        Returns:
            Optional[Intention]: Cached Query object if exists, None otherwise
        """
        logger.info("Checking intentions cache")
        return self.cache.get(input)

    def _try_regex_match(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to match query against regex patterns.
        
        Args:
            query: Raw query string
            
        Returns:
            Optional[Dict]: Query structure if match found, None otherwise
        """
        logger.info("Attempting regex matching")
        
        # Try age patterns
        if match := self.patterns['age_greater'].search(query):
            age = int(match.group(1))
            return {
                "field": "Edad",
                "operation": "greater_than",
                "value": age
            }
            
        if match := self.patterns['age_less'].search(query):
            age = int(match.group(1))
            return {
                "field": "Edad",
                "operation": "less_than",
                "value": age
            }
            
        # Try condition pattern
        if match := self.patterns['condition_equals'].search(query):
            condition = match.group(1).strip()
            return {
                "field": "Descripcion",
                "operation": "equals",
                "value": condition
            }
            
        return None

    def update_cache(self, user_input: str, intention: Intention) -> None:
        """
        Update cache with processed Query object.
        
        Args:
            raw_query: Original raw query string
            query: Processed Query object
        """
        logger.info(f"Updating cache for query: {user_input}")
        self.cache[user_input] = intention

    def clear_cache(self) -> None:
        """Clear the query cache."""
        logger.info("Clearing query cache")
        self.cache.clear()

    def get_cache_size(self) -> int:
        """
        Get current size of the cache.
        
        Returns:
            int: Number of cached queries
        """
        return len(self.cache)
