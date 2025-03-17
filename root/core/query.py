from typing import Dict, List, Any, TYPE_CHECKING
from datetime import datetime
from utils.logger import logger
from utils.logger import setup_logger
logger = setup_logger(__name__)

if TYPE_CHECKING:
    from core.data_manager import DataManager

class Query:
    """
    A class representing a query that can be either simple or complex.
    
    A simple query is a basic comparison operation on a single field, while
    a complex query combines two queries with a logical operator (AND/OR).

    Examples:
        Simple Query:
        >>> simple_query = Query({
        ...     "field": "pacientes.Genero",
        ...     "operation": "equals",
        ...     "value": "Femenino"
        ... })

        Complex Query (AND):
        >>> complex_query = Query({
        ...     "operation": "and",
        ...     "criteria" : [query_1, query_2]
        ... })

    Attributes:
        simple (bool): True if query is a simple comparison, False if it's a complex logical operation
        
    Supported Operations:
        Simple Query Operations:
            - equals
            - not_equals
            - greater_than
            - less_than
        
        Complex Query Operations:
            - and
            - or
    
    Can be constructed either from LLM response format:
        {
            "operation": "and",
            "criteria": [
                {
                    "field": "pacientes.Genero",
                    "operation": "equals",
                    "value": "Femenino"
                },
                {
                    "field": "pacientes.Edad",
                    "operation": "greater_than",
                    "value": 60
                }
            ]
        }
    
    Or using explicit constructors:
        simple_query = Query.create_simple("pacientes.Genero", "equals", "Femenino")
        complex_query = Query.create_complex("and", simple_query1, simple_query2)

    Raises:
        ValueError: If the query dictionary doesn't match either simple or complex format
    """
    
    # Supported operations and their human-readable translations
    OPERATIONS = {
        "equals": "es igual a",
        "not_equals": "no es igual a",
        "greater_than": "es mayor que",
        "less_than": "es menor que",
        "and": "Y",
        "or": "O"
    }
    
    # Valid operations for different data types
    TYPE_OPERATIONS = {
        'int64': ['equals', 'not_equals', 'greater_than', 'less_than'],
        'float64': ['equals', 'not_equals', 'greater_than', 'less_than'],
        'object': ['equals', 'not_equals'],  # string type in pandas
        'datetime64[ns]': ['equals', 'not_equals', 'greater_than', 'less_than']
    }

    def __init__(self, query_dict: dict, is_complex: bool):
        """
        Simple constructor that takes a dictionary and boolean flag.
        
        Args:
            query_dict (dict): The query dictionary
            is_complex (bool): Whether this is a complex query
        """
        self.query_dict = query_dict
        self.is_complex = is_complex

    def get_operation(self) -> str:
        """
        Returns query operation
        """
        operation = self.query_dict.get('operation', '')
        return operation

    def get_query1(self) -> 'Query':
        """
        Returns first query in a complex query
        """
        if not self.is_complex:
            raise ValueError("Attempting get a first query of a simple query, but simple queries don't have a first query")
        
        query_1 = self.query_dict.get('criteria', [{}])[0]
        return Query.create_from_dict(query_1)
    
    def get_query2(self) -> 'Query':
        """
        Returns second query in a complex query
        """
        if not self.is_complex:
            raise ValueError("Attempting get a second query of a simple query, but simple queries don't have a second query")

        query_2 = self.query_dict.get('criteria', [{}])[1]
        return Query.create_from_dict(query_2)
    
    def get_field(self) -> str:
        """
        Returns query field
        """
        if self.is_complex:
            raise ValueError("Attempting get a field of a complex query, but complex queries don't have a field")
        return self.query_dict.get('field', '')
    
    def get_operation(self) -> str:
        """
        Returns query operation
        """
        return self.query_dict.get('operation', '')
    
    def get_value(self) -> any:
        """
        Returns query value
        """
        if self.is_complex:
            raise ValueError("Attempting get a value of a complex query, but complex queries don't have a value")
        return self.query_dict.get('value', '')

    @classmethod
    def from_llm_response(cls, llm_response: str) -> 'Query':
        """
        Creates a Query object from LLM response string.
        
        Args:
            llm_response (str): JSON string from LLM
            
        Returns:
            Query: New Query object
            
        Example:
            >>> response = '''{"query": {
            ...     "operation": "and",
            ...     "criteria": [
            ...         {"field": "pacientes.Genero", "operation": "equals", "value": "Femenino"},
            ...         {"field": "pacientes.Edad", "operation": "greater_than", "value": 60}
            ...     ]
            ... }}'''
            >>> query = Query.from_llm_response(response)
        """
        import json
        
        # Parse JSON string to dictionary
        try:
            response_dict = json.loads(llm_response)
            query_dict = response_dict.get('query', {})
            return cls.create_from_dict(query_dict)        
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in LLM response: {e}")
        except Exception as e:
            raise ValueError(f"Error processing LLM response: {e}")

    @classmethod
    def create_from_dict(cls, query_dict: dict) -> 'Query':
        """
        Creates a Query object from a dictionary.

        Args:
            query_dict (dict): The query dictionary

        Returns:
            Query: New Query object

        Example:
            >>> query_dict = {"field": "pacientes.Genero", "operation": "equals", "value": "Femenino"}
            >>> query = Query._create_from_dict(query_dict)
        """
        # Check if it's a complex query (has 'criteria')
        is_complex = 'criteria' in query_dict
            
        if is_complex:
            query_1 = query_dict['criteria'][0]
            query_2 = query_dict['criteria'][1]
            query_dict = {
                "operation": query_dict['operation'],
                "criteria"  : [query_1, query_2]
            }
            
        return cls(query_dict, is_complex)

    @classmethod
    def create_simple(cls, field: str, operation: str, value: any) -> 'Query':
        """
        Creates a simple Query object.
        
        Args:
            field (str): Field name (e.g., "pacientes.Genero")
            operation (str): Operation type (e.g., "equals")
            value: The value to compare against
            
        Returns:
            Query: New Query object
            
        Example:
            >>> query = Query.create_simple("pacientes.Genero", "equals", "Femenino")
        """
        query_dict = {
            "field": field,
            "operation": operation,
            "value": value
        }
        return cls(query_dict, is_complex=False)

    @classmethod
    def create_complex(cls, operation: str, query1_dict: dict, query2_dict: dict) -> 'Query':
        """
        Creates a complex Query object combining two queries.
        
        Args:
            operation (str): Logical operation ("and" or "or")
            query1_dict (dict): First query dictionary
            query2_dict (dict): Second query dictionary
            
        Returns:
            Query: New Query object
            
        Example:
            >>> gender_query = {"field": "pacientes.Genero", "operation": "equals", "value": "Femenino"}
            >>> age_query = {"field": "pacientes.Edad", "operation": "greater_than", "value": 60}
            >>> query = Query.create_complex("and", gender_query, age_query)
        """
        query_dict = {
            "operation": operation,
            "criteria": [query1_dict, query2_dict]
        }
        return cls(query_dict, is_complex=True)

    def to_human_readable(self) -> str:
        """
        Converts query to human readable string.

        Returns:
            str: Human readable representation of the query
        """
        if not self.query_dict:
            return "Empty query"
            
        if not self.is_complex:
            try:
                return f"{self.query_dict['field']} {self.query_dict['operation']} {self.query_dict['value']}"
            except KeyError:
                return "Invalid simple query format"
        else:
            try:
                criteria = self.query_dict['criteria']
                op = self.query_dict['operation'].upper()
                return f"({criteria[0]['field']} {criteria[0]['operation']} {criteria[0]['value']} {op} " \
                    f"{criteria[1]['field']} {criteria[1]['operation']} {criteria[1]['value']})"
            except (KeyError, IndexError):
                return "Invalid complex query format"
