# core/application.py
from typing import Dict, Any
from interface.cli import HealthcareCLI
from core.query_preprocessor import QueryPreprocessor
from core.parser import Parser
from core.llm_handler import LLMHandler
from utils.logger import logger
from core.query_manager import QueryManager
from core.data_manager import DataManager


class Application:
    """
    Application service layer that coordinates between different components.
    """
    def __init__(self):
        logger.info("Initializing Application")
        self.preprocessor = QueryPreprocessor()
        self.parser = Parser()
        self.llm_handler = LLMHandler()
        
        # Initialize DataManager first
        self.data_manager = DataManager('data')
        # Pass DataManager to QueryManager
        self.query_manager = QueryManager(self.data_manager)
        
        self.cli = HealthcareCLI(self)
        
    def start(self):
        """Start the application and its interface."""
        logger.info("Starting application")
        try:
            self.cli.cmdloop()
        except KeyboardInterrupt:
            logger.info("Application shutdown initiated by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            self.shutdown()

    def shutdown(self):
        """Cleanup and shutdown application."""
        logger.info("Shutting down application")
        # Add cleanup code here if needed
        
    async def process_user_query(self, query: str, filter_current_cohort: bool = False) -> Dict[str, Any]:
        """
        Process and execute a user query.
        
        Args:
            query: The user's query string
            filter_current_cohort: Whether to filter current cohort or start new search
        """
        try:
            # Preprocessing and parsing (as before)
            processed_query, needs_llm = self.preprocessor.process_query(query)
            
            if needs_llm:
                structured_criteria = self.parser.process_with_llm(processed_query)
                self.preprocessor.update_cache(query, structured_criteria)
            else:
                structured_criteria = processed_query

            # Execute query using QueryManager with cohort parameter
            result = await self.query_manager.execute_query(
                structured_criteria, 
                filter_current_cohort=filter_current_cohort
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise



    def run_test(self, test_name: str) -> None:
        """Run a specific test."""
        logger.info(f"Running test: {test_name}")
        try:
            __import__(f"tests.test_{test_name}")
            logger.info(f"Test {test_name} completed")
        except Exception as e:
            logger.error(f"Error running test {test_name}: {e}")
            raise
