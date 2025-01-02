class OpenAIBackend:
    def __init__(self):
        self.model = "o1-preview"
        self.api_base_url = "https://api.openai.com/v1"
        with open('openai_key') as f:
            self.api_key = f.read().strip()

    def get_model(self, usecase: str):
        return self.model

    def get_endpoint(self, endpoint: str):
        return f"{self.api_base_url}/{endpoint}"

    def get_chat_endpoint(self):
        return "chat/completions"

    def get_auth_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    def extract_message(self, response):
        return response["choices"][0]["message"]

    def extract_usage(self, response):
        return response["usage"]
