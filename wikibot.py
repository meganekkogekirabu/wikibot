import logging
import os
import re
import sys
import discord
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("discord.wikibot")


def get_env(k) -> str:
    k = "WIKIBOT_" + k
    v = os.getenv(k)

    if v is None:
        print(f"could not get environment variable {k}")
        sys.exit(1)
    else:
        return v


class Wikibot(discord.Client):
    wikilink = re.compile(r"\[\[(?:([^:]*?):)?([^\]\|]+)(?:\|[^\]]+)?\]\]")
    template = re.compile(r"\{\{([^\}]+)(?:\|[^\]]+)?\}\}")
    lang = get_env("LANG")
    family = get_env("FAMILY")
    root = f"https://{lang}.{family}.org/wiki"

    def format_link(self, namespace: str, title: str) -> str:
        if namespace == "Template":
            return f"[{{{{`{title}`}}}}](<{self.root}/{title}>)"
        else:
            return f"[[[`{title}`]]](<{self.root}/{title}>)"

    def parse_message(self, message: str) -> list[tuple[str, str]]:
        """
        Parse message into list of tuples (namespace, title).
        """
        ret = []

        for m in self.template.finditer(message):
            title = m.groups()[0]
            ret.append(("Template", title))

        for m in self.wikilink.finditer(message):
            ret.append(m.groups())

        return ret

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")
        await self.change_presence(
            status=discord.Status.online, activity=discord.Game("holy guacamole")
        )

    async def on_message(self, message):
        if message.author == self.user:
            return

        links = self.parse_message(message.content)

        if len(links) == 0:
            return

        for i, link in enumerate(links):
            links[i] = self.format_link(*link)

        links = ", ".join(links)
        links = "Links: " + links

        await message.channel.send(links)


def main():
    token = get_env("TOKEN")

    intents = discord.Intents(messages=True, message_content=True)
    client = Wikibot(intents=intents)

    client.run(token)


if __name__ == "__main__":
    main()
