import asyncio
import random
import re
from telethon import events, TelegramClient
from telethon.errors.rpcerrorlist import MessageNotModifiedError

def setup(client: TelegramClient):
    @client.on(events.NewMessage(pattern=r'(?i)^\.q(?:\s+(.+))?$'))
    async def q_handler(event):
        try:
            question = event.pattern_match.group(1)
            if not question:
                if event.out:
                    await event.edit("Please ask a question! (e.g., `.q Am I lucky today?`)")
                else:
                    await event.reply("Please ask a question! (e.g., `.q Am I lucky today?`)")
                return
                
            # Detect if the question contains any Cyrillic (Russian) characters
            is_russian = bool(re.search(r'[А-Яа-яЁё]', question))
            
            if is_russian:
                answers = [
                    "Да", "Нет", "Может быть", "Абсолютно", 
                    "Ни за что", "Вряд ли", "50/50", "Скорее всего"
                ]
                frames = [
                    "🔮 *Спрашиваю у вселенной...*",
                    "✨ *Читаю по звездам...*",
                    "🌌 *Анализирую вероятности...*",
                    "🎲 *Почти готово...*"
                ]
                q_text = "Вопрос"
                a_text = "Ответ"
            else:
                answers = [
                    "Yes", "No", "Maybe", "Absolutely", 
                    "No way", "Unlikely", "50/50", "Most likely"
                ]
                frames = [
                    "🔮 *Consulting the universe...*",
                    "✨ *Reading the stars...*",
                    "🌌 *Calculating probabilities...*",
                    "🎲 *Almost there...*"
                ]
                q_text = "Question"
                a_text = "Answer"
                
            final_answer = random.choice(answers)
            
            # If we sent the message, we can edit it directly. If someone else sent it, we must reply.
            if event.out:
                msg = event
            else:
                msg = await event.reply("🔮...")
            
            # Run the beautiful animation
            for frame in frames:
                try:
                    await msg.edit(f"❓ **{q_text}:** {question}\n\n{frame}")
                    await asyncio.sleep(0.5)
                except MessageNotModifiedError:
                    continue
                    
            # Set the final result
            await msg.edit(f"❓ **{q_text}:** {question}\n\n🎱 **{a_text}:** {final_answer}")
            
        except Exception as e:
            print(f"Q command error: {e}")
            try:
                if event.out:
                    await event.edit(f"❌ Error: {e}")
                else:
                    await event.reply(f"❌ Error: {e}")
            except:
                pass
