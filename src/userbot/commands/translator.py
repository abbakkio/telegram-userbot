from telethon import events, TelegramClient
from deep_translator import GoogleTranslator

def setup(client: TelegramClient):
    @client.on(events.NewMessage(pattern=r'(?i)^\.tr\s+([a-zA-Z\-]+)'))
    async def tr_handler(event):
        try:
            target_lang = event.pattern_match.group(1).lower()
            
            # Check if it's a reply to a message
            reply_msg = await event.get_reply_message()
            if not reply_msg or not reply_msg.text:
                if event.out:
                    await event.edit("Please reply to a text message to translate it!")
                else:
                    await event.reply("Please reply to a text message to translate it!")
                return
                
            if event.out:
                msg = event
                await msg.edit("Translating...")
            else:
                msg = await event.reply("Translating...")
            
            import asyncio
            
            # Translate using deep-translator without blocking the bot's event loop
            def do_translation():
                return GoogleTranslator(source='auto', target=target_lang).translate(reply_msg.text)
                
            translated = await asyncio.to_thread(do_translation)
            
            # Edit our message with the translation
            await msg.edit(f"**Translated to {target_lang}:**\n{translated}")
            
        except Exception as e:
            try:
                if event.out:
                    await event.edit(f"Translation failed: {e}")
                else:
                    await event.reply(f"Translation failed: {e}")
            except:
                pass
            print(f"Translation error: {e}")
