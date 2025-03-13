# core/application.py
from interface.cli import HealthcareCLI
from core.query_preprocessor import QueryPreprocessor
from core.parser import Parser
from core.llm_handler import LLMHandler
from utils.logger import logger

class Application:
    """
    Application service layer that coordinates between different components.
    """
    def __init__(self):
        logger.info("Initializing Application")
        self.preprocessor = QueryPreprocessor()
        self.parser = Parser()
        self.llm_handler = LLMHandler()
        self.cli = HealthcareCLI(self)  # Pass application instance to CLI

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
        
    async def process_user_query(self, query: str) -> str:
        """Main method to process user queries through the pipeline."""
        try:
            processed_query, needs_llm = self.preprocessor.process_query(query)
            
            if needs_llm:
                logger.info("Routing query to LLM processing")
                structured_criteria = self.parser.process_with_llm(processed_query)
                self.preprocessor.update_cache(query, structured_criteria)
            else:
                logger.info("Using preprocessor structured criteria")
                structured_criteria = processed_query

            return structured_criteria
            
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
