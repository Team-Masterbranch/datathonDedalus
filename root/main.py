"""Main entry point for the healthcare data analysis system."""

from interface.cli import HealthcareCLI

def main():
    cli = HealthcareCLI()
    cli.cmdloop()

if __name__ == "__main__":
    main()
