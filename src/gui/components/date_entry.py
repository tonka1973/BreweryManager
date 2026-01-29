import tkinter as tk
from tkinter import ttk
from ...utilities.date_utils import smart_parse_date, format_date_for_display

class DateEntry(ttk.Entry):
    """
    An Entry widget that automatically formats dates on focus out or return.
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Bind events
        self.bind('<FocusOut>', self._validate_and_format)
        self.bind('<Return>', self._validate_and_format)
        
    def _validate_and_format(self, event=None):
        """
        Parse the current text and update it with the formatted date.
        """
        current_text = self.get()
        if not current_text:
            return
            
        formatted_date = smart_parse_date(current_text)
        
        # Only update if we got a valid non-empty result and it changed
        if formatted_date and formatted_date != current_text:
            self.delete(0, tk.END)
            self.insert(0, formatted_date)
            # Generate a virtual event to notify listeners that the date has changed/formatted
            self.event_generate('<<DateFormatted>>')
