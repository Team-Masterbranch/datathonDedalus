# core/intention.py
from enum import Enum
from typing import Optional, List
from core.query import Query
from core.visualizer_request import VisualizerRequest
from utils.logger import setup_logger

logger = setup_logger(__name__)

class IntentionType(Enum):
    COHORT_FILTER = "cohort_filter"
    VISUALIZATION = "visualization"
    HELP = "help"
    UNKNOWN = "unknown"

class FilterTarget(Enum):
    FULL_DATASET = "full_dataset"
    CURRENT_COHORT = "current_cohort"

class Intention:
    def __init__(self, 
                 intention_type: IntentionType,
                 description: str,
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
        
        
        
        
    @classmethod
    def from_llm_response(cls, llm_response: dict) -> 'Intention':
        """Creates Intention object from LLM response dictionary."""
        try:
            # Get intention type and normalize it
            intention_type_str = llm_response.get("intention_type", "")
            if not intention_type_str:
                logger.warning("No intention type provided")
                return cls(IntentionType.UNKNOWN, "No intention type provided")

            # Convert to uppercase and replace spaces/underscores with underscores
            intention_type_str = intention_type_str.upper().replace(' ', '_').replace('-', '_')
            
            # Try to match with enum
            try:
                intention_type = IntentionType[intention_type_str]
            except (KeyError, AttributeError):
                logger.warning(f"Unknown intention type: {intention_type_str}")
                return cls(IntentionType.UNKNOWN, f"Failed to parse intention type: {intention_type_str}")

            description = llm_response.get("description", "")

            if intention_type == IntentionType.COHORT_FILTER:
                # Get and validate filter target
                filter_target_str = llm_response.get("filter_target", "")
                if not filter_target_str:
                    logger.warning("No filter target provided for COHORT_FILTER intention")
                    return cls(IntentionType.UNKNOWN, "No filter target provided")

                # Normalize filter target string
                filter_target_str = filter_target_str.upper().replace(' ', '_').replace('-', '_')
                
                try:
                    filter_target = FilterTarget[filter_target_str]
                except (KeyError, AttributeError):
                    logger.warning(f"Invalid filter target: {filter_target_str}")
                    return cls(IntentionType.UNKNOWN, f"Failed to parse filter target: {filter_target_str}")

                # Get and validate query
                query_data = llm_response.get("query")
                if not query_data:
                    logger.warning("No query data provided for COHORT_FILTER intention")
                    return cls(IntentionType.UNKNOWN, "No query data provided")

                query = Query(query_data)
                
                return cls(
                    intention_type=intention_type,
                    description=description,
                    query=query,
                    filter_target=filter_target
                )

            elif intention_type == IntentionType.VISUALIZATION:
                visualizer_data = llm_response.get("visualizer_request")
                if not visualizer_data:
                    logger.warning("No visualizer request data provided")
                    return cls(IntentionType.UNKNOWN, "No visualizer request data provided")

                # Ensure title is present
                if "title" not in visualizer_data:
                    visualizer_data["title"] = description or "Visualization"

                try:
                    visualizer_request = VisualizerRequest(**visualizer_data)
                except Exception as e:
                    logger.error(f"Error creating visualizer request: {e}")
                    return cls(IntentionType.UNKNOWN, f"Error creating visualizer request: {e}")

                return cls(
                    intention_type=intention_type,
                    description=description,
                    visualizer_request=visualizer_request
                )


            else:  # HELP or UNKNOWN
                return cls(
                    intention_type=intention_type,
                    description=description
                )

        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return cls(IntentionType.UNKNOWN, f"Failed to parse LLM response: {e}")




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
