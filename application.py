import gi
import os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio
from threading import Thread

from chat_gui import ChatGUI
from chat import Chat
from database import Session, ContextPath
from llm import LLM
from tools import write_file, read_file
from backends import OllamaBackend, OpenAIBackend
from migrations.migrate import upgrade
from database import database
from datetime import datetime, timezone


class Application:
    def __init__(self):
        self.app = Gtk.Application(application_id="com.manticusresearch.CodeBud")
        self.app.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.set_title("CodeBud")
        self.window.set_default_size(800, 600)
        self.window.connect("close-request", self.on_close_request)

        # Main container
        self.stack = Gtk.Stack()
        self.window.set_child(self.stack)

        # Create the sessions view
        self.sessions_view = self.create_sessions_view()
        self.stack.add_named(self.sessions_view, "sessions_view")

        # Show the sessions view initially
        self.stack.set_visible_child_name("sessions_view")

        self.window.present()

    def create_sessions_view(self):
        # Create a box to hold the sessions list and buttons
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)

        # Title label
        title_label = Gtk.Label(label="Select a Session")
        title_label.set_xalign(0)
        title_label.set_margin_bottom(10)
        vbox.append(title_label)

        # Create a scrolled window for the sessions list
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)
        vbox.append(scrolled_window)

        # Create a ListBox to display the sessions
        self.sessions_listbox = Gtk.ListBox()
        self.sessions_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled_window.set_child(self.sessions_listbox)

        # Load sessions from the database
        self.load_sessions()

        # New Session button
        new_session_button = Gtk.Button(label="Start a New Session")
        new_session_button.connect("clicked", self.on_new_session_clicked)
        new_session_button.set_margin_top(10)
        vbox.append(new_session_button)

        return vbox

    def load_sessions(self):
        # Clear existing rows
        index = 0
        while True:
            row = self.sessions_listbox.get_row_at_index(index)
            if row is None:
                break
            self.sessions_listbox.remove(row)

        # Fetch sessions ordered by last_message_at descending
        sessions = Session.select().order_by(Session.last_message_at.desc())
        for session in sessions:
            row = self.create_session_row(session)
            self.sessions_listbox.append(row)

    def create_session_row(self, session):
        # Create a box to hold session details and the Continue button
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.set_margin_top(5)
        hbox.set_margin_bottom(5)
        hbox.set_margin_start(5)
        hbox.set_margin_end(5)

        # Session details
        vbox_details = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        hbox.append(vbox_details)

        # Session name
        name_label = Gtk.Label(label=f"Session Name: {session.name}")
        name_label.set_xalign(0)
        vbox_details.append(name_label)

        # Working directory
        working_dir_label = Gtk.Label(label=f"Working Directory: {session.working_dir}")
        working_dir_label.set_xalign(0)
        vbox_details.append(working_dir_label)

        # Created at
        created_at_str = session.started_at
        created_at_label = Gtk.Label(label=f"Created At: {created_at_str}")
        created_at_label.set_xalign(0)
        vbox_details.append(created_at_label)

        # Last message at
        last_message_at_str = session.last_message_at
        last_message_at_label = Gtk.Label(label=f"Last Message At: {last_message_at_str}")
        last_message_at_label.set_xalign(0)
        vbox_details.append(last_message_at_label)

        # Spacer
        spacer = Gtk.Box()
        hbox.append(spacer)
        spacer.set_hexpand(True)

        # Continue button
        continue_button = Gtk.Button(label="Continue")
        continue_button.connect("clicked", self.on_continue_button_clicked, session)
        hbox.append(continue_button)

        # Delete button
        delete_button = Gtk.Button(label="Delete")
        delete_button.connect("clicked", self.on_delete_button_clicked, session)
        hbox.append(delete_button)

        return hbox

    def on_delete_button_clicked(self, button, session):
        self.delete_confirmation_dialog = Gtk.Dialog(title="Are you sure?", transient_for=self.window, modal=True)
        truncated_name = session.name[0:30] + "..." if len(session.name) > 30 else session.name
        self.delete_confirmation_dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            f"Delete {truncated_name}", Gtk.ResponseType.OK
        )
        content_area = self.delete_confirmation_dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)
        label = Gtk.Label(label=f"Are you sure you want to delete the session '{session.name}'?")
        content_area.append(label)
        self.delete_confirmation_dialog.connect("response", self.on_delete_confirmed, session)
        self.delete_confirmation_dialog.show()

    def on_delete_confirmed(self, dialog, response, session):
        if response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            return

        # Delete the session
        session.delete_instance()

        # Refresh the sessions list
        self.load_sessions()

        self.delete_confirmation_dialog.destroy()

    def on_continue_button_clicked(self, button, session):
        # Start chat with the selected session
        self.continue_chat(session)

    def on_new_session_clicked(self, button):
        # Create a dialog to get session name and working directory
        dialog = Gtk.Dialog(title="New Session", transient_for=self.window, modal=True)
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Create", Gtk.ResponseType.OK
        )

        # Dialog content area
        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)

        # Session name entry
        name_entry_label = Gtk.Label(label="Session Name:")
        content_area.append(name_entry_label)
        name_entry = Gtk.Entry()
        content_area.append(name_entry)

        # Working directory chooser
        file_dialog = Gtk.FileChooserDialog(
            title="Choose Working Directory",
            transient_for=dialog,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        file_dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Select", Gtk.ResponseType.ACCEPT
        )
        file_dialog.set_current_folder(Gio.File.new_for_path(os.getcwd()))
        selected_working_dir = os.getcwd()
        working_dir_entry_label = Gtk.Label(label="Working Dir:")
        content_area.append(working_dir_entry_label)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        working_dir_entry = Gtk.Entry()
        working_dir_entry.set_text(selected_working_dir)
        def change_working_dir(entry):
            selected_working_dir = entry.get_text()

        def on_working_dir_dialog_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                selected_working_dir = file_dialog.get_file().get_path()
                working_dir_entry.set_text(selected_working_dir)
            dialog.hide()
        file_dialog.connect("response", on_working_dir_dialog_response)


        working_dir_entry.connect("changed", change_working_dir)
        row.append(working_dir_entry)
        chooser_button = Gtk.Button(label="Browse")
        def on_chooser_button_clicked(button):
            file_dialog.show()

        chooser_button.connect("clicked", on_chooser_button_clicked)
        row.append(chooser_button)
        content_area.append(row)

        def on_dialog_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                session_name = name_entry.get_text()
                working_dir = selected_working_dir

                # Create a new session
                session = Session.create(
                    name=session_name,
                    working_dir=working_dir,
                    started_at=datetime.now(timezone.utc),
                    last_message_at=datetime.now(timezone.utc),
                )

                # Refresh the sessions list
                self.load_sessions()

                # Start chat with the new session
                self.start_chat(session)

            dialog.destroy()

        dialog.connect("response", on_dialog_response)
        dialog.show()

    def continue_chat(self, session):
        # Check if thre is a chat view for the session
        chat_view = self.stack.get_child_by_name(f"chat_view_{session.id}")
        if chat_view is not None:
            # Switch to the chat view
            self.stack.set_visible_child(chat_view)
        else:
            # Start chat with the session
            self.start_chat(session)

    def start_chat(self, session):
        # Create the chat interface
        default_llm = LLM(OpenAIBackend())
        default_chat = Chat(
            default_llm,
            [],  # context_paths
            session.working_dir,
            session=session,
        )
        chat_gui = ChatGUI(default_chat, self.on_back_to_sessions)

        # Add chat GUI to the stack
        self.stack.add_named(chat_gui.get_widget(), f"chat_view_{session.id}")

        # Switch to chat view
        self.stack.set_visible_child_name(f"chat_view_{session.id}")

    def on_back_to_sessions(self):
        # Switch back to the sessions view
        self.stack.set_visible_child_name("sessions_view")
        self.window.set_titlebar(None)

    def on_close_request(self, window):
        self.app.quit()
        return False  # Allow window to close

    def run(self):
        self.app.run(None)
