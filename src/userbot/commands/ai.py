import asyncio
import traceback
from telethon import events, TelegramClient, errors
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from ollama import AsyncClient

def setup(client: TelegramClient):
    @client.on(events.NewMessage(pattern=r'(?i)^\.ai\s+(.+)'))
    async def ai_handler(event):
        try:
            prompt = event.pattern_match.group(1)
            
            # If the user sent the command, edit it. Otherwise, reply.
            if event.out:
                msg = event
                await msg.edit(f"🧠 **Thinking...**\n\n_Prompt: {prompt}_")
            else:
                msg = await event.reply(f"🧠 **Thinking...**\n\n_Prompt: {prompt}_")
                
            ollama_client = AsyncClient()
            response_text = ""
            last_edit_time = asyncio.get_event_loop().time()
            
            try:
                # Stream the response from the local Llama 3.1 model
                response_stream = await ollama_client.chat(
                    model='llama3.1',
                    messages=[{'role': 'user', 'content': prompt}],
                    stream=True
                )
                
                async for chunk in response_stream:
                    if 'message' in chunk and 'content' in chunk['message']:
                        response_text += chunk['message']['content']
                    
                        # Throttle Telegram edits to once every 3 seconds to avoid FloodWait errors
                        current_time = asyncio.get_event_loop().time()
                        if current_time - last_edit_time > 3.0:
                            try:
                                await msg.edit(f"🤖 **Llama 3.1:** {response_text} ✍️")
                                last_edit_time = current_time
                            except errors.MessageNotModifiedError:
                                pass
                            except errors.FloodWaitError as e:
                                print(f"Sleeping for {e.seconds}s due to FloodWaitError...")
                                await asyncio.sleep(e.seconds)
                                last_edit_time = asyncio.get_event_loop().time()
                            
                # Final edit to remove the typing cursor
                if response_text.strip():
                    try:
                        await msg.edit(f"🤖 **Llama 3.1:** {response_text}")
                    except errors.FloodWaitError as e:
                        await asyncio.sleep(e.seconds)
                        await msg.edit(f"🤖 **Llama 3.1:** {response_text}")
                else:
                    await msg.edit("🤖 **Llama 3.1:** (Empty response)")
                
            except Exception as e:
                error_msg = str(e).lower()
                if "connection refused" in error_msg:
                    await msg.edit("❌ **AI Error**: Ollama is not running in the background!")
                elif "not found" in error_msg:
                    await msg.edit("❌ **AI Error**: Llama 3.1 model is not downloaded yet! Please wait for the download to finish.")
                else:
                    await msg.edit(f"❌ **AI Error**: {e}")
                
        except Exception as e:
            print(f"AI command error: {e}")
            traceback.print_exc()
