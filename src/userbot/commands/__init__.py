from telethon import TelegramClient
from .spam import setup as setup_spam
from .fastfetch import setup as setup_fastfetch
from .reactor import setup as setup_reactor
from .ghost_type import setup as setup_ghost_type
from .bomb import setup as setup_bomb
from .translator import setup as setup_translator
from .quoter import setup as setup_quoter
from .voice import setup as setup_voice
from .roll import setup as setup_roll

def setup_all(client: TelegramClient):
    setup_spam(client)
    setup_fastfetch(client)
    setup_reactor(client)
    setup_ghost_type(client)
    setup_bomb(client)
    setup_translator(client)
    setup_quoter(client)
    setup_voice(client)
    setup_roll(client)
