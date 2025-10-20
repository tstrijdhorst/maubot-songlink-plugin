from typing import Tuple
from maubot import Plugin, MessageEvent
from maubot.handlers import command


class ExampleBot(Plugin):
    @command.passive(r'(https?://open\.spotify\.com/(track|album|artist|playlist|user|episode|show)/[a-zA-Z0-9]+)')
    async def spotify_link_handler(self, evt: MessageEvent, match: Tuple[str]) -> None:
        spotify_url = match[0]


        try:
            # Make HTTP request to song.link API using maubot's built-in client 【1】
            api_url = f"https://api.song.link/v1-alpha.1/links?url={spotify_url}"
            response = await self.http.get(api_url)

            if response.status == 200:
                data = await response.json()
                page_url = data.get('pageUrl')
                entity_unique_id = data.get('entityUniqueId')

                if page_url and entity_unique_id:
                    # Get Spotify entity using the entityUniqueId
                    entities = data.get('entitiesByUniqueId', {})
                    spotify_entity = entities.get(entity_unique_id)

                    if spotify_entity:
                        thumbnail_url = spotify_entity.get('thumbnailUrl')
                        title = spotify_entity.get('title', 'Unknown')
                        artist = spotify_entity.get('artistName', 'Unknown')

                        if thumbnail_url:
                            # Download image data
                            img_response = await self.http.get(thumbnail_url)
                            if img_response.status == 200:
                                img_data = await img_response.read()
                                img_size = len(img_data)

                                # Upload image to Matrix - returns MXC URI string directly
                                mxc_uri = await evt.client.upload_media(
                                    data=img_data,
                                    mime_type="image/jpeg",
                                    filename="cover.jpg"
                                )

                                # Send text message first
                                await evt.respond(
                                    f"🎵 **{title}** - {artist}\n🔗 {page_url}"
                                )

                                # Send image message separately with proper info fields
                                await evt.client.send_message(
                                    room_id=evt.room_id,
                                    content={
                                        "msgtype": "m.image",
                                        "body": "Cover art",
                                        "url": mxc_uri,
                                        "info": {
                                            "mimetype": "image/jpeg",
                                            "w": spotify_entity.get('thumbnailWidth', 640),
                                            "h": spotify_entity.get('thumbnailHeight', 640),
                                            "size": img_size,  # Required field
                                            "thumbnail_info": {  # Required for proper display
                                                "mimetype": "image/jpeg",
                                                "w": 200,
                                                "h": 200,
                                                "size": img_size
                                            },
                                            "thumbnail_url": mxc_uri  # Use same image as thumbnail
                                        }
                                    }
                                )
                            else:
                                await evt.reply(f"🎵 **{title}** - {artist}\n🔗 {page_url}")
                        else:
                            await evt.reply(f"🎵 **{title}** - {artist}\n🔗 {page_url}")
                    else:
                        await evt.reply(f"🎵 Universal link: {page_url}")
                else:
                    await evt.reply("❌ Could not find universal link")
            else:
                await evt.reply(f"❌ API error: {response.status}")

        except Exception as e:
            await evt.reply(f"❌ Error: {str(e)}")
