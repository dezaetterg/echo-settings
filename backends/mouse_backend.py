import os
import re
import sys
import subprocess

try:
    if "/usr/lib/python3/dist-packages" not in sys.path:
        sys.path.append("/usr/lib/python3/dist-packages")
    import gi
    gi.require_version('Gio', '2.0')
    from gi.repository import Gio
    _has_gio = True
except Exception:
    _has_gio = False

SCHEMA_MOUSE = "org.gnome.desktop.peripherals.mouse"

class MouseBackend:
    """
    Unified GNOME Wayland backend for system mouse settings and hardware detection.
    Interfaces directly with GNOME/Mutter GSettings (`org.gnome.desktop.peripherals.mouse`)
    via Gio.Settings with transparent subprocess CLI fallback.
    """
    def __init__(self):
        self._settings = None
        if _has_gio:
            try:
                source = Gio.SettingsSchemaSource.get_default()
                if source and source.lookup(SCHEMA_MOUSE, True):
                    self._settings = Gio.Settings.new(SCHEMA_MOUSE)
                else:
                    self._settings = None
            except Exception:
                self._settings = None

    # -------------------------------------------------------------------------
    # GSettings Helpers
    # -------------------------------------------------------------------------
    def _get_boolean(self, key: str, default: bool = False) -> bool:
        if self._settings:
            try:
                return self._settings.get_boolean(key)
            except Exception:
                pass
        for schema in (SCHEMA_MOUSE, "org.cinnamon.desktop.peripherals.mouse", "org.cinnamon.desktop.peripherals.touchpad"):
            try:
                res = subprocess.run(['gsettings', 'get', schema, key], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip().lower() == 'true'
            except Exception:
                pass
        return default

    def _set_boolean(self, key: str, val: bool) -> bool:
        val_bool = bool(val)
        if self._settings:
            try:
                self._settings.set_boolean(key, val_bool)
                Gio.Settings.sync()
            except Exception:
                pass
        val_str = 'true' if val_bool else 'false'
        for schema in (SCHEMA_MOUSE, "org.cinnamon.desktop.peripherals.mouse", "org.cinnamon.desktop.peripherals.touchpad"):
            try:
                subprocess.Popen(
                    ['gsettings', 'set', schema, key, val_str],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass
        return True

    def _get_double(self, key: str, default: float = 0.0) -> float:
        if self._settings:
            try:
                return float(self._settings.get_double(key))
            except Exception:
                pass
        for schema in (SCHEMA_MOUSE, "org.cinnamon.desktop.peripherals.mouse", "org.cinnamon.desktop.peripherals.touchpad"):
            try:
                res = subprocess.run(['gsettings', 'get', schema, key], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    return float(res.stdout.strip())
            except Exception:
                pass
        return default

    def _set_double(self, key: str, val: float) -> bool:
        val_float = float(val)
        if self._settings:
            try:
                self._settings.set_double(key, val_float)
                Gio.Settings.sync()
            except Exception:
                pass
        for schema in (SCHEMA_MOUSE, "org.cinnamon.desktop.peripherals.mouse", "org.cinnamon.desktop.peripherals.touchpad"):
            try:
                subprocess.Popen(
                    ['gsettings', 'set', schema, key, str(val_float)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass
        return True

    def _get_int(self, key: str, default: int = 400) -> int:
        if self._settings:
            try:
                return int(self._settings.get_int(key))
            except Exception:
                pass
        for schema in (
            SCHEMA_MOUSE,
            "org.cinnamon.desktop.peripherals.mouse",
            "org.mate.peripherals-mouse",
            "org.gnome.settings-daemon.peripherals.mouse"
        ):
            try:
                res = subprocess.run(['gsettings', 'get', schema, key], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    cleaned = res.stdout.strip().replace("uint32", "").strip()
                    if cleaned.isdigit():
                        return int(cleaned)
            except Exception:
                pass
        return default

    def _set_int(self, key: str, val: int) -> bool:
        val_int = int(val)
        if self._settings:
            try:
                self._settings.set_int(key, val_int)
                Gio.Settings.sync()
            except Exception:
                pass
        for schema in (
            SCHEMA_MOUSE,
            "org.cinnamon.desktop.peripherals.mouse",
            "org.mate.peripherals-mouse",
            "org.gnome.settings-daemon.peripherals.mouse"
        ):
            try:
                subprocess.Popen(
                    ['gsettings', 'set', schema, key, str(val_int)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass
        return True

    def _get_string(self, key: str, default: str = "") -> str:
        if self._settings:
            try:
                return self._settings.get_string(key)
            except Exception:
                pass
        for schema in (SCHEMA_MOUSE, "org.cinnamon.desktop.peripherals.mouse", "org.cinnamon.desktop.peripherals.touchpad"):
            try:
                res = subprocess.run(['gsettings', 'get', schema, key], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip().strip("'")
            except Exception:
                pass
        return default

    def _set_string(self, key: str, val: str) -> bool:
        val_str = str(val).strip("'")
        if self._settings:
            try:
                self._settings.set_string(key, val_str)
                Gio.Settings.sync()
            except Exception:
                pass
        for schema in (SCHEMA_MOUSE, "org.cinnamon.desktop.peripherals.mouse", "org.cinnamon.desktop.peripherals.touchpad"):
            try:
                subprocess.Popen(
                    ['gsettings', 'set', schema, key, f"'{val_str}'"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass
        return True

    # -------------------------------------------------------------------------
    # 1. Primary Button (Left vs Right handed)
    # -------------------------------------------------------------------------
    def get_primary_button(self) -> str:
        """Returns 'left' if left-click is primary, 'right' if right-click is primary."""
        is_left_handed = self._get_boolean("left-handed", False)
        return "right" if is_left_handed else "left"

    def set_primary_button(self, button: str) -> bool:
        """Sets primary button. Accepts 'left', 'right', or boolean (True = right-handed primary / left button)."""
        if isinstance(button, bool):
            is_left_handed = not button
        else:
            is_left_handed = (str(button).lower() == "right")
        return self._set_boolean("left-handed", is_left_handed)

    def is_left_handed(self) -> bool:
        return self._get_boolean("left-handed", False)

    def set_left_handed(self, enabled: bool) -> bool:
        return self._set_boolean("left-handed", bool(enabled))

    # -------------------------------------------------------------------------
    # 2. Pointer Speed (-1.0 to 1.0)
    # -------------------------------------------------------------------------
    def get_pointer_speed(self) -> float:
        """Returns pointer speed in range [-1.0 .. 1.0], default 0.0."""
        return max(-1.0, min(1.0, self._get_double("speed", 0.0)))

    def set_pointer_speed(self, speed: float) -> bool:
        """Sets pointer speed clamped to [-1.0 .. 1.0]."""
        clamped = max(-1.0, min(1.0, float(speed)))
        return self._set_double("speed", clamped)

    # -------------------------------------------------------------------------
    # 3. Natural Scrolling
    # -------------------------------------------------------------------------
    def get_natural_scroll(self) -> bool:
        """Returns True if natural (reverse) scrolling is enabled."""
        return self._get_boolean("natural-scroll", False)

    def set_natural_scroll(self, enabled: bool) -> bool:
        """Enables or disables natural (reverse) scrolling."""
        return self._set_boolean("natural-scroll", bool(enabled))

    # -------------------------------------------------------------------------
    # 4. Double-click Speed (ms) - Universal Desktop Support
    # -------------------------------------------------------------------------
    def get_double_click(self) -> int:
        """
        Returns double-click threshold in milliseconds (default 400).
        Checks GSettings (Cinnamon/MATE), GTK settings.ini (GNOME/PikaOS),
        KDE kdeglobals, or persistent app configuration.
        """
        # 1. Check GSettings schemas (Mint / Cinnamon / MATE)
        for schema in (
            "org.cinnamon.desktop.peripherals.mouse",
            "org.mate.peripherals-mouse",
            "org.gnome.settings-daemon.peripherals.mouse"
        ):
            try:
                res = subprocess.run(['gsettings', 'get', schema, 'double-click'], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    cleaned = res.stdout.strip().replace("uint32", "").strip()
                    if cleaned.isdigit():
                        return max(100, min(1000, int(cleaned)))
            except Exception:
                pass

        # 2. Check GTK3 & GTK4 settings.ini (GNOME / PikaOS / Ubuntu)
        import configparser
        for ini_path in [
            os.path.expanduser("~/.config/gtk-4.0/settings.ini"),
            os.path.expanduser("~/.config/gtk-3.0/settings.ini")
        ]:
            if os.path.isfile(ini_path):
                try:
                    cp = configparser.ConfigParser()
                    cp.read(ini_path)
                    if cp.has_section("Settings") and cp.has_option("Settings", "gtk-double-click-time"):
                        val = int(cp.get("Settings", "gtk-double-click-time"))
                        return max(100, min(1000, val))
                except Exception:
                    pass

        # 3. Check persistent App settings
        try:
            from PySide6.QtCore import QSettings
            qs = QSettings("TahoeSettings", "Mouse")
            val = qs.value("double_click", None)
            if val is not None:
                return max(100, min(1000, int(val)))
        except Exception:
            pass

        return 400

    def set_double_click(self, ms: int) -> bool:
        """
        Sets double-click threshold in milliseconds (100 to 1000 ms)
        across GNOME/GTK, Cinnamon/Mint, KDE/Qt, and persistent storage.
        """
        clamped = max(100, min(1000, int(ms)))

        # 1. Update GSettings (Cinnamon, MATE, GNOME daemon)
        self._set_int("double-click", clamped)

        # 2. Update GTK3 and GTK4 settings.ini (GNOME / PikaOS / Wayland)
        import configparser
        for ini_path in [
            os.path.expanduser("~/.config/gtk-3.0/settings.ini"),
            os.path.expanduser("~/.config/gtk-4.0/settings.ini")
        ]:
            try:
                os.makedirs(os.path.dirname(ini_path), exist_ok=True)
                cp = configparser.ConfigParser()
                if os.path.exists(ini_path):
                    cp.read(ini_path)
                if not cp.has_section("Settings"):
                    cp.add_section("Settings")
                cp.set("Settings", "gtk-double-click-time", str(clamped))
                with open(ini_path, "w", encoding="utf-8") as f:
                    cp.write(f)
            except Exception:
                pass

        # 3. Update KDE kdeglobals if directory exists
        kde_cfg = os.path.expanduser("~/.config/kdeglobals")
        if os.path.exists(os.path.expanduser("~/.config")):
            try:
                kcp = configparser.ConfigParser()
                if os.path.exists(kde_cfg):
                    kcp.read(kde_cfg)
                if not kcp.has_section("KDE"):
                    kcp.add_section("KDE")
                kcp.set("KDE", "DoubleClickInterval", str(clamped))
                with open(kde_cfg, "w", encoding="utf-8") as f:
                    kcp.write(f)
            except Exception:
                pass

        # 4. Save to persistent App configuration
        try:
            from PySide6.QtCore import QSettings
            qs = QSettings("TahoeSettings", "Mouse")
            qs.setValue("double_click", clamped)
        except Exception:
            pass

        # 5. Live update Qt Application double click interval
        try:
            from PySide6.QtWidgets import QApplication
            app_inst = QApplication.instance()
            if app_inst:
                app_inst.setDoubleClickInterval(clamped)
        except Exception:
            pass

        return True

    # -------------------------------------------------------------------------
    # 5. Pointer Acceleration (accel-profile: 'adaptive', 'flat', 'default')
    # -------------------------------------------------------------------------
    def get_accel_profile(self) -> str:
        """Returns current acceleration profile: 'adaptive', 'flat', or 'default'."""
        val = self._get_string("accel-profile", "default").lower()
        if val in ["adaptive", "flat", "default"]:
            return val
        return "default"

    def set_accel_profile(self, profile: str) -> bool:
        """Sets acceleration profile ('adaptive', 'flat', 'default')."""
        val = str(profile).lower()
        if val not in ["adaptive", "flat", "default"]:
            val = "default"
        return self._set_string("accel-profile", val)

    def is_acceleration_enabled(self) -> bool:
        """Returns True if pointer acceleration profile is adaptive (or default)."""
        return self.get_accel_profile() == "adaptive"

    def set_acceleration_enabled(self, enabled: bool) -> bool:
        """Quick toggle: True sets 'adaptive', False sets 'flat' (1:1 direct tracking)."""
        return self.set_accel_profile("adaptive" if enabled else "flat")

    # -------------------------------------------------------------------------
    # Hardware & Device Detection
    # -------------------------------------------------------------------------
    def get_primary_mouse_info(self) -> dict:
        """
        Parses /proc/bus/input/devices to find the primary connected pointing device.
        Returns dict with name, connection type, and status.
        """
        try:
            if os.path.exists("/proc/bus/input/devices"):
                with open("/proc/bus/input/devices", "r") as f:
                    content = f.read()

                blocks = content.split("\n\n")
                best_device = None

                for block in blocks:
                    if not block.strip():
                        continue

                    name_line = [l for l in block.split("\n") if l.startswith("N: Name=")]
                    phys_line = [l for l in block.split("\n") if l.startswith("P: Phys=")]
                    handlers_line = [l for l in block.split("\n") if l.startswith("H: Handlers=")]
                    bus_line = [l for l in block.split("\n") if l.startswith("I: ")]

                    if not name_line:
                        continue

                    raw_name = name_line[0].split("=", 1)[1].strip('"').strip()
                    phys = phys_line[0].split("=", 1)[1].strip() if phys_line else ""
                    handlers = handlers_line[0].split("=", 1)[1].strip() if handlers_line else ""

                    # Filter out non-pointing devices or helper endpoints
                    ignore_patterns = ["consumer control", "system control", "keyboard", "video bus", "power button", "audio", "headphone"]
                    if any(ign in raw_name.lower() for ign in ignore_patterns):
                        continue

                    is_mouse_handler = "mouse" in handlers.split()
                    is_mouse_name = "mouse" in raw_name.lower() or "trackball" in raw_name.lower() or "touchpad" in raw_name.lower()

                    if is_mouse_handler or is_mouse_name:
                        conn_type = "USB"
                        if "bluetooth" in phys.lower() or ("0005:" in (bus_line[0] if bus_line else "")):
                            conn_type = "Bluetooth"
                        elif "2.4g" in raw_name.lower() or "wireless" in raw_name.lower():
                            conn_type = "Wireless (2.4GHz)"
                        elif "ps/2" in phys.lower() or "synaptics" in raw_name.lower() or "touchpad" in raw_name.lower():
                            conn_type = "Built-in / Touchpad"
                        elif "usb" in phys.lower():
                            conn_type = "USB"

                        clean_name = raw_name

                        device_info = {
                            "name": clean_name,
                            "type": conn_type,
                            "status": "Connected"
                        }

                        # Prefer device with explicit mouse handler
                        if is_mouse_handler:
                            return device_info
                        if best_device is None:
                            best_device = device_info

                if best_device:
                    return best_device
        except Exception:
            pass

        return {
            "name": "Standard Mouse / Pointer",
            "type": "Internal / System",
            "status": "Active"
        }
