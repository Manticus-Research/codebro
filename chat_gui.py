from nicegui import ui
from chat import Chat
import asyncio


class ChatGUI(Chat):
    def __init__(self, title, default_llm, context_paths, working_dir, session):
        super().__init__(default_llm, context_paths, working_dir, session)
        self.title = title
        self.last_displayed_message = 0

        # Store references to UI elements
        self.messages_container = None
        self.input_field = None

        # Flag to indicate if the app should exit
        self.exit_flag = False

    def construct_ui(self):
        @ui.page("/")
        def page():
            with ui.column().classes("w-full").style("height: calc(100vh - 2rem)"):
                with (
                    ui.row()
                    .classes("flex-grow w-full overflow-auto")
                    .style("box-sizing: border-box; height: 40px")
                ):
                    ui.label(f"{self.title}").classes("text-center")
                with (
                    ui.row()
                    .classes("flex-grow w-full overflow-auto")
                    .style("box-sizing: border-box; height: calc(80% - 40px)")
                ):
                    self.messages_container = ui.column().classes("w-full")
                with (
                    ui.row()
                    .classes("flex-grow w-full p-4")
                    .style("height: 20%; box-sizing: border-box;")
                ):
                    self.input_field = (
                        ui.input(placeholder="Type your message here...")
                        .props("autofocus")
                        .classes("w-full")
                    )
                    self.input_field.on(
                        "keydown",
                        lambda event: event.args["key"] == "Enter"
                        and self.send_message(),
                    )
                    ui.button("Send", on_click=self.send_message).classes("ml-2")

            # Start the background task to update the chat display
            ui.timer(0.5, self.update_chat_display)

    def send_message(self, _=None):
        message = self.input_field.value
        self.input_field.value = ""
        if message.strip():
            # Send to LLM asynchronously
            asyncio.create_task(self.handle_user_message(message))

    async def handle_user_message(self, message):
        await asyncio.to_thread(self.post_to_llm, self.default_llm, message)

    def update_chat_display(self):
        while self.last_displayed_message < len(self.history):
            message = self.history[self.last_displayed_message]
            self.print_message(message)
            self.last_displayed_message += 1

    def print_message(self, message):
        if message.get("is_context"):
            return

        sender = message.get("role", "")
        content = message.get("content", "")

        # Determine alignment and style based on sender
        if sender == "assistant":
            alignment = "start"
            bg_color = "lightgray"
            text_color = "black"
            sender_label = "Assistant"
        elif sender == "system":
            alignment = "center"
            bg_color = "#ffffe0"  # Light yellow
            text_color = "black"
            sender_label = "System"
        else:
            alignment = "end"
            bg_color = "#d1ffd6"  # Light green
            text_color = "black"
            sender_label = "You"

        with self.messages_container:
            with (
                ui.card()
                .style(
                    f"""
                        align-self: {alignment};
                        background-color: {bg_color};
                        color: {text_color};
                        max-width: 70%;
                        margin: 5px;
                        overflow-y: auto;
                    """
                )
                .classes("p-2")
            ):
                with ui.row():
                    ui.label(f"{sender_label}:").style("font-weight: bold")
                ui.markdown(content).classes("p-2")

        # Scroll to bottom
        self.messages_container.update()
        ui.run_javascript("window.scrollTo(0, document.body.scrollHeight);")

    def main(self):
        self.construct_ui()
        ui.run(title=self.title)

    def exit_app(self):
        # Set the exit flag to True
        self.exit_flag = True
