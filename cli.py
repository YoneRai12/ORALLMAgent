"""Command line interface for service automation tools."""

from __future__ import annotations

import sys

from dotenv import load_dotenv

from agent.tools import (
    amazon_search,
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
    else:
        print("unknown command")


if __name__ == "__main__":
    main()
