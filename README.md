# CodeBro

CodeBro is a GTK4-based desktop chat application designed for AI-powered software development assistance. It provides an intuitive interface for interacting with various LLM backends while maintaining context awareness of your codebase.

## Features

- **Multi-Session Management**: Create and manage multiple chat sessions with persistent history
- **Context-Aware Conversations**: Automatically loads project files as context for more relevant AI assistance
- **Multiple LLM Backends**: Support for both OpenAI and Ollama APIs
- **File Operations**: Built-in tools for reading and writing files through LLM function calls
- **Command System**: Rich command interface for managing sessions, context, and chat history
- **GTK4 Interface**: Modern, responsive desktop GUI built with GTK4

## Architecture

### Core Components

#### Application Layer (`application.py`)
- **Application**: Main GTK4 application class managing the overall UI flow
- **Session Management**: Handles creation, deletion, and navigation between chat sessions
- **UI Orchestration**: Manages the stack-based navigation between sessions view and chat view

#### Chat System (`chat.py`)
- **Chat**: Core chat logic handling message flow and context management
- **Context Loading**: Automatically scans working directories and loads relevant files
- **Message History**: Maintains conversation history with database persistence
- **File Context**: Intelligently adds code files as context while respecting .gitignore patterns

#### Database Layer (`database.py`)
- **SQLite + Peewee ORM**: Lightweight database setup for local data persistence
- **Session Model**: Stores session metadata (name, working directory, timestamps)
- **Message Model**: Persists full conversation history with role and content
- **ContextPath Model**: Tracks which files/directories are loaded as context

#### LLM Integration (`llm.py`)
- **LLM**: Unified interface for different AI backends
- **Function Calling**: Supports LLM tool/function calling capabilities
- **Usage Tracking**: Monitors API usage across different models
- **Response Handling**: Processes both regular responses and function call requests

#### Backend Abstraction (`backends/`)
- **OpenAI Backend**: Integration with OpenAI's GPT models (o1-preview, gpt-4o)
- **Ollama Backend**: Local LLM support through Ollama API
- **Unified Interface**: Common API surface for different LLM providers
- **Authentication**: Handles API keys and authentication for each backend

#### Tool System (`tools/`)
- **File Operations**: Read and write file tools for LLM function calling
- **Tool Framework**: Decorator-based system for creating LLM-callable functions
- **Argument Validation**: Type-safe argument handling for tool functions

#### User Interface (`chat_gui.py`)
- **ChatGUI**: GTK4-based chat interface with message threading
- **Message Display**: Styled message bubbles with role-based formatting
- **Input Handling**: Multi-line text input with send functionality
- **Auto-scrolling**: Automatic scroll-to-bottom for new messages

#### Command Parser (`command_parser.py`)
- **Command System**: Handles special user commands (\\help, \\history, etc.)
- **Context Management**: Commands for adding/refreshing file context
- **Session Control**: Commands for managing chat history and sessions

### Data Flow

1. **Session Creation**: User creates a new session with name and working directory
2. **Context Loading**: System automatically scans working directory and loads relevant files
3. **Message Processing**: User messages are processed through the command parser or sent to LLM
4. **LLM Interaction**: Messages are sent to configured backend (OpenAI/Ollama) with context
5. **Function Calls**: LLM can call file operation tools to read/write files
6. **Response Display**: Assistant responses are displayed in the GUI with proper formatting
7. **Persistence**: All messages and session data are saved to SQLite database

### Configuration

- **Config System**: INI-based configuration for Ollama backend settings
- **API Keys**: OpenAI key stored in `openai_key` file
- **Model Selection**: Configurable model selection per backend

## Installation

### Prerequisites

- Python 3.8+
- GTK4 development libraries
- PyGObject (GTK4 Python bindings)

### Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

Key dependencies include:
- `PyGObject` - GTK4 Python bindings
- `peewee` - Lightweight ORM for SQLite
- `requests` - HTTP client for API calls
- `pycairo` - Cairo graphics library

### System Dependencies

On Ubuntu/Debian:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
```

On Fedora:
```bash
sudo dnf install python3-gobject gtk4-devel
```

## Configuration

### OpenAI Backend
Create an `openai_key` file in the project root with your OpenAI API key:
```
your-openai-api-key-here
```

### Ollama Backend
Create an `ollama_cat.conf` file with your Ollama configuration:
```ini
[OLLAMA_API]
url = http://localhost:11434/api/v1
username = your_username
password = your_password
default_chat_model = llama3.2:3b
```

## Usage

### Starting the Application

```bash
python main.py
```

### Basic Workflow

1. **Create a Session**: Click "Start a New Session" and provide a name and working directory
2. **Chat with AI**: Type messages in the input area and press "Send"
3. **Use Commands**: Type commands starting with `\` for special functions:
   - `\help` - Show available commands
   - `\history` - View message history
   - `\add_context <path>` - Add files/folders as context
   - `\refresh_context` - Reload context from files
   - `\usage` - Show API usage statistics

### File Operations

The AI can read and write files in your working directory using built-in tools:
- Ask the AI to read specific files: "Can you read the contents of main.py?"
- Request file modifications: "Please update the README with installation instructions"

### Session Management

- **Continue Sessions**: Return to previous conversations from the sessions list
- **Multiple Sessions**: Work on different projects simultaneously
- **Persistent History**: All conversations are saved and restored

## Development

### Project Structure

```
codebro/
├── main.py                 # Application entry point
├── application.py          # Main GTK4 application
├── chat.py                # Core chat logic
├── chat_gui.py            # GTK4 chat interface
├── database.py            # Database models
├── llm.py                 # LLM integration
├── command_parser.py      # Command system
├── config.py              # Configuration management
├── backends/              # LLM backend implementations
│   ├── __init__.py
│   ├── openai.py         # OpenAI integration
│   └── ollama.py         # Ollama integration
├── tools/                 # LLM function calling tools
│   ├── __init__.py
│   ├── base.py           # Tool framework
│   └── file_handling.py  # File operation tools
├── migrations/            # Database migrations
└── requirements.txt       # Python dependencies
```

### Adding New Backends

1. Create a new backend class implementing the required interface
2. Add authentication and endpoint configuration
3. Register the backend in `backends/__init__.py`
4. Update the application to use the new backend

### Creating New Tools

Use the `@llmtool` decorator to create new LLM-callable functions:

```python
from tools.base import llmtool, LLMToolArgument

@llmtool(
    name="my_tool",
    description="Description of what the tool does",
    args=[
        LLMToolArgument("param", "string", "Parameter description", required=True)
    ]
)
def my_tool(param):
    # Tool implementation
    return "Result"
```

## License

[License information not specified in repository]

## Contributing

[Contributing guidelines not specified in repository]
