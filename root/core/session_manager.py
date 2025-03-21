# core/context_manager.py
import os
import stat
import shutil
from typing import List, Dict
from pathlib import Path
import logging
from utils.config import SESSION_BASE_DIR

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manages conversation context by storing system, user messages and LLM responses.
    """
    def __init__(self):
        self._system_messages: List[Dict[str, str]] = []
        self._user_messages: List[Dict[str, str]] = []
        self._llm_responses: List[Dict[str, str]] = []
        self._full_conversation: List[Dict[str, str]] = []
        self.interactions_counter: int = 0
        self.base_session_dir = SESSION_BASE_DIR
        self.current_interaction_folder: Path = self._get_current_session_dir()
    
    def wipe_session_folder(self) -> None:
        """
        Deletes everything inside the session base directory.
        Handles Windows permission errors.
        """
        
        def handle_remove_readonly(func, path, exc):
            """Handle permission error for read-only files"""
            excvalue = exc[1]
            if func in (os.rmdir, os.remove, os.unlink):
                # Change file permissions
                os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                # Try again
                func(path)
            else:
                raise
        
        try:
            # Delete all contents inside SESSION_BASE_DIR
            for item in SESSION_BASE_DIR.iterdir():
                if item.is_file():
                    item.unlink(missing_ok=True)  # Delete file
                elif item.is_dir():
                    shutil.rmtree(item, onerror=handle_remove_readonly)  # Delete directory and its contents
                    
            logger.debug(f"Wiped all contents from session directory: {SESSION_BASE_DIR}")
            
        except Exception as e:
            logger.error(f"Error wiping session folder: {str(e)}")
            raise


    
    def increment_interaction(self) -> str:
        """
        Increment interaction counter and create new session directory.
        
        Returns:
            Path to the new session directory
        """
        self.interactions_counter += 1
        self.current_interaction_folder = self._get_current_session_dir()
        self.current_interaction_folder.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created session directory: {self.current_interaction_folder}")
        return str(self.current_interaction_folder)
    
    def _get_current_session_dir(self) -> Path:
        """Get path to current session directory."""
        # Use at least 3 digits with zero padding
        return self.base_session_dir / f"{self.interactions_counter:03d}"
    
    def get_current_session_path(self) -> str:
        """Get current session directory path."""
        return str(self.current_interaction_folder)


    def set_system_messages(self, system_messages: List[Dict[str, str]]) -> None:
        """
        Set system messages that will be included in every conversation.
        
        Args:
            system_messages: List of system messages in format [{"role": "system", "content": "message"}]
        """
        if not all(self._validate_message(msg, "system") for msg in system_messages):
            raise ValueError("Invalid system message format")
        self._system_messages = system_messages.copy()
        self._update_full_conversation()

    def get_last_request(self) -> str:
        """
        Get the last user message in the conversation.

        Returns:
            The last user message as a string.
        """
        if self._user_messages:
            return self._user_messages[-1]
        return ""

    def add_user_message(self, user_message: str) -> None:
        """
        Add only a user message to the context.

        Args:
            user_message: The content of user's message
        """        
        user_msg = {"role": "user", "content": user_message}
        self._user_messages.append(user_msg)
        self._update_full_conversation()

    def add_llm_response(self, llm_response: str) -> None:
        """
        Add only a LLM response to the context.

        Args:
            user_message: The content of user's message
        """
        llm_msg = {"role": "user", "content": llm_response}
        self._llm_responses.append(llm_msg)
        self._update_full_conversation()

    def add_exchange(self, user_message: str, llm_response: str) -> None:
        """
        Add a new exchange (user message and LLM response) to the context.

        Args:
            user_message: The content of user's message
            llm_response: The content of LLM's response
        """
        user_msg = {"role": "user", "content": user_message}
        llm_msg = {"role": "assistant", "content": llm_response}

        self._user_messages.append(user_msg)
        self._llm_responses.append(llm_msg)
        self._update_full_conversation()

    def _update_full_conversation(self) -> None:
        """Update the full conversation list with all messages in order."""
        conversation = self._system_messages.copy()
        
        # Add complete exchanges (user + llm pairs)
        complete_exchanges = min(len(self._user_messages), len(self._llm_responses))
        for i in range(complete_exchanges):
            conversation.append(self._user_messages[i])
            conversation.append(self._llm_responses[i])
        
        # Add any remaining user message without response
        if len(self._user_messages) > len(self._llm_responses):
            conversation.append(self._user_messages[-1])
        
        self._full_conversation = conversation

    @staticmethod
    def _validate_message(message: Dict[str, str], expected_role: str) -> bool:
        """
        Validate message format.

        Args:
            message: Message dictionary to validate
            expected_role: Expected role ("system", "user", or "assistant")
        """
        return (isinstance(message, dict) and 
                "role" in message and 
                "content" in message and 
                message["role"] == expected_role)

    def clear_context(self) -> None:
        """Clear conversation history but keep system messages."""
        self._user_messages.clear()
        self._llm_responses.clear()
        self._update_full_conversation()

    def clear_all(self) -> None:
        """Clear all messages including system messages."""
        self._system_messages.clear()
        self.clear_context()

    def get_user_messages(self) -> List[str]:
        """Get all user messages in the conversation."""
        return self._user_messages.copy()
    
    def get_messages(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Get all messages in format ready for LLM.

        Args:
            include_system: Whether to include system messages

        Returns:
            List of messages in format required by LLM
        """
        if include_system:
            return self._full_conversation.copy()
        return [msg for msg in self._full_conversation if msg["role"] != "system"]

    def get_last_n_exchanges(self, n: int, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Get the last n exchanges from the conversation history.

        Args:
            n: Number of exchanges to retrieve
            include_system: Whether to include system messages

        Returns:
            List of messages in format required by LLM
        """
        if n <= 0:
            return []

        messages = self.get_messages(include_system=include_system)
        if not include_system:
            return messages[-2*n:]  # Each exchange has 2 messages
        
        system_count = len(self._system_messages)
        return self._system_messages + messages[system_count:][-2*n:]

    def __len__(self) -> int:
        """Return the number of exchanges (excluding system messages)."""
        return len(self._user_messages)