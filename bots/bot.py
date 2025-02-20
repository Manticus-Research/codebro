# Example of an action
# conditions = [
#   Condition("code_requested", "The user requested a code change or new code to be written."),
#   Condition("code_generated", "The assistant generated code in response to a user request."),
#   Condition("file_intent", "The generated code is intended to be written to a file."),
# ]
# write_to_file = Action(
#    lambda met_conditions: all(
#       condition in met_conditions for condition in [conditions[0], conditions[1], conditions[2]]
#    ),
#    lambda llm, messages:
#       changes = extract_code_changes(llm, messages)
#       for change in changes:
#           write_to_file(change)
#   ),
#

class Bot:
    """A bot is an entity that monitors the chat and perform actions based on the messages it receives."""

    def __init__(self, llm, actions):
        self.llm = llm
        self.conditions = sum([action.conditions for action in actions], [])
        self.actions = actions

    def handle_message(self, messages):
        """Handle a message from the chat."""
        met_conditions = self.evaluate_conditions(messages)
        selected_actions = self.select_actions(met_conditions)
        return selected_actions

    def select_actions(self, met_conditions):
        """Select actions based on the conditions met."""
        return [action for action in self.actions if action.evaluate(met_conditions)]

    def evaluate_conditions(self, messages):
        """Evaluate whether a chat excpert meets any conditions."""
        met_conditions = []
        for condition in self.conditions:
            if condition.evaluate(messages):
                met_conditions.append(condition)

        return met_conditions

    def apply_actions(self, met_conditions, messages):
        """Map conditions to actions."""
        for action in self.actions:
            if action.evaluate(met_conditions):
                action.perform(messages)
            else:
                continue
