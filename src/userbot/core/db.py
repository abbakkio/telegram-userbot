import sqlite3
import os

# Create the database in the root userbot directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "userbot.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER,
            chat_id INTEGER,
            sender_id INTEGER,
            text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create an index for ultra-fast lookup by message_id
    c.execute('CREATE INDEX IF NOT EXISTS idx_msg_id ON messages (message_id)')
    conn.commit()
    conn.close()

def save_message(message_id, chat_id, sender_id, text):
    if not text:
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO messages (message_id, chat_id, sender_id, text)
        VALUES (?, ?, ?, ?)
    ''', (message_id, chat_id, sender_id, text))
    
    # Automatically clean up old messages to keep the database small (keep last 10,000)
    c.execute('''
        DELETE FROM messages 
        WHERE id NOT IN (
            SELECT id FROM messages ORDER BY id DESC LIMIT 10000
        )
    ''')
    conn.commit()
    conn.close()

def get_messages(message_ids):
    if not message_ids:
        return []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    placeholders = ','.join('?' * len(message_ids))
    # We select the most recent match for the message_id
    c.execute(f'''
        SELECT chat_id, sender_id, text 
        FROM messages 
        WHERE message_id IN ({placeholders}) 
        ORDER BY id DESC
    ''', message_ids)
    results = c.fetchall()
    conn.close()
    return results
