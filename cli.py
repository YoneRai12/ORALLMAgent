"""Command line interface for service automation tools."""

from __future__ import annotations

import json
import sys

from dotenv import load_dotenv

from agent.tools import (
    amazon_search,
    browser_automation,
    twitter_post_tweet,
    twitter_send_dm,
    web_search,
)


def main() -> None:
    """Entry point for the CLI.

    Commands
    --------
    !websearch <query>
        Run a DuckDuckGo search.
    !amazon <product>
        Search Amazon for a product and return the first price.
    !twitter tweet <message>
        Post a tweet with *message*.
    !twitter dm <user> <message>
        Send a DM to *user* with *message*.
    !browse <url> <USER_ENV> <PASS_ENV> [actions_json]
        Log into a website and optionally perform extra actions. ``actions_json``
        is a JSON array describing follow-up steps.
    """

    load_dotenv()
    command = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("> ").strip()

    if command.startswith("!websearch"):
        query = command[len("!websearch") :].strip()
        print(web_search(query))
    elif command.startswith("!amazon"):
        product = command[len("!amazon") :].strip()
        print(amazon_search(product))
    elif command.startswith("!twitter"):
        rest = command[len("!twitter") :].strip()
        if rest.startswith("tweet"):
            msg = rest[len("tweet") :].strip()
            print(twitter_post_tweet(msg))
        elif rest.startswith("dm"):
            parts = rest.split(maxsplit=2)
            if len(parts) < 3:
                print("usage: !twitter dm <user> <message>")
            else:
                print(twitter_send_dm(parts[1], parts[2]))
        else:
            print("unknown twitter subcommand")
    elif command.startswith("!browse"):
        parts = command.split(maxsplit=4)
        if len(parts) < 4:
            print("usage: !browse <url> <USER_ENV> <PASS_ENV> [actions_json]")
        else:
            url, user_env, pass_env = parts[1:4]
            actions = json.loads(parts[4]) if len(parts) > 4 else []
            print(browser_automation(url, user_env, pass_env, actions))
    else:
        print("unknown command")


if __name__ == "__main__":
    main()
