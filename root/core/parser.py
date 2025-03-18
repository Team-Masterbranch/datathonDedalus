# core/parser.py
from typing import List, Optional, Dict, Any
from pathlib import Path
from core.intention import Intention
from core.data_manager import DataManager
from core.llm_handler import LLMHandler
from core.query import Query
from utils.logger import setup_logger
logger = setup_logger(__name__)

class Parser:
    """
    Parser module that handles:
    1. Receiving preprocessed queries
    2. Interacting with LLM when needed
    3. Converting responses to Query objects
    4. Updating preprocessor cache
    """

    def __init__(self, llm_handler: LLMHandler, data_manager: DataManager):
        self.llm_handler = llm_handler
        self.data_manager = data_manager
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        logger.info("Initializing Parser")

    def process_with_llm(self, query: str) -> Query:
        """
        Process query through LLM to get structured Query object.
        
        Args:
            query: Raw or preprocessed query string
            
        Returns:
            Query: Structured Query object for the Query Manager
            
        Raises:
            ValueError: If LLM response cannot be converted to valid Query
        """
        logger.info(f"Processing query with LLM: {query}")
        
        # Get structured criteria from LLM
        structured_criteria = self._get_llm_response(query)
        
        # Validate and format the response
        formatted_criteria = self._format_criteria(structured_criteria)
        
        # Create Query object
        try:
            query_obj = Query(formatted_criteria)
            logger.info(f"Generated Query object: {query_obj}")
            return query_obj
        except Exception as e:
            logger.error(f"Failed to create Query object: {e}")
            raise ValueError(f"Invalid query structure from LLM: {e}")

    def _get_llm_response(self, query: str) -> Dict[str, Any]:
        """
        Stub method for LLM interaction that returns meaningful mock criteria.
        Will be replaced with actual LLM call later.
        
        Args:
            query: User query string
            
        Returns:
            dict: Query structure for creating Query object
        """
        logger.info("Getting LLM response")
        
        # Mock different response patterns based on query keywords
        if "edad" in query.lower():
            return {
                "field": "Edad",
                "operation": "greater_than",
                "value": 40
            }
        elif "condicion" in query.lower():
            return {
                "operation": "or",
                "criteria": [
                    {
                        "field": "Descripcion",
                        "operation": "equals",
                        "value": "Diabetes tipo 2"
                    },
                    {
                        "field": "Descripcion",
                        "operation": "equals",
                        "value": "Hipertensión"
                    }
                ]
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
                        "field": "Descripcion",
                        "operation": "equals",
                        "value": "Diabetes tipo 2"
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

    def _format_criteria(self, llm_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format and validate LLM response into proper criteria structure.
        
        Args:
            llm_response: Dictionary containing filtering criteria
            
        Returns:
            dict: Formatted and validated criteria
            
        Raises:
            ValueError: If criteria structure is invalid
        """
        logger.info("Formatting LLM response into criteria")
        
        if not self.validate_criteria(llm_response):
            raise ValueError(f"Invalid criteria structure: {llm_response}")
            
        return llm_response

    def validate_criteria(self, criteria: Dict[str, Any]) -> bool:
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


    def process_single_message(self, message: Dict[str, str]) -> Intention:
        """
        Process message through LLM and return structured Intention object.
        
        Args:
            message: Dictionary containing message with format {"role": str, "content": str}
            
        Returns:
            Intention: Structured Intention object
            
        Raises:
            ValueError: If message format is invalid or LLM response cannot be parsed
        """
        try:
            # Get current schema
            schema = self.data_manager.get_full_schema()
            formatted_schema = self._format_schema(schema)
            
            # Create system messages with prompts and schema
            system_messages = [
                {
                    "role": "system",
                    "content": self._load_prompt("system_intentions.txt")
                },
                {
                    "role": "system",
                    "content": f"{self._load_prompt('schema_description.txt')}\n{formatted_schema}"
                },
                {
                    "role": "system",
                    "content": self._load_prompt("system_examples.txt")
                }
            ]

            # Combine system messages with user message
            messages = system_messages + [message]
            
            # Get LLM response using llm_handler
            llm_response = self.llm_handler.send_chat_request(messages)
            
            # Convert LLM response to Intention object
            intention = Intention.from_llm_response(llm_response)
            logger.info(f"Generated Intention object: {intention}")
            
            return intention

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise

    def process_message_list(self, messages: List[Dict[str, str]]) -> Intention:
        """
        Process multiple messages through LLM and return structured Intention object.
        Similar to process_message but handles a list of messages for context.
        
        Args:
            messages: List of dictionaries containing messages with format [{"role": str, "content": str}, ...]
                
        Returns:
            Intention: Structured Intention object
                
        Raises:
            ValueError: If message format is invalid or LLM response cannot be parsed
        """
        try:
            # Get current schema
            schema = self.data_manager.get_full_schema()
            formatted_schema = self._format_schema(schema)
            
            # Create system messages with prompts and schema
            system_messages = [
                {
                    "role": "system",
                    "content": self._load_prompt("system_intentions.txt")
                },
                {
                    "role": "system",
                    "content": f"{self._load_prompt('schema_description.txt')}\n{formatted_schema}"
                },
                {
                    "role": "system",
                    "content": self._load_prompt("system_examples.txt")
                }
            ]

            # Combine system messages with user messages
            all_messages = system_messages + messages
            
            # Get LLM response using llm_handler
            llm_response = self.llm_handler.send_chat_request(all_messages)
            
            # Convert LLM response to Intention object
            intention = Intention.from_llm_response(llm_response)
            logger.info(f"Generated Intention object from multiple messages: {intention}")
            
            return intention

        except Exception as e:
            logger.error(f"Error processing messages: {e}")
            raise


    def _format_schema(self, schema: dict) -> str:
        """Format schema into a readable string"""
        return '\n'.join([f"{col}: {dtype}" for col, dtype in schema.items()])
    
    def _load_prompt(self, filename: str) -> str:
        """Load prompt from file"""
        with open(self.prompts_dir / filename, 'r', encoding='utf-8') as f:
            return f.read().strip()