#!/bin/bash
# Uninstall ha-semantic-memory service (stops and removes the service definition)
# Does NOT delete the application directory, database, or pyenv virtualenv.
#
# Usage:
#   ./scripts/uninstall.sh

set -e

LABEL="com.ha-semantic-memory"

if [[ "$(uname)" == "Darwin" ]]; then
    PLIST="/Library/LaunchDaemons/${LABEL}.plist"

    if sudo launchctl list "$LABEL" &>/dev/null; then
        echo "Stopping service..."
        sudo launchctl unload "$PLIST" 2>/dev/null || true
    fi

    if [ -f "$PLIST" ]; then
        sudo rm "$PLIST"
        echo "Removed $PLIST"
    else
        echo "Plist not found (already removed?)"
    fi

    echo "Service uninstalled"

elif [[ "$(uname)" == "Linux" ]]; then
    echo "Stopping service..."
    sudo systemctl stop ha-semantic-memory 2>/dev/null || true
    sudo systemctl disable ha-semantic-memory 2>/dev/null || true

    SERVICE="/etc/systemd/system/ha-semantic-memory.service"
    if [ -f "$SERVICE" ]; then
        sudo rm "$SERVICE"
        sudo systemctl daemon-reload
        echo "Removed $SERVICE"
    fi

    echo "Service uninstalled"
fi

echo ""
echo "The following were NOT removed (clean up manually if desired):"
echo "  - Application directory: $(cd "$(dirname "$0")/.." && pwd)"
echo "  - pyenv virtualenv: pyenv uninstall ha-semantic-memory-3.12"
echo "  - Database: dropdb ha_memory"
