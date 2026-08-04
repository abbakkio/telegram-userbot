from telethon import TelegramClient
from .spam import setup as setup_spam
from .fastfetch import setup as setup_fastfetch

def setup_all(client: TelegramClient):
    setup_spam(client)
    setup_fastfetch(client)
