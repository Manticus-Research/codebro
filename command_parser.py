import os
import json

class CommandParser:
    """
    CommandParser is responsible for handling user commands.

    Attributes:
        client (object): A client instance containing user history and usage statistics.
        commands (list): A list of command dictionaries containing command names (aliases), handler function, and help text.

    Methods:
        __init__(client):
            Initializes the command parser with a reference to the client and registers available commands.

        add_command(names, func, help_text=""):
            Registers a command with its aliases, handler function, and an optional help text.

        run(command_line):
            Parses the command_line to identify which registered command to execute, and calls the appropriate function with arguments.

        _exit(*args):
            Exits the program.

        _help(*args):
            Prints each registered command alongside its help text.

        _history(*args):
            Displays the client's previous messages in JSON format.

        _clear_history(*args):
            Clears the client's message history.

        _usage(*args):
            Aggregates and prints usage statistics, including prompt tokens, completion tokens, and the total.

        _debug(*args):
            Initiates a debugging session.

        _add_context(*args):
            Adds the specified file or directory as context for the assistant.

        _refresh_context(*args):
            Refreshes the context from the initial files or directories provided.
    """
    def __init__(self, client):
        self.client = client
        self.commands = []
        self.command_function_map = {}
        self.add_command(["\\exit", "\\quit", "\\q"], self._exit, "Quit the program")
        self.add_command(["\\help", "\\h"], self._help, "Display available commands")
        self.add_command(["\\history", "\\hist", "\\hi"], self._history, "Show previous messages")
        self.add_command(["\\clearhistory", "\\ch"], self._clear_history, "Clear previous messages")
        self.add_command(["\\usage", "\\u"], self._usage, "Show usage statistics")
        self.add_command(["\\debug", "\\d"], self._debug, "Start debugger")
        self.add_command(["\\add_context", "\\ac"], self._add_context, "<path> - Add a file or folder as context")
        self.add_command(["\\refresh_context", "\\rc"], self._refresh_context, "Refresh context from files")

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
                self.command_function_map[cmd](*args)
            except TypeError as e:
                print(f"Incorrect usage of {cmd}: {e}")
                # Find the command to get the usage
                command = next((c for c in self.commands if cmd in c["names"]), None)
                if command:
                    print(f"Usage: {'/'.join(command['names'])} {command['help']}")
                else:
                    print(f"No usage information for {cmd}")
            return
        else:
            print(f"Unknown command: {cmd}")
            print("Type '/help' to see available commands.")

    def _exit(self, *args):
        exit(0)

    def _help(self, *args):
        for command in self.commands:
            names = ', '.join(command['names'])
            print(f"{names} - {command['help']}")

    def _history(self, *args):
        for message in self.client.history:
            print(json.dumps(message, indent=2))

    def _clear_history(self, *args):
        self.client.history = []
        print("History cleared.")

    def _usage(self, *args):
        print(json.dumps(self.client.aggregate_usage, indent=2))

    def _debug(self, *args):
        import pdb; pdb.set_trace()

    def _add_context(self, *args):
        if not args:
            print("Usage: /add_context <path>")
            return
        path = ' '.join(args)
        if os.path.isfile(path):
            self.client.add_file_as_context(path)
            print(f"Added file '{path}' as context.")
        elif os.path.isdir(path):
            self.client.add_folder_as_context(path)
            print(f"Added directory '{path}' and its contents as context.")
        else:
            print(f"Invalid path: {path}")

    def _refresh_context(self, *args):
        self.client.refresh_context()
        print("Context refreshed.")
