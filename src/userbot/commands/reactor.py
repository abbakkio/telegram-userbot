from telethon import events, TelegramClient
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

def setup(client: TelegramClient):
    # React to any message containing the number "107"
    @client.on(events.NewMessage())
    async def reactor_handler(event):
        try:
            if event.raw_text and '107' in event.raw_text:
                await event.client(SendReactionRequest(
                    peer=await event.get_input_chat(),
                    msg_id=event.id,
                    reaction=[ReactionEmoji(emoticon='❤️‍🔥')]
                ))
        except Exception as e:
            # We silently pass errors because some chats don't allow reactions
            pass
