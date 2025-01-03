#!/usr/bin/env python3
from argument_parser import parse_args

from codebro import CodeBro
from backends import OllamaBackend, OpenAIBackend
from tools import update_file, read_file

if __name__ == "__main__":
    parsed_args = parse_args()
    if not parsed_args.context_paths:
        print("Please provide at least one context path using the -c or --context_paths option.")
        exit(1)
    client = CodeBro(OpenAIBackend(), parsed_args.context_paths)
    client.add_function(update_file)
    client.add_function(read_file)
    client.main()
