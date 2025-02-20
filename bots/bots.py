from .bot import Bot
from .action import Action
from .condition import Condition, LLMCondition

from llm import LLM
from backends import OllamaBackend, OpenAIBackend

llm = LLM(OllamaBackend())

import re
import json

def extract_code_changes(llm, message):
    """Extract code changes from a message."""
    code = message.get("content", "")
    if not code.strip():
        return []
    # Extract code chunks wrapped in triple backticks
    chunks = re.findall(r"```(?:\w+)?\n(.*?)\n```", code, flags=re.DOTALL)
    if not chunks:
        chunks = [code]  # fallback to full content if no backticks found

    # Build a prompt listing the extracted chunks.
    prompt = (
        "The following are code chunks extracted from a generated message. "
        "For each chunk, determine the intended file path to which it should be applied (if any), "
        "and whether the provided code is complete or partial (partial code will contain ellipsis '...').\n"
        "Return a JSON array of objects, each containing:\n"
        "  - 'file': the intended file path as a string or null if unspecified\n"
        "  - 'complete': a boolean, true if the snippet is a complete code block, false if partial\n"
        "  - 'changes': the code chunk as a string\n"
        "Do not include any extra text.\n"
    )
    for idx, chunk in enumerate(chunks):
        prompt += f"\nChunk {idx+1}:\n{chunk}\n"

    response = llm.post_to_chat([], [{"role": "user", "content": prompt}])
    try:
        changes = json.loads(response[-1]["content"])
    except Exception:
        # Fallback: treat each chunk as a change with unknown details.
        changes = [{"file": None, "complete": None, "changes": chunk} for chunk in chunks]

    # # For each partial change, ask llm to classify each line.
    # for change in changes:
    #     if change.get("complete") is False:
    #         code_chunk = change.get("changes", "")
    #         classification_prompt = (
    #             "For the following partial code snippet (which may contain ellipsis '...'), "
    #             "classify each line into one of the categories: 'ellipsis' (if it is an ellipsis line), "
    #             "'context' (if it is unchanged context), or 'new' (if it is new or modified code).\n"
    #             "Return a JSON array where each element is an object with 'line_number' (1-indexed) and 'classification'.\n"
    #             "Do not include any extra text.\n"
    #             "The code snippet is delimited by triple backticks:\n"
    #             "```\n" + code_chunk + "\n```"
    #         )
    #         analysis_response = llm.post_to_chat([], [{"role": "user", "content": classification_prompt}])
    #         try:
    #             analysis = json.loads(analysis_response[-1]["content"])
    #             change["analysis"] = analysis
    #         except Exception:
    #             change["analysis"] = None
    return changes


def write_to_file(change):
    """Write a code change to a file."""
    file_path = change.get("file")
    code = change.get("changes")
    if file_path:
        with open(file_path, "w") as f:
            f.write(code)


def write_code(llm, messages):
    """Write code to a file."""
    last_message = messages[-1]
    changes = extract_code_changes(llm, last_message)
    for change in changes:
        write_to_file(change)


code_writer_bot = Bot(
    llm,
    [
        Action(
            [
                # LLMCondition(
                #     "code_requested",
                #     "Checks if the user requested a code change or new code to be written.",
                #     lambda messages: [messages[-2]] if len(messages) > 2 and messages[-2]["role"] == "user" else [],
                #     llm,
                #     "The user requested a code change or new code to be written.",
                # ),
                LLMCondition(
                    "file_path",
                    "Check whether there is a file path in the message.",
                    lambda messages: [messages[-1]] if messages and messages[-1]["role"] == "assistant" else [],
                    llm,
                    "There is a file path in the message.",
                ),
                LLMCondition(
                    "code_generated",
                    "Check whether the assistant generated code in response to a user request.",
                    lambda messages: [messages[-1]] if messages and messages[-1]["role"] == "assistant" else [],
                    llm,
                    "There is code in the message.",
                ),
            ],
            write_code,
        ),
    ],
)
