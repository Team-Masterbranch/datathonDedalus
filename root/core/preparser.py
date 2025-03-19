import pickle
import re
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, Union
from core.intention import FilterTarget, Intention, IntentionType
from core.query import Query
from utils.logger import logger, setup_logger

logger = setup_logger(__name__)

class Preparser:
    def __init__(self, max_cache_size: int = 1000):
        """
        Initialize Preparser with a maximum cache size.
        
        Args:
            max_cache_size: Maximum number of entries to store in cache
        """
        self.max_cache_size = max_cache_size
        # Replace regular dict with OrderedDict for LRU tracking
        self.cache = OrderedDict()
        # Add usage counter for each entry
        self.cache_usage = {}
        logger.info(f"Initializing QueryPreprocessor with max cache size: {max_cache_size}")
        self._compile_regex_patterns()

    def _check_cache(self, input: str) -> Optional[Intention]:
        """
        Check if input exists in cache and update usage statistics.
        
        Args:
            input: Raw input string
            
        Returns:
            Optional[Intention]: Cached Intention object if exists, None otherwise
        """
        logger.info("Checking intentions cache")
        if input in self.cache:
            # Move the accessed item to the end (most recently used)
            intention = self.cache.pop(input)
            self.cache[input] = intention
            # Increment usage counter
            self.cache_usage[input] = self.cache_usage.get(input, 0) + 1
            return intention
        return None

    def update_cache(self, user_input: str, intention: Intention) -> None:
        """
        Update cache with processed Intention object, maintaining LRU order
        and respecting maximum size.
        
        Args:
            user_input: Original raw query string
            intention: Processed Intention object
        """
        logger.info(f"Updating cache for query: {user_input}")

        # If entry already exists, update it and move to end
        if user_input in self.cache:
            self.cache.pop(user_input)
            self.cache[user_input] = intention
            self.cache_usage[user_input] = self.cache_usage.get(user_input, 0) + 1
            return

        # If we're at max capacity, remove an entry
        if len(self.cache) >= self.max_cache_size:
            self._remove_least_valuable_entry()

        # Add new entry
        self.cache[user_input] = intention
        self.cache_usage[user_input] = 1

    def _remove_least_valuable_entry(self) -> None:
        """
        Remove the least valuable entry from the cache based on a combination
        of usage frequency and recency.
        """
        # Get the 5 least recently used items
        lru_candidates = list(self.cache.keys())[:5]
        
        # Find the least used among the LRU candidates
        least_used = min(lru_candidates, key=lambda x: self.cache_usage[x])
        
        # Remove from both cache and usage tracking
        self.cache.pop(least_used)
        self.cache_usage.pop(least_used)
        logger.debug(f"Removed least valuable entry: {least_used}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current cache state.
        
        Returns:
            Dict containing cache statistics
        """
        return {
            "size": len(self.cache),
            "max_size": self.max_cache_size,
            "most_used_queries": sorted(
                self.cache_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5 most used queries
        }

    def clear_cache(self) -> None:
        """Clear both the query cache and usage statistics."""
        logger.info("Clearing query cache")
        self.cache.clear()
        self.cache_usage.clear()

    def save_cache_to_file(self, filepath: str) -> None:
        """
        Save the current cache and usage statistics to a file.
        
        Args:
            filepath: Path where the cache file should be saved
        """
        cache_data = {
            "cache": dict(self.cache),
            "usage": self.cache_usage,
            "max_size": self.max_cache_size
        }
        
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as f:
                pickle.dump(cache_data, f)
            logger.info(f"Cache saved successfully to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving cache to {filepath}: {str(e)}")
            raise IOError(f"Failed to save cache: {str(e)}")

    def load_cache_from_file(self, filepath: str) -> None:
        """
        Load cache and usage statistics from a file.
        
        Args:
            filepath: Path to the cache file
        """
        try:
            if not Path(filepath).exists():
                raise FileNotFoundError(f"Cache file not found: {filepath}")
                
            with open(filepath, 'rb') as f:
                cache_data = pickle.load(f)
                
            # Validate loaded data
            if not all(key in cache_data for key in ["cache", "usage", "max_size"]):
                raise ValueError("Invalid cache format")
                
            # Restore cache state
            self.cache = OrderedDict(cache_data["cache"])
            self.cache_usage = cache_data["usage"]
            self.max_cache_size = cache_data["max_size"]
            
            logger.info(f"Cache loaded successfully from {filepath}")
            logger.debug(f"Loaded {len(self.cache)} cached items")
                
        except Exception as e:
            logger.error(f"Error loading cache from {filepath}: {str(e)}")
            raise IOError(f"Failed to load cache: {str(e)}")

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
