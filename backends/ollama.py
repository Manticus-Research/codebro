from config import Config



class OllamaBackend:
    def __init__(self):
        self.config = Config('ollama_cat.conf')
        self.ollama_api_conf = self.config.get_ollama_api()

        self.api_base_url = self.ollama_api_conf['url']

    def get_model(self, usecase: str):
        return self.ollama_api_conf['default_chat_model']

    def get_endpoint(self, endpoint: str):
        return f"{self.api_base_url}/{endpoint}"

    def get_chat_endpoint(self):
        return "chat"

    def get_auth_headers(self):
        return {
            "Authorization": f"Basic {self.ollama_api_conf['username']}:{self.ollama_api_conf['password']}"
        }

    def extract_message(self, response):
        return response["message"]

    def extract_usage(self, response):
        return None
