#!/usr/bin/env python3

import json
import os, fnmatch
import requests
from typing import Dict, List

from tools import LLMTool
from command_parser import CommandParser

class CodeBro:
    def __init__(self, backend, context_paths):
        self.history = []
        self.usage = []
        self.functions = []  # Initialize a list for function definitions
        self.function_implementations_map = {}  # Initialize a map for function implementations
        self.backend = backend
        self.context_paths = context_paths
        self.load_context()

    def add_function(self, tool: LLMTool):
        definition = tool.get_definition()
        self.functions.append(definition)
        self.function_implementations_map[definition['name']] = tool

    def load_context(self):
        for context_path in self.context_paths:
            if os.path.isfile(context_path):
                self.add_file_as_context(context_path)
            elif os.path.isdir(context_path):
                self.add_folder_as_context(context_path)
            else:
                print(f"Invalid context path: {context_path}")
                exit(1)

    def refresh_context(self):
        # Remove all context messages from history
        self.history = [msg for msg in self.history if not msg.get('is_context')]
        # Reload the context
        self.load_context()
        print("Context refreshed.")

    def request(self, method: str, endpoint: str, **kwargs):
        url = self.backend.get_endpoint(endpoint)

        auth_headers = self.backend.get_auth_headers()
        headers = kwargs.get('headers', {})
        headers.update(auth_headers)

        response = requests.request(method, url, headers=headers, **kwargs)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            import pdb; pdb.set_trace()
            raise

        return response

    def add_file_as_context(self, file_path: str):
        with open(file_path, 'r') as f:
            try:
                context = f.read()
            except:
                import pdb; pdb.set_trace()
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
        ignore_patterns = [".git/*",]
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

    def post_to_chat(self, message: str):
        wrapped_message = {
            "role": "user",
            "content": message
        }
        self.history.append(wrapped_message)
        payload = {
            'model': self.backend.get_model('chat'),
            'messages': self.history,
            "stream": False,
        }
        payload = self.backend.append_functions(payload, self.functions)
        response = self.request(
            'POST',
            self.backend.get_chat_endpoint(),
            json=payload
        )

        return response.json()

    def handle_chat_response(self, response: Dict):
        message = self.backend.extract_message(response)
        self.history.append(message)
        self.usage.append(self.backend.extract_usage(response))

        if 'function_call' in message:
            # The assistant wants to call a function
            function_call = message['function_call']
            self.handle_function_call(function_call)
        else:
            # Regular assistant message
            print(message['content'])

    def handle_function_call(self, function_call):
        function_name = function_call['name']
        arguments = json.loads(function_call['arguments'])
        function = self.function_implementations_map.get(function_name)
        if function is None:
            print(f"Function {function_name} not found.")
            return

        result = function(*arguments)

        # Add the assistant's function call to history
        self.history.append({
            "role": "assistant",
            "content": None,
            "function_call": function_call,
        })

        # Add the function's response to history
        self.history.append({
            "role": "function",
            "name": function_name,
            "content": json.dumps(result),
        })

        # Continue the conversation with the function's result
        payload = {
            'model': self.backend.get_model('chat'),
            'messages': self.history,
            "stream": False,
        }
        response = self.request(
            'POST',
            self.backend.get_chat_endpoint(),
            json=payload
        )
        self.handle_chat_response(response.json())

    def main(self):
        while True:
            prompt = input("> ")
            if prompt.startswith("/"):
                self.handle_command(prompt)
            else:
                chat_response = self.post_to_chat(prompt)
                self.handle_chat_response(chat_response)

    def handle_command(self, command: str):
        parser = CommandParser(self)
        parser.run(command)
