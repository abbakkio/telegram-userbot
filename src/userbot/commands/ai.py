import asyncio
import traceback
import google.generativeai as genai
from telethon import events, TelegramClient, errors

from ..core.config import settings

# Configure Gemini with the API Key
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

def setup(client: TelegramClient):
    @client.on(events.NewMessage(pattern=r'(?i)^\.ai\s+(.+)'))
    async def ai_handler(event):
        try:
            prompt = event.pattern_match.group(1)
            
            if not settings.gemini_api_key:
                if event.out:
                    await event.edit("❌ **AI Error**: Please add `GEMINI_API_KEY` to your `.env` file!")
                else:
                    await event.reply("❌ **AI Error**: Please add `GEMINI_API_KEY` to your `.env` file!")
                return
            
            # If the user sent the command, edit it. Otherwise, reply.
            if event.out:
                msg = event
                await msg.edit(f"🧠 **Thinking (Gemini)...**\n\n_Prompt: {prompt}_")
            else:
                msg = await event.reply(f"🧠 **Thinking (Gemini)...**\n\n_Prompt: {prompt}_")
                
            response_text = ""
            last_edit_time = asyncio.get_event_loop().time()
            
            try:
                # Use the latest Gemini Flash model to prevent version deprecation errors
                model = genai.GenerativeModel('gemini-flash-latest')
                
                # Run the blocking network call in a separate thread so it doesn't freeze the bot
                def fetch_stream():
                    return model.generate_content(prompt, stream=True)
                    
                response_stream = await asyncio.to_thread(fetch_stream)
                
                for chunk in response_stream:
                    if chunk.text:
                        response_text += chunk.text
                    
                        # Throttle Telegram edits to once every 4 seconds to avoid FloodWait errors
                        current_time = asyncio.get_event_loop().time()
                        if current_time - last_edit_time > 4.0:
                            try:
                                await msg.edit(f"🤖 **Gemini Flash:** {response_text[:4000]} ✍️")
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
                        await msg.edit(f"🤖 **Gemini Flash:** {final_text}")
                    except errors.FloodWaitError as e:
                        # If we still can't edit, reply with the final result instead
                        await msg.reply(f"🤖 **Gemini Flash (Final):**\n\n{final_text}")
                else:
                    await msg.edit("🤖 **Gemini Flash:** (Empty response)")
                
            except Exception as e:
                error_msg = str(e).lower()
                if "api_key" in error_msg or "authentication" in error_msg:
                    await msg.edit("❌ **AI Error**: Invalid Gemini API Key!")
                else:
                    await msg.edit(f"❌ **AI Error**: {e}")
                
        except Exception as e:
            print(f"AI command error: {e}")
            traceback.print_exc()
