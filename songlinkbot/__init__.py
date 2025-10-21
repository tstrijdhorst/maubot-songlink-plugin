from typing import Tuple
from maubot import Plugin, MessageEvent
from maubot.handlers import command


class SongLinkBot(Plugin):
    async def _handle_music_url(self, evt: MessageEvent, url: str, silent_on_no_result: bool = False) -> None:
        # Make HTTP request to song.link API using maubot's built-in client
        api_url = f"https://api.song.link/v1-alpha.1/links?url={url}"
        response = await self.http.get(api_url)

        # Early return on API error
        if response.status != 200:
            if not silent_on_no_result:
                await evt.reply(f"❌ API error: {response.status}")
            return

        data = await response.json()
        page_url = data.get('pageUrl')

        # Early return if no pageUrl found
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

        # Early return if no entity found
        if not entity:
            await evt.reply(f"🎵 Universal link: {page_url}")
            return

        title = entity.get('title', 'Unknown')
        artist = entity.get('artistName', 'Unknown')

        # Send a final response with details and universal link
        await evt.reply(f"🎵 **{title}** - {artist}\n🔗 {page_url}")
    @command.passive(r'(https?://open\.spotify\.com/(track|album|artist|playlist|user|episode|show)/[a-zA-Z0-9]+)')
    async def spotify_link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        spotify_url = match[0]
        await self._handle_music_url(evt, spotify_url)

    @command.passive(r'(https?://[a-zA-Z0-9-]+\.bandcamp\.com/(track|album)/[^\s]+)')
    async def bandcamp_link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        bandcamp_url = match[0]
        await self._handle_music_url(evt, bandcamp_url)

    @command.passive(r'(https?://(?:youtu\.be/[^\s]+|(?:www\.)?(?:music\.)?youtube\.com/watch\?[^\s]+))')
    async def youtube_link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        youtube_url = match[0]
        await self._handle_music_url(evt, youtube_url, silent_on_no_result=True)

    @command.passive(r'(https?://(?:m\.)?soundcloud\.com/[^\s]+)')
    async def soundcloud_link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        soundcloud_url = match[0]
        await self._handle_music_url(evt, soundcloud_url)

    # Apple Music: match music.apple.com or itunes.apple.com share links
    @command.passive(r'(https?://(?:music|itunes)\.apple\.com/[^\s]+)')
    async def apple_music_link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        apple_url = match[0]
        await self._handle_music_url(evt, apple_url)

    # Tidal: match tidal.com browse links for track/album/playlist/artist
    @command.passive(r'(https?://(?:listen\.)?tidal\.com/(?:browse/)?(?:track|album|playlist|artist)/[^\s]+)')
    async def tidal_link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        tidal_url = match[0]
        await self._handle_music_url(evt, tidal_url)

    # Deezer: match deezer.com share links
    @command.passive(r'(https?://(?:www\.)?deezer\.com/[^\s]+)')
    async def deezer_link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        deezer_url = match[0]
        await self._handle_music_url(evt, deezer_url)

    # Amazon Music: match music.amazon.<tld> share links
    @command.passive(r'(https?://music\.amazon\.[^/\s]+/[^\s]+)')
    async def amazon_music_link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        amazon_url = match[0]
        await self._handle_music_url(evt, amazon_url)

    # Napster: match napster.com and app.napster.com links
    @command.passive(r'(https?://(?:app\.)?napster\.com/[^\s]+)')
    async def napster_link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        napster_url = match[0]
        await self._handle_music_url(evt, napster_url)

    # Pandora: match pandora.com links
    @command.passive(r'(https?://(?:www\.)?pandora\.com/[^\s]+)')
    async def pandora_link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        pandora_url = match[0]
        await self._handle_music_url(evt, pandora_url)
