# core/query_manager.py
from typing import Dict, Any
import pandas as pd
from core.data_manager import DataManager
from utils.logger import logger

class QueryManager:
    """
    Manages query execution on pandas DataFrames using DataManager.
    Handles cohort filtering and maintains query state.
    """
    def __init__(self, data_manager: DataManager):
        logger.info("Initializing Query Manager")
        self.data_manager = data_manager
        self.last_query: Dict[str, Any] = {}

    async def execute_query(self, 
                          structured_criteria: Dict[str, Any], 
                          filter_current_cohort: bool = False) -> Dict[str, Any]:
        """
        Execute a query based on structured criteria.
        
        Args:
            structured_criteria: Dictionary containing parsed query parameters
            filter_current_cohort: If True, apply filter to current cohort,
                                 if False, reset cohort before applying filter
        
        Returns:
            Dict containing query results and metadata
        """
        logger.info(f"Executing query with filter_current_cohort={filter_current_cohort}")
        logger.debug(f"Query criteria: {structured_criteria}")

        try:
            # Store query for reference
            self.last_query = structured_criteria

            # Get starting DataFrame
            if not filter_current_cohort:
                logger.info("Resetting cohort before applying filter")
                self.data_manager.reset_cohort()
            
            # Apply filter and get results
            filtered_df = self.data_manager.apply_filter(structured_criteria)
            
            # Prepare result metadata
            result = {
                "criteria": structured_criteria,
                "row_count": len(filtered_df),
                "filtered_from": len(self.data_manager.get_current_cohort()),
                "columns": list(filtered_df.columns),
                "filter_type": "current_cohort" if filter_current_cohort else "new_search"
            }

            logger.info(f"Query executed successfully. Found {result['row_count']} records")
            return result

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise QueryExecutionError(f"Query execution failed: {str(e)}")

    def get_last_query(self) -> Dict[str, Any]:
        """Get the criteria from the last executed query."""
        return self.last_query

    def get_current_cohort_size(self) -> int:
        """Get the size of the current cohort."""
        return len(self.data_manager.get_current_cohort())


class QueryExecutionError(Exception):
    """Custom exception for query execution errors."""
    pass
