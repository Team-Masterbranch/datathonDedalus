"""Basic CLI interface for the healthcare data analysis system."""

import cmd
import os
from utils.logger import logger
import importlib
import glob

class HealthcareCLI(cmd.Cmd):
    intro = 'Welcome to the Healthcare Data Analysis System. Type help or ? to list commands.\n'
    prompt = '(healthcare) '

    def __init__(self):
        super().__init__()
        logger.info("Initializing CLI interface")
        self.tests_dir = "tests"

    def do_exit(self, arg):
        """Exit the application."""
        print("Goodbye!")
        return True

    def do_test(self, arg):
        """Run tests from the tests folder.
        Usage: test [test_name]
        If no test_name is provided, shows a list of available tests."""
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
        """Helper method to display numbered list of tests."""
        for i, name in enumerate(test_names, 1):
            print(f"{i}. {name}")

    def _run_test(self, test_name):
        """Helper method to run a specific test."""
        try:
            logger.info(f"Running test: {test_name}")
            module_name = f"tests.test_{test_name}"
            test_module = importlib.import_module(module_name)
            
            # Find all test functions in the module
            test_functions = [
                func for func_name, func in vars(test_module).items()
                if func_name.startswith('test_') and callable(func)
            ]
            
            if test_functions:
                print(f"Running {len(test_functions)} test(s) from {test_name}")
                for test_func in test_functions:
                    test_func()
            else:
                print(f"No test functions found in {module_name}")
                
        except Exception as e:
            logger.error(f"Error running test {test_name}: {e}")
            print(f"Error running test: {e}")
    
