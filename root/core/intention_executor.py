# core/intention_executor.py
from typing import Optional, Dict, Any
from core.intention import FilterTarget, Intention, IntentionType
from core.query_manager import QueryManager
from core.visualizer import Visualizer
from core.data_manager import DataManager
from core.query import Query
from utils.logger import setup_logger

logger = setup_logger(__name__)

class IntentionExecutor:
    def __init__(self, query_manager: QueryManager, visualizer: Visualizer, data_manager: DataManager):
        self.query_manager = query_manager
        self.visualizer = visualizer
        self.data_manager = data_manager
        
    def execute(self, intention: Intention) -> Dict[str, Any]:
        """
        Execute the intention based on its type.
        
        Args:
            intention: Intention object to execute
            
        Returns:
            Dict containing execution results
        """
        logger.debug(f"Entered intention_executor.execute method")
        # Validate intention first
        if not intention.validate(self.data_manager):
            return {
                "success": False,
                "errors": intention.get_validation_errors()
            }

        try:
            if intention.intention_type == IntentionType.NON_FILTER:
                return {
                    "success": True
                }
            
            if intention.intention_type == IntentionType.COHORT_FILTER:
                query = intention.query
                if intention.filter_target == FilterTarget.FULL_DATASET:
                    logger.debug(f"Resetting cohort to full dataset")
                    self.data_manager.reset_to_full()
                logger.debug(f"Cohort shape before query execution: {self.data_manager.get_current_cohort().shape}")
                self.data_manager.apply_query_on_current_cohort(query)
                logger.debug(f"Cohort shape after query execution: {self.data_manager.get_current_cohort().shape}")
                return {
                    "success": True,
                    "type": "cohort_filter",
                }

            elif intention.intention_type == IntentionType.VISUALIZATION:
                # Execute visualization request
                if intention.visualizer_request:
                    viz_paths = self.visualizer.create_visualizations(
                        self.data_manager.get_current_cohort(),
                        [intention.visualizer_request]
                    )
                    return {
                        "success": True,
                        "type": "visualization",
                        "visualization_paths": viz_paths
                    }

            elif intention.intention_type == IntentionType.HELP:
                # Return help information
                return {
                    "success": True,
                    "type": "help",
                    "message": intention.description
                }

            return {
                "success": False,
                "error": f"Unsupported intention type: {intention.intention_type}"
            }

        except Exception as e:
            logger.error(f"Error executing intention: {e}")
            return {
                "success": False,
                "error": str(e)
            }
