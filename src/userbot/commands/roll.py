import asyncio
import random
from telethon import events, TelegramClient
from telethon.errors.rpcerrorlist import MessageNotModifiedError

def setup(client: TelegramClient):
    @client.on(events.NewMessage(pattern=r'(?i)^\.roll(?:\s+(\d+)-(\d+))?$'))
    async def roll_handler(event):
        try:
            min_val = 1
            max_val = 100
            
            # If the user provided a custom range like ".roll 5-1993"
            if event.pattern_match.group(1) and event.pattern_match.group(2):
                min_val = int(event.pattern_match.group(1))
                max_val = int(event.pattern_match.group(2))
                
                # Swap if they typed it backwards
                if min_val > max_val:
                    min_val, max_val = max_val, min_val
                    
            final_result = random.randint(min_val, max_val)
            
            # Cool animation effect (slot machine / rolling dice)
            frames_count = 8
            dice_emojis = ["🎲", "🎰", "🔥", "✨", "💥"]
            
            # If we sent the message, we can edit it directly. If someone else sent it, we must reply.
            if event.out:
                msg = event
            else:
                msg = await event.reply(f"🎲 Rolling...")
            
            for i in range(frames_count):
                temp_num = random.randint(min_val, max_val)
                emoji = random.choice(dice_emojis)
                
                try:
                    await msg.edit(f"{emoji} **Rolling:** {temp_num}")
                    await asyncio.sleep(0.2)
                except MessageNotModifiedError:
                    continue # Ignore if the random number happened to be the same as the last frame
                    
            # Set the final result
            await msg.edit(f"🎯 **Result:** {final_result}  *(Range: {min_val}-{max_val})*")
            
        except Exception as e:
            print(f"Roll command error: {e}")
            try:
                if event.out:
                    await event.edit(f"❌ Error: {e}")
                else:
                    await event.reply(f"❌ Error: {e}")
            except:
                pass
