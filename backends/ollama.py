from base64 import b64encode
from config import Config


class OllamaBackend:
    tool_call_property = "tool_calls"
    tool_role = "tool"
    system_role = "system"

    function_support = {
        "phi4": False,
        "lamma3.2:3b": False,  # Actually True
        "lamma3.2:1b": False,  # Actually True
        "qwen2.5:0.5b": True,
    }

    default_context_size = {
        "phi4": 16 * 1024,
        "lamma3.2:3b": 4 * 1024,
        "lamma3.2:1b": 4 * 1024,
        "qwen2.5:0.5b": 4 * 1024,
    }

    def __init__(self):
        self.config = Config("ollama_cat.conf")
        self.ollama_api_conf = self.config.get_ollama_api()

        self.api_base_url = self.ollama_api_conf["url"]

    def get_default_model(self):
        return "llama3.2:3b"

    def get_endpoint(self, endpoint: str):
        return f"{self.api_base_url}/{endpoint}"

    def get_chat_endpoint(self):
        return "chat"

    def get_auth_headers(self):
        encoded = b64encode(
            f"{self.ollama_api_conf['username']}:{self.ollama_api_conf['password']}".encode(
                "utf-8"
            )
        ).decode("utf-8")
        return {"Authorization": f"Basic {encoded}"}

    def extract_message(self, response):
        return response["message"]

    def extract_usage(self, response):
        return None

    def append_functions(self, payload, functions, model):
        if not self.function_support.get(model):
            return payload

        payload["tools"] = [
            {"type": "function", "function ": function} for function in functions
        ]
        return payload

    def unwrap_function_call(self, function_call):
        return function_call["function"]

    def prepare_payload(self, messages, model, options=None):
        if not options:
            options = {}

        if "num_ctx" not in options:
            options["num_ctx"] = self.default_context_size.get(model, 4 * 1024)

        return {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": options,
        }
