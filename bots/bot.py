import json

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
        # self.chat = chat
        self.conditions = sum([action.conditions for action in actions], [])
        self.actions = actions
        # self.internal_state = {
        #     "condition_evaluation_context": [],
        # }

    def handle_message(self, messages):
        """Handle a message from the chat."""
        met_conditions = self.evaluate_conditions(messages)
        # selected_actions = self.select_actions(met_conditions)
        # self.perform_actions(selected_actions)

    def evaluate_conditions(self, messages):
        """Evaluate whether a chat excpert meets any conditions."""

        met_conditions = []
        condition_evaluation_prompt = {
            "role": self.llm.backend.system_role,
            "content": ""
            "You MUST evaluate whether a chat excerpt meets a condition that will be provided.\n"
            "You MUST respond with a boolean value (TRUE or FALSE) and nothing else.\n"
            "You MUST NOT respond in any other way.\n"
            "The chat excerpt WILL be in json format",
        }
        evaluation_messages = [
            condition_evaluation_prompt,
            {
                "role": self.llm.backend.system_role,
                "content": "The chat excerpt is as follows:\n"
                f"{json.dumps(messages)}",
            },
        ]
        for condition in self.conditions:
            response_messages = self.llm.post_to_chat(
                self.chat,
                evaluation_messages
                + {
                    "role": self.llm.backend.system_role,
                    "content": f"The condition is as follows:{condition.description}",
                },
            )
            if response_messages[-1]["content"] == "TRUE":
                met_conditions.append(condition)
            elif response_messages[-1]["content"] == "FALSE":
                continue
            else:
                raise ValueError("Invalid response to condition evaluation")
        return met_conditions

    def apply_actions(self, met_conditions, messages):
        """Map conditions to actions."""
        for action in self.actions:
            if action.evaluate(met_conditions):
                action.perform(messages)
            else:
                continue
