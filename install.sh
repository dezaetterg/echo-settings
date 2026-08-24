#!/usr/bin/env bash
# ==============================================================================
# Echo Settings - Linux Installer
# Installs Echo Settings as a native user application on Linux/GNOME.
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect project source directory
if [ -f "$SCRIPT_DIR/Tahoe Settings/main.py" ]; then
    SRC_DIR="$SCRIPT_DIR/Tahoe Settings"
elif [ -f "$SCRIPT_DIR/main.py" ]; then
    SRC_DIR="$SCRIPT_DIR"
else
    echo "Error: Could not find Echo Settings source files in $SCRIPT_DIR"
    exit 1
fi

INSTALL_PREFIX="${HOME}/.local"
APP_DIR="${INSTALL_PREFIX}/share/echo-settings"
BIN_DIR="${INSTALL_PREFIX}/bin"
DESKTOP_DIR="${INSTALL_PREFIX}/share/applications"
ICONS_DIR="${INSTALL_PREFIX}/share/icons/hicolor"

echo "================================================="
echo "  Installing Echo Settings for current user...   "
echo "================================================="
echo "Source:      $SRC_DIR"
echo "Destination: $APP_DIR"
echo ""

# 1. Create target directories
mkdir -p "$APP_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"

# 2. Copy application components
echo "[1/5] Copying application files..."
rsync -a --delete \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '*.log' \
    --exclude '.git*' \
    "$SRC_DIR/" "$APP_DIR/"

# 3. Create launcher executable in ~/.local/bin/echo-settings
echo "[2/5] Creating launcher in $BIN_DIR/echo-settings..."
cat << 'EOF' > "$BIN_DIR/echo-settings"
#!/usr/bin/env bash
# Echo Settings - Launcher Script
set -e

APP_DIR="${HOME}/.local/share/echo-settings"
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Echo Settings is not installed in $APP_DIR"
    exit 1
fi

PYTHON_EXEC="$APP_DIR/venv/bin/python"
if [ ! -x "$PYTHON_EXEC" ]; then
    PYTHON_EXEC="$(which python3)"
fi

export PYTHONPATH="$APP_DIR:$PYTHONPATH"
exec "$PYTHON_EXEC" "$APP_DIR/main.py" "$@"
EOF
chmod +x "$BIN_DIR/echo-settings"

# Also create echo-settings launcher inside APP_DIR
cp "$BIN_DIR/echo-settings" "$APP_DIR/echo-settings"
chmod +x "$APP_DIR/echo-settings"

# 4. Generate and install desktop icons
echo "[3/5] Installing desktop icons..."
"$APP_DIR/venv/bin/python" - << 'PYEOF'
import os
import sys

install_prefix = os.path.expanduser("~/.local")
app_dir = os.path.join(install_prefix, "share", "echo-settings")
icon_src = os.path.join(app_dir, "assets", "echo_icon.jpg")
if not os.path.exists(icon_src):
    icon_src = os.path.join(app_dir, "icon.png")

from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

sizes = [16, 24, 32, 48, 64, 128, 256, 512]
hicolor_base = os.path.join(install_prefix, "share", "icons", "hicolor")

img = QImage(icon_src)
if not img.isNull():
    for sz in sizes:
        sz_dir = os.path.join(hicolor_base, f"{sz}x{sz}", "apps")
        os.makedirs(sz_dir, exist_ok=True)
        dest = os.path.join(sz_dir, "echo-settings.png")
        scaled = img.scaled(sz, sz, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled.save(dest, "PNG")

    # Scalable directory
    scalable_dir = os.path.join(hicolor_base, "scalable", "apps")
    os.makedirs(scalable_dir, exist_ok=True)
    img.save(os.path.join(scalable_dir, "echo-settings.png"), "PNG")
    print("  Icons installed successfully.")
else:
    print("  Warning: could not load icon source image.")
PYEOF

# 5. Create and validate desktop entry
echo "[4/5] Creating desktop entry in $DESKTOP_DIR/echo-settings.desktop..."
cat << EOF > "$DESKTOP_DIR/echo-settings.desktop"
[Desktop Entry]
Type=Application
Name=Echo Settings
GenericName=System Settings
Comment=Modern System Control Center for Echo Linux
Exec=$BIN_DIR/echo-settings %U
Icon=echo-settings
Terminal=false
Categories=Settings;HardwareSettings;DesktopSettings;GTK;Qt;
Keywords=Preferences;Settings;Control;Center;Echo;Display;Appearance;WiFi;Network;Bluetooth;Power;Sound;Storage;Keyboard;
StartupWMClass=Echo_Settings
StartupNotify=true
SingleMainWindow=true
EOF
chmod +x "$DESKTOP_DIR/echo-settings.desktop"

# Validate desktop file if validator is available
if command -v desktop-file-validate >/dev/null 2>&1; then
    desktop-file-validate "$DESKTOP_DIR/echo-settings.desktop" || true
fi

# 6. Update system databases
echo "[5/5] Updating desktop and icon databases..."
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$ICONS_DIR" || true
fi

echo ""
echo "================================================="
echo "  Echo Settings successfully installed!          "
echo "================================================="
echo "You can now launch Echo Settings from:"
echo "  • GNOME App Grid / Search ('Echo Settings')"
echo "  • Terminal: echo-settings"
echo "================================================="
