from typing import Callable, Optional, List
import tkinter as tk
from tkinter import ttk
import asyncio
from dataclasses import dataclass
from enum import Enum

class MessageType(Enum):
    """Types of messages that can be displayed in chat"""
    USER = "user"
    SYSTEM = "system"
    ERROR = "error"

@dataclass
class HistoryEntry:
    """Represents a single entry in query history"""
    query: str
    timestamp: str
    result_available: bool

class GUI:
    """
    Main GUI class that handles all visual elements and user interactions.
    Provides interface for application to update visual state.
    """
    
    def __init__(self, on_query_callback: Callable[[str], None]):
        """
        Initialize GUI with callback for query processing.
        
        Args:
            on_query_callback: Function to be called when user submits query
        """
        pass

    async def run(self) -> None:
        """
        Start the GUI event loop.
        Should be called by application to begin GUI operation.
        """
        pass

    def display_message(self, text: str, msg_type: MessageType = MessageType.SYSTEM) -> None:
        """
        Display a new message from chatbot in chat area.
        
        Args:
            text: Message text to display
            msg_type: Type of message (user/system/error)
        """
        pass

    def set_processing_state(self, is_processing: bool) -> None:
        """
        Show/hide processing indicator and disable/enable input.
        
        Args:
            is_processing: True if application is processing query
        """
        pass

    def add_history_entry(self, entry: HistoryEntry) -> None:
        """
        Add new entry to query history panel.
        
        Args:
            entry: HistoryEntry object containing query details
        """
        pass

    def update_cohort_info(self, total_records: int, active_filters: List[str]) -> None:
        """
        Update cohort statistics panel.
        
        Args:
            total_records: Number of records in current cohort
            active_filters: List of active filter descriptions
        """
        pass

    def show_error(self, message: str) -> None:
        """
        Display error message to user.
        
        Args:
            message: Error message to display
        """
        pass

    def _setup_layout(self) -> None:
        """
        Private method to initialize GUI layout.
        Creates all necessary widgets and arranges them.
        """
        pass

    def _handle_query_submit(self) -> None:
        """
        Private method to handle query submission.
        Gets input text and calls callback function.
        """
        pass

    def _create_chat_area(self) -> None:
        """
        Private method to create chat display area.
        """
        pass

    def _create_input_area(self) -> None:
        """
        Private method to create query input area.
        """
        pass

    def _create_history_panel(self) -> None:
        """
        Private method to create history panel.
        """
        pass

    def _create_cohort_panel(self) -> None:
        """
        Private method to create cohort information panel.
        """
        pass
    
"""
# -------------------------------------------------------------------
# ======================= Usage Pattern: ===========================
# -------------------------------------------------------------------
# In application.py
async def main():
    gui = GUI(on_query_callback=process_query)
    await gui.run()

# Example updates
gui.display_message("Processing your query...")
gui.set_processing_state(True)
gui.add_history_entry(HistoryEntry("show all patients", "12:00", True))
gui.update_cohort_info(100, ["age > 50", "gender = F"])


# -------------------------------------------------------------------
# ======================= Example workflow: =========================
# -------------------------------------------------------------------

# GUI Class (interface/webui.py)
class GUI:
    def __init__(self, on_query_callback: Callable[[str], None]):
        self.on_query_callback = on_query_callback
        self.input_field = None  # Will be tkinter Entry widget
        self._setup_layout()

    def _handle_query_submit(self) -> None:
        # 1. Gets called when user hits Enter or clicks Submit
        query_text = self.input_field.get()
        # 2. Displays user message in chat
        self.display_message(query_text, MessageType.USER)
        # 3. Disables input during processing
        self.set_processing_state(True)
        # 4. Calls the callback provided by application
        self.on_query_callback(query_text)

# Application (application.py)
class Application:
    def __init__(self):
        self.data_manager = DataManager()
        self.query_manager = QueryManager()
        self.gui = GUI(on_query_callback=self.process_query)

    def process_query(self, query_text: str):
        try:
            # 5. Process the query
            result = self.query_manager.process(query_text)
            # 6. Update GUI with result
            self.gui.display_message(result)
        finally:
            # 7. Re-enable input
            self.gui.set_processing_state(False)

    async def run(self):
        # 0. Start the application
        await self.gui.run()

"""