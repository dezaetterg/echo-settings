# Maintainer: Echo Contributors <https://github.com/dezaetterg/echo-settings>
pkgname=echo-settings
pkgver=1.0.3
pkgrel=1
pkgdesc="Modern Liquid Glass System Control Center for Linux"
arch=('any')
url="https://github.com/dezaetterg/echo-settings"
license=('GPL-3.0-or-later')
depends=(
    'python>=3.10'
    'pyside6'
    'python-psutil'
)
optdepends=(
    'python-pulsectl: PulseAudio/PipeWire audio mixer controls'
    'networkmanager: Network & WiFi management'
    'bluez: Bluetooth device management'
    'wireplumber: PipeWire session manager'
    'brightnessctl: Display backlight brightness control'
)
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    install -d "$pkgdir/usr/bin"
    install -d "$pkgdir/usr/share/echo-settings"
    install -d "$pkgdir/usr/share/applications"
    install -d "$pkgdir/usr/share/icons/hicolor/scalable/apps"
    install -d "$pkgdir/usr/share/licenses/echo-settings"
    install -d "$pkgdir/usr/share/doc/echo-settings"

    # Application files
    cp -r assets backends components models pages services styles theme installer *.py "$pkgdir/usr/share/echo-settings/"
    
    # Clean temporary files if any
    find "$pkgdir/usr/share/echo-settings" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$pkgdir/usr/share/echo-settings" -name "*.pyc" -delete 2>/dev/null || true

    # Launcher wrapper
    cat << 'BIN_EOF' > "$pkgdir/usr/bin/echo-settings"
#!/usr/bin/env bash
export PYTHONPATH="/usr/share/echo-settings:$PYTHONPATH"
exec python3 /usr/share/echo-settings/main.py "$@"
BIN_EOF
    chmod 755 "$pkgdir/usr/bin/echo-settings"

    # Desktop entry
    cat << 'DESK_EOF' > "$pkgdir/usr/share/applications/echo-settings.desktop"
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
    chmod 644 "$pkgdir/usr/share/applications/echo-settings.desktop"

    # Icons
    if [ -f icon.png ]; then
        install -m 644 icon.png "$pkgdir/usr/share/icons/hicolor/scalable/apps/echo-settings.png"
        for sz in 16 32 48 64 128 256 512; do
            install -d "$pkgdir/usr/share/icons/hicolor/${sz}x${sz}/apps"
            install -m 644 icon.png "$pkgdir/usr/share/icons/hicolor/${sz}x${sz}/apps/echo-settings.png"
        done
    fi

    # License and Docs
    install -m 644 LICENSE "$pkgdir/usr/share/licenses/echo-settings/LICENSE"
    install -m 644 LICENSE "$pkgdir/usr/share/doc/echo-settings/copyright"
    install -m 644 README.md "$pkgdir/usr/share/doc/echo-settings/README.md"
}
