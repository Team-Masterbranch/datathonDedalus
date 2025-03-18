#interface/gui.py
import sys
import os
import logging
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any
from nicegui import ui

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.application import Application
from interface.chat_history import save_chat_session, load_chat_history, get_chat_session

logger = logging.getLogger(__name__)

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
        
        with ui.header().classes('bg-primary text-white h-[5vh] items-center'):
            ui.label('Masterbranch Cohort Identifier').classes('text-2xl font-bold')
            with ui.row().classes('ml-auto gap-2'):
                ui.button("New Chat", icon="add", on_click=self.new_chat)
                ui.button(icon="history", on_click=self.load_history).tooltip("Refresh History")
                
        with ui.row().classes('w-full h-[95vh] no-wrap'):
            # Chat History (1/4 width)
            with ui.column().classes('w-1/4 h-full p-4 bg-gray-100 border-r overflow-y-auto'):
                self.history_panel = ui.column().classes('w-full h-full gap-2')
                
            # Main chat interface (3/4 width)
            with ui.column().classes('w-3/4 h-full p-4 bg-white'):
                self.setup_chat_interface()

    def setup_chat_interface(self):
        """Main chat components"""
        with ui.column().classes('w-full h-full gap-4'):
            # Chat history
            self.chat_container = ui.column().classes('w-full h-[85%] overflow-y-auto p-4 space-y-4')
            
            # Input area
            with ui.row().classes('w-full h-[15%] items-center gap-2 p-4 border-t'):
                self.user_input = ui.input(placeholder='Enter cohort query...') \
                    .props('rounded outlined') \
                    .classes('flex-grow') \
                    .on('keydown.enter', self.process_query)
                
                self.send_btn = ui.button(icon='send', on_click=self.process_query) \
                    .props('round dense') \
                    .classes('bg-primary text-white')

    async def process_query(self):
        """Handle user query submission"""
        if self.processing:
            return
            
        query = self.user_input.value.strip()
        if not query:
            return

        self.processing = True
        self.send_btn.props('disabled')
        loading_id = None
        
        try:
            # Add user message
            self._add_message(query, 'user')
            
            # Add loading indicator
            with self.chat_container:
                loading_id = f"loading_{uuid.uuid4()}"
                with ui.row().classes('w-full justify-start').style('animation: pulse 2s infinite;') as row:
                    row.id = loading_id
                    with ui.card().classes('bg-gray-100 items-center gap-2 p-3'):
                        ui.spinner(size='sm', color='primary')
                        ui.label('Analyzing query and generating cohort...').classes('text-sm text-gray-600')
            
            # Process query
            result = await asyncio.get_event_loop().run_in_executor(
                None,  # Uses default executor
                lambda: self.app.process_user_query(query)
            )
            
            # Remove loading indicator
            if loading_id:
                self.chat_container.remove(loading_id)
            
            # Handle response
            if result and hasattr(result, 'get'):
                response = self._format_response(result)
                self._add_message(response, 'system', 'green')
                
                # Save to history
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
                        "record_count": result.get('count', 0)
                    }
                )
                self.load_history()
            else:
                raise ValueError("Invalid response from backend")

        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg)
            self._add_message(error_msg, 'system', 'red')
            
        finally:
            self.processing = False
            self.send_btn.props(remove='disabled')
            self.user_input.value = ''
            ui.update()

    def _format_response(self, result: Dict) -> str:
        """Format backend response for display"""
        return f"""✅ Cohort successfully generated!

📁 File path: {result.get('file_path', 'N/A')}
📊 Records processed: {result.get('count', 'N/A')}
⏱️ Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    def _add_message(self, text: str, sender: str, color: str = None):
        """Add a message to the chat"""
        with self.chat_container:
            alignment = 'justify-end' if sender == 'user' else 'justify-start'
            bg_color = 'bg-primary text-white' if sender == 'user' else 'bg-gray-50'
            
            if color == 'green':
                bg_color = 'bg-green-100 text-green-800'
            elif color == 'red':
                bg_color = 'bg-red-100 text-red-800'
                
            with ui.row().classes(f'w-full {alignment} message-entrance'):
                with ui.card().classes(f'{bg_color} max-w-[75%] rounded-2xl p-4 shadow-sm transition-all') \
                    .style('animation: fadeIn 0.3s ease-in-out;'):
                    ui.label(text).classes('text-sm break-words whitespace-pre-wrap')
                    ui.label(datetime.now().strftime('%H:%M:%S')).classes('text-xs opacity-70 mt-1')
        
        # Auto-scroll and update UI
        ui.run_javascript('''
            setTimeout(() => {
                const container = document.querySelector('.chat-container');
                container.scrollTop = container.scrollHeight;
            }, 100)
        ''')

    def load_history(self):
        """Reload and display chat history"""
        try:
            self.history_panel.clear()
            with self.history_panel:
                ui.label('Chat History').classes('text-xl font-bold mb-4')
                sessions = load_chat_history()
                
                if not sessions:
                    ui.label('No previous chats').classes('text-gray-500')
                    
                for session in sessions:
                    with ui.card().classes('w-full p-2 mb-2 cursor-pointer hover:bg-gray-200 transition-colors') \
                        .on('click', lambda _, s=session: self.show_old_chat(s['id'])):
                        with ui.column().classes('gap-1'):
                            ui.label(session['preview']).classes('text-sm font-medium truncate')
                            ui.label(session['timestamp'][:16].replace('T', ' ')).classes('text-xs text-gray-500')
        except Exception as e:
            logger.error(f"Error loading history: {str(e)}")

    def show_old_chat(self, session_id: str):
        """Display a previous chat session"""
        try:
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
                    )
        except Exception as e:
            logger.error(f"Error loading chat {session_id}: {str(e)}")
            self._add_message(f"Error loading chat history", 'system', 'red')

    def new_chat(self):
        """Start a new chat session"""
        try:
            self.current_session = str(uuid.uuid4())
            self.current_messages = []
            self.chat_container.clear()
            self.user_input.value = ''
            self.load_history()
        except Exception as e:
            logger.error(f"Error creating new chat: {str(e)}")

def main():
    ui.run(title='Masterbranch Cohort Identifier', 
          dark=False, 
          reload=False, 
          port=8080,
          binding_refresh_interval=0.1)

if __name__ == "__main__":
    gui = HealthcareGUI()
    main()