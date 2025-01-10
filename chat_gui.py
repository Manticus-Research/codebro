import tkinter as tk
from chat import Chat

class ChatGUI(Chat):
    def __init__(self, default_llm, context_paths, working_dir):
        super().__init__(default_llm, context_paths, working_dir)

        self.root = tk.Tk()
        self.root.title("Chat Assistant")

        # Configure the root window's grid
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        self.root.columnconfigure(0, weight=1)

        # Use grid layout manager instead of pack
        self.chat_display = tk.Text(self.root, state='disabled')
        self.chat_display.grid(row=0, column=0, sticky="nsew")

        self.input_field = tk.Entry(self.root)
        self.input_field.grid(row=1, column=0, sticky="ew")
        self.input_field.bind("<Return>", self.send_message)

        self.last_displayed_message = 0
        self.update_chat_display()

    def send_message(self, event=None):
        message = self.input_field.get()
        self.input_field.delete(0, tk.END)
        if message.strip():
            self.post_to_llm(self.default_llm, message)

    def update_chat_display(self):
        while self.last_displayed_message < len(self.history):
            message = self.history[self.last_displayed_message]
            self.print_message(message)
            self.last_displayed_message += 1
        self.root.after(100, self.update_chat_display)

    def print_message(self, message):
        if message.get('is_context'):
            return

        sender = message.get("role")
        content = message['content']

        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {content}\n\n")
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def main(self):
        self.root.mainloop()
