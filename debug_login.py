import asyncio
from telethon import TelegramClient
from src.userbot.core.config import settings

async def main():
    phone = settings.phone_number
    client = TelegramClient('anon_debug', settings.api_id, settings.api_hash)
    await client.connect()
    
    if not await client.is_user_authorized():
        try:
            print(f"Sending code request for {phone}...")
            result = await client.send_code_request(phone)
            print(f"Code sent successfully!")
            print(f"Telegram says it sent the code via: {type(result.type).__name__}")
            print(result)
        except Exception as e:
            print(f"Error requesting code: {type(e).__name__} - {e}")
    else:
        print("Already authorized!")
        
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
