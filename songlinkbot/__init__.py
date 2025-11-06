from typing import Tuple
from maubot import Plugin, MessageEvent
from maubot.handlers import command


class SongLinkBot(Plugin):
    async def __handle_music_url(self, evt: MessageEvent, url: str, silent_on_no_result: bool = False) -> None:
        api_url = f"https://api.song.link/v1-alpha.1/links?url={url}"
        response = await self.http.get(api_url)

        if response.status != 200:
            if not silent_on_no_result:
                await evt.reply(f"❌ API error: {response.status}")
            return

        data = await response.json()
        page_url = data.get('pageUrl')

        if not page_url:
            if not silent_on_no_result:
                await evt.reply("❌ Could not find universal link")
            return

        # Use the entityUniqueId to get canonical entity details if available
        entity_unique_id = data.get('entityUniqueId')
        if not entity_unique_id:
            await evt.reply(f"🎵 Universal link: {page_url}")
            return

        entities = data.get('entitiesByUniqueId', {})
        entity = entities.get(entity_unique_id)

        if not entity:
            await evt.reply(f"🎵 Universal link: {page_url}")
            return

        title = entity.get('title', 'Unknown')
        artist = entity.get('artistName', 'Unknown')

        await evt.reply(f"🎵 **{title}** - {artist}\n🔗 {page_url}")

    @command.passive(r'(https?://open\.spotify\.com/(track|album|artist|playlist|user|episode|show)/[a-zA-Z0-9]+)')
    @command.passive(r'(https?://[a-zA-Z0-9-]+\.bandcamp\.com/(track|album)/[^\s]+)')
    @command.passive(r'(https?://(?:youtu\.be/[^\s]+|(?:www\.)?(?:music\.)?youtube\.com/watch\?[^\s]+))')
    @command.passive(r'(https?://(?:m\.)?soundcloud\.com/[^\s]+)')
    @command.passive(r'(https?://(?:music|itunes)\.apple\.com/[^\s]+)')
    @command.passive(r'(https?://(?:listen\.)?tidal\.com/(?:browse/)?(?:track|album|playlist|artist)/[^\s]+)')
    @command.passive(r'(https?://(?:www\.)?deezer\.com/[^\s]+)')
    @command.passive(r'(https?://music\.amazon\.[^/\s]+/[^\s]+)')
    @command.passive(r'(https?://(?:app\.)?napster\.com/[^\s]+)')
    @command.passive(r'(https?://(?:www\.)?pandora\.com/[^\s]+)')
    async def link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        url = match[0]
        await self.__handle_music_url(evt, url)