# Telegram Userbot

A modular Telegram userbot built with Telethon.

## Setup

1. Create a `.env` file based on your credentials:
```env
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=your_phone_number
PASSWORD=your_2fa_password
```
2. Install dependencies and run:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt # or equivalent
python3 main.py
```

### macOS Background Autostart
You can configure the bot to start automatically in the background every time you log in to your Mac. If your session expires while running in the background, it will automatically open an `iTerm` window for you to scan the QR code.

To enable autostart, run the included script:
```bash
./install_autostart.sh
```
*Note: Your bot's background logs will be saved to `userbot.log` in this directory.*

## Commands

### `.spam`
A powerful and flexible spamming command.

**Usage:**
- `.spam <count> <message> [-d <delay>]`: Spams the `message` for `count` times.
- `.spam <duration> <message> [-d <delay>]`: Spams the `message` for a given `duration`.
- `.spam on <message> [-d <delay>]`: Spams the `message` indefinitely until stopped.
- `.spam off`: Stops all active spam tasks in the current chat.

**Time Formats:**
You can specify durations and delays using suffixes:
- `s` = seconds (default)
- `m` = minutes
- `h` = hours
- `d` = days
- `w` = weeks

**Examples:**
- `.spam 10 Hello` — Sends "Hello" 10 times.
- `.spam 1d Hello` — Spams "Hello" continuously for 1 day.
- `.spam 10 Hello -d 3m` — Sends "Hello" 10 times, waiting 3 minutes between each message.
- `.spam on Hello -d 0.3s` — Spams "Hello" every 0.3 seconds until you type `.spam off`.

### `fastfetch`
Retrieves and displays the host machine's system specs (OS, Kernel, CPU, RAM, Battery, etc.).

**Usage:**
- Type exactly `fastfetch` (no dot prefix).
- This command is accessible to **anyone** (if another user types it, your bot will reply with the stats).

### `.type`
Ghost typing! The bot will edit the message sequentially to look like the text is being typed out in real-time.

**Usage:**
- `.type <message>`: Animates the typing of `<message>`.

### `.bomb`
Self-destructing messages. Sends a message that deletes itself after a specified number of seconds.

**Usage:**
- `.bomb <seconds> <message>`: Shows `⏳ <message>` and deletes it for everyone when the timer runs out.

### `.tr`
Auto-translator. Translates any message into the language of your choice.

**Usage:**
- Reply to any text message with `.tr <lang_code>` (e.g., `.tr en`, `.tr ru`, `.tr fr`). The bot automatically detects the source language and edits your message to show the translation.

### `.quote`
Quote generator. Turns any message into a beautiful sticker quote.

**Usage:**
- Reply to a message with `.quote`. The bot will secretly fetch a sticker from `@QuotLyBot` and reply with it, making you look like a pro.

### `.voice`
Voice note transcriber. Converts voice messages to text.

**Usage:**
- Reply to any voice note with `.voice`. The bot will download the audio, transcribe it to text locally, and reply with the transcript.

### `.roll`
Random number generator with a cool casino-style slot machine animation.

**Usage:**
- `.roll`: Drops a random number between 1 and 100.
- `.roll <min>-<max>`: Drops a random number between your chosen range (e.g., `.roll 5-1993`).

### `.q`
Magic 8-Ball that answers your questions with a cool animation. Automatically detects if your question is in English or Russian and replies in the same language!

**Usage:**
- `.q <question>` (e.g., `.q Am I lucky today?` or `.q Мне сегодня повезет?`)

### Hidden Features
- **Anti-Delete**: The bot silently caches every single message it sees across all chats into a local SQLite database on your Mac. If someone deletes their message for everyone, the bot intercepts the delete signal, recovers the lost text from the database, and automatically forwards it to your **Saved Messages** along with the sender's details!
- **Auto-Reactor**: If any message contains the number `107` (or a math equation evaluating to 107 like `(1000-7)-886`), the bot will automatically react to it with a ❤️‍🔥.
- **Poop Reactor**: Automatically reacts with 💩 to any message sent by specific user IDs you defined in your `.env` file.
