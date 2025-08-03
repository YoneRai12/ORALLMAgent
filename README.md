# ORALLMAgent

Minimal prototype of an autonomous task execution system inspired by projects
like Manus.  The goal is to demonstrate a clean API surface that can later be
extended to chat bots, web apps or mobile clients.

## Features

* Accepts natural language instructions via an HTTP API.
* Asks an LLM to produce an execution plan.
* Executes the plan step by step using simple tool functions.
* Built‑in tools for web search, Amazon price lookup, Twitter automation and
  generic browser control via Playwright.
* Command line interface with ``!websearch``, ``!amazon``, ``!twitter`` and
  ``!browse`` commands.
* After each step the LLM can perform a short reflection.
* The architecture separates planning, execution and the HTTP layer which makes
  it easy to integrate the core logic elsewhere.

## Usage

```bash
pip install -r requirements.txt
playwright install  # installs browser binaries
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
``winget``), clones this repository, prepares a virtual environment, installs
all dependencies and downloads Playwright browser binaries.  Run the following
from an elevated PowerShell prompt:

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
python cli.py "!browse https://example.com/login EXAMPLE_SITE_USERNAME EXAMPLE_SITE_PASSWORD"
```

Twitter commands require API credentials.  Amazon scraping is intended for
simple experiments and may need adjustments to comply with Amazon's terms of
service.  Generic browsing uses real browser automation and may trigger
CAPTCHA or 2FA challenges; the agent will not attempt to bypass them and should
prompt for manual input when necessary.

### LLM configuration

Set ``LLM_PROVIDER`` in ``.env`` to ``openai``, ``llama_cpp`` or ``stub``.  When
using local models provide ``LLM_MODEL_PATH`` pointing to the model file.

### Security notes

* Keep `.env` outside version control and restrict file permissions.
* Prefer Windows Credential Manager for long‑term storage of passwords.
* Browser automation should respect target site terms of service.  Manual
  intervention is required for CAPTCHA/2FA challenges.
