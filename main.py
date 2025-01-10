#!/usr/bin/env python3
from argument_parser import parse_args

from llm import LLM
from chat_gui import ChatGUI  # Import the new ChatGUI class
from backends import OllamaBackend, OpenAIBackend
from tools import write_file, read_file

if __name__ == "__main__":
    parsed_args = parse_args()
    local_llm = LLM(OllamaBackend())
    local_llm.add_tool(write_file)
    local_llm.add_tool(read_file)
    openai_llm = LLM(OpenAIBackend())
    chat = ChatGUI(openai_llm, parsed_args.context_paths or [], parsed_args.working_dir)
    chat.main()
