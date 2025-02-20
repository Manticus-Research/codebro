Code assist.

1. Specification gatherer.
    - Read the chat and gather notes about the requirements sourrounding the system.

2. Typist
    - Read the chat find generated code and write it to the filesystem.

3. Code Watcher
    - Watch the filesystem and keep track of agent and user changes to the codebase.
-----------------------------------------------------------------------------

Specs Interrogator
==================

1. Wait for user input.
2. Evaluate user input.
3. Ask more details.
4. Express assumptions.


Code writing agent.
=====================

1. Environment.
-----------

- A docker image containing the code.


2. Actions
-------------

- Modify code.
- Execute bash commands?


3. Reasoning Process
--------------------

    1. Retrieve Goal
    2. Sense environment state.
    3, Propose changes
    4. Apply changes
    5. Evaluate change impact.


-----------------------------------------------------------------

Next steps.

1. Add the typist and specification gatherer bots.
    A bot is an entity that observes a chat and generates actions based
    on the chat.

2. Define Code projects
    A project may have multiple sessions with different llms etc.
    A project is something an agent can work on.
    As a user I should be able to crud projects and crud sessions related
    to projects.
