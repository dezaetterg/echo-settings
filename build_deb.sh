#!/bin/bash
set -e

# ==============================================================================
# Echo Settings - Debian Package Builder (.deb)
# Compatible with Ubuntu, Debian, Linux Mint, PikaOS, Pop!_OS
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VERSION="1.0.3"
PKGNAME="echo-settings"
ARCH="amd64"
DEB_NAME="${PKGNAME}_${VERSION}_${ARCH}.deb"

BUILD_DIR="$SCRIPT_DIR/build/deb-package"
DIST_DIR="$SCRIPT_DIR/dist"

echo "=========================================="
echo "📦 Сборка deb-пакета: ${PKGNAME} v${VERSION}"
echo "=========================================="

# 1. Clean previous builds
echo "[1/6] Очистка предыдущих сборок..."
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$DIST_DIR"

# 2. Create package layout
echo "[2/6] Создание структуры каталогов..."
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/echo-settings"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/512x512/apps"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/128x128/apps"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/64x64/apps"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/48x48/apps"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/32x32/apps"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/16x16/apps"
mkdir -p "$BUILD_DIR/usr/share/doc/echo-settings"

# 3. Copy application files
echo "[3/6] Копирование компонентов приложения..."
rsync -a     --exclude '__pycache__'     --exclude '*.pyc'     --exclude '*.log'     --exclude '.git*'     --exclude 'build'     --exclude 'dist'     --exclude 'venv'     --exclude '.vscode'     --exclude '*.deb'     "$SCRIPT_DIR/" "$BUILD_DIR/usr/share/echo-settings/"

# Copy icons and desktop entry
if [ -f "$SCRIPT_DIR/icon.png" ]; then
    cp "$SCRIPT_DIR/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps/echo-settings.png"
    cp "$SCRIPT_DIR/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/512x512/apps/echo-settings.png"
    cp "$SCRIPT_DIR/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps/echo-settings.png"
    cp "$SCRIPT_DIR/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/128x128/apps/echo-settings.png"
    cp "$SCRIPT_DIR/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/64x64/apps/echo-settings.png"
    cp "$SCRIPT_DIR/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/48x48/apps/echo-settings.png"
    cp "$SCRIPT_DIR/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/32x32/apps/echo-settings.png"
    cp "$SCRIPT_DIR/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/16x16/apps/echo-settings.png"
fi

# Executable launcher wrapper
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
Comment=Modern System Control Center for Echo Linux
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

# Docs
cp "$SCRIPT_DIR/README.md" "$BUILD_DIR/usr/share/doc/echo-settings/README.md" 2>/dev/null || true
cp "$SCRIPT_DIR/LICENSE" "$BUILD_DIR/usr/share/doc/echo-settings/copyright"

# 4. Debian package metadata
echo "[4/6] Подготовка метаданных пакета..."
INSTALLED_SIZE=$(du -sk "$BUILD_DIR/usr" | awk '{print $1}')

cat << META_EOF > "$BUILD_DIR/DEBIAN/control"
Package: echo-settings
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Installed-Size: ${INSTALLED_SIZE}
Maintainer: Echo Contributors <https://github.com/dezaetterg/echo-settings>
Depends: python3 (>= 3.10), python3-pyside6 | python3-pyqt6, python3-psutil, python3-dbus-next | python3-dbus, python3-jeepney
Recommends: network-manager, wireplumber | pulseaudio, bluez
Description: Modern System Control Center for Linux
 Echo Settings is an elegant, modular system control center built with Qt6/PySide6.
 Provides native controls for Appearance, Display, Network, Sound, Power,
 Privacy, Storage, Bluetooth, Keyboard, and Echo Search launcher configuration.
META_EOF

cat << 'POST_EOF' > "$BUILD_DIR/DEBIAN/postinst"
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
exit 0
POST_EOF
chmod 755 "$BUILD_DIR/DEBIAN/postinst"

cat << 'POSTRM_EOF' > "$BUILD_DIR/DEBIAN/postrm"
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
exit 0
POSTRM_EOF
chmod 755 "$BUILD_DIR/DEBIAN/postrm"

# 5. Fix permissions
echo "[5/6] Настройка прав доступа..."
find "$BUILD_DIR" -type d -exec chmod 755 {} +
find "$BUILD_DIR/usr/share/echo-settings" -type f -exec chmod 644 {} +
chmod 755 "$BUILD_DIR/usr/bin/echo-settings"
chmod 755 "$BUILD_DIR/DEBIAN/postinst" "$BUILD_DIR/DEBIAN/postrm"

# 6. Build .deb package
echo "[6/6] Сборка .deb архива..."
dpkg-deb --build --root-owner-group "$BUILD_DIR" "$DIST_DIR/$DEB_NAME"
cp "$DIST_DIR/$DEB_NAME" "$DIST_DIR/echo-settings_latest.deb"

cd "$DIST_DIR"
sha256sum "$DEB_NAME" > "${DEB_NAME}.sha256"
cd "$SCRIPT_DIR"

rm -rf "$BUILD_DIR"

echo "=========================================="
echo "✅ Пакет успешно собран: $DIST_DIR/$DEB_NAME"
ls -lh "$DIST_DIR/$DEB_NAME"
echo "=========================================="
