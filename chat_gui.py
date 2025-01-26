import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from threading import Thread

import json

class ChatGUI:
    def __init__(self, chat, on_back_to_sessions):
        self.chat = chat
        self.on_back_to_sessions = on_back_to_sessions  # Callback function
        self.title = chat.get_name()
        self.last_displayed_message = 0

        # Create the main container for the chat GUI
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # **Add the header bar with the "Back to Sessions" button**
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(False)
        header_bar.set_title_widget(Gtk.Label(label=self.title))

        back_button = Gtk.Button(label="Back to Sessions")
        back_button.connect("clicked", self.on_back_button_clicked)
        header_bar.pack_start(back_button)

        self.widget.append(header_bar)

        # Create the messages container as a Box inside a ScrolledWindow
        self.messages_container = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.messages_scrolled_window = Gtk.ScrolledWindow()
        self.messages_scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        self.messages_scrolled_window.set_child(self.messages_container)
        self.messages_scrolled_window.set_vexpand(True)
        self.widget.append(self.messages_scrolled_window)

        # Create the input area and send button in a horizontal box
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.widget.append(hbox)

        input_scrolled_window = Gtk.ScrolledWindow()
        input_scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        input_scrolled_window.set_min_content_height(100)  # Set desired height
        input_scrolled_window.set_vexpand(False)
        input_scrolled_window.set_hexpand(True)

        self.input_textview = Gtk.TextView()
        self.input_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.input_textview.set_vexpand(True)
        self.input_textview.set_hexpand(True)
        self.input_buffer = self.input_textview.get_buffer()
        input_scrolled_window.set_child(self.input_textview)

        hbox.append(input_scrolled_window)

        send_button = Gtk.Button(label="Send")
        send_button.connect("clicked", self.send_message)
        hbox.append(send_button)

        self.update_chat_display()
        # Set up a timer or idle function to update the chat display
        GLib.timeout_add(500, self.update_chat_display)

    def get_widget(self):
        return self.widget

    def send_message(self, widget):
        start_iter = self.input_buffer.get_start_iter()
        end_iter = self.input_buffer.get_end_iter()
        message = self.input_buffer.get_text(start_iter, end_iter, True)
        self.input_buffer.set_text("")
        if message.strip():
            # Send to LLM in a separate thread
            thread = Thread(target=self.handle_user_message, args=(message,))
            thread.start()

    def handle_user_message(self, message):
        self.chat.post_to_llm(self.chat.default_llm, message)

    def update_chat_display(self):
        while self.last_displayed_message < len(self.chat.history):
            message = self.chat.history[self.last_displayed_message]
            self.last_displayed_message += 1
            GLib.idle_add(self.print_message, message)
        return True  # Continue calling this function

    def print_message(self, message):
        if message.get("is_context"):
            return

        sender = message.get("role", "")
        content = message.get("content", "")

        # Format sender label and styling
        if sender == "assistant":
            sender_label = "Assistant"
            text_color = "blue"
            alignment = Gtk.Align.START
            bg_color = "#E0F7FA"  # Light cyan
        elif sender == "system":
            sender_label = "System"
            text_color = "green"
            alignment = Gtk.Align.CENTER
            bg_color = "#E8F5E9"  # Light green
        else:
            sender_label = "You"
            text_color = "black"
            alignment = Gtk.Align.END
            bg_color = "#FFF3E0"  # Light orange

        # Create a box for the message
        message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        message_box.set_halign(alignment)
        message_box.set_hexpand(True)
        message_box.set_margin_top(5)
        message_box.set_margin_bottom(5)
        message_box.set_margin_start(10)
        message_box.set_margin_end(10)
        message_box.set_css_classes(["message-box"])

        # Create sender label
        sender_label_widget = Gtk.Label()
        sender_label_widget.set_markup(f"<b>{sender_label}:</b>")
        sender_label_widget.set_xalign(0)  # Left-align text
        sender_label_widget.add_css_class("sender-label")
        sender_label_widget.get_style_context().add_class(f"text-{text_color}")
        message_box.append(sender_label_widget)

        # Create content label
        content_label = Gtk.Label()
        content_label.set_text(content)
        content_label.set_wrap(True)
        content_label.set_xalign(0)
        content_label.set_selectable(True)
        message_box.append(content_label)

        # Apply background color via CSS
        message_box.set_name("message_box")
        css_provider = Gtk.CssProvider()
        css = f"""
        #message_box {{
            background-color: {bg_color};
        }}
        .text-blue {{
            color: blue;
        }}
        .text-green {{
            color: green;
        }}
        .text-black {{
            color: black;
        }}
        """
        css_provider.load_from_data(css.encode())
        style_context = message_box.get_style_context()
        style_context.add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        # Add the message box to the messages container
        self.messages_container.append(message_box)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        adjustment = self.messages_scrolled_window.get_vadjustment()
        adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())

    def on_close_request(self, window):
        # Handle any cleanup if necessary
        return False  # Allow window to close

    def exit_app(self):
        # Handle application exit if necessary
        pass

    # **Add this method to handle the back button click event**
    def on_back_button_clicked(self, button):
        if self.on_back_to_sessions:
            self.on_back_to_sessions()
