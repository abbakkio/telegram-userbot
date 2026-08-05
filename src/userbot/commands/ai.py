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
                    
                        # Throttle Telegram edits to once every 4 seconds to avoid FloodWait errors
                        current_time = asyncio.get_event_loop().time()
                        if current_time - last_edit_time > 4.0:
                            try:
                                await msg.edit(f"🤖 **Llama 3.1:** {response_text[:4000]} ✍️")
                                last_edit_time = current_time
                            except errors.MessageNotModifiedError:
                                pass
                            except errors.FloodWaitError as e:
                                print(f"FloodWait for {e.seconds}s. Stopping live edits.")
                                last_edit_time = current_time + 999999  # Stop editing for the rest of this generation
                            except Exception:
                                pass
                            
                # Final output
                if response_text.strip():
                    # If it's too long, just send the first 4000 chars. 
                    final_text = response_text[:4000]
                    if len(response_text) > 4000:
                        final_text += "\n\n*(Message truncated due to Telegram limits)*"
                        
                    try:
                        await msg.edit(f"🤖 **Llama 3.1:** {final_text}")
                    except errors.FloodWaitError as e:
                        # If we still can't edit, reply with the final result instead
                        await msg.reply(f"🤖 **Llama 3.1 (Final):**\n\n{final_text}")
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
