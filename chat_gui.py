import tkinter as tk
from tkinter import ttk
from chat import Chat


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = ttk.Frame(self.canvas)

        # Create a window inside the canvas for the scrollable frame
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Update scrollregion when the size of the scrollable_frame changes
        self.scrollable_frame.bind(
            "<Configure>",
            self._on_frame_configure
        )

        # Bind the canvas width to the scrollable frame width
        self.canvas.bind(
            "<Configure>",
            self._on_canvas_configure
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Resize the inner frame to match the canvas width"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def bind_mousewheel(self):
        """Enable scrolling with the mouse wheel"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class ChatMessage(tk.Text):
    def __init__(self, message, *args, **kwargs):
        self.message = message

        sender = message.get("role")
        # Determine background color based on sender
        if sender == "assistant" or sender == "system":
            bg_color = "#e6e6e6"  # Light gray for assistant messages
            self.anchor = "w"
        else:
            bg_color = "#d1ffd6"  # Light green for user messages
            self.anchor = "e"

        _kwargs = {
            "bg": bg_color,
            "wrap": "none",
            "padx": 5,
            "pady": 5,
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 0,
        }
        _kwargs.update(kwargs)
        super().__init__(*args, **_kwargs)
        self.insert(tk.END, message["content"])
        self.configure(state="disabled")

        self.update_idletasks()
        num_of_lines = int(self.index("end - 1 line").split(".")[0])
        self.configure(height=num_of_lines)

class ChatGUI(Chat):
    def __init__(self, title, default_llm, context_paths, working_dir, session):
        super().__init__(default_llm, context_paths, working_dir, session)

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("600x500")  # Set a default window size

        # Configure the root window"s grid
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        self.root.columnconfigure(0, weight=1)

        # Create the scrollable frame for messages
        self.scrollable_frame = ScrollableFrame(self.root)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")

        # Enable mouse wheel scrolling
        self.scrollable_frame.bind_mousewheel()

        # Reference to the inner frame where messages will be added
        self.messages_frame = self.scrollable_frame.scrollable_frame
        self.messages_frame.columnconfigure(0, weight=1)

        # Entry field for user input
        self.input_field = tk.Text(self.root, height=10)
        self.input_field.grid(row=1, column=0, sticky="ew")
        self.input_field.bind("<Return>", self.send_message)

        self.last_displayed_message = 0
        self.update_chat_display()

    def send_message(self, event=None):
        message = self.input_field.get("1.0", tk.END)
        self.input_field.delete("1.0", tk.END)
        if message.strip():
            self.post_to_llm(self.default_llm, message)

    def update_chat_display(self):
        while self.last_displayed_message < len(self.history):
            message = self.history[self.last_displayed_message]
            self.print_message(message)
            self.last_displayed_message += 1
        self.root.after(100, self.update_chat_display)

    def print_message(self, message):
        if message.get("is_context"):
            return

        # Create a frame for each message
        message_frame = ChatMessage(message, self.messages_frame)
        # message_frame.grid(row=self.last_displayed_message, column=0, sticky="ew", padx=5, pady=2)

        # Configure grid to ensure the message fills the width
        message_frame.columnconfigure(0, weight=1)
        self.messages_frame.rowconfigure(self.last_displayed_message, weight=1)

        # Align the message to the left or right based on the sender
        if message_frame.anchor == "e":
            message_frame.grid(row=self.last_displayed_message, column=0, sticky="e", padx=5, pady=2)
        else:
            message_frame.grid(row=self.last_displayed_message, column=0, sticky="w", padx=5, pady=2)

        # Auto-scroll to the bottom
        self.messages_frame.update_idletasks()
        self.scrollable_frame.canvas.yview_moveto(1.0)

    def main(self):
        self.root.mainloop()
