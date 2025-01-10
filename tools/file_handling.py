from .base import LLMToolArgument, llmtool


@llmtool(
    name="write_file",
    description="Overwrite a file with new content.",
    args=[
        LLMToolArgument("file_path", "string", "Path to the file to update.", required=True),
        LLMToolArgument("content", "string", "Content to write to the file.", required=True),
    ],
)
def write_file(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)
    return f"Wrote to file: {file_path}"


@llmtool(
    name="read_file",
    description="Read the contents of a file.",
    args=[
        LLMToolArgument("file_path", "string", "Path to the file to read.", required=True),
    ],
)
def read_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    return content
