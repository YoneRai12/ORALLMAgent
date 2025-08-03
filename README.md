# ORALLMAgent

Minimal prototype of an autonomous task execution system inspired by projects
like Manus.  The goal is to demonstrate a clean API surface that can later be
extended to chat bots, web apps or mobile clients.

## Features

* Accepts natural language instructions via an HTTP API.
* Asks an LLM to produce an execution plan.
* Executes the plan step by step using simple tool functions.
* Built‑in tools for web search, Amazon price lookup and Twitter automation.
* Command line interface with ``!websearch``, ``!amazon`` and ``!twitter``
  commands.
* After each step the LLM can perform a short reflection.
* The architecture separates planning, execution and the HTTP layer which makes
  it easy to integrate the core logic elsewhere.

## Usage

```bash
pip install -r requirements.txt
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

### Command line usage

The ``cli.py`` helper exposes a very small command interface:

```bash
python cli.py "!websearch sushi"
python cli.py "!amazon raspberry pi"
python cli.py "!twitter tweet hello world"
```

Twitter commands require API credentials.  Amazon scraping is intended for
simple experiments and may need adjustments to comply with Amazon's terms of
service.
