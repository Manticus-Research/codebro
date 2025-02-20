import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from chat_gui import ChatGUI
from action_panel import ActionPanel

################################################################################
# Session View: Combines a header spanning full width with Chat Area and ActionPanel.
################################################################################
class SessionView:
    """
    SessionView arranges a header bar spanning the full width above a horizontal box
    containing the ChatGUI and ActionPanel.
    """
    def __init__(self, chat, on_back_to_sessions):
        self.chat = chat
        # Create Chat Area.
        self.chat_area = ChatGUI(chat, on_back_to_sessions)
        # Create Side Panel.
        self.side_panel = ActionPanel(chat)

        # Header Bar covering full width.
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(False)
        header_bar.set_title_widget(Gtk.Label(label=self.chat_area.title))
        back_button = Gtk.Button(label="Back to Sessions")
        back_button.connect("clicked", self.chat_area.on_back_button_clicked)
        header_bar.pack_start(back_button)

        # Horizontal container for Chat Area and Side Panel.
        horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        chat_widget = self.chat_area.get_widget()
        chat_widget.set_hexpand(True)
        chat_widget.set_vexpand(True)
        horizontal_box.append(chat_widget)

        side_widget = self.side_panel.get_widget()
        side_widget.set_hexpand(False)
        side_widget.set_vexpand(False)
        horizontal_box.append(side_widget)

        # Main container: vertical box with header bar on top.
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.widget.append(header_bar)
        self.widget.append(horizontal_box)

    def get_widget(self):
        return self.widget
