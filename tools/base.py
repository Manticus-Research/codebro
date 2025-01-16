class LLMToolArgument:
    def __init__(self, name, type, description, required=False, options=None):
        self.name = name
        self.type = type
        self.description = description
        self.required = required
        self.options = options

    def get_definition(self):
        definition = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
        }

        if self.options:
            definition["enum"] = self.options
        return definition


class LLMTool:
    def __init__(self, name, description, args, function):
        self.name = name
        self.description = description
        self.args = args
        self.function = function

    def get_arguments(self):
        return self.args

    def get_definition(self):
        return {
            "name": self.name,
            "description": "Run a language model.",
            "parameters": {
                "type": "object",
                "properties": {arg.name: arg.get_definition() for arg in self.args},
                "required": [arg.name for arg in self.args if arg.required],
            },
        }

    def __call__(self, *args, **kwargs):
        return staticmethod(self.function)(*args, **kwargs)


class llmtool:
    def __init__(self, name, description, args):
        self.name = name
        self.description = description
        self.args = args

    def __call__(self, function):
        return LLMTool(self.name, self.description, self.args, function)
