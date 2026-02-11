#!/bin/bash
# Start ha-semantic-memory service
#
# Usage:
#   ./scripts/start.sh

set -e

LABEL="com.ha-semantic-memory"

if [[ "$(uname)" == "Darwin" ]]; then
    PLIST="/Library/LaunchDaemons/${LABEL}.plist"
    if [ ! -f "$PLIST" ]; then
        echo "ERROR: Plist not found at $PLIST"
        echo "Run ./scripts/install.sh first"
        exit 1
    fi

    # Check if already loaded
    if sudo launchctl list "$LABEL" &>/dev/null; then
        echo "Service already running. Use ./scripts/restart.sh to restart."
        exit 0
    fi

    sudo launchctl load "$PLIST"
    echo "Service started"

elif [[ "$(uname)" == "Linux" ]]; then
    sudo systemctl start ha-semantic-memory
    echo "Service started"
fi

# Wait briefly and verify
sleep 2
if curl -sf http://localhost:8920/health > /dev/null 2>&1; then
    echo "Health check: OK"
else
    echo "WARNING: Health check failed — check logs"
    if [[ "$(uname)" == "Darwin" ]]; then
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
        APP_DIR="$(dirname "$SCRIPT_DIR")"
        echo "  tail -f $APP_DIR/logs/ha-semantic-memory.err"
    else
        echo "  journalctl -u ha-semantic-memory -f"
    fi
fi
