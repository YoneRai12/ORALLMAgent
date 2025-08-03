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

try:  # Local model backend
    from llama_cpp import Llama  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Llama = None  # type: ignore


@dataclass
class Step:
    """Simple representation of an execution step planned by the LLM."""

    tool: str
    args: Dict[str, Any]
    description: str


class LLMClient:
    """Very small wrapper around an LLM provider.

    The client supports ``openai`` for hosted models and ``llama_cpp`` for local
    execution.  Additional providers can be integrated with minimal changes.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model_path: Optional[str] = None,
    ) -> None:
        self.provider = provider or "stub"
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model_path = model_path or os.getenv("LLM_MODEL_PATH")
        self._model = None
        if self.provider == "llama_cpp" and self.model_path and Llama is not None:
            try:
                self._model = Llama(model_path=self.model_path)
            except Exception:
                # Fallback to stub when model loading fails
                self.provider = "stub"

    # ------------------------------------------------------------------
    def plan(self, instruction: str) -> List[Step]:
        """Create a naive execution plan for *instruction*.

        The real implementation would send the request to the configured LLM
        provider.  If no provider is configured we return a deterministic plan
        so that the rest of the system can be exercised.
        """

        if self.provider == "openai" and self.api_key and openai is not None:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Plan steps to: {instruction}"}],
            )
            plan_text: str = response["choices"][0]["message"]["content"]  # type: ignore[index]
            return [Step(tool="echo", args={"text": plan_text}, description="raw plan")]

        if self.provider == "llama_cpp" and self._model is not None:
            out = self._model(f"Plan steps to: {instruction}")
            plan_text = out["choices"][0]["text"]  # type: ignore[index]
            return [Step(tool="echo", args={"text": plan_text}, description="raw plan")]

        # Fallback deterministic plan when no provider is configured
        return [
            Step(
                tool="echo",
                args={"text": f"LLM unavailable. Instruction was: {instruction}"},
                description="echo fallback",
            )
        ]

    # ------------------------------------------------------------------
    def reflect(self, result: str) -> str:
        """Allow the LLM to reflect on the latest *result*.

        When the provider is not available we simply return the original
        result.  This keeps the call synchronous for easier reasoning.
        """

        if self.provider == "openai" and self.api_key and openai is not None:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Reflect on: {result}"}],
            )
            return response["choices"][0]["message"]["content"]  # type: ignore[index]

        if self.provider == "llama_cpp" and self._model is not None:
            out = self._model(f"Reflect on: {result}")
            return out["choices"][0]["text"]  # type: ignore[index]

        return result
