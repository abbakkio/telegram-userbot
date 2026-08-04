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
