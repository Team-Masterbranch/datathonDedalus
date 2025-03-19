# main.py
"""Main entry point for the healthcare data analysis system."""
from core.application import Application
import tkinter as tk

def main():
    app = Application()
    app.start()  # This will now start the GUI and handle the application loop

if __name__ == "__main__":
    main()
