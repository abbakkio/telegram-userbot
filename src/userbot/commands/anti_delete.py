from telethon import events, TelegramClient
from src.userbot.core.db import init_db, save_message, get_messages

def setup(client: TelegramClient):
    # Initialize the local SQLite database
    init_db()

    # 1. Silently intercept and cache all incoming and outgoing messages
    @client.on(events.NewMessage())
    async def cache_message(event):
        try:
            if event.raw_text:
                save_message(event.id, event.chat_id, event.sender_id, event.raw_text)
        except Exception:
            pass

    # 2. Catch whenever a message is deleted for everyone
    @client.on(events.MessageDeleted())
    async def deleted_handler(event):
        try:
            if not event.deleted_ids:
                return
                
            # Look up the deleted IDs in our secret database
            deleted_msgs = get_messages(event.deleted_ids)
            
            for chat_id, sender_id, text in deleted_msgs:
                chat_name = "Private Chat / Unknown"
                sender_name = "Unknown"
                
                # Try to nicely resolve the Chat Name
                try:
                    if chat_id:
                        chat = await event.client.get_entity(chat_id)
                        chat_name = getattr(chat, 'title', str(chat_id))
                except:
                    pass
                    
                # Try to nicely resolve the Sender's Name
                try:
                    if sender_id:
                        sender = await event.client.get_entity(sender_id)
                        sender_name = getattr(sender, 'first_name', str(sender_id))
                        username = getattr(sender, 'username', None)
                        if username:
                            sender_name += f" (@{username})"
                except:
                    pass
                
                # Format our recovery report
                report = (
                    f"🗑 **[DELETED MESSAGE RECOVERED]**\n"
                    f"👤 **From:** {sender_name}\n"
                    f"💬 **Chat:** {chat_name}\n\n"
                    f"**Message:**\n{text}"
                )
                
                # Automatically forward it to the user's "Saved Messages"
                await event.client.send_message('me', report)
                
        except Exception as e:
            print(f"Anti-delete error: {e}")
