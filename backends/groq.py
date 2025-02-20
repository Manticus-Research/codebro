class GroqBackend:
    function_support = {
        "llama-3.3-70b-versatile": True,
        "mistral-8x7b-32768": True,
    }

    tool_call_property = "function_call"
    tool_role = "function"
    system_role = "user"

    def __init__(self):
        self.api_base_url = "https://api.groq.com/openai/v1"
        with open("groq_key") as f:
            self.api_key = f.read

    def get_default_model(self, usecase: str):
        return "llama-3.3-70b-versatile"

    def get_endpoint(self, endpoint: str):
        return f"{self.api_base_url}/{endpoint}"

    def get_chat_endpoint(self):
        return "chat/completions"

    def get_auth_headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def extract_message(self, response):
        return response["choices"][0]["message"]

    def extract_usage(self, response):
        return response.get("usage", {})

    def append_functions(self, payload, functions, model):
        if self.function_support.get(model):
            payload["functions"] = functions
            payload["function_call"] = "auto"

        return payload

    def unwrap_function_call(self, function_call):
        return function_call

    def prepare_payload(self, messages, model, options=None):
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,

        }
        if options:
            payload.update(options)
        return payload
