# interface/cli.py
import cmd
import glob
import os
from core.query_preprocessor import QueryPreprocessor
from core.parser import Parser
from utils.logger import logger

class HealthcareCLI(cmd.Cmd):
    intro = 'Welcome to the Healthcare Data Analysis System. Type help or ? to list commands.\n'
    prompt = '(healthcare) '

    def __init__(self):
        super().__init__()
        logger.info("Initializing CLI interface")
        self.preprocessor = QueryPreprocessor()
        self.parser = Parser()
        # Set tests directory relative to project root
        self.tests_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests')
        logger.info(f"Tests directory set to: {self.tests_dir}")

    def do_exit(self, arg):
        """Exit the application."""
        logger.info("Shutting down CLI")
        return True

    def do_test(self, arg):
        """Run test suite."""
        # Get all test files
        test_files = glob.glob(os.path.join(self.tests_dir, "test_*.py"))
        test_names = [os.path.basename(f)[5:-3] for f in test_files]  # Remove 'test_' and '.py'

        if not test_names:
            print("No tests found in tests directory")
            return

        if arg:
            # Try to run specific test
            if arg in test_names:
                self._run_test(arg)
            else:
                print(f"Test '{arg}' not found. Available tests:")
                self._list_tests(test_names)
        else:
            # Show numbered list and ask for selection
            print("Available tests:")
            self._list_tests(test_names)
            
            try:
                choice = input("Enter test number to run (or press Enter to cancel): ")
                if not choice:
                    return
                
                test_index = int(choice) - 1
                if 0 <= test_index < len(test_names):
                    self._run_test(test_names[test_index])
                else:
                    print("Invalid test number")
            except ValueError:
                print("Invalid input - operation cancelled")

    def _list_tests(self, test_names):
        """Helper method to list available tests."""
        for i, name in enumerate(test_names, 1):
            print(f"{i}. {name}")

    def _run_test(self, test_name):
        """Helper method to run a specific test."""
        logger.info(f"Running test: {test_name}")
        try:
            # Import and run the test module
            __import__(f"tests.test_{test_name}")
            logger.info(f"Test {test_name} completed")
        except Exception as e:
            logger.error(f"Error running test {test_name}: {e}")
            print(f"Error running test: {e}")

    def default(self, line):
        """Handle any input that isn't a specific command as a query to the chatbot."""
        try:
            # First stage: Preprocessing
            processed_query, needs_llm = self.preprocessor.process_query(line)
            
            # Second stage: Parsing
            if needs_llm:
                logger.info("Routing query to LLM processing")
                structured_criteria = self.parser.process_with_llm(processed_query)
                # Update preprocessor cache with LLM result
                self.preprocessor.update_cache(line, structured_criteria)
            else:
                logger.info("Using preprocessor structured criteria")
                structured_criteria = processed_query

            # Continue pipeline with structured criteria...
            # (Context, Query Manager, etc. will be added later)
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"Error: {e}")

    def emptyline(self):
        """Do nothing on empty line."""
        pass

    def do_help(self, arg):
        """List available commands."""
        print("\nAvailable commands:")
        print("  test    - Run test suite")
        print("  exit    - Exit the application")
        print("  help    - Show this help message")
        print("\nAny other input will be treated as a query to the system.")
