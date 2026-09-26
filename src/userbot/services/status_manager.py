import asyncio
import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import httpx
from telethon import TelegramClient
from telethon.tl.functions.account import UpdateProfileRequest
from src.userbot.core.config import settings

logger = logging.getLogger(__name__)

STATUS_CONFIG = {
    "work": {"state": "working", "emoji": "👨‍💻", "label": "Working", "surname_suffix": "[👨‍💻 Working]"},
    "working": {"state": "working", "emoji": "👨‍💻", "label": "Working", "surname_suffix": "[👨‍💻 Working]"},
    "studying": {"state": "studying", "emoji": "📚", "label": "Studying", "surname_suffix": "[📚 Studying]"},
    "study": {"state": "studying", "emoji": "📚", "label": "Studying", "surname_suffix": "[📚 Studying]"},
    "free": {"state": "free", "emoji": None, "label": "Free", "surname_suffix": ""},
}

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "status_state.json")


def parse_duration(text: Optional[str]) -> Optional[int]:
    """Parse string duration like '45m', '2h', '1h30m' into total minutes."""
    if not text:
        return None
    text = text.strip().lower()

    # Match combinations of hours and minutes, e.g., '1h30m', '2h', '45m', or plain digits as minutes
    hours_match = re.search(r"(\d+)\s*h", text)
    mins_match = re.search(r"(\d+)\s*m", text)

    total_mins = 0
    if hours_match:
        total_mins += int(hours_match.group(1)) * 60
    if mins_match:
        total_mins += int(mins_match.group(1))

    if not hours_match and not mins_match:
        if text.isdigit():
            total_mins = int(text)

    return total_mins if total_mins > 0 else None


class StatusManager:
    def __init__(self):
        self._current_task: Optional[asyncio.Task] = None
        self._last_update_time: float = 0.0
        self._client: Optional[TelegramClient] = None

    def _save_state(self, state_data: dict):
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save status state to {STATE_FILE}: {e}")

    def _load_state(self) -> dict:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load status state from {STATE_FILE}: {e}")
        return {"state": "free"}

    async def initialize(self, client: TelegramClient):
        """Called upon userbot startup to resume pending timers or recover state."""
        self._client = client
        state_data = self._load_state()
        state = state_data.get("state", "free")
        expires_at_ts = state_data.get("expires_at_timestamp")

        if state != "free" and expires_at_ts:
            now_ts = datetime.now(timezone.utc).timestamp()
            remaining_secs = expires_at_ts - now_ts
            if remaining_secs <= 0:
                logger.info(f"Prior status '{state}' expired while offline. Reverting to free.")
                await self.apply_status(client, "free")
            else:
                logger.info(f"Resuming prior status '{state}' with {int(remaining_secs)}s remaining.")
                self._schedule_timer(client, remaining_secs)

    async def sync_cv_backend(self, state: str, emoji: Optional[str], label: str, duration_minutes: Optional[int]):
        """Non-blocking notification to cv FastAPI backend."""
        if not settings.cv_api_url:
            return

        url = f"{settings.cv_api_url.rstrip('/')}/api/status"
        headers = {"X-Status-Key": settings.cv_api_key}
        payload = {
            "state": state,
            "emoji": emoji,
            "label": label,
            "duration_minutes": duration_minutes,
        }

        try:
            async with httpx.AsyncClient(timeout=3.0) as http_client:
                res = await http_client.post(url, json=payload, headers=headers)
                if res.is_success:
                    logger.info(f"Successfully synced status '{state}' with cv backend.")
                else:
                    logger.warning(f"cv backend returned status code {res.status_code}: {res.text}")
        except Exception as e:
            logger.warning(f"Could not reach cv backend at {url}: {e}")

    async def apply_status(
        self,
        client: TelegramClient,
        command_name: str,
        duration_str: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Apply status change to Telegram profile, schedule timer, and sync cv backend."""
        normalized = command_name.lower().strip()
        config = STATUS_CONFIG.get(normalized)
        if not config:
            return False, f"Unknown status: {command_name}"

        # Cancel any active countdown task
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self._current_task = None

        state = config["state"]
        emoji = config["emoji"]
        label = config["label"]
        suffix = config["surname_suffix"]

        # Parse duration
        duration_minutes = parse_duration(duration_str)
        if state != "free" and duration_minutes is None:
            # Default to 4 hours (240 mins) if no explicit duration was provided
            duration_minutes = 240

        # Construct new last name
        base_last_name = settings.base_last_name or "Madiyev"
        if suffix:
            new_last_name = f"{base_last_name} {suffix}"
        else:
            new_last_name = base_last_name

        # 1. Update Telegram Profile via Telethon
        try:
            await client(UpdateProfileRequest(last_name=new_last_name))
            logger.info(f"Updated Telegram surname to: '{new_last_name}'")
        except Exception as e:
            logger.error(f"Failed to update Telegram profile surname: {e}")
            return False, f"Telegram API error: {e}"

        # 2. Persist state locally
        now_utc = datetime.now(timezone.utc)
        expires_at_ts = (now_utc + timedelta(minutes=duration_minutes)).timestamp() if duration_minutes and state != "free" else None

        state_data = {
            "state": state,
            "emoji": emoji,
            "label": label,
            "last_name": new_last_name,
            "duration_minutes": duration_minutes,
            "updated_at": now_utc.isoformat(),
            "expires_at_timestamp": expires_at_ts,
        }
        self._save_state(state_data)

        # 3. Schedule auto-revert timer if active
        if state != "free" and duration_minutes:
            total_seconds = duration_minutes * 60
            self._schedule_timer(client, total_seconds)

        # 4. Notify cv backend (async fire-and-forget in background)
        asyncio.create_task(self.sync_cv_backend(state, emoji, label, duration_minutes))

        if state == "free":
            return True, "Status reset to Free (normal state restored)."
        return True, f"Status updated to {label} {emoji} for {duration_minutes}m."

    def _schedule_timer(self, client: TelegramClient, delay_seconds: float):
        async def timer_job():
            try:
                await asyncio.sleep(delay_seconds)
                logger.info("Status duration expired. Reverting to free...")
                await self.apply_status(client, "free")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Error in status timer job: {e}")

        self._current_task = asyncio.create_task(timer_job())


status_manager = StatusManager()
