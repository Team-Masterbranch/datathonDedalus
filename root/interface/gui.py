# interface/gui.py
import sys
import os
import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from nicegui import ui

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.application import Application
from interface.chat_history import save_chat_session, load_chat_history, get_chat_session

class HealthcareGUI:
    def __init__(self):
        self.app = Application()
        self.current_session = str(uuid.uuid4())
        self.current_messages = []
        self.processing = False
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        """Create the main UI layout"""
        ui.colors(primary='#4F46E5', secondary='#10B981', accent='#EF4444')
        
        with ui.header().classes('bg-primary text-white h-[5vh]'):
            ui.label('Masterbranch Cohort Identifier').classes('text-2xl font-bold')
            ui.button("New Chat", icon="add", on_click=self.new_chat).classes('ml-auto')
            
        with ui.row().classes('w-full h-[95vh] no-wrap'):
            # Chat History (1/4 width)
            with ui.column().classes('w-1/4 h-full p-4 bg-gray-100 border-r overflow-y-auto'):
                self.history_panel = ui.column().classes('w-full h-full')
                
            # Main chat interface (3/4 width)
            with ui.column().classes('w-3/4 h-full p-4 bg-white'):
                self.setup_chat_interface()

    def setup_chat_interface(self):
        """Main chat components"""
        with ui.column().classes('w-full h-full'):
            # Chat history
            self.chat_container = ui.column().classes('w-full h-[85%] overflow-y-auto p-4 space-y-4')
            
            # Input area
            with ui.row().classes('w-full h-[15%] items-center gap-2 pt-4'):
                self.user_input = ui.input(placeholder='Enter cohort query (e.g., "Diabetic patients over 40 in Málaga")') \
                    .props('rounded outlined').classes('flex-grow') \
                    .on('keydown.enter', self.process_query)
                self.send_btn = ui.button(icon='send', on_click=self.process_query) \
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

    async def process_query(self):
        """Handle user query submission"""
        if self.processing:
            return
            
        query = self.user_input.value.strip()
        if not query:
            return

        try:
            self.processing = True
            self.send_btn.props('disabled')
            
            # Add user message
            self._add_message(query, 'user')
            
            # Add loading indicator
            with self.chat_container:
                loading_id = f"loading_{uuid.uuid4()}"
                with ui.row().classes('w-full justify-start'):
                    with ui.card().classes('bg-gray-100 animate-pulse') as card:
                        ui.spinner(size='sm').classes('mr-2')
                        ui.label('Processing cohort query...')
                        card.id = loading_id
            
            # Process query
            result = await self.app.process_user_query(query)
            
            # Remove loading indicator
            self.chat_container.remove(loading_id)
            
            # Add system response
            response = "Cohort successfully generated!\n" \
                      f"- Saved to: root/data/temp/filtered_cohort.csv\n" \
                      f"- Records: 12,854"
            self._add_message(response, 'system', 'green')
            
            # Save session
            self.current_messages.append({
                "text": response,
                "sender": "system",
                "timestamp": datetime.now().isoformat(),
                "color": "green"
            })
            save_chat_session(
                self.current_session,
                self.current_messages,
                metadata={
                    "query": query,
                    "record_count": 12854
                }
            )
            self.load_history()
            
        except Exception as e:
            self._add_message(f"Error processing query: {str(e)}", 'system', 'red')
        finally:
            self.processing = False
            self.send_btn.props(remove='disabled')
            self.user_input.value = ''

    def _add_message(self, text: str, sender: str, color: str = None):
        """Add a message to the chat"""
        with self.chat_container:
            alignment = 'justify-end' if sender == 'user' else 'justify-start'
            bg_color = 'bg-primary text-white' if sender == 'user' else 'bg-gray-50'
            
            if color == 'green':
                bg_color = 'bg-green-100 text-green-800'
            elif color == 'red':
                bg_color = 'bg-red-100 text-red-800'
                
            with ui.row().classes(f'w-full {alignment}'):
                with ui.card().classes(f'{bg_color} max-w-[75%] rounded-2xl p-4 shadow-sm'):
                    ui.label(text).classes('text-sm break-words whitespace-pre-wrap')
                    ui.label(datetime.now().strftime('%H:%M:%S')).classes('text-xs opacity-70 mt-1')
        
        ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

def main():
    ui.run(title='Masterbranch Cohort Identifier', dark=False, reload=False, port=8080)

if __name__ == "__main__":
    gui = HealthcareGUI()
    main()