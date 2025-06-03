# Agent Project - TaskWarrior DSPy Assistant

This project includes a DSPy-based assistant to interact with Taskwarrior using natural language. It utilizes a local LLM (Phi-3 via Ollama) for processing requests.

## Setup

1.  **Ensure you are in the project root directory: `/home/tom/git/agent/`**

2.  **Create and activate a Python virtual environment (if you haven't already for this project):**
    ```bash
    python3.11 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install or update dependencies:**
    If `requirements.txt` is new or you've just created it:
    ```bash
    uv pip install -r requirements.txt
    ```
    If you are adding to an existing `requirements.txt`, ensure the new packages are installed.

4.  **Ensure Ollama is running and you have pulled the `phi3` model:**
    *   Install Ollama if you haven't: [https://ollama.com/](https://ollama.com/)
    *   Pull the model:
        ```bash
        ollama pull phi3
        ```
    *   Ensure Ollama server is running (it usually starts automatically after installation).

5.  **(Optional) Create a `.env` file in this directory (`/home/tom/git/agent/.env`) to customize settings:**
    ```env
    # OLLAMA_BASE_URL=http://localhost:11434
    # OLLAMA_MODEL=phi3
    ```
    The application will use sensible defaults if this file is not present. Note: Your global gitignore might prevent direct creation of this file by tools; you may need to create it manually.

6.  **Run the TaskWarrior assistant:**
    ```bash
    python taskwarrior_dspy_agent.py
    ```

## Development

*   The main TaskWarrior assistant script is `taskwarrior_dspy_agent.py`.
*   DSPy modules and signatures for Taskwarrior are in `taskwarrior_dspy_definitions.py`.
*   Remember to keep your local Ollama server running when developing or using the agent.
