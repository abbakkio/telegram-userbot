import asyncio
from telethon import events, TelegramClient

def setup(client: TelegramClient):
    @client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.bomb\s+(\d+)\s+(.+)'))
    async def bomb_handler(event):
        try:
            seconds = int(event.pattern_match.group(1))
            secret_text = event.pattern_match.group(2)
            
            # Edit the command message to show only the secret text (adds a small clock emoji as an indicator)
            await event.edit(f"⏳ {secret_text}")
            
            # Wait for the specified number of seconds
            # (Telethon runs this concurrently, so it won't block your other commands)
            await asyncio.sleep(seconds)
            
            # Delete the message for everyone
            await event.delete()
            
        except Exception as e:
            print(f"Bomb command error: {e}")
