# ORALLMAgent

Minimal prototype of an autonomous task execution system inspired by projects
like Manus.  The goal is to demonstrate a clean API surface that can later be
extended to chat bots, web apps or mobile clients.

## Features

* Accepts natural language instructions via an HTTP API.
* Asks an LLM to produce an execution plan.
* Executes the plan step by step using simple tool functions.
* Built‑in tools for web search, Amazon price lookup and Twitter automation.
* Generic browser automation powered by Playwright for logging into arbitrary
  web sites and performing actions in a human‑like manner.
* Command line interface with ``!websearch``, ``!amazon``, ``!twitter`` and
  ``!browser`` commands.
* Pluggable LLM backend: choose OpenAI, a local ``llama.cpp`` model or any
  ``transformers`` model via environment variables.
* After each step the LLM can perform a short reflection.
* The architecture separates planning, execution and the HTTP layer which makes
  it easy to integrate the core logic elsewhere.

## Usage

```bash
pip install -r requirements.txt
python -m playwright install  # installs browser drivers
uvicorn main:app --reload
```

Then send a request:

```bash
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" \
    -d '{"instruction": "write hello to test.txt"}'
```

Without an API key the system falls back to deterministic behaviour which keeps
it functional for local experiments.

### Windows quick start

The repository ships with a PowerShell script that installs Python (via
``winget``), clones this repository, prepares a virtual environment and installs
all dependencies.  Run the following from an elevated PowerShell prompt:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
./setup.ps1
```

After setup, start the API using:

```powershell
./run_agent.ps1
```

Environment variables such as API keys can be stored in a ``.env`` file.  A
``.env.example`` template is provided for convenience.  **Never commit real
credentials to source control.**  Store API keys and passwords in ``.env`` or
the Windows credential manager.

### Security notes

Credentials must never be hardcoded.  Populate the ``.env`` file or the
credential manager and reference variables from automation steps using the
``env`` field.  The browser tool intentionally stops when CAPTCHA or two‑factor
authentication is detected so the user can intervene manually.

### Command line usage

The ``cli.py`` helper exposes a very small command interface:

```bash
python cli.py "!websearch sushi"
python cli.py "!amazon raspberry pi"
python cli.py "!twitter tweet hello world"
python cli.py "!browser https://example.com '[{"action":"click","selector":"#login"}]'"
```

Twitter commands require API credentials.  Amazon scraping is intended for
simple experiments and may need adjustments to comply with Amazon's terms of
service.
