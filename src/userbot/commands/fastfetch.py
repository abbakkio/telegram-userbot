import asyncio
import re
from telethon import events, TelegramClient

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def setup(client: TelegramClient):
    @client.on(events.NewMessage(pattern=r'(?i)^fastfetch$'))
    async def fastfetch_handler(event):
        try:
            # Run the fastfetch command with absolute path since launchd doesn't have homebrew in PATH
            process = await asyncio.create_subprocess_shell(
                '/opt/homebrew/bin/fastfetch --logo none -s os:host:kernel:uptime:shell:cpu:gpu:memory:disk:battery',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if stdout:
                # Decode and strip ANSI color codes just in case fastfetch outputs them
                result = strip_ansi(stdout.decode('utf-8')).strip()
                
                # Format as a monospaced code block
                formatted_result = f"```\n{result}\n```"
                
                if event.out:
                    # If it's our own message, edit the original command message
                    await event.edit(formatted_result)
                else:
                    # If it's from another user, reply to them
                    await event.reply(formatted_result)
            elif stderr:
                error = stderr.decode('utf-8').strip()
                if event.out:
                    await event.edit(f"Error running fastfetch: `{error}`")
                else:
                    await event.reply(f"Error running fastfetch: `{error}`")
                    
        except Exception as e:
            print(f"Fastfetch command error: {e}")
