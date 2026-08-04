import asyncio
import re
import time
from telethon import events, TelegramClient

active_spams = {}

def parse_duration(time_str):
    match = re.match(r'^([\d\.]+)([smhdw])$', time_str)
    if not match:
        return None
    val = float(match.group(1))
    unit = match.group(2)
    if unit == 's': return val
    if unit == 'm': return val * 60
    if unit == 'h': return val * 3600
    if unit == 'd': return val * 86400
    if unit == 'w': return val * 604800
    return None

def parse_delay(time_str):
    match = re.match(r'^([\d\.]+)([smhdw])?$', time_str)
    if not match: return 0.1
    val = float(match.group(1))
    unit = match.group(2)
    if not unit or unit == 's': return val
    if unit == 'm': return val * 60
    if unit == 'h': return val * 3600
    if unit == 'd': return val * 86400
    if unit == 'w': return val * 604800
    return 0.1

async def spam_task_runner(client, chat_id, mode, count, duration, message_text, delay):
    task = asyncio.current_task()
    start_time = time.time()
    sent_count = 0
    try:
        while True:
            if mode == 'count' and sent_count >= count:
                break
            if mode == 'duration' and (time.time() - start_time) >= duration:
                break
            
            await client.send_message(chat_id, message_text)
            sent_count += 1
            await asyncio.sleep(delay)
    except asyncio.CancelledError:
        pass
    finally:
        if chat_id in active_spams and task in active_spams[chat_id]:
            active_spams[chat_id].remove(task)

def setup(client: TelegramClient):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.spam(?:\s+(.*))?'))
    async def spam_handler(event):
        try:
            raw_text = event.pattern_match.group(1)
            if not raw_text:
                return
            
            text = raw_text.strip()
            chat_id = event.chat_id
            
            if text == 'off':
                await event.delete()
                if chat_id in active_spams:
                    for task in active_spams[chat_id]:
                        task.cancel()
                    active_spams[chat_id] = []
                return
            
            # Extract delay if present
            delay_sec = 0.1
            match_delay = re.search(r'\s-d\s+([\d\.]+[smhdw]?)$', text)
            if match_delay:
                delay_str = match_delay.group(1)
                delay_sec = parse_delay(delay_str)
                text = text[:match_delay.start()].strip()
            
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                return
            
            arg = parts[0]
            message_text = parts[1]
            
            mode = None
            count = 0
            duration = 0
            
            if arg == 'on':
                mode = 'infinite'
            elif arg.isdigit():
                mode = 'count'
                count = int(arg)
            else:
                parsed_dur = parse_duration(arg)
                if parsed_dur is not None:
                    mode = 'duration'
                    duration = parsed_dur
                else:
                    return # Invalid format
            
            await event.delete()
            
            task = asyncio.create_task(spam_task_runner(
                event.client, chat_id, mode, count, duration, message_text, delay_sec
            ))
            
            if chat_id not in active_spams:
                active_spams[chat_id] = []
            active_spams[chat_id].append(task)
            
        except Exception as e:
            print(f"Spam command error: {e}")
