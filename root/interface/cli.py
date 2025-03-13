# interface/cli.py
import cmd
import glob
import os
from utils.logger import logger

class HealthcareCLI(cmd.Cmd):
    intro = 'Welcome to the Healthcare Data Analysis System. Type help or ? to list commands.\n'
    prompt = '(healthcare) '

    def __init__(self, application):
        super().__init__()
        logger.info("Initializing CLI interface")
        self.app = application  # Store reference to application
        self.tests_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests')

    def do_exit(self, arg):
        """Exit the application."""
        logger.info("Shutting down CLI")
        return True


    def do_test(self, arg):
        """Run test suite."""
        test_files = glob.glob(os.path.join(self.tests_dir, "test_*.py"))
        test_names = [os.path.basename(f)[5:-3] for f in test_files]

        if not test_names:
            print("No tests found in tests directory")
            return

        if arg:
            if arg in test_names:
                self._run_test(arg)
            else:
                print(f"Test '{arg}' not found. Available tests:")
                self._list_tests(test_names)
        else:
            print("Available tests:")
            self._list_tests(test_names)
            self._handle_test_selection(test_names)

    def _list_tests(self, test_names):
        for i, name in enumerate(test_names, 1):
            print(f"{i}. {name}")

    def _handle_test_selection(self, test_names):
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

    def _run_test(self, test_name):
        try:
            self.app.run_test(test_name)
            print(f"Test {test_name} completed successfully")
        except Exception as e:
            print(f"Error running test: {e}")

    def default(self, line):
        """Handle any input that isn't a specific command as a query to the chatbot."""
        try:
            result = self.app.process_user_query(line)
            print(result)
        except Exception as e:
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
