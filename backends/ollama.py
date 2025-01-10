from base64 import b64encode
from config import Config



class OllamaBackend:
    tool_call_property = "tool_calls"
    tool_role = "tool"
    system_role = "system"

    function_support= {
        "phi3.5": False,
        "lamma3.2:3b": False,  # Actually True
        "lamma3.2:1b": False,  # Actually True
        "qwen2.5:0.5b": True,
    }

    def __init__(self):
        self.config = Config('ollama_cat.conf')
        self.model = self.config.get_ollama_api()['default_chat_model']
        self.ollama_api_conf = self.config.get_ollama_api()

        self.api_base_url = self.ollama_api_conf['url']

    def get_model(self, usecase: str):
        return self.model

    def get_endpoint(self, endpoint: str):
        return f"{self.api_base_url}/{endpoint}"

    def get_chat_endpoint(self):
        return "chat"

    def get_auth_headers(self):
        encoded = b64encode(f"{self.ollama_api_conf['username']}:{self.ollama_api_conf['password']}".encode("utf-8")).decode('utf-8')
        return {
            "Authorization": f"Basic {encoded}"
        }

    def extract_message(self, response):
        return response["message"]

    def extract_usage(self, response):
        return None

    def append_functions(self, payload, functions):
        if not self.function_support.get(self.model):
            return payload

        payload["tools"] = [
            {
                "type": "function",
                "function": function
            } for function in functions
        ]
        return payload

    def unwrap_function_call(self, function_call):
        return function_call['function']
