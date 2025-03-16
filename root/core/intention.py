# core/intention.py
from enum import Enum
import json
from typing import Any, Dict, Optional, List
from core.query import Query
from core.visualizer_request import VisualizerRequest
from utils.logger import setup_logger

logger = setup_logger(__name__)

class IntentionType(Enum):
    COHORT_FILTER = "COHORT_FILTER"
    VISUALIZATION = "VISUALIZATION"
    HELP = "HELP"
    UNKNOWN = "UNKNOWN"

class FilterTarget(Enum):
    FULL_DATASET = "FULL_DATASET"
    CURRENT_COHORT = "CURRENT_COHORT"

class Intention:
    def __init__(self, 
                 intention_type: IntentionType,
                 description: Optional[str] = '',
                 query: Optional[Query] = None,
                 filter_target: Optional[FilterTarget] = None,
                 visualizer_request: Optional[VisualizerRequest] = None):
        self.intention_type = intention_type
        self.description = description
        self.query = query
        self.filter_target = filter_target
        self.visualizer_request = visualizer_request
        self.validation_errors: List[str] = []



    def validate(self, data_manager = None) -> bool:
        """Validates intention based on its type."""
        self.validation_errors = []

        try:
            if not self.description:
                self.validation_errors.append("Description is required")

            if self.intention_type == IntentionType.COHORT_FILTER:
                if not self.query:
                    self.validation_errors.append("Query is required for COHORT_FILTER intention")
                if not self.filter_target:
                    self.validation_errors.append("Filter target is required")
                elif not isinstance(self.filter_target, FilterTarget):
                    self.validation_errors.append("Filter target must be a valid FilterTarget enum value")
                
                # Validate query against schema if data_manager is provided
                if self.query and isinstance(self.filter_target, FilterTarget) and data_manager:
                    schema = (data_manager.get_full_schema() 
                            if self.filter_target == FilterTarget.FULL_DATASET 
                            else data_manager.get_current_schema())
                    
                    if not schema:
                        self.validation_errors.append("Could not get schema from data manager")
                    elif not self.query.validate(schema):
                        self.validation_errors.append("Invalid query for the given schema")

            elif self.intention_type == IntentionType.VISUALIZATION:
                if not self.visualizer_request:
                    self.validation_errors.append("VisualizerRequest is required for VISUALIZATION intention")
                elif data_manager:
                    # Get available columns from data manager's current schema
                    schema = data_manager.get_current_schema()
                    if schema:
                        available_columns = list(schema.keys())
                        if self.visualizer_request.y_column == "count":
                            available_columns.append("count")
                        if not self.visualizer_request.validate(available_columns):
                            self.validation_errors.append("Invalid visualizer request for current schema")
                    else:
                        self.validation_errors.append("Could not get schema from data manager")
                else:
                    # If no data_manager provided, skip column validation
                    return True

            return len(self.validation_errors) == 0

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            self.validation_errors.append(f"Unexpected validation error: {str(e)}")
            return False
    
    
    @staticmethod
    def _parse_query_dict(query_dict: Dict[str, Any]) -> Query:
        """
        Parse a query dictionary from LLM response.
        
        Simple query format from LLM:
        {
            "field": "pacientes.Edad",
            "operation": "greater_than",
            "value": 65
        }
        
        Complex query format from LLM:
        {
            "operation": "and",
            "criteria": [
                {
                    "field": "Descripcion",
                    "operation": "equals",
                    "value": "Diabetes"
                },
                {
                    "field": "Edad",
                    "operation": "greater_than",
                    "value": 31
                }
            ]
        }
        """
        # If it's a simple query (no nested conditions)
        if "field" in query_dict:
            # Keep the same structure as received from LLM
            return Query(query_dict)
        
        # If it's a complex query with AND/OR operators
        if "operation" in query_dict and "criteria" in query_dict:
            return Query({
                "operation": query_dict["operation"],
                "criteria": [
                    Intention._parse_query_dict(cond) for cond in query_dict["criteria"]
                ]
            })
        
        raise ValueError("Invalid query format")
    
    
    @classmethod
    def from_llm_response(cls, llm_response: str) -> 'Intention':
        """
        Create an Intention object from LLM response string.
        Handles both simple and complex nested queries.
        
        Expected format:
        {
            "intention_type": "COHORT_FILTER",
            "description": "Filtrar pacientes con diabetes mayores de 31 años",
            "query": {
                "operation": "and",
                "criteria": [
                    {
                        "field": "Descripcion",
                        "operation": "equals",
                        "value": "Diabetes"
                    },
                    {
                        "field": "Edad",
                        "operation": "greater_than",
                        "value": 31
                    }
                ]
            },
            "filter_target": "FULL_DATASET"
        }
        """
        try:
            # Parse the JSON string into a dictionary
            intention_dict = json.loads(llm_response)
            
            # Parse the query structure
            query_dict = intention_dict.get('query', {})
            query = cls._parse_query_dict(query_dict)
            
            # Create Intention object
            return cls(
                intention_type=IntentionType(intention_dict.get('intention_type')),
                query=query,
                filter_target=FilterTarget(intention_dict.get('filter_target', 'FULL_DATASET'))
            )
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in LLM response: {e}")
        except KeyError as e:
            raise ValueError(f"Missing required field in LLM response: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid value in LLM response: {e}")

        
    def get_validation_errors(self) -> List[str]:
        """Returns list of validation errors."""
        return self.validation_errors

    def __str__(self) -> str:
        """Returns string representation of intention."""
        base_str = f"Intention(type={self.intention_type.value}, description='{self.description}'"
        
        if self.intention_type == IntentionType.COHORT_FILTER:
            base_str += f", target='{self.filter_target.value if self.filter_target else None}'"
            if self.query:
                base_str += f", query={str(self.query)}"
                
        elif self.intention_type == IntentionType.VISUALIZATION:
            if self.visualizer_request:
                base_str += f", visualization={str(self.visualizer_request)}"
                
        base_str += ")"
        return base_str
