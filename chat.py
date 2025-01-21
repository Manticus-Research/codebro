import uuid
import json
import os
import fnmatch
from hashlib import md5

from collections import defaultdict
from datetime import datetime

from command_parser import CommandParser
from database import Message, ContextPath  # Import database models


class Chat:
    def __init__(self, default_llm, context_paths, working_dir, session):
        self.default_llm = default_llm
        self.command_parser = CommandParser(self)
        self.context_paths = context_paths
        self.known_context = set()
        self.working_dir = os.path.relpath(working_dir, os.getcwd())
        self.session = session
        self.llms = {}
        self.history = []
        for msg in session.messages:
            self._add_message_to_history(json.loads(msg.full_message))
        self.last_displayed_message = 0

        if not self.history:
            self.setup_assistant_prompt()
        self.load_context()

    def add_llm(self, llm, role):
        self.llms[role] = llm

    def _add_message_to_history(self, message):
        self.history.append(message)
        if message.get("is_context"):
            self.known_context.add(message["context_hash"])

    def add_message(self, message):
        self._add_message_to_history(message)
        Message.create(
            session=self.session,
            role=message["role"],
            content=message["content"],
            full_message=json.dumps(message),
            model=self.default_llm.get_model(),
        )

        self.session.last_message_at = datetime.now()
        self.session.save()

    def get_messages(self):
        return self.history

    def get_name(self):
        return self.session.name

    def __str__(self):
        return self.session.name

    def add_context_path(self, path):
        resolved_path = os.path.abspath(path)
        if os.path.isfile(path):
            self._add_file_as_context(path)
        elif os.path.isdir(path):
            self._add_folder_as_context(path)
        else:
            return
        ContextPath.create(
            path=resolved_path,
            session=self.session,
        )
        return path

    def _get_file_content(self, file_path):
        is_binary = False
        with open(file_path, "r") as f:
            try:
                content = f.read()
            except UnicodeDecodeError:
                is_binary = True
                content = ""
        _hash = md5(content.encode()).hexdigest()
        return content, _hash, is_binary

    def _add_file_as_context(self, file_path: str):
        relative_path = os.path.relpath(file_path, self.working_dir)

        file_content, file_content_hash, is_binary = self._get_file_content(file_path)
        if file_content_hash in self.known_context or is_binary:
            return
        self.known_context.add(file_content_hash)
        boundary = uuid.uuid4().hex
        message_content = (
            f"File: {relative_path}\nBoundary: {boundary}\n{file_content}{boundary}\n"
        )
        self.add_message(
            {
                "role": "user",
                "content": message_content,
                "is_context": True,
                "context_hash": file_content_hash,
            }
        )

    def _add_folder_as_context(self, folder_path: str):
        ignore_patterns = [".git/*"]
        gitignore_path = os.path.join(folder_path, ".gitignore")
        if os.path.isfile(gitignore_path):
            with open(gitignore_path) as f:
                ignore_patterns += [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        for root, _dirs, files in os.walk(folder_path):
            for filename in files:
                if filename == ".gitignore":
                    continue
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, folder_path)
                if not any(fnmatch.fnmatch(rel_path, pat) for pat in ignore_patterns):
                    self._add_file_as_context(full_path)

    def load_context(self):
        self._add_folder_as_context(self.working_dir)

        for context_path in self.context_paths:
            if os.path.isfile(context_path):
                self._add_file_as_context(context_path)
            elif os.path.isdir(context_path):
                self._add_folder_as_context(context_path)
            else:
                print(f"Invalid context path: {context_path}")
                raise ValueError(f"Invalid context path: {context_path}")

    def refresh_context(self):
        # Reload the context
        self.load_context()
        print("Context refreshed.")

    def post_to_llm(self, llm, message):
        wrapped_message = {"role": "user", "content": message}
        self.add_message(wrapped_message)
        assistant_messages = llm.post_to_chat(self.history)
        for msg in assistant_messages:
            self.add_message(msg)

    def get_chat_history(self):
        return [msg for msg in self.history if not msg.get("internal")]

    def clear_history(self):
        # Delete messages from the database for this session
        Message.delete().where(Message.session == self.session).execute()
        self.history = []

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
        if message.get("is_context"):
            return

        if message.get("role") == "user":
            return

        print(f"{datetime.now().isoformat()} - {message['role']}:")
        print(message["content"])
        print("========================================")

    def setup_assistant_prompt(self):
        self.add_message(
            {
                "role": self.default_llm.backend.system_role,
                "content": """
                You are a software development assistant.
                You will be able to interact with the codebase and perform various tasks.
                You MUST not remove code unless asked to do so.
                You MUST take care to not overwrite existing code when using the provided tools.
                You will be helpful, precise and thorough.

            """,
            }
        )

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
