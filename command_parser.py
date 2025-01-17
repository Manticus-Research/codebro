import json


class CommandParser:
    """
    CommandParser is responsible for handling user commands.
    """

    def __init__(self, client):
        self.client = client
        self.commands = []
        self.command_function_map = {}
        self.add_command(["\\exit", "\\quit", "\\q"], self._exit, "Quit the program")
        self.add_command(["\\help", "\\h"], self._help, "Display available commands")
        self.add_command(
            ["\\history", "\\hist", "\\hi"], self._history, "Show previous messages"
        )
        self.add_command(
            ["\\clearhistory", "\\ch"], self._clear_history, "Clear previous messages"
        )
        self.add_command(["\\usage", "\\u"], self._usage, "Show usage statistics")
        self.add_command(["\\debug", "\\d"], self._debug, "Start debugger")
        self.add_command(
            ["\\add_context", "\\ac"],
            self._add_context,
            "<path> - Add a file or folder as context",
        )
        self.add_command(
            ["\\refresh_context", "\\rc"],
            self._refresh_context,
            "Refresh context from files",
        )
        self.add_command(
            ["\\clear_commands", "\\cc"],
            self._clear_commands,
            "Delete all command messags",
        )

    def add_command(self, names, func, help_text=""):
        if isinstance(names, str):
            names = [names]
        self.commands.append({"names": names, "func": func, "help": help_text})
        for name in names:
            self.command_function_map[name] = func

    def run(self, command_line):
        parts = command_line.strip().split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]
        if cmd in self.command_function_map:
            try:
                result = self.command_function_map[cmd](*args)
                if result:
                    return result
            except TypeError as e:
                error_message = f"Incorrect usage of {cmd}: {e}"
                # Find the command to get the usage
                command = next((c for c in self.commands if cmd in c["names"]), None)
                if command:
                    error_message += (
                        f"\nUsage: {' / '.join(command['names'])} {command['help']}"
                    )
                else:
                    error_message += f"\nNo usage information for {cmd}"
                return error_message
        else:
            return f"Unknown command: {cmd}\nType '\\help' to see available commands."

    def _exit(self, *args):
        # Since we're in a GUI, we should close the application gracefully
        self.client.exit_app()
        return "Exiting application."

    def _help(self, *args):
        output = []
        for command in self.commands:
            names = ", ".join(command["names"])
            output.append(f"{names} - {command['help']}")
        return "\n".join(output)

    def _history(self, *args):
        output = []
        for message in self.client.history:
            output.append(json.dumps(message, indent=2))
        return "\n".join(output)

    def _clear_history(self, *args):
        self.client.clear_history()
        return "History cleared."

    def _usage(self, *args):
        usage_info = json.dumps(self.client.aggregate_usage, indent=2)
        return usage_info

    def _debug(self, *args):
        return "Debugger not implemented."

    def _add_context(self, *args):
        if not args:
            return "Usage: \\add_context <path>"
        path = " ".join(args)

        added = self.client.add_context_path(path)
        if added:
            return f"Added context: {added}"
        else:
            return f"Could not add context: {path}"

    def _refresh_context(self, *args):
        self.client.refresh_context()
        return "Context refreshed."

    def _clear_commands(self, *args):
        self.client.clear_commands()
        return "Commands cleared."
