"""Browser automation helpers using Playwright.

This module performs simple login and post-login actions using Playwright.  It
simulates basic human behaviour with small delays.  **Never hard-code real
credentials; use environment variables or a credential manager.**
"""

from __future__ import annotations

import random
from typing import Dict, List

from playwright.sync_api import sync_playwright


def _slow_type(locator, text: str) -> None:
    """Type ``text`` into ``locator`` with random delays."""

    for ch in text:
        locator.type(ch, delay=random.randint(50, 150))


def login_and_run(url: str, username: str, password: str, actions: List[Dict[str, str]]) -> str:
    """Log into ``url`` and execute additional ``actions``.

    Parameters
    ----------
    url:
        Login page URL.
    username/password:
        Credentials for the site.  They must be supplied securely by the caller.
    actions:
        List of dictionaries describing follow-up actions.  Supported keys are
        ``action`` ("goto"/"click"/"type"/"wait"), ``selector``, ``text`` and
        ``url``/``ms`` depending on the action.
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        user = page.query_selector("input[type='email'], input[type='text'][name*='user'], input[name*='email']")
        pw = page.query_selector("input[type='password']")
        submit = page.query_selector("button[type='submit'], input[type='submit']")
        if not user or not pw or not submit:
            browser.close()
            return "login form not found; manual intervention required"

        user.click()
        _slow_type(user, username)
        pw.click()
        _slow_type(pw, password)
        submit.click()
        page.wait_for_load_state("networkidle")

        for act in actions:
            kind = act.get("action")
            if kind == "goto":
                dest = act.get("url")
                if dest:
                    page.goto(dest)
            elif kind == "click":
                sel = act.get("selector")
                if sel and (el := page.query_selector(sel)):
                    el.click()
                    page.wait_for_timeout(300)
            elif kind == "type":
                sel = act.get("selector")
                txt = act.get("text", "")
                if sel and (el := page.query_selector(sel)):
                    el.click()
                    _slow_type(el, txt)
            elif kind == "wait":
                ms = int(act.get("ms", 1000))
                page.wait_for_timeout(ms)

        browser.close()
        return "completed"
