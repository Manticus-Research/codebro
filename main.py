#!/usr/bin/env python3
import os

from argument_parser import parse_args
from backends import OllamaBackend, OpenAIBackend
from database import database, Session, ContextPath
from migrations.migrate import upgrade
from llm import LLM
from tools import write_file, read_file

from chat_gui import ChatGUI  # Import the updated ChatGUI

if __name__ in ("__main__", "__mp_main__"):
    upgrade(database)

    parsed_args = parse_args()
    local_llm = LLM(OllamaBackend())
    local_llm.add_tool(write_file)
    local_llm.add_tool(read_file)
    openai_llm = LLM(OpenAIBackend())

    working_dir = os.path.abspath(parsed_args.working_dir)
    working_dir_name = os.path.basename(working_dir)
    session_name = f"CodeBud Chat - {working_dir_name}"

    session = Session.select().where(Session.name == session_name).first()
    if session:
        context_paths = [
            context_path.path for context_path in session.context_paths or []
        ]
    else:
        session = Session.create(
            name=session_name,
            working_dir=working_dir,
        )
        for context_path in parsed_args.context_paths:
            ContextPath.create(
                path=context_path,
                session=session,
            )

    chat = ChatGUI(
        session_name,
        openai_llm,
        parsed_args.context_paths,
        parsed_args.working_dir,
        session=session,
    )
    # Start the NiceGUI app
    chat.main()
