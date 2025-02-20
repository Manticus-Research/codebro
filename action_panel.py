import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk  # Added Gdk for CSS provider


class ActionPanel:
    """
    ActionPanel is responsible for displaying the list of proposed actions (from bots)
    and the list of currently running bots.
    """
    def __init__(self, chat):
        self.chat = chat

        # Main container for the side panel.
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.widget.set_size_request(300, -1)
        self.widget.set_name("action-panel")  # Set CSS ID for the entire action panel

        # Proposed Actions Header
        actions_label = Gtk.Label(label="Proposed Actions")
        actions_label.get_style_context().add_class("sidepanel-header")
        self.widget.append(actions_label)

        # Container for proposed actions.
        self.proposed_actions_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.proposed_actions_box.set_vexpand(False)
        self.proposed_actions_box.set_name("actions-list")  # Set CSS ID for actions list
        self.widget.append(self.proposed_actions_box)

        # Running Bots Header
        bots_label = Gtk.Label(label="Running Bots")
        bots_label.get_style_context().add_class("sidepanel-header")
        self.widget.append(bots_label)

        # Container for running bots.
        self.running_bots_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.running_bots_box.set_vexpand(False)
        self.running_bots_box.set_name("bots-list")  # Set CSS ID for bots list
        self.widget.append(self.running_bots_box)

        # Start periodic updates for the side panel.
        GLib.timeout_add(2000, self.update_sidepanel)

        # Load CSS for backgrounds.
        css = """
        #action-panel {
            background-color: #d0d0d0;  /* light grey for the panel background */
            padding: 10px;
        }
        #actions-list {
            background-color: #ffffff;  /* white for the proposed actions list */
            padding: 5px;
        }
        #bots-list {
            background-color: #f8f8f8;  /* slightly off-white for the running bots list */
            padding: 5px;
        }
        """
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css.encode())
        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def get_widget(self):
        return self.widget

    def update_sidepanel(self):
        # Update Proposed Actions.
        child = self.proposed_actions_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.proposed_actions_box.remove(child)
            child = next_child

        proposed_actions = self.chat.proposed_actions
        if proposed_actions:
            for action in proposed_actions:
                action_name = getattr(action.action, "__name__", str(action.action))
                label = Gtk.Label(label=f"• {action_name}")
                label.set_xalign(0)
                self.proposed_actions_box.append(label)
        else:
            label = Gtk.Label(label="(none)")
            label.set_xalign(0)
            self.proposed_actions_box.append(label)

        # Update Running Bots.
        child = self.running_bots_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.running_bots_box.remove(child)
            child = next_child
        if self.chat.bots:
            for bot in self.chat.bots:
                bot_name = getattr(bot, "name", bot.__class__.__name__)
                label = Gtk.Label(label=f"• {bot_name}")
                label.set_xalign(0)
                self.running_bots_box.append(label)
        else:
            label = Gtk.Label(label="(none)")
            label.set_xalign(0)
            self.running_bots_box.append(label)
        return True
