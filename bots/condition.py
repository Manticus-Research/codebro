class Condition:
    """A condition is a rule that a chat excerpt must meet in order to trigger an action."""

    def __init__(self, name, description):
        self.description = description
        self.name = name
