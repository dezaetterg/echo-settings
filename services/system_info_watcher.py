"""
SystemInfoWatcher — периодически опрашивает систему и сигналит об изменениях
в имени пользователя, аватаре, hostname, GPU, RAM, ядре и т.д.
"""

import os
import subprocess
import hashlib

from PySide6.QtCore import QObject, QThread, Signal, QTimer


class _InfoFetcher(QThread):
    """Рабочий поток — собирает снимок системной информации."""
    done = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        self.done.emit(SystemInfoWatcher._collect())



class SystemInfoWatcher(QObject):
    """
    Singleton-подобный наблюдатель. Каждые interval_ms миллисекунд он
    перепроверяет информацию о системе. Если что-то изменилось — испускает
    `info_changed(dict)` с полным свежим снимком.

    Поля снимка:
        full_name      — полное имя пользователя (pw_gecos или username)
        username       — логин
        hostname       — имя хоста
        avatar_path    — путь к ~/.face (или '' если нет)
        avatar_hash    — MD5 файла аватара (или '' если нет)
        gpu            — строка GPU из lspci
        ram            — строка ОЗУ из /proc/meminfo
        kernel         — uname -r
        architecture   — uname -m
        disk           — df /
        cpu            — /proc/cpuinfo model name
        session_type   — XDG_SESSION_TYPE (wayland / x11)
        desktop        — XDG_CURRENT_DESKTOP
    """

    info_changed = Signal(dict)

    def __init__(self, interval_ms: int = 5000, parent=None):
        super().__init__(parent)
        self._last_snapshot: dict = {}
        self._fetcher: _InfoFetcher | None = None

        # Запуск сразу при создании
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._poll)
        self._timer.start()

        # Первая проверка — немедленно
        self._poll()

    # ------------------------------------------------------------------
    # Публичный API
    # ------------------------------------------------------------------
    def stop(self):
        """Остановить таймер и фоновый поток."""
        if hasattr(self, '_timer'):
            self._timer.stop()
        if self._fetcher and self._fetcher.isRunning():
            self._fetcher.quit()
            self._fetcher.wait(500)

    def get_snapshot(self) -> dict:
        """Вернуть последний известный снимок (синхронно)."""
        if not self._last_snapshot:
            self._last_snapshot = self._collect()
        return dict(self._last_snapshot)


    # ------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------
    def _poll(self):
        """Запустить фоновый поток для сбора данных."""
        if self._fetcher and self._fetcher.isRunning():
            return  # предыдущий ещё не закончил
        self._fetcher = _InfoFetcher(self)
        self._fetcher.done.connect(self._on_fetched)
        self._fetcher.start()

    def _on_fetched(self, snapshot: dict):
        if snapshot != self._last_snapshot:
            self._last_snapshot = snapshot
            self.info_changed.emit(dict(snapshot))

    # ------------------------------------------------------------------
    # Сбор данных (статический, вызывается из потока)
    # ------------------------------------------------------------------
    @staticmethod
    def _collect() -> dict:
        import pwd

        # --- Пользователь ---
        try:
            user_info = pwd.getpwuid(os.getuid())
            full_name = user_info.pw_gecos.split(',')[0].strip() or user_info.pw_name
            username = user_info.pw_name
        except Exception:
            full_name = os.environ.get("USER", "User")
            username = full_name

        # --- Avatar ---
        avatar_path = ""
        avatar_hash = ""

        # Priority: AccountsService icon (updated by GNOME Settings) → ~/.face
        accounts_icon = f"/var/lib/AccountsService/icons/{username}"
        if os.path.exists(accounts_icon):
            avatar_path = accounts_icon
        else:
            face = os.path.expanduser("~/.face")
            if os.path.exists(face):
                avatar_path = face

        if avatar_path:
            try:
                with open(avatar_path, "rb") as f:
                    avatar_hash = hashlib.md5(f.read()).hexdigest()
            except Exception:
                pass

        # --- Хост ---
        try:
            hostname = subprocess.check_output(["hostname"], text=True,
                                               stderr=subprocess.DEVNULL).strip()
        except Exception:
            hostname = os.environ.get("HOSTNAME", "localhost")

        # --- CPU ---
        cpu = "Unknown CPU"
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("model name"):
                        cpu = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass

        # --- GPU ---
        gpu = "Unknown GPU"
        try:
            out = subprocess.check_output(["lspci"], text=True,
                                          stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                if "VGA compatible controller" in line or "3D controller" in line:
                    gpu = line.split(":", 2)[-1].strip()
                    break
        except Exception:
            pass

        # --- RAM ---
        ram = "Unknown RAM"
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        kb = int(line.split()[1])
                        gb = round(kb / (1024 * 1024), 1)
                        ram = f"{int(gb)} GB" if gb.is_integer() else f"{gb} GB"
                        break
        except Exception:
            pass

        # --- Kernel & Arch ---
        def _cmd(args, default=""):
            try:
                return subprocess.check_output(args, text=True,
                                               stderr=subprocess.DEVNULL).strip()
            except Exception:
                return default

        kernel = _cmd(["uname", "-r"])
        arch = _cmd(["uname", "-m"])

        # --- Disk ---
        disk = "Unknown Disk"
        try:
            out = _cmd(["df", "-h", "/"])
            parts = out.splitlines()[1].split()
            disk = f"{parts[1]} ({parts[3]} free)"
        except Exception:
            pass

        # --- Session / Desktop ---
        session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "unknown")

        # --- OS version ---
        os_name = "Linux"
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        os_name = line.split("=", 1)[1].strip().strip('"')
                        break
        except Exception:
            pass

        return {
            "full_name": full_name,
            "username": username,
            "hostname": hostname,
            "avatar_path": avatar_path,
            "avatar_hash": avatar_hash,
            "cpu": cpu,
            "gpu": gpu,
            "ram": ram,
            "kernel": kernel,
            "architecture": arch,
            "disk": disk,
            "session_type": session_type,
            "desktop": desktop,
            "os_name": os_name,
        }
