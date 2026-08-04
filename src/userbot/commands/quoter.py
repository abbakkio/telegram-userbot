import asyncio
from telethon import events, TelegramClient

def setup(client: TelegramClient):
    @client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.quote$'))
    async def quote_handler(event):
        try:
            if not event.is_reply:
                await event.edit("Please reply to a message to quote it!")
                return
                
            await event.edit("Generating quote...")
            reply_msg = await event.get_reply_message()
            
            # Forward the message to QuotLyBot
            quotly_bot = await event.client.get_entity('@QuotLyBot')
            fwd_msg = await event.client.forward_messages(quotly_bot, reply_msg)
            
            # Wait for QuotLyBot to reply with the sticker
            sticker_msg = None
            for _ in range(30): # Wait up to 15 seconds
                await asyncio.sleep(0.5)
                # Fetch recent messages from QuotLyBot
                async for msg in event.client.iter_messages(quotly_bot, limit=1):
                    # We check if it's a new message and if it contains media (the sticker)
                    if msg.id > fwd_msg.id and msg.media:
                        sticker_msg = msg
                        break
                if sticker_msg:
                    break
                    
            if sticker_msg:
                # Send the generated sticker to the original chat as a reply
                await event.client.send_message(
                    event.chat_id, 
                    file=sticker_msg.media, 
                    reply_to=reply_msg.id
                )
                await event.delete() # Remove the .quote command
            else:
                await event.edit("Failed to generate quote. Is @QuotLyBot down?")
                
        except Exception as e:
            await event.edit(f"Quote generation error: {e}")
            print(f"Quote error: {e}")
