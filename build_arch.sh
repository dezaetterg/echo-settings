#!/bin/bash
set -e

# ==============================================================================
# Echo Settings - Arch Linux Package Builder (.pkg.tar.zst)
# Compatible with Arch Linux, Manjaro, EndeavourOS, Garuda, CachyOS
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VERSION="1.0.4"
RELEASE="1"
PKGNAME="echo-settings"
PKG_FULL="${PKGNAME}-${VERSION}-${RELEASE}-any.pkg.tar.zst"

BUILD_DIR="$SCRIPT_DIR/build/arch-package"
DIST_DIR="$SCRIPT_DIR/dist"

echo "=========================================="
echo "📦 Сборка Arch-пакета: ${PKG_FULL}"
echo "=========================================="

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/echo-settings"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps"
for sz in 16 32 48 64 128 256 512; do
    mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/${sz}x${sz}/apps"
done
mkdir -p "$BUILD_DIR/usr/share/licenses/echo-settings"
mkdir -p "$BUILD_DIR/usr/share/doc/echo-settings"
mkdir -p "$DIST_DIR"

# Copy application files
rsync -a     --exclude '__pycache__'     --exclude '*.pyc'     --exclude '*.log'     --exclude '.git*'     --exclude 'build'     --exclude 'dist'     --exclude 'venv'     --exclude '.vscode'     --exclude '*.deb'     --exclude '*.tar.zst'     "$SCRIPT_DIR/" "$BUILD_DIR/usr/share/echo-settings/"

# Launcher wrapper
cat << 'BIN_EOF' > "$BUILD_DIR/usr/bin/echo-settings"
#!/usr/bin/env bash
export PYTHONPATH="/usr/share/echo-settings:$PYTHONPATH"
if [ "$XDG_SESSION_TYPE" = "wayland" ] && [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]] && [ -z "$QT_QPA_PLATFORM" ]; then
    export QT_QPA_PLATFORM="xcb"
fi
exec python3 /usr/share/echo-settings/main.py "$@"
BIN_EOF
chmod 755 "$BUILD_DIR/usr/bin/echo-settings"

# Desktop entry
cat << 'DESK_EOF' > "$BUILD_DIR/usr/share/applications/echo-settings.desktop"
[Desktop Entry]
Type=Application
Name=Echo Settings
GenericName=System Settings
Comment=Modern System Control Center for Linux
Exec=/usr/bin/echo-settings %U
Icon=echo-settings
Terminal=false
Categories=Settings;HardwareSettings;DesktopSettings;Qt;
Keywords=Preferences;Settings;Control;Center;Echo;Display;Appearance;WiFi;Network;Bluetooth;Power;Sound;Storage;Keyboard;
StartupWMClass=Echo_Settings
StartupNotify=true
SingleMainWindow=true
DESK_EOF
chmod 644 "$BUILD_DIR/usr/share/applications/echo-settings.desktop"

# Icons
if [ -f "$SCRIPT_DIR/icon.png" ]; then
    cp "$SCRIPT_DIR/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps/echo-settings.png"
    for sz in 16 32 48 64 128 256 512; do
        cp "$SCRIPT_DIR/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/${sz}x${sz}/apps/echo-settings.png"
    done
fi

# License & Docs
cp "$SCRIPT_DIR/LICENSE" "$BUILD_DIR/usr/share/licenses/echo-settings/LICENSE"
cp "$SCRIPT_DIR/LICENSE" "$BUILD_DIR/usr/share/doc/echo-settings/copyright"
cp "$SCRIPT_DIR/README.md" "$BUILD_DIR/usr/share/doc/echo-settings/README.md"

# Calculate installed size
TOTAL_SIZE=$(du -sb "$BUILD_DIR/usr" | awk '{print $1}')
BUILD_DATE=$(date +%s)

# Create .PKGINFO metadata
cat << PKG_EOF > "$BUILD_DIR/.PKGINFO"
pkgname = ${PKGNAME}
pkgbase = ${PKGNAME}
pkgver = ${VERSION}-${RELEASE}
pkgdesc = Modern Liquid Glass System Control Center for Linux
url = https://github.com/dezaetterg/echo-settings
builddate = ${BUILD_DATE}
packager = Echo Contributors <https://github.com/dezaetterg/echo-settings>
size = ${TOTAL_SIZE}
arch = any
license = GPL-3.0-or-later
depend = python>=3.10
depend = pyside6
depend = python-psutil
optdepend = python-pulsectl: Audio volume mixer control
optdepend = networkmanager: Network & WiFi management
optdepend = bluez: Bluetooth device management
optdepend = wireplumber: PipeWire session manager
optdepend = brightnessctl: Display backlight brightness control
PKG_EOF

# Set canonical package permissions
find "$BUILD_DIR/usr" -type d -exec chmod 755 {} +
find "$BUILD_DIR/usr" -type f -exec chmod 644 {} +
chmod 755 "$BUILD_DIR/usr/bin/echo-settings"
chmod 644 "$BUILD_DIR/.PKGINFO"

# Package with tar and zstd
tar -c --owner=0 --group=0 --numeric-owner --mode='a-st' -C "$BUILD_DIR" .PKGINFO usr | zstd -c -T0 > "$DIST_DIR/$PKG_FULL"
cp "$DIST_DIR/$PKG_FULL" "$DIST_DIR/echo-settings_latest-any.pkg.tar.zst"

cd "$DIST_DIR"
sha256sum "$PKG_FULL" > "${PKG_FULL}.sha256"
cd "$SCRIPT_DIR"

rm -rf "$BUILD_DIR"
echo "=========================================="
echo "✅ Arch-пакет успешно собран: $DIST_DIR/$PKG_FULL"
ls -lh "$DIST_DIR/$PKG_FULL"
echo "=========================================="
