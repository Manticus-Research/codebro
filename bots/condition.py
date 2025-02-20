import json

import uuid

class Condition:
    """A condition is a rule that a chat excerpt must meet in order to trigger an action."""

    def __init__(self, name, description, filter_messages=None):
        self.description = description
        self.name = name
        def noop(messages):
            return messages
        self.filter_messages = filter_messages or noop

    def evaluate(self, messages):
        """Evaluate whether a chat excerpt meets the condition."""
        raise NotImplementedError("Conditions must implement the evaluate method.")


class LLMCondition(Condition):
    """A condition that uses a language model to evaluate chat excerpts."""

    def __init__(self, name, description, filter_messages, llm, condition_prompt):
        super().__init__(name, description, filter_messages)
        self.llm = llm
        self.condition_prompt = condition_prompt

    def evaluate(self, messages):
        """Evaluate whether a chat excerpt meets the condition."""
        messages = self.filter_messages([message for message in messages if not message.get("is_context")])
        if not messages:
            return False

        condition_evaluation_prompt = {
            "role": "system",
            "content": ""
            "You MUST evaluate whether a chat excerpt meets a condition that will be provided.\n"
            "You MUST respond with a boolean value (Yes or No).\n"
            "YOU WILL NOT try to mak up reasons to say no.\n"
            "Lean towards saying yes.\n"
        }

        message_boundary = uuid.uuid4().hex
        response_messages = self.llm.post_to_chat(
            [
                condition_evaluation_prompt,
                {
                    "role": "user",
                    "content": (
                        "Does the chat excerpt meet the following condition?\n"
                        + f"Condition: {self.condition_prompt}\n"
                        + f"Boundary: {message_boundary}\n"
                        + "Chat Excerpt:\n"
                        + f"\n{message_boundary}\n".join(
                            [f"{msg['role']}:\n {msg['content']}" for msg in messages]
                        )
                    ),
                },
            ],
        )

        print(response_messages)
        if "yes" in response_messages[-1]["content"].lower():
            return True
        elif "no" in response_messages[-1]["content"].lower():
            return False
        else:
            print(response_messages)
            import pdb; pdb.set_trace()
            raise ValueError("Invalid response to condition evaluation")
