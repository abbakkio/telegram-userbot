import os
import asyncio
import qrcode
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError
from src.userbot.core.config import settings

async def login():
    session_name = 'session_qr'
    session_file = f'{session_name}.session'

    client = TelegramClient(session_name, settings.api_id, settings.api_hash)
    try:
        await client.connect()
    except Exception as e:
        if "AuthKeyDuplicatedError" in type(e).__name__:
            print("⚠️ Detected invalidated session key. Resetting session file...")
            await client.disconnect()
            if os.path.exists(session_file):
                os.remove(session_file)
            client = TelegramClient(session_name, settings.api_id, settings.api_hash)
            await client.connect()
        else:
            raise

    if await client.is_user_authorized():
        print("Already logged in.")
        await client.disconnect()
        return

    # Initiate QR Login
    qr_login = await client.qr_login()
    
    # Generate and display the QR code in the terminal
    qr = qrcode.QRCode()
    qr.add_data(qr_login.url)
    print("Scan this QR code using Telegram -> Settings -> Devices -> Link Desktop Device:\n")
    qr.print_ascii(tty=True)

    try:
        # Wait for the user to scan the QR code (timeout in seconds)
        user = await qr_login.wait(timeout=60)
        print(f"Successfully logged in as: {user.first_name}")
        
    except asyncio.TimeoutError:
        print("Login timed out. Please try again.")
        
    except SessionPasswordNeededError:
        print("\n[2FA Required] Two-step verification is enabled.")
        
        # Safe retry loop for your 2FA password to prevent crashes on typos
        while True:
            try:
                password = settings.password
                # Corrected: Using client.sign_in instead of qr_login.confirm_password
                user = await client.sign_in(password=password)
                print(f"Successfully logged in as: {user.first_name}")
                break
            except PasswordHashInvalidError:
                print("❌ Incorrect password. Please try again.")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(login())
