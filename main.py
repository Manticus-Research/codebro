#!/usr/bin/env python3
from argument_parser import parse_args

from llm import LLM
from chat import Chat
from backends import OllamaBackend, OpenAIBackend
from tools import write_file, read_file

if __name__ == "__main__":
    parsed_args = parse_args()
    llm = LLM(OllamaBackend())
    llm.add_tool(write_file)
    llm.add_tool(read_file)
    chat = Chat(llm, parsed_args.context_paths or [], parsed_args.working_dir)
    chat.main()
