from collections import defaultdict
from datetime import datetime
import os
import fnmatch
from command_parser import CommandParser

class Chat:
    def __init__(self, default_llm, context_paths, working_dir):
        self.default_llm = default_llm
        self.history = []
        self.command_parser = CommandParser(self)
        self.context_paths = context_paths
        self.working_dir = working_dir
        self.context = {}
        self.llms = {}
        self.load_context()
        self.last_displayed_message = 0
        self.setup_assistant_prompt()

    def add_llm(self, llm, role):
        self.llms[role] = llm

    def add_message(self, message):
        self.messages.append(message)

    def get_messages(self):
        return self.messages

    def get_name(self):
        return self.name

    def __str__(self):
        return self.name

    def add_file_as_context(self, file_path: str):
        with open(file_path, 'r') as f:
            self.context[file_path] = f.read()

        with open(file_path, 'r') as f:
            context = f.read()
            self.history.append({
                "role": "user",
                "content": f"File: {file_path}\n----------------",
                "is_context": True
            })

            self.history.append({
                "role": "user",
                "content": context,
                "is_context": True
            })

            self.history.append({
                "role": "user",
                "content": f"File: {file_path} end of file",
                "is_context": True
            })

    def add_folder_as_context(self, folder_path: str):
        ignore_patterns = [".git/*"]
        gitignore_path = os.path.join(folder_path, '.gitignore')
        if os.path.isfile(gitignore_path):
            with open(gitignore_path) as f:
                ignore_patterns += [
                    line.strip() for line in f
                    if line.strip() and not line.startswith('#')
                ]
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename == '.gitignore':
                    continue
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, folder_path)
                if not any(fnmatch.fnmatch(rel_path, pat) for pat in ignore_patterns):
                    self.add_file_as_context(full_path)

    def load_context(self):
        self.add_folder_as_context(self.working_dir)

        for context_path in self.context_paths:
            if os.path.isfile(context_path):
                self.add_file_as_context(context_path)
            elif os.path.isdir(context_path):
                self.add_folder_as_context(context_path)
            else:
                print(f"Invalid context path: {context_path}")
                raise ValueError(f"Invalid context path: {context_path}")

    def refresh_context(self):
        # Remove all context messages from history
        self.history = [msg for msg in self.history if not msg.get('is_context')]
        # Reload the context
        self.load_context()
        print("Context refreshed.")

    def post_to_llm(self, llm, message):
        wrapped_message = {
            "role": "user",
            "content": message
        }
        self.history.append(wrapped_message)
        llm.post_to_chat(self.history)

    def main(self):
        COMMAND_PREFIX = "\\"

        while True:
            prompt = input("> ")
            if prompt.startswith(COMMAND_PREFIX):
                self.command_parser.run(prompt)
            else:
                print("========================================")
                self.post_to_llm(self.default_llm, prompt)
                while self.last_displayed_message < len(self.history):
                    self.print_message(self.history[self.last_displayed_message])
                    self.last_displayed_message += 1

    def print_message(self, message):
        if message.get('is_context'):
            return

        if message.get("role") == "user":
            return

        print(f"{datetime.now().isoformat()} - {message['role']}:")
        print(message['content'])
        print("========================================")

    def setup_assistant_prompt(self):
        self.history.append({
            "role": self.default_llm.backend.system_role,
            "content": """
                You are a software development assistant.
                You will be able to interact with the codebase and perform various tasks.
                When you are asked to modify, alter, change, augment or manipulate code, you MUST use the provided tools.
                You MUST not remove code unless asked to do so.
                You MUST take care to not overwrite existing code when using the provided tools.
                You will be helpful, precise and thorough.

            """,
        })

    @property
    def aggregate_usage(self):
        usage = [
            (self.default_llm.get_model(), self.default_llm.usage),
        ]
        for role, llm in self.llms.items():
            usage.append((llm.get_model(), llm.usage))

        by_model = defaultdict(list)
        for model, usage in usage:
            by_model[model] += usage

        total_usage_by_model = {}
        for model, usage in by_model.items():
            total_usage = defaultdict(int)
            for message_usage in by_model[model]:
                for key, value in message_usage.items():
                    total_usage[key] += value
            total_usage_by_model[model] = total_usage

        return total_usage_by_model
