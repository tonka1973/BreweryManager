import tkinter as tk
import ttkbootstrap as ttk
from ...utilities.window_manager import enable_mousewheel_scrolling

class ScrollableFrame(ttk.Frame):
    """
    A reusable frame offering specific dimensions and a vertical scrollbar.
    
    The content should be added to the `inner_frame` attribute.
    """
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Configure grid expansion
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Create canvas
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Create scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create inner frame for content
        self.inner_frame = ttk.Frame(self.canvas)
        
        # Create window inside canvas
        # anchor="n" ensures it stays at top
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Bind events
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Enable mousewheel scrolling
        enable_mousewheel_scrolling(self.canvas)
        
        # Bind mouse enter/leave to enable/disable scrolling
        self.inner_frame.bind('<Enter>', self._bind_mouse_scroll)
        self.inner_frame.bind('<Leave>', self._unbind_mouse_scroll)

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """When canvas resizes, resize the inner frame to match width"""
        # Set the width of the inner frame to the width of the canvas
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _bind_mouse_scroll(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mouse_scroll(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if self.canvas.winfo_exists():
            if event.delta:
                self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
            else:
                self.canvas.yview_scroll(-1 if event.num == 4 else 1, "units")
