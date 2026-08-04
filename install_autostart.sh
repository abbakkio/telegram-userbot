#!/bin/bash

echo "Setting up macOS autostart for Telegram Userbot..."

PLIST_PATH="$HOME/Library/LaunchAgents/com.telegram.userbot.plist"
WORK_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$WORK_DIR/.venv/bin/python"
MAIN_SCRIPT="$WORK_DIR/main.py"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Virtual environment python not found at $VENV_PYTHON"
    echo "Please create the virtual environment first."
    exit 1
fi

cat << EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.telegram.userbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV_PYTHON</string>
        <string>$MAIN_SCRIPT</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$WORK_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>StandardOutPath</key>
    <string>$WORK_DIR/userbot.log</string>
    <key>StandardErrorPath</key>
    <string>$WORK_DIR/userbot.log</string>
</dict>
</plist>
EOF

# Unload if it already exists, then load it
launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

echo "Autostart configured successfully!"
echo "The userbot will now run automatically in the background when you log in."
echo "Logs can be found at $WORK_DIR/userbot.log"
