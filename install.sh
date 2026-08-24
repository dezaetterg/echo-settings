#!/usr/bin/env bash
# ==============================================================================
# Echo Settings - Linux User Installer
# Installs Echo Settings as a native user application on Linux (Debian, Ubuntu, Mint, Arch, Fedora, etc.)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect project source directory
if [ -f "$SCRIPT_DIR/Tahoe Settings/main.py" ]; then
    SRC_DIR="$SCRIPT_DIR/Tahoe Settings"
elif [ -f "$SCRIPT_DIR/main.py" ]; then
    SRC_DIR="$SCRIPT_DIR"
else
    echo "❌ Ошибка: Файлы исходного кода Echo Settings не найдены в $SCRIPT_DIR"
    exit 1
fi

INSTALL_PREFIX="${HOME}/.local"
APP_DIR="${INSTALL_PREFIX}/share/echo-settings"
BIN_DIR="${INSTALL_PREFIX}/bin"
DESKTOP_DIR="${INSTALL_PREFIX}/share/applications"
ICONS_DIR="${INSTALL_PREFIX}/share/icons/hicolor"

GREEN='[0;32m'
BLUE='[0;34m'
YELLOW='[1;33m'
CYAN='[0;36m'
RED='[0;31m'
BOLD='[1m'
RESET='[0m'

echo -e "${BLUE}=================================================${RESET}"
echo -e "${BOLD}  Установка Echo Settings для текущего пользователя...${RESET}"
echo -e "${BLUE}=================================================${RESET}"
echo -e "Источник:    ${CYAN}$SRC_DIR${RESET}"
echo -e "Назначение:  ${CYAN}$APP_DIR${RESET}"
echo ""

# 1. Create target directories
mkdir -p "$APP_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"

# 2. Copy application components safely
echo -e "${BLUE}[1/5]${RESET} Копирование файлов приложения..."
rsync -a     --exclude '__pycache__'     --exclude '*.pyc'     --exclude '*.log'     --exclude '.git*'     --exclude 'venv'     --exclude 'build'     --exclude 'dist'     --exclude '*.deb'     --exclude '.vscode'     "$SRC_DIR/" "$APP_DIR/"

# 3. Check and setup Python environment
echo -e "${BLUE}[2/5]${RESET} Настройка окружения Python и зависимостей..."
HAS_PYSIDE=false
if python3 -c "import PySide6, psutil" 2>/dev/null; then
    HAS_PYSIDE=true
    echo -e "  ${GREEN}✓ Системный Python содержит PySide6 и psutil${RESET}"
fi

# If system python doesn't have PySide6, setup virtual environment or check package manager
if [ "$HAS_PYSIDE" = false ]; then
    echo -e "  ${YELLOW}ℹ Настройка изолированного окружения (venv)...${RESET}"
    if [ ! -d "$APP_DIR/venv" ] || [ ! -f "$APP_DIR/venv/bin/python" ]; then
        python3 -m venv "$APP_DIR/venv" 2>/dev/null || {
            echo -e "  ${YELLOW}⚠ python3-venv не найден в системе. Попытка установки через apt...${RESET}"
            if command -v apt >/dev/null 2>&1; then
                sudo apt update && sudo apt install -y python3-venv python3-pip python3-pyside6.qtcore python3-pyside6.qtgui python3-pyside6.qtwidgets python3-psutil python3-jeepney python3-dbus || true
            fi
            python3 -m venv "$APP_DIR/venv" 2>/dev/null || true
        }
    fi

    if [ -f "$APP_DIR/venv/bin/pip" ]; then
        echo -e "  ${CYAN}Установка зависимостей из requirements.txt...${RESET}"
        "$APP_DIR/venv/bin/pip" install --upgrade pip --quiet 2>/dev/null || true
        "$APP_DIR/venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt" || true
    fi
fi

# 4. Create launcher executable in ~/.local/bin/echo-settings
echo -e "${BLUE}[3/5]${RESET} Создание исполняемого файла в $BIN_DIR/echo-settings..."
cat << 'LAUNCHER_EOF' > "$BIN_DIR/echo-settings"
#!/usr/bin/env bash
# Echo Settings - Launcher Script
set -e

APP_DIR="${HOME}/.local/share/echo-settings"
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Echo Settings is not installed in $APP_DIR" >&2
    exit 1
fi

# Prioritize venv if PySide6 is installed there, otherwise use system python3
if [ -x "$APP_DIR/venv/bin/python" ] && "$APP_DIR/venv/bin/python" -c "import PySide6" 2>/dev/null; then
    PYTHON_EXEC="$APP_DIR/venv/bin/python"
elif python3 -c "import PySide6" 2>/dev/null; then
    PYTHON_EXEC="$(command -v python3)"
elif [ -x "$APP_DIR/venv/bin/python" ]; then
    PYTHON_EXEC="$APP_DIR/venv/bin/python"
else
    PYTHON_EXEC="$(command -v python3)"
fi

export PYTHONPATH="$APP_DIR:$PYTHONPATH"
exec "$PYTHON_EXEC" "$APP_DIR/main.py" "$@"
LAUNCHER_EOF
chmod +x "$BIN_DIR/echo-settings"

# Also place launcher copy inside APP_DIR
cp "$BIN_DIR/echo-settings" "$APP_DIR/echo-settings"
chmod +x "$APP_DIR/echo-settings"

# 5. Install desktop icons
echo -e "${BLUE}[4/5]${RESET} Установка иконок приложения..."
ICON_SRC=""
if [ -f "$APP_DIR/icon.png" ]; then
    ICON_SRC="$APP_DIR/icon.png"
elif [ -f "$APP_DIR/assets/echo_icon.png" ]; then
    ICON_SRC="$APP_DIR/assets/echo_icon.png"
elif [ -f "$APP_DIR/assets/echo_icon.jpg" ]; then
    ICON_SRC="$APP_DIR/assets/echo_icon.jpg"
fi

if [ -n "$ICON_SRC" ]; then
    # Try scaling with python if possible
    python3 - << PYEOF 2>/dev/null || true
import os
icon_src = "$ICON_SRC"
install_prefix = os.path.expanduser("~/.local")
hicolor_base = os.path.join(install_prefix, "share", "icons", "hicolor")
sizes = [16, 24, 32, 48, 64, 128, 256, 512]

# Try PIL first
try:
    from PIL import Image
    img = Image.open(icon_src)
    for sz in sizes:
        sz_dir = os.path.join(hicolor_base, f"{sz}x{sz}", "apps")
        os.makedirs(sz_dir, exist_ok=True)
        dest = os.path.join(sz_dir, "echo-settings.png")
        resized = img.resize((sz, sz), Image.Resampling.LANCZOS)
        resized.save(dest, "PNG")
    sc_dir = os.path.join(hicolor_base, "scalable", "apps")
    os.makedirs(sc_dir, exist_ok=True)
    img.save(os.path.join(sc_dir, "echo-settings.png"), "PNG")
except Exception:
    # Try PySide6
    try:
        from PySide6.QtGui import QImage
        from PySide6.QtCore import Qt
        img = QImage(icon_src)
        if not img.isNull():
            for sz in sizes:
                sz_dir = os.path.join(hicolor_base, f"{sz}x{sz}", "apps")
                os.makedirs(sz_dir, exist_ok=True)
                dest = os.path.join(sz_dir, "echo-settings.png")
                scaled = img.scaled(sz, sz, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                scaled.save(dest, "PNG")
            sc_dir = os.path.join(hicolor_base, "scalable", "apps")
            os.makedirs(sc_dir, exist_ok=True)
            img.save(os.path.join(sc_dir, "echo-settings.png"), "PNG")
    except Exception:
        pass
PYEOF

    # Ensure icons exist in scalable and standard sizes as fallback
    sizes=(16 24 32 48 64 128 256 512)
    for sz in "${sizes[@]}"; do
        mkdir -p "$ICONS_DIR/${sz}x${sz}/apps"
        if [ ! -f "$ICONS_DIR/${sz}x${sz}/apps/echo-settings.png" ]; then
            cp "$ICON_SRC" "$ICONS_DIR/${sz}x${sz}/apps/echo-settings.png"
        fi
    done
    mkdir -p "$ICONS_DIR/scalable/apps"
    cp "$ICON_SRC" "$ICONS_DIR/scalable/apps/echo-settings.png" 2>/dev/null || true
    echo -e "  ${GREEN}✓ Иконки успешно установлены в hicolor${RESET}"
fi

# 6. Create desktop entry
echo -e "${BLUE}[5/5]${RESET} Создание ярлыка приложения..."
cat << DESK_EOF > "$DESKTOP_DIR/echo-settings.desktop"
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
DESK_EOF
chmod +x "$DESKTOP_DIR/echo-settings.desktop"

# Validate desktop file if validator is available
if command -v desktop-file-validate >/dev/null 2>&1; then
    desktop-file-validate "$DESKTOP_DIR/echo-settings.desktop" || true
fi

# Update system databases
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$ICONS_DIR" || true
fi

# Check PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo -e "${YELLOW}ℹ Совет: Добавьте ~/.local/bin в переменную PATH:${RESET}"
    echo -e "  export PATH="\$HOME/.local/bin:\$PATH" (в ~/.bashrc или ~/.zshrc)"
fi

echo ""
echo -e "${GREEN}=================================================${RESET}"
echo -e "${GREEN}✨ Echo Settings успешно установлен!             ${RESET}"
echo -e "${GREEN}=================================================${RESET}"
echo -e "Запуск приложения:"
echo -e "  • Из меню приложений: ${CYAN}Echo Settings${RESET}"
echo -e "  • Из терминала:       ${CYAN}echo-settings${RESET}"
echo -e "${GREEN}=================================================${RESET}"
