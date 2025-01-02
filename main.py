import json
import os, fnmatch
import requests
from typing import Dict, List

from command_parser import CommandParser
from argument_parser import parse_args

from backends import OllamaBackend, OpenAIBackend

class CodeBro:
    def __init__(self, backend, context_paths):
        self.history = []
        self.usage = []
        self.backend = backend
        self.context_paths = context_paths
        self.load_context()

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
        ignore_patterns = []
        gitignore_path = os.path.join(folder_path, '.gitignore')
        if os.path.isfile(gitignore_path):
            with open(gitignore_path) as f:
                ignore_patterns = [
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
        response = self.request(
            'POST',
            self.backend.get_chat_endpoint(),
            json={
                'messages': self.history,
                'model': self.backend.get_model('chat'),
                "stream": False,
            }
        )

        return response.json()

    def handle_chat_response(self, response: Dict):
        message = self.backend.extract_message(response)
        self.history.append(message)
        self.usage.append(self.backend.extract_usage(response))
        print(message['content'])

    def handle_command(self, command: str):
        parser = CommandParser(self)
        parser.run(command)

    def main(self):
        while True:
            prompt = input("> ")
            if prompt.startswith("/"):
                self.handle_command(prompt)
            else:
                chat_response = self.post_to_chat(prompt)
                self.handle_chat_response(chat_response)

if __name__ == "__main__":
    parsed_args = parse_args()
    if not parsed_args.context_paths:
        print("Please provide at least one context path using the -c or --context_paths option.")
        exit(1)
    client = CodeBro(OpenAIBackend(), parsed_args.context_paths)
    client.main()
