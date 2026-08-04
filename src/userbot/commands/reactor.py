from telethon import events, TelegramClient
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
from src.userbot.core.config import settings

import re

def setup(client: TelegramClient):
    # Parse the user IDs from the config
    poop_ids = []
    if settings.poop_user_ids:
        try:
            poop_ids = [int(x.strip()) for x in settings.poop_user_ids.split(",") if x.strip()]
        except ValueError:
            print("Error parsing POOP_USER_IDS in .env. Ensure they are comma-separated numbers.")

    @client.on(events.NewMessage())
    async def reactor_handler(event):
        try:
            # 1. Poop reaction for specific users
            if poop_ids and event.sender_id in poop_ids:
                await event.client(SendReactionRequest(
                    peer=await event.get_input_chat(),
                    msg_id=event.id,
                    reaction=[ReactionEmoji(emoticon='💩')]
                ))
                
            # 2. React to any message containing "107" or a math equation evaluating to 107
            if event.raw_text:
                should_react = False
                if '107' in event.raw_text:
                    should_react = True
                else:
                    # Look for math expressions like 87+20, (1000-7)-886
                    # Optimized regex to prevent catastrophic backtracking on long numbers
                    matches = re.findall(r"[\d\(\)]+(?:\s*[+\-*/]\s*[\d\(\)]+)+", event.raw_text)
                    for match in matches:
                        try:
                            # Safe to eval because regex only matched digits and basic operators
                            if eval(match) == 107:
                                should_react = True
                                break
                        except Exception:
                            pass
                            
                if should_react:
                    await event.client(SendReactionRequest(
                        peer=await event.get_input_chat(),
                        msg_id=event.id,
                        reaction=[ReactionEmoji(emoticon='❤️‍🔥')]
                    ))
        except Exception as e:
            # We silently pass errors because some chats don't allow reactions
            pass
