import os
import subprocess
import stat
import shutil

ICON_NAME = "echo-settings"

def install_icon(project_dir):
    """Устанавливает иконку в системные папки для поддержки дока и апплет GNOME."""
    icon_src = os.path.join(project_dir, "assets", "echo_icon.jpg")
    if not os.path.exists(icon_src):
        print(f"ВНИМАНИЕ: Файл {icon_src} не найден в {project_dir}.")
        return "preferences-system"

    sizes = [16, 32, 48, 64, 128, 256, 512]
    hicolor_base = os.path.expanduser("~/.local/share/icons/hicolor")

    try:
        from PIL import Image
        img = Image.open(icon_src)
        for size in sizes:
            size_dir = os.path.join(hicolor_base, f"{size}x{size}", "apps")
            os.makedirs(size_dir, exist_ok=True)
            dest = os.path.join(size_dir, f"{ICON_NAME}.jpg")
            resized = img.resize((size, size), Image.LANCZOS)
            resized.save(dest)
        print(f"Иконки установлены в {hicolor_base} (размеры: {sizes})")
    except ImportError:
        # Без Pillow — просто копируем оригинал в 256x256
        size_dir = os.path.join(hicolor_base, "256x256", "apps")
        os.makedirs(size_dir, exist_ok=True)
        dest = os.path.join(size_dir, f"{ICON_NAME}.jpg")
        shutil.copy2(icon_src, dest)
        print(f"Иконка установлена (без масштабирования): {dest}")

    # Также ставим scalable (SVG-место) с оригиналом
    scalable_dir = os.path.join(hicolor_base, "scalable", "apps")
    os.makedirs(scalable_dir, exist_ok=True)
    shutil.copy2(icon_src, os.path.join(scalable_dir, f"{ICON_NAME}.jpg"))

    # Обновляем кэш иконок
    try:
        subprocess.run(["gtk-update-icon-cache", "-f", "-t", hicolor_base], check=False)
    except FileNotFoundError:
        pass

    return ICON_NAME


def main():
    project_dir = os.path.abspath(os.path.dirname(__file__))
    venv_python = os.path.join(project_dir, "venv", "bin", "python")

    icon = install_icon(project_dir)

    desktop_content = f"""[Desktop Entry]
Type=Application
Name=Echo Settings
GenericName=System Settings
Comment=System Settings for Echo
Exec="{venv_python}" "{os.path.join(project_dir, 'main.py')}"
Path={project_dir}
Icon={icon}
Terminal=false
Categories=Settings;DesktopSettings;Qt;GNOME;
Keywords=settings;system;preferences;display;network;wifi;bluetooth;storage;
StartupWMClass=Echo_Settings
StartupNotify=true
X-GNOME-SingleWindow=true
"""

    # Сохраняем .desktop файл
    applications_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(applications_dir, exist_ok=True)

    desktop_file_path = os.path.join(applications_dir, "echo-settings.desktop")

    with open(desktop_file_path, "w") as f:
        f.write(desktop_content)

    # Делаем исполняемым
    st = os.stat(desktop_file_path)
    os.chmod(desktop_file_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # Обновляем базу данных ярлыков
    try:
        subprocess.run(["update-desktop-database", applications_dir], check=True)
        print("База данных ярлыков обновлена.")
    except FileNotFoundError:
        print("Утилита update-desktop-database не найдена. База данных обновится при перезагрузке сессии.")
    except Exception as e:
        print(f"Ошибка при обновлении базы данных ярлыков: {e}")

    print(f"\n✓ Ярлык создан: {desktop_file_path}")
    print("✓ Echo Settings доступен в меню приложений.")
    print("✓ Иконку можно закрепить на доке GNOME: ПКМ на иконке в меню → 'Добавить в избранное'.")


if __name__ == "__main__":
    main()
