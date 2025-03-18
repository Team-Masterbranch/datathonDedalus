# core/application.py
from core.context_manager import ContextManager
from core.intention import Intention, IntentionType
from core.intention_executor import IntentionExecutor
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
from core.result_analyzer import ResultAnalyzer
from core.visualizer import Visualizer


class Application:
    """
    Application service layer that coordinates between different components.
    """
    def __init__(self):
        logger.setLevel(LOG_LEVEL)
        logger.info("Initializing Application")
        self.preparser = Preparser()
        self.llm_handler = LLMHandler()
        self.data_manager = DataManager(DATA_DIR)
        self.parser = Parser(self.llm_handler, self.data_manager)
        self.query_manager = QueryManager(self.data_manager)
        self.cli = HealthcareCLI(self)
        self.result_analyzer = ResultAnalyzer()
        self.visualizer = Visualizer()
        self.context_manager = ContextManager()
        self.intention_executer = IntentionExecutor(self.query_manager, self.visualizer, self.data_manager)
        
    def start(self):
        """Start the application and its interface."""
        logger.info("Starting application")
        self.visualizer.clear_output_directory()
        
        # Load existing or newly created cache to preparser
        cache_path = "root/data/cache.json"
        if not os.path.exists(cache_path):
            logger.info("Cache file not found. Creating new cache.")
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                # Save empty cache
                self.preparser.save_cache_to_file(cache_path)
            except IOError as e:
                logger.error(f"Failed to create cache file: {e}")
                raise
        try:
            self.preparser.load_cache_from_file(cache_path)
        except IOError as e:
            logger.error(f"Failed to load cache: {e}")
            raise
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
        self.visualizer.clear_output_directory()
        self.preparser.save_cache_to_file("root/data/cache.json")
        logger.info("Shutting down application")
        # Add cleanup code here if needed
        
    async def process_user_query(self, user_input: str, filter_current_cohort: bool = False) -> Dict[str, Any]:
        """
        Process and execute a user query.
        
        Args:
            query: The user's query string
            filter_current_cohort: Whether to filter current cohort or start new search
        """
        try:
            self.context_manager.add_user_message(user_input)
            # Preprocessing and parsing (as before)
            preparse_result, needs_llm = self.preparser.preparse_user_input(user_input)
            
            if needs_llm:
                message = self.context_manager.get_last_request()
                # user_messages = self.context_manager.get_user_messages()
                user_intention = self.parser.process_single_message(message)
                # user_intention = self.parser.process_message_list(user_messages)
                self.preparser.update_cache(user_input, user_intention)
            else:
                user_intention = preparse_result
            
            if user_intention.intention_type == IntentionType.HELP:
                # Print help from \root\prompts\help_message.txt
                self.text_file_output("root/prompts/help_message.txt")
                
            elif user_intention.intention_type == IntentionType.UNKNOWN:
                # Print help from root\prompts\unknown_intention_message.txt
                self.text_file_output("root/prompts/unknown_intention_message.txt")
                
            self.intention_executer.execute(user_intention)
            print("Cohort shape in application")
            print(self.data_manager.get_current_cohort().shape)
            # print(self.data_manager.get_readable_schema_current_cohort())
            self.data_manager.save_current_cohort()
            
            self.shutdown
            
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
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            test_file = test_file if test_file.startswith('test_') else f'test_{test_file}'
            test_path = os.path.join(project_root, 'tests', f'{test_file}.py')
            
            import ast
            
            with open(test_path, 'r') as file:
                tree = ast.parse(file.read())
                
            test_functions = [
                node.name for node in ast.walk(tree)
                if (isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef))
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

    def text_output(self, message: str, message_type: str = "info") -> None:
        """
        Output text messages to console (and later to GUI).
        
        Args:
            message (str): The message to output
            message_type (str): Type of message. Can be "info", "error", "warning", or "success"
                            Used for different styling in future GUI implementation
        """
        # Dictionary of prefix symbols for different message types
        prefix_dict = {
            "info": "ℹ️",
            "error": "❌",
            "warning": "⚠️",
            "success": "✅"
        }
        
        # Get prefix (default to info if message_type is not recognized)
        prefix = prefix_dict.get(message_type.lower(), prefix_dict["info"])
        
        # For now, just print to console
        print(f"{prefix} {message}")
        
        # Log the message with appropriate level
        if message_type.lower() == "error":
            logger.error(message)
        elif message_type.lower() == "warning":
            logger.warning(message)
        else:
            logger.info(message)

    def text_file_output(self, file_path: str, message_type: str = "info") -> None:
        """
        Print the contents of a text file using text_output method
        
        Args:
            file_path (str): Path to the text file
            message_type (str): Type of message for formatting (default: "info")
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_output(content, message_type)
        except FileNotFoundError:
            self.text_output(f"File not found at {file_path}", "error")
        except Exception as e:
            self.text_output(f"Error reading file: {str(e)}", "error")
