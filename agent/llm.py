"""LLM helper utilities.

The real system would talk to OpenAI, Anthropic or a local model.  The
implementation below keeps the interface but falls back to deterministic
responses when no API key is provided.  This keeps the prototype fully
functional in offline environments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import os

try:  # Optional import; the package may not be installed.
    import openai  # type: ignore
except Exception:  # pragma: no cover - we do not want tests to fail here
    openai = None  # type: ignore


@dataclass
class Step:
    """Simple representation of an execution step planned by the LLM."""

    tool: str
    args: Dict[str, Any]
    description: str


class LLMClient:
    """Very small wrapper around an LLM provider."""

    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.provider = provider or "stub"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    # ------------------------------------------------------------------
    def plan(self, instruction: str) -> List[Step]:
        """Create a naive execution plan for *instruction*.

        The real implementation would send the request to the configured LLM
        provider.  If no provider is configured we return a deterministic plan
        so that the rest of the system can be exercised.
        """

        if not self.api_key or self.provider == "stub" or openai is None:
            return [
                Step(
                    tool="echo",
                    args={"text": f"LLM unavailable. Instruction was: {instruction}"},
                    description="echo fallback",
                )
            ]

        # Example call to OpenAI's API.  Error handling is purposely omitted for
        # brevity; production code should be more robust.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Plan steps to: {instruction}"}],
        )
        plan_text: str = response["choices"][0]["message"]["content"]  # type: ignore[index]
        # For a prototype we expect the model to return JSON-like structures.
        # In production one would want proper parsing and safety checks.
        return [Step(tool="echo", args={"text": plan_text}, description="raw plan")]

    # ------------------------------------------------------------------
    def reflect(self, result: str) -> str:
        """Allow the LLM to reflect on the latest *result*.

        When the provider is not available we simply return the original
        result.  This keeps the call synchronous for easier reasoning.
        """

        if not self.api_key or self.provider == "stub" or openai is None:
            return result

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Reflect on: {result}"}],
        )
        return response["choices"][0]["message"]["content"]  # type: ignore[index]
