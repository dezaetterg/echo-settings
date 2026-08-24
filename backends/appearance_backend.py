import os
import subprocess
import sys

try:
    if "/usr/lib/python3/dist-packages" not in sys.path:
        sys.path.append("/usr/lib/python3/dist-packages")
    import gi
    gi.require_version('Gio', '2.0')
    from gi.repository import Gio
    _has_gio = True
except Exception:
    _has_gio = False

class AppearanceBackend:
    def __init__(self):
        self._iface_settings = None
        self._bg_settings = None
        self._mutter_settings = None
        self._wm_settings = None
        self._app_switcher_settings = None
        self._win_switcher_settings = None

        if _has_gio:
            def _get_schema(schema_id: str):
                try:
                    source = Gio.SettingsSchemaSource.get_default()
                    if source and source.lookup(schema_id, True):
                        return Gio.Settings.new(schema_id)
                except Exception:
                    pass
                return None

            self._iface_settings = _get_schema("org.gnome.desktop.interface")
            self._bg_settings = _get_schema("org.gnome.desktop.background")
            self._mutter_settings = _get_schema("org.gnome.mutter")
            self._wm_settings = _get_schema("org.gnome.desktop.wm.preferences")
            self._app_switcher_settings = _get_schema("org.gnome.shell.app-switcher")
            self._win_switcher_settings = _get_schema("org.gnome.shell.window-switcher")

    def get_theme_mode(self) -> str:
        """
        Returns configured theme mode: 'auto', 'default' (light), or 'prefer-dark' (dark).
        """
        try:
            from PySide6.QtCore import QSettings
            qs = QSettings("TahoeSettings", "Appearance")
            saved = qs.value("theme_mode", None)
            if saved in ("auto", "default", "prefer-dark"):
                return saved
        except Exception:
            pass

        # Fallback to system GSettings if not explicitly set in App config
        sys_scheme = self.get_color_scheme()
        return "prefer-dark" if sys_scheme == "prefer-dark" else "default"

    def set_theme_mode(self, mode: str) -> bool:
        """
        Sets theme mode ('auto', 'default', 'prefer-dark') and applies the effective scheme.
        """
        if mode not in ("auto", "default", "prefer-dark"):
            mode = "default"

        try:
            from PySide6.QtCore import QSettings
            qs = QSettings("TahoeSettings", "Appearance")
            qs.setValue("theme_mode", mode)
        except Exception:
            pass

        effective = self.get_effective_color_scheme(mode)
        return self.apply_effective_color_scheme(effective)

    def get_effective_color_scheme(self, mode: str = None) -> str:
        """
        Returns actual active color scheme ('default' or 'prefer-dark').
        If mode is 'auto', resolves based on morning/day (06:00-18:59:59) vs evening/night (19:00-05:59:59).
        """
        if mode is None:
            mode = self.get_theme_mode()

        if mode == "auto":
            from datetime import datetime
            hour = datetime.now().hour
            return "default" if (6 <= hour < 19) else "prefer-dark"
        elif mode == "prefer-dark":
            return "prefer-dark"
        else:
            return "default"

    def get_color_scheme(self) -> str:
        if self._iface_settings:
            try:
                if "color-scheme" in self._iface_settings.list_keys():
                    return self._iface_settings.get_string("color-scheme")
            except Exception:
                pass
        try:
            res = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                capture_output=True, text=True, check=True
            )
            return res.stdout.strip().strip("'")
        except Exception:
            # Check Cinnamon GTK theme
            try:
                res = subprocess.run(['gsettings', 'get', 'org.cinnamon.desktop.interface', 'gtk-theme'], capture_output=True, text=True)
                theme = res.stdout.strip().strip("'").lower()
                if "dark" in theme:
                    return "prefer-dark"
            except Exception:
                pass
            return "default"

    def set_color_scheme(self, scheme: str) -> bool:
        return self.set_theme_mode(scheme)

    def apply_effective_color_scheme(self, scheme: str) -> bool:
        """
        Applies 'default' (light) or 'prefer-dark' (dark) to system desktop environments
        (GNOME, Cinnamon, GTK3, GTK4).
        """
        # 1. GNOME Schema
        if self._iface_settings:
            try:
                if "color-scheme" in self._iface_settings.list_keys():
                    self._iface_settings.set_string("color-scheme", scheme)
                if "gtk-theme" in self._iface_settings.list_keys():
                    current_gtk = self._iface_settings.get_string("gtk-theme")
                    if scheme == 'prefer-dark':
                        new_gtk = current_gtk.replace('-Light', '-Dark').replace('-light', '-dark')
                        if "-Dark" not in new_gtk and "-dark" not in new_gtk and not new_gtk.endswith("-dark"):
                            new_gtk += "-Dark" if any(c.isupper() for c in new_gtk) else "-dark"
                    else:
                        new_gtk = current_gtk.replace('-Dark', '-Light').replace('-dark', '-light')
                    if new_gtk != current_gtk:
                        self._iface_settings.set_string("gtk-theme", new_gtk)
                Gio.Settings.sync()
            except Exception:
                pass
        try:
            subprocess.Popen(
                ['gsettings', 'set', 'org.gnome.desktop.interface', 'color-scheme', scheme],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

        # 2. Cinnamon Schema
        try:
            res = subprocess.run(['gsettings', 'get', 'org.cinnamon.desktop.interface', 'gtk-theme'], capture_output=True, text=True)
            current_gtk = res.stdout.strip().strip("'")
            if current_gtk:
                if scheme == 'prefer-dark':
                    new_gtk = current_gtk.replace('-Light', '-Dark').replace('-light', '-dark')
                    if "Dark" not in new_gtk and "dark" not in new_gtk:
                        new_gtk += "-Dark" if any(c.isupper() for c in new_gtk) else "-dark"
                else:
                    new_gtk = current_gtk.replace('-Dark', '-Light').replace('-dark', '-light')
                if new_gtk != current_gtk:
                    subprocess.Popen(
                        ['gsettings', 'set', 'org.cinnamon.desktop.interface', 'gtk-theme', new_gtk],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
        except Exception:
            pass

        # 3. GTK3 and GTK4 settings.ini
        import configparser
        is_dark_num = "1" if scheme == "prefer-dark" else "0"
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
                cp.set("Settings", "gtk-application-prefer-dark-theme", is_dark_num)
                with open(ini_path, "w", encoding="utf-8") as f:
                    cp.write(f)
            except Exception:
                pass

        return True

    def supports_accent_color(self) -> bool:
        if self._iface_settings:
            try:
                return "accent-color" in self._iface_settings.list_keys()
            except Exception:
                pass
        try:
            res = subprocess.run(
                ['gsettings', 'list-keys', 'org.gnome.desktop.interface'],
                capture_output=True, text=True
            )
            return "accent-color" in res.stdout
        except Exception:
            return True

    def get_accent_color(self) -> str:
        if self._iface_settings:
            try:
                if "accent-color" in self._iface_settings.list_keys():
                    val = self._iface_settings.get_string("accent-color")
                    if val:
                        return val
            except Exception:
                pass
        try:
            res = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'accent-color'],
                capture_output=True, text=True, check=True
            )
            return res.stdout.strip().strip("'")
        except Exception:
            pass

        state_file = os.path.expanduser("~/.config/tahoe_accent_color")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    return f.read().strip()
            except Exception:
                pass
        return "blue"

    def get_accent_intensity(self) -> int:
        state_file = os.path.expanduser("~/.config/tahoe_accent_intensity")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    val = int(f.read().strip())
                    if 20 <= val <= 100:
                        return val
            except Exception:
                pass
        return 80

    @staticmethod
    def compute_accent_hex(base_name_or_hex: str, intensity: int = 80) -> str:
        color_hex_map = {
            "blue": "#007AFF",
            "teal": "#5AC8FA",
            "green": "#28CD41",
            "yellow": "#FFCC00",
            "orange": "#FF9500",
            "red": "#FF3B30",
            "pink": "#FF2D55",
            "purple": "#AF52DE",
            "slate": "#8E8E93",
            "multicolor": "#007AFF"
        }
        val = str(base_name_or_hex).strip().lower()
        base_hex = color_hex_map.get(val, val if val.startswith("#") else "#007AFF")
        
        try:
            from PySide6.QtGui import QColor
            col = QColor(base_hex)
            if not col.isValid():
                col = QColor("#007AFF")
                
            h, s, v, _ = col.getHsv()
            if h < 0:  # Slate / Grayscale
                factor = 0.5 + (intensity / 100.0) * 0.6
                new_v = max(30, min(255, int(v * factor)))
                active_col = QColor.fromHsv(0, 0, new_v)
            else:
                factor = 0.35 + (intensity / 100.0) * 0.75
                new_s = max(25, min(255, int(s * factor)))
                new_v = max(45, min(255, int(v * (0.65 + (intensity / 100.0) * 0.35))))
                active_col = QColor.fromHsv(h, new_s, new_v)
            return active_col.name().upper()
        except Exception:
            return base_hex

    @staticmethod
    def closest_gnome_color(hex_str: str) -> str:
        gnome_colors = {
            'blue': '#007AFF',
            'teal': '#5AC8FA',
            'green': '#28CD41',
            'yellow': '#FFCC00',
            'orange': '#FF9500',
            'red': '#FF3B30',
            'pink': '#FF2D55',
            'purple': '#AF52DE',
            'slate': '#8E8E93',
        }
        try:
            from PySide6.QtGui import QColor
            col = QColor(hex_str)
            if not col.isValid():
                return 'blue'
            best_name = 'blue'
            min_dist = float('inf')
            for name, hx in gnome_colors.items():
                c = QColor(hx)
                dist = (col.red() - c.red())**2 + (col.green() - c.green())**2 + (col.blue() - c.blue())**2
                if dist < min_dist:
                    min_dist = dist
                    best_name = name
            return best_name
        except Exception:
            return 'blue'

    def set_accent_color(self, color: str, intensity: int = 80, custom_hex: str = None) -> bool:
        color_hex_map = {
            "blue": "#007AFF",
            "teal": "#5AC8FA",
            "green": "#28CD41",
            "yellow": "#FFCC00",
            "orange": "#FF9500",
            "red": "#FF3B30",
            "pink": "#FF2D55",
            "purple": "#AF52DE",
            "slate": "#8E8E93",
            "multicolor": "#007AFF"
        }

        # 1. Resolve base name and exact computed hex
        base_name = color.lower().strip() if color else "blue"
        if custom_hex and custom_hex.startswith("#"):
            final_hex = custom_hex.upper()
        else:
            final_hex = self.compute_accent_hex(base_name, intensity)

        if base_name in color_hex_map:
            gnome_enum = base_name if base_name != "multicolor" else "blue"
        else:
            gnome_enum = self.closest_gnome_color(final_hex)

        # 2. Save persistent state
        try:
            with open(os.path.expanduser("~/.config/tahoe_accent_color"), "w") as f:
                f.write(base_name)
            with open(os.path.expanduser("~/.config/tahoe_accent_intensity"), "w") as f:
                f.write(str(intensity))
            with open(os.path.expanduser("~/.config/tahoe_accent_hex"), "w") as f:
                f.write(final_hex)
        except Exception:
            pass

        # 3. GNOME 47 GSettings
        if self._iface_settings:
            try:
                if "accent-color" in self._iface_settings.list_keys():
                    self._iface_settings.set_string("accent-color", gnome_enum)
            except Exception:
                pass
        try:
            subprocess.run(
                ['gsettings', 'set', 'org.gnome.desktop.interface', 'accent-color', gnome_enum],
                check=False, stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

        # 4. Universal GTK3 / GTK4 / Libadwaita CSS Injection (Applies system-wide depth & shade)
        fg_hex = "#FFFFFF"
        try:
            from PySide6.QtGui import QColor
            col = QColor(final_hex)
            lum = 0.299 * col.red() + 0.587 * col.green() + 0.114 * col.blue()
            fg_hex = "#000000" if lum > 170 else "#FFFFFF"
        except Exception:
            pass

        css_snippet = f"""/* Echo Settings System Accent Color & Depth */
@define-color accent_color {final_hex};
@define-color accent_bg_color {final_hex};
@define-color accent_fg_color {fg_hex};
@define-color theme_selected_bg_color {final_hex};
@define-color theme_selected_fg_color {fg_hex};
@define-color focus_border_color {final_hex};
"""
        for gtk_ver in ("gtk-3.0", "gtk-4.0"):
            css_dir = os.path.expanduser(f"~/.config/{gtk_ver}")
            os.makedirs(css_dir, exist_ok=True)
            css_file = os.path.join(css_dir, "gtk.css")
            try:
                existing = ""
                if os.path.exists(css_file):
                    with open(css_file, "r") as f:
                        lines = [l for l in f.readlines() if not l.startswith("@define-color accent") and not l.startswith("@define-color theme_selected") and not l.startswith("@define-color focus_border") and "Echo Settings" not in l]
                        existing = "".join(lines)
                with open(css_file, "w") as f:
                    f.write(css_snippet + existing)
            except Exception:
                pass

        return True

    def set_wallpaper(self, uri: str, is_dark: bool = False) -> bool:
        # Normalize URI and Path
        clean_path = uri.replace("file://", "") if uri.startswith("file://") else uri
        file_uri = f"file://{clean_path}" if not uri.startswith("file://") else uri

        # 1. GNOME Desktop Background
        key = 'picture-uri-dark' if is_dark else 'picture-uri'
        if self._bg_settings:
            try:
                if key in self._bg_settings.list_keys():
                    self._bg_settings.set_string(key, file_uri)
            except Exception:
                pass
        try:
            subprocess.Popen(['gsettings', 'set', 'org.gnome.desktop.background', key, f"'{file_uri}'"])
        except Exception:
            pass

        # 2. Cinnamon Desktop Background
        try:
            subprocess.Popen(['gsettings', 'set', 'org.cinnamon.desktop.background', 'picture-uri', f"'{file_uri}'"])
        except Exception:
            pass

        # 3. MATE Desktop Background
        try:
            subprocess.Popen(['gsettings', 'set', 'org.mate.background', 'picture-filename', f"'{clean_path}'"])
        except Exception:
            pass

        # 4. XFCE Desktop Background
        try:
            if shutil.which("xfconf-query"):
                subprocess.Popen(['xfconf-query', '-c', 'xfce4-desktop', '-p', '/backdrop/screen0/monitor0/workspace0/last-image', '-s', clean_path])
        except Exception:
            pass

        return True

    def get_current_wallpaper(self) -> str:
        is_dark = self.get_color_scheme() == "prefer-dark"
        key = 'picture-uri-dark' if is_dark else 'picture-uri'
        
        # Try Cinnamon first if active
        try:
            res = subprocess.run(['gsettings', 'get', 'org.cinnamon.desktop.background', 'picture-uri'], capture_output=True, text=True)
            out = res.stdout.strip().strip("'")
            if out:
                return out
        except Exception:
            pass

        if self._bg_settings:
            try:
                if key in self._bg_settings.list_keys():
                    return self._bg_settings.get_string(key)
            except Exception:
                pass
        try:
            res = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.background', key],
                capture_output=True, text=True, check=True
            )
            return res.stdout.strip().strip("'")
        except Exception:
            return ""
            
    def _get_bool(self, schema_obj, schema_id: str, key: str, default: bool = False) -> bool:
        if schema_obj:
            try:
                if key in schema_obj.list_keys():
                    return schema_obj.get_boolean(key)
            except Exception:
                pass
        try:
            res = subprocess.run(['gsettings', 'get', schema_id, key], capture_output=True, text=True, check=True)
            return res.stdout.strip().lower() == 'true'
        except Exception:
            return default

    def _set_bool(self, schema_obj, schema_id: str, key: str, val: bool) -> bool:
        if schema_obj:
            try:
                if key in schema_obj.list_keys():
                    schema_obj.set_boolean(key, bool(val))
                    return True
            except Exception:
                pass
        try:
            subprocess.run(['gsettings', 'set', schema_id, key, 'true' if val else 'false'], check=True)
            return True
        except Exception:
            return False

    def _get_int(self, schema_obj, schema_id: str, key: str, default: int = 4) -> int:
        if schema_obj:
            try:
                if key in schema_obj.list_keys():
                    val = schema_obj.get_value(key)
                    if val is not None:
                        return int(val.unpack())
            except Exception:
                pass
        try:
            res = subprocess.run(['gsettings', 'get', schema_id, key], capture_output=True, text=True, check=True)
            return int(res.stdout.strip().replace('uint32', '').strip())
        except Exception:
            return default

    def _set_int(self, schema_obj, schema_id: str, key: str, val: int) -> bool:
        if schema_obj:
            try:
                if key in schema_obj.list_keys():
                    schema_obj.set_int(key, int(val))
                    return True
            except Exception:
                pass
        try:
            subprocess.run(['gsettings', 'set', schema_id, key, str(val)], check=True)
            return True
        except Exception:
            return False

    def is_hot_corners_supported(self) -> bool:
        import os
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
        if any(d in desktop for d in ("GNOME", "UBUNTU", "POP", "PANTHEON")):
            if self._iface_settings:
                try:
                    return "enable-hot-corners" in self._iface_settings.list_keys()
                except Exception:
                    pass
            return True
        return False

    def is_multitasking_supported(self) -> bool:
        return self._mutter_settings is not None

    # 1. Hot Corners
    def get_hot_corners_enabled(self) -> bool:
        return self._get_bool(self._iface_settings, "org.gnome.desktop.interface", "enable-hot-corners", False)

    def set_hot_corners_enabled(self, enabled: bool) -> bool:
        return self._set_bool(self._iface_settings, "org.gnome.desktop.interface", "enable-hot-corners", enabled)

    def get_top_left_corner_action(self) -> str:
        from PySide6.QtCore import QSettings
        settings = QSettings("EchoSettings", "Appearance")
        val = settings.value("hot_corner_top_left", None, type=str)
        if val is None or val == "":
            return "overview" if self.get_hot_corners_enabled() else "none"
        return val

    def set_top_left_corner_action(self, action: str) -> bool:
        from PySide6.QtCore import QSettings
        settings = QSettings("EchoSettings", "Appearance")
        settings.setValue("hot_corner_top_left", action)
        self.set_hot_corners_enabled(action != "none")
        return True

    def get_top_right_corner_action(self) -> str:
        from PySide6.QtCore import QSettings
        settings = QSettings("EchoSettings", "Appearance")
        return settings.value("hot_corner_top_right", "none", type=str)

    def set_top_right_corner_action(self, action: str) -> bool:
        from PySide6.QtCore import QSettings
        settings = QSettings("EchoSettings", "Appearance")
        settings.setValue("hot_corner_top_right", action)
        return True

    def get_bottom_left_corner_action(self) -> str:
        from PySide6.QtCore import QSettings
        settings = QSettings("EchoSettings", "Appearance")
        return settings.value("hot_corner_bottom_left", "none", type=str)

    def set_bottom_left_corner_action(self, action: str) -> bool:
        from PySide6.QtCore import QSettings
        settings = QSettings("EchoSettings", "Appearance")
        settings.setValue("hot_corner_bottom_left", action)
        return True

    def get_bottom_right_corner_action(self) -> str:
        from PySide6.QtCore import QSettings
        settings = QSettings("EchoSettings", "Appearance")
        return settings.value("hot_corner_bottom_right", "none", type=str)

    def set_bottom_right_corner_action(self, action: str) -> bool:
        from PySide6.QtCore import QSettings
        settings = QSettings("EchoSettings", "Appearance")
        settings.setValue("hot_corner_bottom_right", action)
        return True

    # 2. Workspaces
    def get_is_dynamic_workspaces(self) -> bool:
        return self._get_bool(self._mutter_settings, "org.gnome.mutter", "dynamic-workspaces", True)

    def set_dynamic_workspaces(self, dynamic: bool) -> bool:
        return self._set_bool(self._mutter_settings, "org.gnome.mutter", "dynamic-workspaces", dynamic)

    def get_num_workspaces(self) -> int:
        return max(1, min(32, self._get_int(self._wm_settings, "org.gnome.desktop.wm.preferences", "num-workspaces", 4)))

    def set_num_workspaces(self, num: int) -> bool:
        clamped = max(1, min(32, int(num)))
        return self._set_int(self._wm_settings, "org.gnome.desktop.wm.preferences", "num-workspaces", clamped)

    # 3. Displays / Multiple Monitors
    def get_workspaces_only_on_primary(self) -> bool:
        return self._get_bool(self._mutter_settings, "org.gnome.mutter", "workspaces-only-on-primary", True)

    def set_workspaces_only_on_primary(self, primary_only: bool) -> bool:
        return self._set_bool(self._mutter_settings, "org.gnome.mutter", "workspaces-only-on-primary", primary_only)

    # 4. Application Switching
    def get_app_switcher_current_workspace_only(self) -> bool:
        return self._get_bool(self._app_switcher_settings, "org.gnome.shell.app-switcher", "current-workspace-only", True)

    def set_app_switcher_current_workspace_only(self, current_only: bool) -> bool:
        res1 = self._set_bool(self._app_switcher_settings, "org.gnome.shell.app-switcher", "current-workspace-only", current_only)
        res2 = self._set_bool(self._win_switcher_settings, "org.gnome.shell.window-switcher", "current-workspace-only", current_only)
        return res1 or res2

