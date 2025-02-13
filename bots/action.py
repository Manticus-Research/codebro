class Action:
    """An action is a command that a bot can perform based on the messages it receives."""

    def __init__(self, conditions, action):
        self.conditions = conditions
        self.required_condition_ids = set([condition.id for condition in conditions])
        self.action = action

    def evaluate(self, met_conditions):
        """Evaluate whether the action should be performed."""
        met_condition_ids = set([condition.id for condition in met_conditions])
        return self.required_condition_ids.issubset(met_condition_ids)

    def perform(self, llm, messages):
        """Perform the action."""
        self.action(llm, messages)
