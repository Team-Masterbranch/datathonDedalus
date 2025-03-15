# core/application.py
from utils.config import (
    DATA_DIR,
    LOG_LEVEL,
)

import pytest
import os
from typing import Dict, Any, Optional, List
from interface.cli import HealthcareCLI
from core.preparser import Preparser
from core.parser import Parser
from core.llm_handler import LLMHandler
from utils.logger import logger
from utils.logger import setup_logger
logger = setup_logger(__name__)
from core.query_manager import QueryManager
from core.data_manager import DataManager


class Application:
    """
    Application service layer that coordinates between different components.
    """
    def __init__(self):
        logger.setLevel(LOG_LEVEL)
        logger.info("Initializing Application")
        self.preprocessor = Preparser()
        self.parser = Parser()
        self.llm_handler = LLMHandler()
        self.data_manager = DataManager(DATA_DIR)
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

    def get_available_tests(self) -> List[str]:
        """
        Get list of available test files.
        
        Returns:
            List of test file names without .py extension
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tests_dir = os.path.join(project_root, 'tests')
        
        if not os.path.exists(tests_dir):
            logger.error(f"Tests directory not found at {tests_dir}")
            return []
            
        test_files = [
            f[5:-3] for f in os.listdir(tests_dir) 
            if f.startswith('test_') and f.endswith('.py')
        ]
        return sorted(test_files)

    def get_test_functions(self, test_file: str) -> List[str]:
        """
        Get list of test functions in a specific test file.
        
        Args:
            test_file: Name of the test file without .py extension
            
        Returns:
            List of test function names
        """
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            test_path = os.path.join(project_root, 'tests', f'test_{test_file}.py')
            
            # Use ast module instead of importing
            import ast
            
            with open(test_path, 'r') as file:
                tree = ast.parse(file.read())
                
            test_functions = [
                node.name for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) 
                and node.name.startswith('test_')
            ]
            
            return sorted(test_functions)
                
        except Exception as e:
            logger.error(f"Error getting test functions: {e}")
            return []

    def run_tests(self, test_file: Optional[str] = None, test_function: Optional[str] = None) -> Dict[str, Any]:
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            tests_dir = os.path.join(project_root, 'tests')

            if not os.path.exists(tests_dir):
                return {"success": False, "error": "Tests directory not found"}

            test_args = ["-v", "-s"]  # Verbose output and no capture
            
            if test_file:
                # Remove .py extension if provided
                test_file = test_file.replace('.py', '')
                # Remove 'test_' prefix if provided
                test_file = test_file[5:] if test_file.startswith('test_') else test_file
                
                test_path = os.path.join(tests_dir, f"test_{test_file}.py")
                if not os.path.exists(test_path):
                    return {"success": False, "error": f"Test file not found: {test_file}"}
                
                if test_function:
                    # Fix -k argument format
                    test_args.extend([test_path, "-k", test_function])
                else:
                    test_args.append(test_path)
            else:
                test_args.append(tests_dir)

            # Convert paths to strings and ensure proper formatting
            test_args = [str(arg) for arg in test_args]
            
            logger.info(f"Running tests with args: {test_args}")
            result = pytest.main(test_args)
            
            return {
                "success": result == 0,
                "exit_code": result,
                "test_file": test_file,
                "test_function": test_function,
                "args_used": test_args
            }

        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_file": test_file,
                "test_function": test_function
            }

