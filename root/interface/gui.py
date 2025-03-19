from pathlib import Path
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk

class GUI:
    def __init__(self):
        """Initialize the GUI component"""
        self.root = tk.Tk()
        self.root.title("Healthcare Data Analysis System")
        self.callback = None
        self.image_references = []  # Add this to keep image references
        
        # Configure fonts
        default_font = ('Arial', 16)  # You can adjust size (12) as needed
        
        # Configure styles for ttk widgets
        style = ttk.Style()
        style.configure('TLabel', font=default_font)
        style.configure('TButton', font=default_font)
        style.configure('TEntry', font=default_font)
        style.configure('TLabelframe.Label', font=default_font)  # For LabelFrame titles
        
        # Configure main window
        self.root.geometry("1024x768")
        
        # Configure default font for tk widgets
        self.root.option_add('*TButton*font', default_font)
        self.root.option_add('*TEntry*font', default_font)
        self.root.option_add('*Text*font', default_font)
        
        # Create main container
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Setup left and right panels
        self._setup_left_panel()
        self._setup_right_panel()
        
        # Configure weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def add_image_to_chat(self, image_path):
        """Add an image to the chat history"""
        try:
            # Open and resize image
            pil_image = Image.open(image_path)
            # Resize while maintaining aspect ratio
            max_size = (300, 300)  # Maximum width and height
            pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            tk_image = ImageTk.PhotoImage(pil_image)
            self.image_references.append(tk_image)  # Keep reference
            
            # Enable text widget for editing
            self.history_text.configure(state=tk.NORMAL)
            
            # Add timestamp and prefix
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.history_text.insert(tk.END, f"[{timestamp}] Assistant:\n")
            
            # Insert image
            self.history_text.image_create(tk.END, image=tk_image)
            self.history_text.insert(tk.END, "\n\n")
            
            # Disable text widget and scroll to bottom
            self.history_text.configure(state=tk.DISABLED)
            self.history_text.see(tk.END)
            
        except Exception as e:
            self.add_system_message(f"Error displaying image: {str(e)}")

    def set_submit_callback(self, callback):
        """Set the callback function for when a message is submitted"""
        self.callback = callback

    # To remove later
    def _setup_left_panel_old(self):
        """Setup left panel with visualization area"""
        self.left_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.left_panel, weight=60)
        
        # Create visualization frame
        files_frame = ttk.LabelFrame(self.left_panel, text="Ficheros")
        files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _setup_left_panel(self):
        """Setup left panel with files area"""
        self.left_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.left_panel, weight=60)
        
        # Create files frame
        self.files_frame = ttk.LabelFrame(self.left_panel, text="Ficheros")
        self.files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create container for file links
        self.files_container = ttk.Frame(self.files_frame)
        self.files_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def add_file_to_panel(self, filepath: str, icon_type: str = 'questhead'):
        """
        Add a file link to the files panel
        
        Args:
            filepath: Path to the file
            icon_type: Type of icon ('questhead' for documents, 'photo' for images)
        """
        try:
            # Create container for this file link
            filename = Path(filepath).name
            link_container = ttk.Frame(self.files_frame)
            link_container.pack(
                fill=tk.X,      # Fill horizontally
                pady=2,         # Vertical padding between items
                side=tk.TOP,    # Explicitly pack from top
                anchor=tk.N     # Anchor to the north/top
            )
            
            # Add icon
            icon_label = tk.Label(link_container, bitmap=icon_type)
            icon_label.pack(side=tk.LEFT, padx=5)
            
            # Add filename label that acts as a link
            file_label = tk.Label(
                link_container, 
                text=filename,
                cursor="hand2",
                font=('Arial', 12)
            )
            file_label.pack(side=tk.LEFT, padx=5)

            
            # Bind click event to open file
            def open_file(event):
                try:
                    import os
                    import platform
                    if platform.system() == 'Darwin':  # macOS
                        os.system(f'open "{filepath}"')
                    elif platform.system() == 'Windows':
                        os.system(f'start "" "{filepath}"')
                    else:  # Linux
                        os.system(f'xdg-open "{filepath}"')
                except Exception as e:
                    print(f"Error opening file: {e}")
            
            file_label.bind('<Button-1>', open_file)
            
            # Optional: Add hover effect
            def on_enter(event):
                file_label.configure(foreground="blue")
            
            def on_leave(event):
                file_label.configure(foreground="black")
            
            file_label.bind('<Enter>', on_enter)
            file_label.bind('<Leave>', on_leave)
            
        except Exception as e:
            print(f"Error adding file to panel: {e}")


    def _setup_right_panel(self):
        """Setup right panel with chat history and input"""
        self.right_panel = ttk.PanedWindow(self.main_container, orient=tk.VERTICAL)
        self.main_container.add(self.right_panel, weight=40)
        
        self._setup_chatbot_output_frame()
        self._setup_chatbot_input_panel()

    def _setup_chatbot_output_frame(self):
        """Setup chat history panel"""
        chatbot_output_frame = ttk.LabelFrame(self.right_panel, text="Respuestas del Asistente")
        
        # Create container frame for chat history with padding
        history_container = ttk.Frame(chatbot_output_frame)
        history_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure container's grid
        history_container.grid_columnconfigure(0, weight=1)
        history_container.grid_rowconfigure(0, weight=1)
        
        # Create text widget for chat history
        self.history_text = tk.Text(
            history_container,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.history_text.grid(row=0, column=0, sticky='nsew')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            history_container,
            orient=tk.VERTICAL,
            command=self.history_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Configure text widget to use scrollbar
        self.history_text.configure(yscrollcommand=scrollbar.set)
        
        # Add frame to right panel with weight for proper expansion
        self.right_panel.add(chatbot_output_frame, weight=98)

    def _setup_chatbot_input_panel(self):
        """Setup chatbot input panel with text entry and send button"""
        user_input_frame = ttk.LabelFrame(self.right_panel, text="Consulta:")
        
        # Create a frame for input and button with padding
        input_frame = ttk.Frame(user_input_frame)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure input_frame's grid
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)
        
        # Add input field using grid with larger font
        self.input_field = ttk.Entry(input_frame, font=('Arial', 32))  # Increased font size to 16
        self.input_field.grid(row=0, column=0, sticky='new', padx=5)
        
        # Add send button using grid
        send_button = ttk.Button(input_frame, text="Send", command=self._handle_submit)
        send_button.grid(row=0, column=1, sticky='nsew', padx=(0, 5))
        
        # Bind Enter key to submit
        self.input_field.bind("<Return>", lambda e: self._handle_submit())
        
        # Add frame to right panel with weight for proper expansion
        self.right_panel.add(user_input_frame, weight=2)



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
