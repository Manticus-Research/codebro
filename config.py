import configparser

class Config:
    def __init__(self, filename: str):
        self.config = configparser.ConfigParser()
        self.config.read(filename)

    def get_ollama_api(self) -> dict:
        return {
            'url': self.get('OLLAMA_API', 'url'),
            'username': self.get('OLLAMA_API', 'username'),
            'password': self.get('OLLAMA_API', 'password'),
            'default_chat_model': self.get('OLLAMA_API', 'default_chat_model'),
        }

    def get(self, section: str, option: str) -> str:
        value = None
        try:
            value = self.config[section][option]
        except KeyError:
            pass
        if not value:
            raise KeyError(f"Missing configuration for {section}.{option}")
        return value
