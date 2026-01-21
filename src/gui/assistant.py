import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
import threading
from src.config.constants import *

class AISettingsDialog(ttk.Toplevel):
    """Dialog to configure AI Provider and API Key"""
    def __init__(self, parent, ai_client, on_save_callback):
        super().__init__(parent)
        self.title("AI Assistant Setup")
        self.ai_client = ai_client
        self.on_save = on_save_callback
        self.geometry("450x300")
        self.resizable(False, False)
        
        self.create_widgets()
        self.load_current_settings()
        
    def create_widgets(self):
        container = ttk.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=True)

        # Buttons (Top)
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=X, side=TOP, pady=(0, 20))

        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.destroy).pack(side=LEFT)
        ttk.Button(btn_frame, text="Save & Connect", bootstyle="success", command=self.save).pack(side=RIGHT)
        
        # Header
        ttk.Label(container, text="Configure Brewery AI", font=("Segoe UI", 12, "bold")).pack(pady=(0, 20))
        
        # Provider Selection
        ttk.Label(container, text="Select AI Brain:").pack(anchor=W)
        self.provider_var = tk.StringVar()
        self.provider_combo = ttk.Combobox(container, textvariable=self.provider_var, state="readonly")
        self.provider_combo['values'] = ("Google Gemini", "Anthropic Claude", "OpenAI ChatGPT")
        self.provider_combo.pack(fill=X, pady=(5, 15))
        self.provider_combo.bind("<<ComboboxSelected>>", self.update_help_text)
        
        # API Key
        ttk.Label(container, text="API Key:").pack(anchor=W)
        self.api_key_var = tk.StringVar()
        self.key_entry = ttk.Entry(container, textvariable=self.api_key_var, show="*")
        self.key_entry.pack(fill=X, pady=(5, 5))
        
        # Help Text
        self.help_lbl = ttk.Label(container, text="", font=("Segoe UI", 8), bootstyle="secondary")
        self.help_lbl.pack(anchor=W, pady=(0, 15))
        

    def load_current_settings(self):
        # Map internal codes to display names
        pmap = {
            "gemini": "Google Gemini",
            "anthropic": "Anthropic Claude",
            "openai": "OpenAI ChatGPT"
        }
        
        current_p = self.ai_client.provider
        self.provider_var.set(pmap.get(current_p, "Google Gemini"))
        if self.ai_client.api_key:
            self.api_key_var.set(self.ai_client.api_key)
            
        self.update_help_text()

    def update_help_text(self, event=None):
        selection = self.provider_var.get()
        if selection == "Google Gemini":
            self.help_lbl.config(text="Free Tier available.\nGet key: aistudio.google.com/app/apikey")
        elif selection == "Anthropic Claude":
            self.help_lbl.config(text="Best for logic/coding. Usage costs money.\nGet key: console.anthropic.com")
        elif selection == "OpenAI ChatGPT":
            self.help_lbl.config(text="Industrial standard. Usage costs money.\nGet key: platform.openai.com")

    def save(self):
        display_name = self.provider_var.get()
        key = self.api_key_var.get().strip()
        
        if not key:
            tk.messagebox.showerror("Error", "API Key is required")
            return
            
        # Map back to internal codes
        pmap_rev = {
            "Google Gemini": "gemini",
            "Anthropic Claude": "anthropic",
            "OpenAI ChatGPT": "openai"
        }
        internal_code = pmap_rev[display_name]
        
        success = self.ai_client.save_settings(internal_code, key)
        if success:
            self.on_save()
            self.destroy()
        else:
            tk.messagebox.showerror("Error", "Failed to save settings")


class AIAssistantWidget(ttk.Frame):
    """
    Floating widget for AI interactions.
    """
    def __init__(self, parent, ai_client, get_context_callback):
        super().__init__(parent)
        self.parent = parent
        self.ai_client = ai_client
        self.get_context_callback = get_context_callback
        
        self.is_expanded = False
        self.conversation_history = []
        
        self.create_widgets()
        
    def create_widgets(self):
        # Search Bar Frame
        self.search_frame = ttk.Frame(self)
        self.search_frame.pack(fill=X, expand=True)
        
        # AI Icon/Button
        self.icon_btn = ttk.Button(
            self.search_frame, 
            text="✨", 
            bootstyle="link",
            command=self.toggle_chat
        )
        self.icon_btn.pack(side=LEFT, padx=5)
        
        # Entry
        self.search_var = tk.StringVar()
        self.entry = ttk.Entry(
            self.search_frame, 
            textvariable=self.search_var,
            font=("Segoe UI", 10)
        )
        self.entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.entry.bind("<Return>", self._on_submit)
        
        # Placeholder logic
        self.placeholder = "Ask Brewery Assistant..."
        self.entry.insert(0, self.placeholder)
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        # Settings Button
        self.settings_btn = ttk.Button(
            self.search_frame,
            text="⚙️",
            bootstyle="link-secondary",
            command=self.open_settings
        )
        self.settings_btn.pack(side=RIGHT, padx=5)

    def _on_focus_in(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(foreground='black')

    def _on_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(foreground='grey')

    def open_settings(self):
        print("DEBUG: Settings button clicked!")
        try:
            dlg = AISettingsDialog(self.winfo_toplevel(), self.ai_client, self.on_settings_saved)
            # Center the dialog
            self.center_window(dlg)
        except Exception as e:
            print(f"DEBUG: Error opening settings: {e}")

    def on_settings_saved(self):
        # Notify user or refresh state if needed
        pass

    def center_window(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def _on_submit(self, event):
        print("DEBUG: Enter key pressed!")
        query = self.entry.get()
        print(f"DEBUG: Query value: '{query}'")
        if not query or query == self.placeholder:
            return

        # Check configuration
        if not self.ai_client.api_key:
            self.open_settings()
            return

        # Get context
        context = self.get_context_callback()
        
        # Open Chat Dialog
        dialog = AIChatDialog(self.winfo_toplevel(), self.ai_client, query, context)
        
        # Reset entry
        self.search_var.set("")
        self.entry.insert(0, self.placeholder)
        self.parent.focus() # Remove focus from entry

    def toggle_chat(self):
        # Just open empty chat window
        pass


class AIChatDialog(ttk.Toplevel):
    def __init__(self, parent, ai_client, initial_query, context):
        super().__init__(parent)
        self.title("Brewery Assistant")
        self.ai_client = ai_client
        self.context = context
        self.geometry("600x500")
        
        self.create_widgets()
        self.process_query(initial_query)
        
    def create_widgets(self):
        # Input Area (Pack First so it stays at bottom)
        input_frame = ttk.Frame(self, padding=10)
        input_frame.pack(fill=X, side=BOTTOM)
        
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var)
        self.input_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", self.send_followup)
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_followup)
        send_btn.pack(side=RIGHT)

        # Chat History Area (Pack Last to fill remaining space)
        self.history_area = ScrolledText(self, padding=10, font=("Segoe UI", 10), wrap=WORD)
        self.history_area.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.history_area.text.configure(state='disabled')
        
        # Resize Grip (Bottom Right)
        ttk.Sizegrip(self).place(relx=1.0, rely=1.0, anchor='se')

    def append_message(self, role, text):
        self.history_area.text.configure(state='normal')
        
        if role == "User":
            self.history_area.text.insert(tk.END, f"\nYou: {text}\n", "user")
        else:
            self.history_area.text.insert(tk.END, f"\nAssistant: {text}\n", "ai")
            
        self.history_area.text.configure(state='disabled')
        self.history_area.text.see(tk.END)

    def process_query(self, query):
        self.append_message("User", query)
        self.append_message("System", "Analyzing...")
        
        # Run in thread to not block UI
        threading.Thread(target=self._run_ai_query, args=(query,), daemon=True).start()

    def _run_ai_query(self, query):
        response = self.ai_client.query(query, self.context)
        
        # Update UI on main thread
        self.after(0, lambda: self._update_response(response))

    def _update_response(self, response):
        # Remove "Analyzing..." placeholder if possible, or just append
        self.history_area.text.configure(state='normal')
        # Simple hack: delete last line "System: Analyzing..."
        # self.history_area.text.delete("end-2l", "end-1l") 
        self.history_area.text.insert(tk.END, f"{response}\n")
        self.history_area.text.configure(state='disabled')
        self.history_area.text.see(tk.END)

    def send_followup(self, event=None):
        text = self.input_var.get()
        if not text:
            return
            
        self.input_entry.delete(0, tk.END)
        self.process_query(text)
