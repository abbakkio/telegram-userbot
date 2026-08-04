import asyncio
from telethon import events, TelegramClient
from telethon.errors.rpcerrorlist import FloodWaitError, MessageNotModifiedError

def setup(client: TelegramClient):
    @client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.type\s+(.+)'))
    async def ghost_type_handler(event):
        try:
            text = event.pattern_match.group(1)
            typed_text = ""
            
            for i, char in enumerate(text):
                typed_text += char
                try:
                    # Show a cool terminal-style block cursor effect
                    cursor = "▒" if i % 2 == 0 else "█"
                    
                    # On the last character, remove the cursor entirely
                    if i == len(text) - 1:
                        await event.edit(typed_text)
                    else:
                        await event.edit(typed_text + cursor)
                        
                    # 150ms delay to give a realistic typing speed and avoid Telegram spam limits
                    await asyncio.sleep(0.15)
                    
                except MessageNotModifiedError:
                    continue
                except FloodWaitError as e:
                    # If we type too fast and Telegram complains, just wait it out
                    await asyncio.sleep(e.seconds)
                    
        except Exception as e:
            print(f"Ghost type command error: {e}")
