import os
import sys
import asyncio
import subprocess
from telethon import TelegramClient, events
from src.userbot.core.config import settings
from src.userbot.commands import setup_all

async def main():
    client = TelegramClient('session_qr', settings.api_id, settings.api_hash)
    await client.connect()

    # Check if the user is logged in
    if not await client.is_user_authorized():
        print("Not logged in. Triggering login.py...")
        await client.disconnect()
        
        if sys.stdout.isatty():
            # Trigger login.py directly if running in a terminal
            subprocess.run([sys.executable, "login.py"])
        else:
            # Running in background. Open iTerm to show QR code.
            login_cmd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_login.command")
            with open(login_cmd_path, "w") as f:
                f.write(f"#!/bin/bash\ncd \"{os.path.dirname(os.path.abspath(__file__))}\"\n\"{sys.executable}\" login.py\n")
            os.chmod(login_cmd_path, 0o755)
            
            subprocess.run(["open", "-a", "iTerm", login_cmd_path])
            
            print("Waiting for login via iTerm...")
            while True:
                await asyncio.sleep(5)
                await client.connect()
                if await client.is_user_authorized():
                    break
                await client.disconnect()
        
        # Re-connect to ensure state is completely valid
        if not client.is_connected():
            await client.connect()
        if not await client.is_user_authorized():
            print("Login failed or was cancelled.")
            return

    print("Client is running and logged in!")
    
    # Initialize all command handlers
    setup_all(client)
    
    # Run the client until disconnected
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
