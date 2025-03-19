import tkinter as tk
from tkinter import ttk
from datetime import datetime

class GUI:
    def __init__(self):
        """Initialize the GUI component"""
        self.root = tk.Tk()
        self.root.title("Healthcare Data Analysis System")
        self.callback = None
        
        # Configure main window
        self.root.geometry("1024x768")
        
        # Create main container
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Setup left and right panels
        self._setup_left_panel()
        self._setup_right_panel()
        
        # Configure weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def set_submit_callback(self, callback):
        """Set the callback function for when a message is submitted"""
        self.callback = callback

    def _setup_left_panel(self):
        """Setup left panel with visualization area"""
        self.left_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.left_panel, weight=60)
        
        # Create visualization frame
        viz_frame = ttk.LabelFrame(self.left_panel, text="Visualization")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _setup_right_panel(self):
        """Setup right panel with chat history and input"""
        self.right_panel = ttk.PanedWindow(self.main_container, orient=tk.VERTICAL)
        self.main_container.add(self.right_panel, weight=40)
        
        self._setup_chat_history()
        self._setup_chatbot_input_panel()

    def _setup_chat_history(self):
        """Setup chat history panel"""
        history_frame = ttk.LabelFrame(self.right_panel, text="Chat History")
        
        # Create text widget for chat history
        self.history_text = tk.Text(history_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, command=self.history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.configure(yscrollcommand=scrollbar.set)
        
        self.right_panel.add(history_frame, weight=80)

    def _setup_chatbot_input_panel(self):
        """Setup chatbot input panel with text entry and send button"""
        frame = ttk.LabelFrame(self.right_panel, text="Query Input")
        
        # Create a frame for input and button
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add input field
        self.input_field = ttk.Entry(input_frame)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add send button
        send_button = ttk.Button(input_frame, text="Send", command=self._handle_submit)
        send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Bind Enter key to submit
        self.input_field.bind("<Return>", lambda e: self._handle_submit())
        
        self.right_panel.add(frame, weight=20)

    def _handle_submit(self):
        """Handle input submission"""
        user_input = self.input_field.get()
        if user_input.strip():
            self.add_history_entry(user_input)
            self.input_field.delete(0, tk.END)
            if self.callback:
                self.callback(user_input)

    def add_history_entry(self, text, is_user=True):
        """Add an entry to the chat history"""
        self.history_text.configure(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "You" if is_user else "Assistant"
        
        # Add the entry with timestamp
        self.history_text.insert(tk.END, f"[{timestamp}] {prefix}: {text}\n")
        
        # Scroll to the bottom
        self.history_text.see(tk.END)
        self.history_text.configure(state=tk.DISABLED)

    def add_system_message(self, text):
        """Add a system message to the chat history"""
        self.add_history_entry(text, is_user=False)

    def update(self):
        """Update the GUI"""
        self.root.update()
