import sys
import asyncio
import subprocess
from telethon import TelegramClient
from src.userbot.core.config import settings

async def main():
    client = TelegramClient('session_qr', settings.api_id, settings.api_hash)
    await client.connect()

    # Check if the user is logged in
    if not await client.is_user_authorized():
        print("Not logged in. Triggering login.py...")
        await client.disconnect()
        
        # Trigger login.py as a separate process
        subprocess.run([sys.executable, "login.py"])
        
        # Re-connect to check if login was successful
        await client.connect()
        if not await client.is_user_authorized():
            print("Login failed or was cancelled.")
            return

    print("Client is running and logged in!")
    
    # Run the client until disconnected
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
