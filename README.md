# Agent Project - SimpleDSPy Agent

This project features a DSPy-based agent that can run commands and interact with users. It uses OpenRouter models for processing requests.

## Setup

1.  **Ensure you are in the project root directory: `/home/tom/git/agent/`**

2.  **Run the setup script**
    ```bash
    ./setup_env.sh
    ```
    This creates a Python virtual environment in `.venv`, installs the requirements and
    generates an `.env.example` file. Copy `.env.example` to `.env` and fill in your
    API keys.

3.  **(Manual setup)** If you prefer to do things manually, create and activate the virtual
    environment and install dependencies yourself:
    ```bash
    python3.11 -m venv .venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```

4.  **Set up OpenRouter API key:**
    *   Create a free account at [OpenRouter](https://openrouter.ai/)
    *   Add your API key to environment variables:
        ```bash
        echo "export OPENROUTER_API_KEY='your_api_key'" >> ~/.bashrc
        source ~/.bashrc
        ```

5.  **Run the SimpleDSPy agent:**
    ```bash
    python agent_simpledspy.py
    ```

## Training Data Management

The agent's performance depends on quality training data stored in `.simpledspy/modules/`. To improve results:

1.  **Review logged interactions:**
    ```bash
    less .simpledspy/modules/*/logged.jsonl
    ```

2.  **Add good samples to training data:**
    Copy well-performing examples from `logged.jsonl` to corresponding `training.jsonl` files

3.  **Correct problematic samples:**
    Edit `training.jsonl` to fix incorrect responses

4.  **Add new training examples:**
    Create new entries in `training.jsonl` for desired behaviors

## Development

*   The main agent script is `agent_simpledspy.py`
*   Training data is stored in `.simpledspy/modules/`
*   Use `--lm` flag to switch models: `flash`, `r1`, or `dv3`
    ```bash
    python agent_simpledspy.py --lm r1
    ```
