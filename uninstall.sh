#!/usr/bin/env bash
# ==============================================================================
# Echo Settings - Linux Uninstaller
# Removes installed Echo Settings application files and desktop integration.
# ==============================================================================
set -e

INSTALL_PREFIX="${HOME}/.local"
APP_DIR="${INSTALL_PREFIX}/share/echo-settings"
BIN_FILE="${INSTALL_PREFIX}/bin/echo-settings"
DESKTOP_FILE="${INSTALL_PREFIX}/share/applications/echo-settings.desktop"
ICONS_DIR="${INSTALL_PREFIX}/share/icons/hicolor"

echo "================================================="
echo "  Uninstalling Echo Settings...                  "
echo "================================================="

# 1. Remove launcher
if [ -f "$BIN_FILE" ]; then
    echo "Removing $BIN_FILE..."
    rm -f "$BIN_FILE"
fi

# 2. Remove desktop entry
if [ -f "$DESKTOP_FILE" ]; then
    echo "Removing $DESKTOP_FILE..."
    rm -f "$DESKTOP_FILE"
fi

# 3. Remove icons
echo "Removing desktop icons..."
sizes=(16 24 32 48 64 128 256 512 scalable)
for sz in "${sizes[@]}"; do
    if [ "$sz" = "scalable" ]; then
        rm -f "$ICONS_DIR/$sz/apps/echo-settings.png" "$ICONS_DIR/$sz/apps/echo-settings.jpg"
    else
        rm -f "$ICONS_DIR/${sz}x${sz}/apps/echo-settings.png" "$ICONS_DIR/${sz}x${sz}/apps/echo-settings.jpg"
    fi
done

# 4. Remove application directory
if [ -d "$APP_DIR" ]; then
    echo "Removing $APP_DIR..."
    rm -rf "$APP_DIR"
fi

# 5. Update databases
echo "Updating desktop and icon databases..."
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${INSTALL_PREFIX}/share/applications" || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$ICONS_DIR" || true
fi

echo ""
echo "================================================="
echo "  Echo Settings has been uninstalled.            "
echo "  (User configuration in ~/.config was preserved)"
echo "================================================="
