from typing import Tuple, Optional
from maubot import Plugin, MessageEvent
from maubot.handlers import command


class SongLinkBot(Plugin):
    async def __handle_music_url(self, evt: MessageEvent, url: str, input_platform_keys: Optional[set[str]] = None, silent_on_no_result: bool = False) -> None:
        api_url = f"https://api.song.link/v1-alpha.1/links?url={url}"
        response = await self.http.get(api_url)

        if response.status != 200:
            if not silent_on_no_result:
                await evt.reply(f"❌ API error: {response.status}")
            return

        data = await response.json()

        # If the only result platforms match the input platform(s), stay silent
        links_by_platform = data.get('linksByPlatform') or {}
        platform_keys = set(links_by_platform.keys())
        if input_platform_keys and platform_keys and platform_keys.issubset(input_platform_keys):
            return

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

    # Use the command regexes themselves to determine the platform of the input URL.
    @command.passive(r'(https?://open\.spotify\.com/(track|album|artist|playlist|user|episode|show)/[a-zA-Z0-9]+)')
    async def link_spotify(self, evt: MessageEvent, match: Tuple[str]) -> None:
        url = match[0]
        await self.__handle_music_url(evt, url, input_platform_keys={'spotify'})

    @command.passive(r'(https?://[a-zA-Z0-9-]+\.bandcamp\.com/(track|album)/[^\s]+)')
    async def link_bandcamp(self, evt: MessageEvent, match: Tuple[str]) -> None:
        url = match[0]
        await self.__handle_music_url(evt, url, input_platform_keys={'bandcamp'})

    @command.passive(r'(https?://(?:youtu\.be/[^\s]+|(?:www\.)?(?:music\.)?youtube\.com/watch\?[^\s]+))')
    async def link_youtube(self, evt: MessageEvent, match: Tuple[str]) -> None:
        url = match[0]
        await self.__handle_music_url(evt, url, input_platform_keys={'youtube', 'youtubeMusic'})

    @command.passive(r'(https?://(?:m\.)?soundcloud\.com/[^\s]+)')
    async def link_soundcloud(self, evt: MessageEvent, match: Tuple[str]) -> None:
        url = match[0]
        await self.__handle_music_url(evt, url, input_platform_keys={'soundcloud'})

    @command.passive(r'(https?://(?:music|itunes)\.apple\.com/[^\s]+)')
    async def link_apple(self, evt: MessageEvent, match: Tuple[str]) -> None:
        url = match[0]
        await self.__handle_music_url(evt, url, input_platform_keys={'appleMusic', 'itunes'})

    @command.passive(r'(https?://(?:listen\.)?tidal\.com/(?:browse/)?(?:track|album|playlist|artist)/[^\s]+)')
    async def link_tidal(self, evt: MessageEvent, match: Tuple[str]) -> None:
        url = match[0]
        await self.__handle_music_url(evt, url, input_platform_keys={'tidal'})

    @command.passive(r'(https?://(?:www\.)?deezer\.com/[^\s]+)')
    async def link_deezer(self, evt: MessageEvent, match: Tuple[str]) -> None:
        url = match[0]
        await self.__handle_music_url(evt, url, input_platform_keys={'deezer'})

    @command.passive(r'(https?://music\.amazon\.[^/\s]+/[^\s]+)')
    async def link_amazon(self, evt: MessageEvent, match: Tuple[str]) -> None:
        url = match[0]
        await self.__handle_music_url(evt, url, input_platform_keys={'amazonMusic', 'amazonStore'})

    @command.passive(r'(https?://(?:app\.)?napster\.com/[^\s]+)')
    async def link_napster(self, evt: MessageEvent, match: Tuple[str]) -> None:
        url = match[0]
        await self.__handle_music_url(evt, url, input_platform_keys={'napster'})

    @command.passive(r'(https?://(?:www\.)?pandora\.com/[^\s]+)')
    async def link_pandora(self, evt: MessageEvent, match: Tuple[str]) -> None:
        url = match[0]
        await self.__handle_music_url(evt, url, input_platform_keys={'pandora'})