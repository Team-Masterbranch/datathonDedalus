from nicegui import ui
from datetime import datetime
import logging
from typing import Dict, Any
import uuid
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.application import Application
from interface.chat_history import save_chat_session, load_chat_history, get_chat_session
class HealthcareGUI:
    def __init__(self):
        self.app = Application()
        self.current_session = str(uuid.uuid4())
        self.current_messages = []
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        """Create the main UI layout"""
        ui.colors(primary='#4F46E5', secondary='#10B981', accent='#EF4444')
        
        with ui.header().classes('bg-primary text-white'):
            ui.label('Healthcare Analytics Chat').classes('text-2xl font-bold')
            ui.button("New Chat", icon="add", on_click=self.new_chat).classes('ml-auto')
            
        with ui.row().classes('w-full h-screen'):
            # Chat History (1/4 width)
            with ui.column().classes('w-1/4 h-full p-4 bg-gray-100 border-r'):
                self.history_panel = ui.column().classes('w-full h-full')
                
            # Main chat interface (3/4 width)
            with ui.column().classes('w-3/4 h-full p-4'):
                self.setup_chat_interface()

    def setup_chat_interface(self):
        """Main chat components"""
        with ui.column().classes('w-full h-full'):
            # Chat history
            self.chat_container = ui.column().classes('w-full h-[85%] overflow-y-auto p-4 space-y-4')
            
            # Input area
            with ui.row().classes('w-full h-[15%] items-center gap-2 pt-4'):
                self.user_input = ui.input(placeholder='Enter your healthcare query...') \
                    .props('rounded outlined').classes('flex-grow')
                ui.button(icon='send', on_click=self.process_query) \
                    .props('round dense').classes('bg-primary text-white')

    def load_history(self):
        """Load and display chat history"""
        self.history_panel.clear()
        with self.history_panel:
            ui.label('Chat History').classes('text-xl font-bold mb-4')
            sessions = load_chat_history()
            
            if not sessions:
                ui.label('No previous chats').classes('text-gray-500')
                
            for session in sessions:
                with ui.card().classes('w-full p-2 mb-2 cursor-pointer hover:bg-gray-200') \
                    .on('click', lambda _, s=session: self.show_old_chat(s['id'])):
                    ui.label(session['preview']).classes('text-sm font-medium truncate')
                    ui.label(session['timestamp'][:10]).classes('text-xs text-gray-500')

    def new_chat(self):
        """Start a new chat session"""
        self.current_session = str(uuid.uuid4())
        self.current_messages = []
        self.chat_container.clear()
        self.user_input.value = ''

    def show_old_chat(self, session_id: str):
        """Display a previous chat session"""
        session = get_chat_session(session_id)
        if not session:
            return
            
        self.chat_container.clear()
        self.current_messages = session['messages']
        
        with self.chat_container:
            for msg in session['messages']:
                self._add_message(
                    msg['text'], 
                    msg['sender'], 
                    msg.get('color'), 
                    msg['timestamp'],
                    update_current=False
                )

    async def process_query(self):
        """Handle user query submission"""
        query = self.user_input.value.strip()
        if not query:
            return

        try:
            # Save user message
            self.current_messages.append({
                "text": query,
                "sender": "user",
                "timestamp": datetime.now().isoformat()
            })
            self._add_message(query, 'user')
            
            # Process query
            result = await self.app.process_user_query(query)
            
            # Save bot response
            response = f"Processed query: {result.get('message', 'Operation completed')}"
            self.current_messages.append({
                "text": response,
                "sender": "bot",
                "timestamp": datetime.now().isoformat()
            })
            self._add_message(response, 'bot')
            
            # Save session
            save_chat_session(
                self.current_session,
                self.current_messages,
                metadata={
                    "query_count": len(self.current_messages),
                    "last_query": query
                }
            )
            self.load_history()
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.current_messages.append({
                "text": error_msg,
                "sender": "system",
                "timestamp": datetime.now().isoformat(),
                "color": "red"
            })
            self._add_message(error_msg, 'system', 'red')
        finally:
            self.user_input.value = ''

    def _add_message(self, text: str, sender: str, color: str = None, 
                   timestamp: str = None, update_current: bool = True):
        """Add a message to the chat"""
        timestamp = timestamp or datetime.now().isoformat()
        with self.chat_container:
            alignment = 'justify-end' if sender == 'user' else 'justify-start'
            bg_color = 'bg-primary' if sender == 'user' else 'bg-secondary'
            text_color = 'text-white' if sender == 'user' else 'text-gray-800'
            
            if color == 'red':
                bg_color = 'bg-red-100'
                text_color = 'text-red-800'
                
            with ui.row().classes(f'w-full {alignment}'):
                with ui.card().classes(f'{bg_color} {text_color} max-w-[75%] rounded-2xl p-4'):
                    ui.label(text).classes('text-sm break-words')
                    ui.label(timestamp[11:19]).classes('text-xs opacity-70 mt-1')
        
        if update_current:
            ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

def main():
    # Create the GUI instance
    gui = HealthcareGUI()
    
    # Run the NiceGUI app
    ui.run(
        title='Healthcare Analytics', 
        dark=False, 
        reload=False, 
        port=8080
    )
if __name__ == "__main__":
    main()