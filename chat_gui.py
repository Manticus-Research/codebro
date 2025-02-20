import gi
import json
import re
from threading import Thread

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib


class ChatGUI:
    """
    ChatGUI now represents only the chat area with messages and input.
    """
    def __init__(self, chat, on_back_to_sessions):
        self.chat = chat
        self.on_back_to_sessions = on_back_to_sessions
        self.title = chat.get_name()
        self.last_displayed_message = 0

        # Main container for the chat area (vertical box).
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Chat messages container inside a scrolled window.
        self.messages_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.messages_scrolled_window = Gtk.ScrolledWindow()
        self.messages_scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        self.messages_scrolled_window.set_child(self.messages_container)
        self.messages_scrolled_window.set_vexpand(True)
        self.widget.append(self.messages_scrolled_window)

        # Input area and send button.
        input_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        input_scrolled_window = Gtk.ScrolledWindow()
        input_scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        input_scrolled_window.set_min_content_height(100)
        input_scrolled_window.set_vexpand(False)
        input_scrolled_window.set_hexpand(True)

        self.input_textview = Gtk.TextView()
        self.input_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.input_textview.set_vexpand(True)
        self.input_textview.set_hexpand(True)
        self.input_buffer = self.input_textview.get_buffer()
        input_scrolled_window.set_child(self.input_textview)
        input_hbox.append(input_scrolled_window)
        send_button = Gtk.Button(label="Send")
        send_button.connect("clicked", self.send_message)
        input_hbox.append(send_button)
        self.widget.append(input_hbox)

        # Start periodic update for chat messages.
        GLib.timeout_add(500, self.update_chat_display)

    def get_widget(self):
        return self.widget

    def send_message(self, widget):
        start_iter = self.input_buffer.get_start_iter()
        end_iter = self.input_buffer.get_end_iter()
        message = self.input_buffer.get_text(start_iter, end_iter, True)
        self.input_buffer.set_text("")
        if message.strip():
            thread = Thread(target=self.handle_user_message, args=(message,))
            thread.start()

    def handle_user_message(self, message):
        self.chat.post_to_llm(self.chat.default_llm, message)

    def update_chat_display(self):
        while self.last_displayed_message < len(self.chat.history):
            message = self.chat.history[self.last_displayed_message]
            self.last_displayed_message += 1
            GLib.idle_add(self.print_message, message)
        return True

    def print_message(self, message):
        if message.get("is_context"):
            return

        sender = message.get("role", "")
        content = message.get("content", "")

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

        message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        message_box.set_halign(alignment)
        message_box.set_hexpand(True)
        message_box.set_margin_top(5)
        message_box.set_margin_bottom(5)
        message_box.set_margin_start(10)
        message_box.set_margin_end(10)
        message_box.set_css_classes(["message-box"])

        sender_label_widget = Gtk.Label()
        sender_label_widget.set_markup(f"<b>{sender_label}:</b>")
        sender_label_widget.set_xalign(0)
        sender_label_widget.add_css_class("sender-label")
        sender_label_widget.get_style_context().add_class(f"text-{text_color}")
        message_box.append(sender_label_widget)

        content_label = Gtk.Label()
        content_label.set_text(content)
        content_label.set_wrap(True)
        content_label.set_xalign(0)
        content_label.set_selectable(True)
        message_box.append(content_label)

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
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.messages_container.append(message_box)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        adjustment = self.messages_scrolled_window.get_vadjustment()
        adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())

    def on_back_button_clicked(self, button):
        if self.on_back_to_sessions:
            self.on_back_to_sessions()
