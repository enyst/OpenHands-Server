# OpenHands Server

As of 2025-08-15 this is a work in progress and subject to rapid change.

A REST/WebSocket interface for OpenHands AI Agent. This server provides HTTP and WebSocket endpoints to interact with the OpenHands agent programmatically.

## Quickstart

- Prerequisites: Python 3.12+, curl
- Install uv (package manager):

  ```
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Restart your shell so "uv" is on PATH, or follow the installer hint
  ```

### Run the server locally

```
# Install dependencies (incl. dev tools)
make install-dev

# Optional: install pre-commit hooks
make install-pre-commit-hooks

# Start the server
make run
# or
uv run openhands-server
```

Tip: Set your model key (one of) so the agent can talk to an LLM:

```
export OPENAI_API_KEY=...
# or
export LITELLM_API_KEY=...
```

### Build a standalone executable

```
# Build (installs PyInstaller if needed)
./build.sh --install-pyinstaller

# The binary will be in dist/
./dist/openhands-server            # macOS/Linux
# dist/openhands-server.exe        # Windows
```

For advanced development (adding deps, updating the spec file, debugging builds), see Development.md.

## API Endpoints

### REST API
- `GET /health` - Health check endpoint
- `POST /chat` - Send a message to the agent
- `GET /status` - Get agent status

### WebSocket API
- `WS /ws` - Real-time communication with the agent

## About

REST/WebSocket interface for OpenHands AI Agent, providing programmatic access to agent capabilities.