#!/usr/bin/env python3
import json
import requests
from typing import Dict

from tools import LLMTool


class LLM:
    def __init__(self, backend, model=None):
        self.usage = []
        self.functions = []  # Initialize a list for function definitions
        self.function_implementations_map = {}  # Initialize a map for function implementations
        self.backend = backend
        self.model = model or self.backend.get_default_model()
        # self.load_context()

    def add_tool(self, tool: LLMTool):
        definition = tool.get_definition()
        self.functions.append(definition)
        self.function_implementations_map[definition["name"]] = tool

    def request(self, method: str, endpoint: str, **kwargs):
        url = self.backend.get_endpoint(endpoint)

        auth_headers = self.backend.get_auth_headers()
        headers = kwargs.get("headers", {})
        headers.update(auth_headers)

        response = requests.request(method, url, headers=headers, **kwargs)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise

        return response

    def post_to_chat(self, messages: str):
        payload = self.backend.prepare_payload(messages, self.model)
        payload = self.backend.append_functions(payload, self.functions, self.model)
        response = self.request("POST", self.backend.get_chat_endpoint(), json=payload)

        return self.handle_chat_response(messages, response.json())

    def handle_chat_response(self, messages, response: Dict):
        message = self.backend.extract_message(response)
        usage = self.backend.extract_usage(response)
        if usage:
            self.usage.append(usage)

        new_messages = [message]

        if self.backend.tool_call_property in message:
            # The assistant wants to call a function

            calls = message[self.backend.tool_call_property]
            if not isinstance(calls, list):
                calls = [calls]
            for call in calls:
                new_messages.extend(self.handle_function_call(messages, call))

        return new_messages

    def handle_function_call(self, messages, emitted_call: Dict):
        function_call = self.backend.unwrap_function_call(emitted_call)
        function_name = function_call["name"]

        arguments = function_call["arguments"]
        function = self.function_implementations_map.get(function_name)

        if function is None:
            print(f"Function {function_name} not found.")
            return []

        try:
            result = function(**arguments)
        except Exception as e:
            result = f"Error: {e}"
            print(f"Error calling function: {e}")

        # Add the function's response to history
        function_response_message = {
            "role": self.backend.tool_role,
            "name": function_name,
            "content": json.dumps(result),
        }
        new_messages = [function_response_message]

        # Continue the conversation with the function's result
        payload = {
            "model": self.model,
            "messages": messages + [function_response_message],
            "stream": False,
        }
        response = self.request("POST", self.backend.get_chat_endpoint(), json=payload)

        return new_messages + self.handle_chat_response(messages, response.json())
