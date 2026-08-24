import subprocess
import os
import socket
import sys

# Try in-process Gio if available
try:
    if "/usr/lib/python3/dist-packages" not in sys.path:
        sys.path.append("/usr/lib/python3/dist-packages")
    import gi
    gi.require_version('Gio', '2.0')
    from gi.repository import Gio
    _has_gio = True
except Exception:
    _has_gio = False

def _get_gio_schema(schema_id: str):
    if _has_gio:
        try:
            source = Gio.SettingsSchemaSource.get_default()
            if source and source.lookup(schema_id, True):
                return Gio.Settings.new(schema_id)
        except Exception:
            pass
    return None

class GeneralBackend:
    _cached_locales = None
    _cached_gpu = None
    _cached_tzs = None

    def _run(self, cmd, default="Unknown", timeout=1.5):
        try:
            return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL, timeout=timeout).strip()
        except Exception:
            return default

    def get_hostname(self):
        try:
            return os.uname().nodename
        except Exception:
            try:
                return socket.gethostname()
            except Exception:
                return self._run(["hostname"])

    def get_cpu(self):
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except Exception:
            pass
        return "Unknown CPU"

    def get_gpu(self):
        if GeneralBackend._cached_gpu:
            return GeneralBackend._cached_gpu
        try:
            out = self._run(["lspci"])
            for line in out.split('\n'):
                if "VGA compatible controller" in line or "3D controller" in line:
                    gpu = line.split(":", 2)[-1].strip()
                    GeneralBackend._cached_gpu = gpu
                    return gpu
        except Exception:
            pass
        return "Unknown GPU"

    def get_ram(self):
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        kb = int(line.split()[1])
                        gb = round(kb / (1024 * 1024), 1)
                        if gb.is_integer():
                            return f"{int(gb)} GB"
                        return f"{gb} GB"
        except Exception:
            pass
        return "Unknown RAM"

    def get_kernel(self):
        try:
            return os.uname().release
        except Exception:
            return self._run(["uname", "-r"])

    def get_architecture(self):
        try:
            return os.uname().machine
        except Exception:
            return self._run(["uname", "-m"])
        
    def get_disk(self):
        try:
            st = os.statvfs('/')
            total_gb = (st.f_blocks * st.f_frsize) / (1024**3)
            free_gb = (st.f_bavail * st.f_frsize) / (1024**3)
            return f"{total_gb:.0f}G ({free_gb:.1f}G free)"
        except Exception:
            try:
                out = self._run(["df", "-h", "/"])
                lines = out.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    return f"{parts[1]} ({parts[3]} free)"
            except Exception:
                pass
        return "Unknown Disk"

    # Default Applications
    def get_default_browser(self):
        out = self._run(["xdg-settings", "get", "default-web-browser"])
        return out if out != "Unknown" else "System Default"
        
    def set_default_browser(self, desktop_file):
        self._run(["xdg-settings", "set", "default-web-browser", desktop_file])
        
    def get_installed_browsers(self):
        try:
            out = self._run(["gio", "mime", "x-scheme-handler/http"])
            browsers = set()
            for line in out.split('\n'):
                line = line.strip()
                if line.endswith(".desktop"):
                    parts = line.split()
                    for p in parts:
                        if p.endswith(".desktop"):
                            browsers.add(p)
                            break
            
            result = {}
            for b in browsers:
                name = b.replace(".desktop", "").replace("-browser", "").title()
                if name.lower() == "google-chrome": name = "Google Chrome"
                if name.lower() == "microsoft-edge": name = "Microsoft Edge"
                if name.lower() == "brave": name = "Brave"
                result[b] = name
            return result
        except Exception:
            return {}

    def get_locales(self):
        if GeneralBackend._cached_locales is not None:
            return GeneralBackend._cached_locales
        try:
            from PySide6.QtCore import QLocale
            out = self._run(["localectl", "list-locales"])
            locales = {}
            for line in out.split():
                if "UTF-8" in line:
                    loc = line.replace(".UTF-8", "")
                    qloc = QLocale(loc)
                    lang = qloc.nativeLanguageName()
                    country = qloc.nativeCountryName()
                    
                    if lang and country:
                        name = f"{lang.title()} ({country})"
                    else:
                        name = loc
                    locales[line] = name
            GeneralBackend._cached_locales = locales if locales else {"en_US.UTF-8": "English (United States)"}
            return GeneralBackend._cached_locales
        except Exception:
            return {"en_US.UTF-8": "English (United States)"}
            
    def get_current_locale(self):
        try:
            lang = os.environ.get("LANG") or os.environ.get("LC_ALL")
            if lang:
                return lang.strip()
            out = self._run(["localectl", "status"])
            for line in out.split('\n'):
                if "System Locale: LANG=" in line:
                    return line.split("LANG=")[1].strip()
        except Exception:
            pass
        return "en_US.UTF-8"
        
    def set_locale(self, locale_str):
        self._run(["pkexec", "localectl", "set-locale", f"LANG={locale_str}"])
        
    # Actions
    def lock_screen(self):
        self._run(["loginctl", "lock-session"])
        
    def log_out(self):
        self._run(["gnome-session-quit", "--logout", "--no-prompt"])
        
    def restart(self):
        self._run(["systemctl", "reboot"])
        
    def power_off(self):
        self._run(["systemctl", "poweroff"])

    def get_region(self):
        s = _get_gio_schema("org.gnome.system.locale")
        if s:
            try:
                if "region" in s.list_keys():
                    val = s.get_string("region")
                    if val:
                        return val
            except Exception:
                pass
        try:
            val = self._run(["gsettings", "get", "org.gnome.system.locale", "region"])
            if val and val != "Unknown":
                return val.strip("'")
        except Exception:
            pass
        return "en_US.UTF-8"
        
    def set_region(self, region_str):
        s = _get_gio_schema("org.gnome.system.locale")
        if s:
            try:
                if "region" in s.list_keys():
                    s.set_string("region", region_str)
                    return
            except Exception:
                pass
        self._run(["gsettings", "set", "org.gnome.system.locale", "region", region_str])
        
    def check_updates(self):
        try:
            out = subprocess.check_output("apt list --upgradable 2>/dev/null", shell=True).decode()
            count = len([line for line in out.split('\n') if line.strip() and "Listing" not in line])
            return count
        except Exception:
            return 0
        
    # Start Settings at Login
    def get_startup(self):
        return os.path.exists(os.path.expanduser("~/.config/autostart/tahoe-settings.desktop"))

    def set_startup(self, enabled):
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_file = os.path.join(autostart_dir, "tahoe-settings.desktop")
        if enabled:
            os.makedirs(autostart_dir, exist_ok=True)
            content = "[Desktop Entry]\nType=Application\nName=Echo Settings\nExec=/usr/bin/echo-settings\nHidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\n"
            try:
                with open(desktop_file, "w") as f:
                    f.write(content)
            except Exception:
                pass
        else:
            if os.path.exists(desktop_file):
                try:
                    os.remove(desktop_file)
                except Exception:
                    pass

    # App Config (QSettings)
    def _get_qsettings(self):
        from PySide6.QtCore import QSettings
        return QSettings("TahoeSettings", "App")

    def get_restore_page(self):
        return self._get_qsettings().value("restore_page", False, type=bool)

    def set_restore_page(self, enabled):
        self._get_qsettings().setValue("restore_page", enabled)

    def get_remember_size(self):
        return self._get_qsettings().value("remember_size", False, type=bool)

    def set_remember_size(self, enabled):
        self._get_qsettings().setValue("remember_size", enabled)

    # Time & Date
    def get_ntp(self):
        try:
            return "NTP=yes" in self._run(["timedatectl", "show"])
        except Exception:
            return True

    def set_ntp(self, enabled):
        self._run(["pkexec", "timedatectl", "set-ntp", "true" if enabled else "false"])

    def get_timezone(self):
        try:
            if os.path.islink('/etc/localtime'):
                target = os.readlink('/etc/localtime')
                if 'zoneinfo/' in target:
                    return target.split('zoneinfo/')[-1]
            if os.path.exists('/etc/timezone'):
                with open('/etc/timezone') as f:
                    tz = f.read().strip()
                    if tz: return tz
            for line in self._run(["timedatectl", "show"]).split('\n'):
                if line.startswith("Timezone="):
                    return line.split("=")[1].strip()
        except Exception:
            pass
        return "UTC"

    def set_timezone(self, tz):
        self._run(["pkexec", "timedatectl", "set-timezone", tz])

    def get_timezones(self):
        if GeneralBackend._cached_tzs:
            return GeneralBackend._cached_tzs
        try:
            zone_tab = "/usr/share/zoneinfo/zone.tab"
            if os.path.exists(zone_tab):
                tzs = []
                with open(zone_tab, 'r') as f:
                    for line in f:
                        if line.startswith('#') or not line.strip():
                            continue
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            tzs.append(parts[2].strip())
                tzs.sort()
                GeneralBackend._cached_tzs = tzs
                return tzs
        except Exception:
            pass
        try:
            tzs = self._run(["timedatectl", "list-timezones"]).split('\n')
            GeneralBackend._cached_tzs = tzs
            return tzs
        except Exception:
            return ["UTC"]

    # 24-hour Time
    def get_24_hour(self):
        s = _get_gio_schema("org.gnome.desktop.interface")
        if s:
            try:
                if "clock-format" in s.list_keys():
                    return s.get_string("clock-format") == "24h"
            except Exception:
                pass
        return self._run(["gsettings", "get", "org.gnome.desktop.interface", "clock-format"]) == "'24h'"

    def set_24_hour(self, enabled):
        fmt = "24h" if enabled else "12h"
        s = _get_gio_schema("org.gnome.desktop.interface")
        if s:
            try:
                if "clock-format" in s.list_keys():
                    s.set_string("clock-format", fmt)
                    return
            except Exception:
                pass
        self._run(["gsettings", "set", "org.gnome.desktop.interface", "clock-format", fmt])

    # Notifications
    def get_dnd(self):
        s = _get_gio_schema("org.gnome.desktop.notifications")
        if s:
            try:
                if "show-banners" in s.list_keys():
                    return not s.get_boolean("show-banners")
            except Exception:
                pass
        return self._run(["gsettings", "get", "org.gnome.desktop.notifications", "show-banners"]) == "false"

    def set_dnd(self, enabled):
        s = _get_gio_schema("org.gnome.desktop.notifications")
        if s:
            try:
                if "show-banners" in s.list_keys():
                    s.set_boolean("show-banners", not enabled)
                    return
            except Exception:
                pass
        val = "false" if enabled else "true"
        self._run(["gsettings", "set", "org.gnome.desktop.notifications", "show-banners", val])
        
    def get_notif_sounds(self):
        s = _get_gio_schema("org.gnome.desktop.sound")
        if s:
            try:
                if "event-sounds" in s.list_keys():
                    return s.get_boolean("event-sounds")
            except Exception:
                pass
        return self._run(["gsettings", "get", "org.gnome.desktop.sound", "event-sounds"]) == "true"
        
    def set_notif_sounds(self, enabled):
        s = _get_gio_schema("org.gnome.desktop.sound")
        if s:
            try:
                if "event-sounds" in s.list_keys():
                    s.set_boolean("event-sounds", enabled)
                    return
            except Exception:
                pass
        val = "true" if enabled else "false"
        self._run(["gsettings", "set", "org.gnome.desktop.sound", "event-sounds", val])


