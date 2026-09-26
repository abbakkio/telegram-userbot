import asyncio
from telethon import events, TelegramClient
from src.userbot.services.status_manager import status_manager

def setup(client: TelegramClient):
    @client.on(events.NewMessage(outgoing=True, pattern=r"(?i)^[./](work|working|studying|study|free)(?:\s+(.+))?$"))
    async def status_handler(event):
        command = event.pattern_match.group(1).lower()
        duration_arg = event.pattern_match.group(2)

        if duration_arg:
            duration_arg = duration_arg.strip()

        success, message = await status_manager.apply_status(
            client=client,
            command_name=command,
            duration_str=duration_arg,
        )

        try:
            if success:
                icon = "👨‍💻" if command in ("work", "working") else ("📚" if command in ("studying", "study") else "✨")
                await event.edit(f"{icon} {message}")
            else:
                await event.edit(f"⚠️ {message}")

            # Keep confirmation visible for 4 seconds then auto-delete to keep chat clean
            await asyncio.sleep(4)
            await event.delete()
        except Exception:
            pass
