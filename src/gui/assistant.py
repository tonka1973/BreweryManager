"""
Assistant GUI for Brewery Management System
Provides the search bar widget and chat interface
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime

class AIAssistantWidget(ttk.Frame):
    """
    The persistent search bar widget in the main header.
    Allows user to type a question and press Enter.
    """
    
    def __init__(self, parent, ai_client, get_context_callback):
        super().__init__(parent)
        self.ai_client = ai_client
        self.get_context_callback = get_context_callback
        
        self.configure(padding=5)
        self.create_widgets()
        
    def create_widgets(self):
        # Container with rounded look
        container = ttk.Frame(self, bootstyle="light")
        container.pack(fill=tk.X, expand=True)
        
        # Search Icon label
        icon_label = ttk.Label(
            container, 
            text="🤖", 
            bootstyle="light",
            font=('Segoe UI Emoji', 12)
        )
        icon_label.pack(side=tk.LEFT, padx=(10, 5))
        
        # Entry field
        self.entry = ttk.Entry(
            container, 
            bootstyle="light",
            width=40,
            font=('Arial', 10)
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        # Placeholder text behavior
        self.placeholder = "Ask the Brewery Assistant..."
        self.entry.insert(0, self.placeholder)
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<Return>', self._on_submit)
        
        # Help/Send Button
        btn = ttk.Button(
            container,
            text="Ask",
            bootstyle="primary-outline",
            command=self._on_submit_btn
        )
        btn.pack(side=tk.RIGHT, padx=5)

    def _on_focus_in(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            
    def _on_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            
    def _on_submit_btn(self):
        self._on_submit(None)

    def _on_submit(self, event):
        query = self.entry.get().strip()
        if not query or query == self.placeholder:
            return
            
        # Get context from main window (current module, etc)
        context = self.get_context_callback()
        
        # Open the chat dialog
        dialog = AIChatDialog(self.winfo_toplevel(), self.ai_client, query, context)
        
        # Clear entry after sending
        self.entry.delete(0, tk.END)
        self.winfo_toplevel().focus() # Remove focus from entry


class AIChatDialog(tk.Toplevel):
    """Floating dialog to show the conversation"""
    
    def __init__(self, parent, ai_client, initial_query, context):
        super().__init__(parent)
        self.title("Brewery Assistant")
        self.geometry("600x500")
        self.ai_client = ai_client
        self.context = context
        
        # Make modal-ish (stay on top)
        self.transient(parent)
        
        self.create_widgets()
        self.process_query(initial_query)
        
    def create_widgets(self):
        # Chat history area
        self.history_frame = ttk.Frame(self, padding=10)
        self.history_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display = tk.Text(
            self.history_frame,
            font=('Arial', 10),
            wrap=tk.WORD,
            state='disabled',
            bg='#f8f9fa',
            padx=10,
            pady=10
        )
        scroll = ttk.Scrollbar(self.history_frame, command=self.chat_display.yview)
        self.chat_display.config(yscrollcommand=scroll.set)
        
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tags for styling
        self.chat_display.tag_config('user', foreground='#2e7d32', font=('Arial', 10, 'bold'))
        self.chat_display.tag_config('ai', foreground='#1565c0')
        self.chat_display.tag_config('system', foreground='#757575', font=('Arial', 9, 'italic'))

        # Input area for follow-up
        input_frame = ttk.Frame(self, padding=10)
        input_frame.pack(fill=tk.X)
        
        self.input_entry = ttk.Entry(input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        self.input_entry.bind('<Return>', self.send_followup)
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_followup)
        send_btn.pack(side=tk.RIGHT)
        
    def append_message(self, sender, text, tag):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        self.chat_display.insert(tk.END, f"{text}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
        
    def process_query(self, query):
        self.append_message("You", query, 'user')
        self.append_message("System", "Analyzing...", 'system')
        
        # Run in a non-blocking way ideally, but for now synchronous is okay for MVP
        self.update() 
        
        response = self.ai_client.query(query, self.context)
        
        # Remove 'Analyzing...' (simple way is just to append response)
        self.append_message("Assistant", response, 'ai')
        
    def send_followup(self, event=None):
        query = self.input_entry.get().strip()
        if not query:
            return
            
        self.input_entry.delete(0, tk.END)
        self.process_query(query)
