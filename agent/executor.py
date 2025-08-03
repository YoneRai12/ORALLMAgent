"""Plan execution utilities."""

from __future__ import annotations

from typing import Dict, Iterable, List

from .llm import LLMClient, Step
from . import tools

# Mapping from tool names to callables.  New tools can be registered here
# without having to touch the execution logic itself.
TOOL_REGISTRY = {
    "web_search": tools.web_search,
    "read_file": tools.read_file,
    "write_file": tools.write_file,
    "image_generate": tools.image_generate,
    "browser": tools.browser_automation,
    "echo": tools.echo,
}


def execute_plan(plan: Iterable[Step], llm: LLMClient) -> List[str]:
    """Execute *plan* sequentially using *llm* for optional reflection."""

    results: List[str] = []
    for step in plan:
        func = TOOL_REGISTRY.get(step.tool)
        if not func:
            results.append(f"unknown tool: {step.tool}")
            continue
        result = func(**step.args)
        results.append(result)
        llm.reflect(result)
    return results
