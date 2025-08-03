"""Utility tool functions used by the agent.

Each tool is a plain Python function so the agent can easily expose
function-calling style interfaces to an LLM.  The implementations here are
minimal stubs suitable for a prototype.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List, Dict

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import tweepy

# Browser automation imports are optional; Playwright is heavy and may not be
# installed in minimal environments.  Import lazily inside the function.


def web_search(query: str) -> str:
    """Search the web via DuckDuckGo and return a short summary."""

    results = []
    with DDGS() as ddgs:
        for res in ddgs.text(query, max_results=3):
            title = res.get("title", "")
            body = res.get("body", "")
            results.append(f"{title}: {body}")
    return "\n".join(results) if results else "no results found"


def amazon_search(product: str) -> str:
    """Fetch the first price for *product* from Amazon.

    Uses a simple HTTP request and HTML scraping. Credentials are read from
    environment variables ``AMAZON_USERNAME`` and ``AMAZON_PASSWORD``. The
    login step here is only illustrative and may need adjustments for real
    use.
    """

    session = requests.Session()
    # Placeholder for an actual login flow using session.post(...)
    _user = os.getenv("AMAZON_USERNAME")
    _password = os.getenv("AMAZON_PASSWORD")
    if not _user or not _password:
        return "Amazon credentials not configured"

    headers = {"User-Agent": "Mozilla/5.0"}
    resp = session.get("https://www.amazon.com/s", params={"k": product}, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    first = soup.select_one("div[data-component-type='s-search-result']")
    if not first:
        return "no results"
    title = first.h2.get_text(strip=True)
    price = first.select_one("span.a-price-whole")
    price_text = price.get_text(strip=True) if price else "N/A"
    return f"{title} - {price_text}"


def twitter_post_tweet(message: str) -> str:
    """Post ``message`` to Twitter using API credentials from ``.env``."""

    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")
    if not all([api_key, api_secret, access_token, access_secret]):
        return "Twitter credentials not configured"

    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    api = tweepy.API(auth)
    api.update_status(message)
    return "tweet posted"


def twitter_send_dm(username: str, message: str) -> str:
    """Send a direct message to ``username`` with ``message``."""

    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")
    if not all([api_key, api_secret, access_token, access_secret]):
        return "Twitter credentials not configured"

    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    api = tweepy.API(auth)
    user = api.get_user(screen_name=username)
    api.send_direct_message(user.id, message)
    return "dm sent"


def read_file(path: str) -> str:
    """Read a text file.

    This is a convenience wrapper around :class:`pathlib.Path` that ignores
    errors and returns an empty string if the file does not exist.
    """

    p = Path(path)
    return p.read_text() if p.exists() else ""


def write_file(path: str, content: str) -> str:
    """Write *content* to *path*.

    Parameters
    ----------
    path:
        Destination file path.
    content:
        Text content to write.

    Returns
    -------
    str
        Confirmation message.
    """

    Path(path).write_text(content)
    return f"wrote {len(content)} characters"


def image_generate(prompt: str) -> str:
    """Stub image generation function.

    In a real system this would call out to an external image generation
    service.  For now it only returns a textual acknowledgement.
    """

    return f"[image] would generate: {prompt}"


def browser_action(url: str, steps: List[Dict[str, Any]]) -> str:
    """Automate a sequence of browser interactions using Playwright.

    SECURITY WARNING: Do not hardcode credentials in code.  Provide secrets via
    environment variables or the Windows credential manager.  This function is
    intentionally simple and does not attempt to bypass CAPTCHA or two-factor
    authentication; if such mechanisms are detected the caller should prompt
    the user for manual input.

    Parameters
    ----------
    url:
        Initial URL to open.
    steps:
        List of action dictionaries.  Supported keys:

        ``action``
            One of ``goto``, ``click``, ``type`` or ``wait``.
        ``selector``
            CSS selector used for ``click``/``type``/``wait`` actions.
        ``text``
            Literal text to type for ``type`` actions.
        ``env``
            Name of an environment variable whose value will be typed instead of
            ``text``.

    Returns
    -------
    str
        Status message describing the outcome.
    """

    import random
    import time
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        for step in steps:
            action = step.get("action")
            if action == "goto":
                page.goto(step["url"])
            elif action == "click":
                page.click(step["selector"], delay=random.randint(50, 150))
            elif action == "type":
                value = step.get("text", "")
                env_name = step.get("env")
                if env_name:
                    value = os.getenv(env_name, "")
                page.click(step["selector"])
                page.type(step["selector"], value, delay=random.randint(50, 150))
            elif action == "wait":
                page.wait_for_selector(step["selector"], timeout=step.get("timeout", 5000))
            time.sleep(random.uniform(0.2, 0.5))
        content = page.content().lower()
        browser.close()
    if "captcha" in content or "two-factor" in content:
        return "manual intervention required"
    return "browser actions completed"


def echo(text: str) -> str:
    """Simple helper tool that just echoes text back."""

    return text
