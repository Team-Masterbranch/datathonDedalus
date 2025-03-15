# core/parser.py
from typing import Optional, Dict, Any
from utils.logger import logger
from utils.logger import setup_logger
logger = setup_logger(__name__)

class Parser:
    """
    Parser module that handles:
    1. Receiving preprocessed queries
    2. Interacting with LLM when needed
    3. Converting responses to structured criteria
    4. Updating preprocessor cache
    """

    def __init__(self):
        logger.info("Initializing Parser")

    def process_with_llm(self, query: str) -> str:
        """
        Process query through LLM to get structured criteria.
        
        Args:
            query: Raw or preprocessed query string
            
        Returns:
            str: Structured criteria for the Query Manager
        """
        logger.info(f"Processing query with LLM: {query}")
        
        # Stub for LLM interaction
        structured_criteria = self._get_llm_response(query)
        
        # Validate and format the response
        formatted_criteria = self._format_criteria(structured_criteria)
        
        logger.info(f"Generated structured criteria: {formatted_criteria}")
        return formatted_criteria

    def _get_llm_response(self, query: str) -> str:
        """
        Stub method for LLM interaction that returns meaningful mock criteria.
        Will be replaced with actual LLM call later.
        
        Args:
            query: User query string
            
        Returns:
            str: JSON-formatted filtering criteria
        """
        logger.info("Getting LLM response")
        
        # Mock different response patterns based on query keywords
        if "edad" in query.lower():
            return {
                "field": "Edad",
                "operation": "between",
                "values": [30, 50]
            }
        elif "condicion" in query.lower():
            return {
                "field": "Condicion",
                "operation": "equals",
                "value": "Diabetes"
            }
        elif "and" in query.lower():
            return {
                "operation": "and",
                "criteria": [
                    {
                        "field": "Edad",
                        "operation": "greater_than",
                        "value": 40
                    },
                    {
                        "field": "Condicion",
                        "operation": "equals",
                        "value": "Hipertension"
                    }
                ]
            }
        else:
            # Default response
            return {
                "field": "Edad",
                "operation": "greater_than",
                "value": 70
            }

    def _format_criteria(self, llm_response: dict) -> dict:
        """
        Format and validate LLM response into proper criteria structure.
        
        Args:
            llm_response: Dictionary containing filtering criteria
            
        Returns:
            dict: Formatted and validated criteria
        """
        logger.info("Formatting LLM response into criteria")
        
        # Here we could add validation logic
        # For now, just return the criteria as is
        return llm_response

    def validate_criteria(self, criteria: dict) -> bool:
        """
        Validate if criteria is properly structured.
        
        Args:
            criteria: Criteria dictionary to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        logger.info(f"Validating criteria: {criteria}")
        
        valid_operations = ["equals", "greater_than", "less_than", "between", "and", "or"]
        
        try:
            if "operation" not in criteria:
                return False
                
            if criteria["operation"] not in valid_operations:
                return False
                
            if criteria["operation"] in ["and", "or"]:
                if "criteria" not in criteria or not isinstance(criteria["criteria"], list):
                    return False
                return all(self.validate_criteria(c) for c in criteria["criteria"])
                
            if "field" not in criteria:
                return False
                
            if criteria["operation"] == "between":
                return "values" in criteria and isinstance(criteria["values"], list) and len(criteria["values"]) == 2
            else:
                return "value" in criteria
                
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
