from typing import Tuple
from maubot import Plugin, MessageEvent
from maubot.handlers import command

class ExampleBot(Plugin):
    @command.passive(r'(https?://open\.spotify\.com/(track|album|artist|playlist|user|episode|show)/[a-zA-Z0-9]+)')
    async def command(self, evt: MessageEvent, match: Tuple[str]) -> None:
        spotify_url = match[0]

        try:
            # Make HTTP request to song.link API using maubot's built-in client 【1】【2】
            api_url = f"https://api.song.link/v1-alpha.1/links?url={spotify_url}"
            response = await self.http.get(api_url)

            if response.status == 200:
                data = await response.json()
                page_url = data.get('pageUrl')

                if page_url:
                    await evt.reply(f"🎵 Universal link: {page_url}")
                else:
                    await evt.reply("❌ Could not find universal link")
            else:
                await evt.reply(f"❌ API error: {response.status}")

        except Exception as e:
            await evt.reply(f"❌ Error: {str(e)}")
