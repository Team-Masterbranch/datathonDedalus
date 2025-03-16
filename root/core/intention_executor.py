# core/intention_executor.py
from typing import Optional, Dict, Any
from core.intention import FilterTarget, Intention, IntentionType
from core.query_manager import QueryManager
from core.visualizer import Visualizer
from core.data_manager import DataManager
from utils.logger import setup_logger

logger = setup_logger(__name__)

class IntentionExecutor:
    def __init__(self, query_manager: QueryManager, visualizer: Visualizer, data_manager: DataManager):
        self.query_manager = query_manager
        self.visualizer = visualizer
        self.data_manager = data_manager

    async def execute(self, intention: Intention) -> Dict[str, Any]:
        """
        Execute the intention based on its type.
        
        Args:
            intention: Intention object to execute
            
        Returns:
            Dict containing execution results
        """
        # Validate intention first
        if not intention.validate(self.data_manager):
            return {
                "success": False,
                "errors": intention.get_validation_errors()
            }

        try:
            if intention.intention_type == IntentionType.COHORT_FILTER:
                # Execute query through query manager
                result = await self.query_manager.execute_query(
                    intention.query,
                    filter_current_cohort=(intention.filter_target == FilterTarget.CURRENT_COHORT)
                )
                return {
                    "success": True,
                    "type": "cohort_filter",
                    "result": result
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
