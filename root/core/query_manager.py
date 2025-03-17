# core/query_manager.py
from typing import Dict, Any, Optional
import pandas as pd
from core.data_manager import DataManager
from core.query import Query
from utils.logger import logger
from utils.logger import setup_logger
logger = setup_logger(__name__)

class QueryManager:
    """
    Manages query execution on pandas DataFrames using DataManager.
    Handles cohort filtering and maintains query state.
    """
    def __init__(self, data_manager: DataManager):
        logger.info("Initializing Query Manager")
        self.data_manager = data_manager
        self.last_query: Optional[Query] = None

    async def execute_query(self, 
                        query: Query, 
                        filter_current_cohort: bool = False) -> Dict[str, Any]:
        """
        Execute a query based on Query object.
        
        Args:
            query: Query object containing filter criteria
            filter_current_cohort: If True, apply filter to current cohort,
                                if False, reset cohort before applying filter
        
        Returns:
            Dict containing query results and metadata
        """
        logger.info(f"Executing query with filter_current_cohort={filter_current_cohort}")
        logger.debug(f"Query criteria: {query._query_dict}")

        try:        
            if filter_current_cohort:
                if not query.validate(self.data_manager.get_current_schema()):
                    raise QueryExecutionError("Invalid query structure or field types")
            else:
                if not query.validate(self.data_manager.get_full_schema()):
                    raise QueryExecutionError("Invalid query structure or field types")

            # Get starting DataFrame
            if not filter_current_cohort:
                logger.info("Resetting cohort before applying filter")
                self.data_manager.reset_to_full()
            
            # Apply filter and get results
            filtered_df = self.data_manager.apply_filter(query)
            if filtered_df is None:
                raise QueryExecutionError("Filter operation returned None")
            
            # Prepare result metadata
            result = {
                "criteria": query._query_dict,
                "human_readable": str(query),
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


    def get_last_query(self) -> Optional[Query]:
        """Get the Query object from the last executed query."""
        return self.last_query

    def get_last_query_description(self) -> str:
        """Get human readable description of the last executed query."""
        if self.last_query is None:
            return "No query executed yet"
        return str(self.last_query)

    def get_current_cohort_size(self) -> int:
        """Get the size of the current cohort."""
        return len(self.data_manager.get_current_cohort())


class QueryExecutionError(Exception):
    """Custom exception for query execution errors."""
    pass
