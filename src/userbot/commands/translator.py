from telethon import events, TelegramClient
from deep_translator import GoogleTranslator

def setup(client: TelegramClient):
    @client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.tr\s+([a-zA-Z\-]+)'))
    async def tr_handler(event):
        try:
            target_lang = event.pattern_match.group(1).lower()
            
            # Check if it's a reply to a message
            reply_msg = await event.get_reply_message()
            if not reply_msg or not reply_msg.text:
                await event.edit("Please reply to a text message to translate it!")
                return
                
            await event.edit("Translating...")
            
            # Translate using deep-translator
            translated = GoogleTranslator(source='auto', target=target_lang).translate(reply_msg.text)
            
            # Edit our message with the translation
            await event.edit(f"**Translated to {target_lang}:**\n{translated}")
            
        except Exception as e:
            await event.edit(f"Translation failed: {e}")
            print(f"Translation error: {e}")
