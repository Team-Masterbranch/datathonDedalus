"""Basic CLI interface for the healthcare data analysis system."""

import cmd
from utils.logger import logger

class HealthcareCLI(cmd.Cmd):
    intro = 'Welcome to the Healthcare Data Analysis System. Type help or ? to list commands.\n'
    prompt = '(healthcare) '

    def __init__(self):
        super().__init__()
        logger.info("Initializing CLI interface")

    def do_exit(self, arg):
        """Exit the application."""
        print("Goodbye!")
        return True
