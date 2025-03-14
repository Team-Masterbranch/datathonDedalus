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
        """
        Run tests with interactive selection.
        Usage: test [file_name] [test_name]
        """
        available_tests = self.app.get_available_tests()
        
        if not available_tests:
            print("No test files found")
            return

        # If no arguments provided, show interactive selection
        if not arg:
            print("\nAvailable test files:")
            for i, test in enumerate(available_tests, 1):
                print(f"{i}. {test}")
            print("0. Run all tests")
            
            try:
                choice = input("\nSelect test file (0-{}): ".format(len(available_tests)))
                if not choice.isdigit() or int(choice) > len(available_tests):
                    print("Invalid selection")
                    return
                
                choice = int(choice)
                if choice == 0:
                    test_file = None
                    test_function = None
                else:
                    test_file = available_tests[choice - 1]
                    
                    # If a test file was selected, show test function selection
                    if test_file:
                        test_functions = self.app.get_test_functions(test_file)
                        
                        if test_functions:
                            print("\nAvailable test functions:")
                            for i, func in enumerate(test_functions, 1):
                                print(f"{i}. {func}")
                            print("0. Run all tests in file")
                            
                            func_choice = input("\nSelect test function (0-{}): ".format(len(test_functions)))
                            if not func_choice.isdigit() or int(func_choice) > len(test_functions):
                                print("Invalid selection")
                                return
                                
                            func_choice = int(func_choice)
                            test_function = test_functions[func_choice - 1] if func_choice > 0 else None
                        else:
                            print("No test functions found in file")
                            return
                            
            except (ValueError, IndexError) as e:
                print(f"Invalid selection: {e}")
                return
        
        # Run selected tests
        result = self.app.run_tests(test_file, test_function)
        
        if result["success"]:
            print("\nTests completed successfully")
        else:
            print(f"\nTests failed: {result.get('error', 'Unknown error')}")


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
