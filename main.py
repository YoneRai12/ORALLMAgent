"""Minimal FastAPI application exposing the agent as an HTTP API."""

from __future__ import annotations

import os
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from agent.llm import LLMClient, Step
from agent.planner import plan_task
from agent.executor import execute_plan
from agent.tools import (
    amazon_search,
    twitter_post_tweet,
    twitter_send_dm,
    web_search,
)
load_dotenv()
app = FastAPI(title="ORALLM Agent")


class TaskRequest(BaseModel):
    """Request schema for the `/tasks` endpoint."""

    instruction: str


class TaskResponse(BaseModel):
    """Response schema returned after executing a task."""

    plan: List[Step]
    results: List[str]


llm_client = LLMClient(provider=os.getenv("LLM_PROVIDER"), api_key=os.getenv("LLM_API_KEY"))


@app.post("/tasks", response_model=TaskResponse)
def run_task(req: TaskRequest) -> TaskResponse:
    """Create a plan for ``req.instruction`` and execute it."""

    plan = plan_task(req.instruction, llm_client)
    results = execute_plan(plan, llm_client)
    return TaskResponse(plan=plan, results=results)


@app.get("/websearch")
def api_websearch(q: str) -> str:
    """Run a DuckDuckGo search for ``q``."""

    return web_search(q)


@app.get("/amazon")
def api_amazon(q: str) -> str:
    """Search Amazon for ``q`` and return the first price."""

    return amazon_search(q)


class TweetRequest(BaseModel):
    """Schema for posting a tweet."""

    message: str


@app.post("/twitter/tweet")
def api_twitter_tweet(req: TweetRequest) -> dict:
    """Post ``req.message`` to Twitter."""

    return {"status": twitter_post_tweet(req.message)}


class DMRequest(BaseModel):
    """Schema for sending a direct message."""

    user: str
    message: str


@app.post("/twitter/dm")
def api_twitter_dm(req: DMRequest) -> dict:
    """Send a DM to ``req.user``."""

    return {"status": twitter_send_dm(req.user, req.message)}
