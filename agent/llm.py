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

try:
    from llama_cpp import Llama  # type: ignore
except Exception:  # pragma: no cover
    Llama = None  # type: ignore

try:
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover
    pipeline = None  # type: ignore


@dataclass
class Step:
    """Simple representation of an execution step planned by the LLM."""

    tool: str
    args: Dict[str, Any]
    description: str


class LLMClient:
    """Very small wrapper around an LLM provider."""

    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.provider = provider or os.getenv("LLM_PROVIDER", "stub")
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        # Optional backends for local models
        self._llama = None
        self._pipe = None
        if self.provider == "llama_cpp" and Llama:
            model_path = os.getenv("LLAMA_MODEL_PATH")
            if model_path:
                self._llama = Llama(model_path=model_path)
        elif self.provider == "transformers" and pipeline:
            model_name = os.getenv("HF_MODEL_NAME", "gpt2")
            try:
                self._pipe = pipeline("text-generation", model=model_name)
            except Exception:
                self._pipe = None

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
        if self.provider == "llama_cpp" and self._llama is not None:
            output = self._llama(f"Plan steps to: {instruction}", max_tokens=128)
            plan_text = output["choices"][0]["text"]  # type: ignore[index]
            return [Step(tool="echo", args={"text": plan_text}, description="raw plan")]
        if self.provider == "transformers" and self._pipe is not None:
            plan_text = self._pipe(f"Plan steps to: {instruction}")[0]["generated_text"]
            return [Step(tool="echo", args={"text": plan_text}, description="raw plan")]
        # Fallback stub implementation
        if not self.api_key or self.provider == "stub":
            return [
                Step(
                    tool="echo",
                    args={"text": f"LLM unavailable. Instruction was: {instruction}"},
                    description="echo fallback",
                )
            ]
        return [Step(tool="echo", args={"text": "LLM provider unavailable"}, description="error")]

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
        if self.provider == "llama_cpp" and self._llama is not None:
            output = self._llama(f"Reflect on: {result}", max_tokens=64)
            return output["choices"][0]["text"]  # type: ignore[index]
        if self.provider == "transformers" and self._pipe is not None:
            return self._pipe(f"Reflect on: {result}")[0]["generated_text"]
        return result
