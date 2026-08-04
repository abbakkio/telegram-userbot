from telethon import TelegramClient
from .spam import setup as setup_spam

def setup_all(client: TelegramClient):
    setup_spam(client)
