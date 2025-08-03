"""High level planning helpers."""

from __future__ import annotations

from typing import List

from .llm import LLMClient, Step


def plan_task(instruction: str, llm: LLMClient) -> List[Step]:
    """Ask *llm* to create a plan for *instruction*."""

    return llm.plan(instruction)
