import os
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

SCHEMA_PRIVACY = "org.gnome.desktop.privacy"
SCHEMA_LOCATION = "org.gnome.system.location"
SCHEMA_REMOTE_RDP = "org.gnome.desktop.remote-desktop.rdp"
SCHEMA_SCREENSAVER = "org.gnome.desktop.screensaver"
SCHEMA_SESSION = "org.gnome.desktop.session"
SCHEMA_NOTIFICATIONS = "org.gnome.desktop.notifications"

class PrivacyBackend:
    """
    Unified GNOME Wayland backend for system privacy controls, hardware
    killswitches (camera/mic), location services, remote desktop, and history.
    """
    def __init__(self):
        self._privacy_settings = self._get_schema_settings(SCHEMA_PRIVACY)
        self._location_settings = self._get_schema_settings(SCHEMA_LOCATION)
        self._remote_rdp_settings = self._get_schema_settings(SCHEMA_REMOTE_RDP)
        self._screensaver_settings = self._get_schema_settings(SCHEMA_SCREENSAVER)
        self._session_settings = self._get_schema_settings(SCHEMA_SESSION)
        self._notifications_settings = self._get_schema_settings(SCHEMA_NOTIFICATIONS)

    def _get_schema_settings(self, schema_id: str):
        if not _has_gio:
            return None
        try:
            source = Gio.SettingsSchemaSource.get_default()
            if source and source.lookup(schema_id, True):
                return Gio.Settings.new(schema_id)
        except Exception:
            pass
        return None

    def _has_key(self, settings_obj, schema_id: str, key: str) -> bool:
        if settings_obj is not None:
            try:
                schema = settings_obj.get_property("settings-schema")
                if schema and schema.has_key(key):
                    return True
            except Exception:
                pass
        try:
            res = subprocess.run(['gsettings', 'list-keys', schema_id], capture_output=True, text=True)
            return key in res.stdout.split()
        except Exception:
            return False

    # -------------------------------------------------------------------------
    # Generic Helpers with Gio.Settings.sync() and CLI fallback
    # -------------------------------------------------------------------------
    def _get_bool(self, settings_obj, schema_id: str, key: str, default: bool = False) -> bool:
        if settings_obj is not None:
            try:
                return settings_obj.get_boolean(key)
            except Exception:
                pass
        try:
            res = subprocess.run(['gsettings', 'get', schema_id, key], capture_output=True, text=True, check=True)
            return res.stdout.strip().lower() == 'true'
        except Exception:
            return default

    def _set_bool(self, settings_obj, schema_id: str, key: str, val: bool) -> bool:
        val_bool = bool(val)
        if settings_obj is not None:
            try:
                settings_obj.set_boolean(key, val_bool)
                Gio.Settings.sync()
                return True
            except Exception:
                pass
        try:
            val_str = 'true' if val_bool else 'false'
            subprocess.run(['gsettings', 'set', schema_id, key, val_str], check=True)
            return True
        except Exception:
            return False

    def _get_string(self, settings_obj, schema_id: str, key: str, default: str = "") -> str:
        if settings_obj is not None:
            try:
                return settings_obj.get_string(key)
            except Exception:
                pass
        try:
            res = subprocess.run(['gsettings', 'get', schema_id, key], capture_output=True, text=True, check=True)
            return res.stdout.strip().strip("'")
        except Exception:
            return default

    def _set_string(self, settings_obj, schema_id: str, key: str, val: str) -> bool:
        val_str = str(val).strip("'")
        if settings_obj is not None:
            try:
                settings_obj.set_string(key, val_str)
                Gio.Settings.sync()
                return True
            except Exception:
                pass
        try:
            subprocess.run(['gsettings', 'set', schema_id, key, f"'{val_str}'"], check=True)
            return True
        except Exception:
            return False

    def _get_int(self, settings_obj, schema_id: str, key: str, default: int = 0) -> int:
        if settings_obj is not None:
            try:
                val = settings_obj.get_value(key)
                if val is not None:
                    return int(val.unpack())
            except Exception:
                pass
            try:
                return int(settings_obj.get_int(key))
            except Exception:
                pass
        try:
            res = subprocess.run(['gsettings', 'get', schema_id, key], capture_output=True, text=True, check=True)
            return int(res.stdout.strip().replace("uint32", "").strip())
        except Exception:
            return default

    def _set_int(self, settings_obj, schema_id: str, key: str, val: int) -> bool:
        val_int = int(val)
        if settings_obj is not None:
            try:
                schema = settings_obj.get_property("settings-schema")
                if schema and schema.has_key(key):
                    vtype = schema.get_key(key).get_value_type().dup_string()
                    if "u" in vtype:
                        settings_obj.set_uint(key, val_int)
                    else:
                        settings_obj.set_int(key, val_int)
                    Gio.Settings.sync()
                    return True
            except Exception:
                pass
            try:
                settings_obj.set_int(key, val_int)
                Gio.Settings.sync()
                return True
            except Exception:
                pass
        try:
            subprocess.run(['gsettings', 'set', schema_id, key, str(val_int)], check=True)
            return True
        except Exception:
            return False

    # -------------------------------------------------------------------------
    # Feature Availability Checks
    # -------------------------------------------------------------------------
    def supports_camera(self) -> bool:
        return self._has_key(self._privacy_settings, SCHEMA_PRIVACY, "disable-camera")

    def supports_microphone(self) -> bool:
        return self._has_key(self._privacy_settings, SCHEMA_PRIVACY, "disable-microphone")

    def supports_location(self) -> bool:
        return self._has_key(self._location_settings, SCHEMA_LOCATION, "enabled")

    def supports_remote_desktop(self) -> bool:
        return self._has_key(self._remote_rdp_settings, SCHEMA_REMOTE_RDP, "enable")

    def supports_recent_files(self) -> bool:
        return self._has_key(self._privacy_settings, SCHEMA_PRIVACY, "remember-recent-files")

    def supports_app_usage(self) -> bool:
        return self._has_key(self._privacy_settings, SCHEMA_PRIVACY, "remember-app-usage")

    def supports_screen_lock(self) -> bool:
        return self._has_key(self._screensaver_settings, SCHEMA_SCREENSAVER, "lock-enabled")

    def supports_device_security(self) -> bool:
        return self._has_key(self._privacy_settings, SCHEMA_PRIVACY, "usb-protection")

    # -------------------------------------------------------------------------
    # 0. Screen Lock & Device Security
    # -------------------------------------------------------------------------
    def get_screen_lock_enabled(self) -> bool:
        """Returns True if automatic screen locking is enabled."""
        return self._get_bool(self._screensaver_settings, SCHEMA_SCREENSAVER, "lock-enabled", True)

    def set_screen_lock_enabled(self, enabled: bool) -> bool:
        """Enables or disables automatic screen locking in GNOME."""
        return self._set_bool(self._screensaver_settings, SCHEMA_SCREENSAVER, "lock-enabled", bool(enabled))

    def get_idle_delay(self) -> int:
        """Returns screen off timeout in seconds (0 = Never)."""
        return self._get_int(self._session_settings, SCHEMA_SESSION, "idle-delay", 0)

    def set_idle_delay(self, seconds: int) -> bool:
        """Sets screen off timeout in seconds."""
        return self._set_int(self._session_settings, SCHEMA_SESSION, "idle-delay", seconds)

    def get_lock_delay(self) -> int:
        """Returns lock delay in seconds (0 = Immediately)."""
        return self._get_int(self._screensaver_settings, SCHEMA_SCREENSAVER, "lock-delay", 0)

    def set_lock_delay(self, seconds: int) -> bool:
        """Sets lock delay in seconds."""
        return self._set_int(self._screensaver_settings, SCHEMA_SCREENSAVER, "lock-delay", seconds)

    def get_lock_screen_notifications(self) -> bool:
        """Returns True if notifications are allowed on lock screen."""
        return self._get_bool(self._notifications_settings, SCHEMA_NOTIFICATIONS, "show-in-lock-screen", True)

    def set_lock_screen_notifications(self, enabled: bool) -> bool:
        """Enables or disables notifications on lock screen."""
        return self._set_bool(self._notifications_settings, SCHEMA_NOTIFICATIONS, "show-in-lock-screen", bool(enabled))

    def get_usb_protection_enabled(self) -> bool:
        """Returns True if USB device protection at lockscreen is enabled."""
        return self._get_bool(self._privacy_settings, SCHEMA_PRIVACY, "usb-protection", True)

    def set_usb_protection_enabled(self, enabled: bool) -> bool:
        """Enables or disables USB device protection at lockscreen."""
        return self._set_bool(self._privacy_settings, SCHEMA_PRIVACY, "usb-protection", bool(enabled))

    def get_usb_protection_level(self) -> str:
        """Returns USB protection level ('lockscreen' or 'always')."""
        return self._get_string(self._privacy_settings, SCHEMA_PRIVACY, "usb-protection-level", "lockscreen")

    def set_usb_protection_level(self, level: str) -> bool:
        """Sets USB protection level ('lockscreen' or 'always')."""
        return self._set_string(self._privacy_settings, SCHEMA_PRIVACY, "usb-protection-level", level)

    def get_default_microphone_name(self) -> str:
        """Returns the human-readable name of the default audio input source."""
        try:
            res = subprocess.run(['wpctl', 'status'], capture_output=True, text=True, timeout=1)
            in_sources = False
            for line in res.stdout.splitlines():
                if "Sources:" in line:
                    in_sources = True
                    continue
                if in_sources:
                    if "*" in line:
                        # e.g. "│  *   62. Audio Adapter (Unitek Y-247A) Mono  [vol: 0.88 MUTED]"
                        clean = line.replace("│", "").replace("*", "").strip()
                        parts = clean.split(".", 1)
                        if len(parts) > 1:
                            name_part = parts[1].split("[")[0].strip()
                            return name_part
                    elif line.strip().startswith("├─") or line.strip().startswith("└─"):
                        clean = line.replace("├─", "").replace("└─", "").replace("│", "").strip()
                        parts = clean.split(".", 1)
                        if len(parts) > 1:
                            name_part = parts[1].split("[")[0].strip()
                            return name_part
                    elif not line.strip():
                        break
        except Exception:
            pass
        return "System Default Microphone"

    # -------------------------------------------------------------------------
    # 1. Camera Access (disable-camera is inverted in UI to "Allow Camera")
    # -------------------------------------------------------------------------
    def is_camera_present(self) -> bool:
        """Checks if a physical camera / webcam device is connected."""
        import glob
        if glob.glob('/dev/video*'):
            return True
        try:
            res = subprocess.run(
                ['gdbus', 'call', '--session', '--dest', 'org.freedesktop.portal.Desktop',
                 '--object-path', '/org/freedesktop/portal/desktop',
                 '--method', 'org.freedesktop.DBus.Properties.Get',
                 'org.freedesktop.portal.Camera', 'IsCameraPresent'],
                capture_output=True, text=True, timeout=1
            )
            if '<true>' in res.stdout.lower():
                return True
        except Exception:
            pass
        return False

    def get_camera_access(self) -> bool:
        """Returns True if camera access is allowed (disable-camera == False)."""
        is_disabled = self._get_bool(self._privacy_settings, SCHEMA_PRIVACY, "disable-camera", False)
        return not is_disabled

    def set_camera_access(self, allowed: bool) -> bool:
        """Sets camera access. True = allowed (disable-camera=False), False = blocked."""
        return self._set_bool(self._privacy_settings, SCHEMA_PRIVACY, "disable-camera", not bool(allowed))

    # -------------------------------------------------------------------------
    # 2. Microphone Access (disable-microphone + PipeWire sync)
    # -------------------------------------------------------------------------
    def is_microphone_present(self) -> bool:
        """Checks if an audio input source (microphone) is detected in PipeWire."""
        try:
            res = subprocess.run(['wpctl', 'status'], capture_output=True, text=True, timeout=1)
            # Check if Sources section contains any source
            in_sources = False
            for line in res.stdout.splitlines():
                if "Sources:" in line:
                    in_sources = True
                    continue
                if in_sources:
                    if line.strip().startswith("├─") or line.strip().startswith("└─") or line.strip().startswith("│"):
                        if any(c.isdigit() for c in line):
                            return True
                    else:
                        break
        except Exception:
            pass
        return True

    def get_microphone_access(self) -> bool:
        """Returns True if microphone access is allowed and unmuted."""
        is_disabled = self._get_bool(self._privacy_settings, SCHEMA_PRIVACY, "disable-microphone", False)
        if is_disabled:
            return False
        # Also verify live PipeWire source mute
        try:
            res = subprocess.run(['wpctl', 'get-volume', '@DEFAULT_AUDIO_SOURCE@'], capture_output=True, text=True, timeout=1)
            if '[MUTED]' in res.stdout:
                return False
        except Exception:
            pass
        return True

    def set_microphone_access(self, allowed: bool) -> bool:
        """Sets microphone access. True = allowed/unmuted, False = blocked/muted."""
        res_gsettings = self._set_bool(self._privacy_settings, SCHEMA_PRIVACY, "disable-microphone", not bool(allowed))
        # Sync PipeWire mute state
        try:
            mute_flag = "0" if allowed else "1"
            subprocess.run(['wpctl', 'set-mute', '@DEFAULT_AUDIO_SOURCE@', mute_flag], check=False, timeout=1)
        except Exception:
            pass
        return res_gsettings

    # -------------------------------------------------------------------------
    # 3. Location Services (GeoClue2)
    # -------------------------------------------------------------------------
    def is_location_available(self) -> bool:
        """
        Checks if Location Services (GeoClue2) daemon and GSettings schema
        are installed and available on the system.
        """
        if not self.supports_location():
            return False

        geoclue_indicators = [
            "/usr/libexec/geoclue",
            "/usr/lib/geoclue-2.0/geoclue",
            "/usr/lib/geoclue/geoclue",
            "/usr/bin/geoclue",
            "/usr/share/dbus-1/system-services/org.freedesktop.GeoClue2.service"
        ]
        return any(os.path.exists(p) for p in geoclue_indicators)

    def get_location_enabled(self) -> bool:
        """Returns True if system location services (GeoClue2) are active."""
        if not self.is_location_available():
            return False
        return self._get_bool(self._location_settings, SCHEMA_LOCATION, "enabled", False)

    def set_location_enabled(self, enabled: bool) -> bool:
        """Enables or disables system location services."""
        if not self.is_location_available():
            return False
        return self._set_bool(self._location_settings, SCHEMA_LOCATION, "enabled", bool(enabled))

    def get_location_accuracy(self) -> str:
        """Returns accuracy level ('exact', 'street', 'city', 'country')."""
        return self._get_string(self._location_settings, SCHEMA_LOCATION, "max-accuracy-level", "exact")

    def set_location_accuracy(self, level: str) -> bool:
        """Sets max accuracy level."""
        return self._set_string(self._location_settings, SCHEMA_LOCATION, "max-accuracy-level", level)

    # -------------------------------------------------------------------------
    # 4. Remote Desktop (GNOME RDP) & Screen Sharing
    # -------------------------------------------------------------------------
    def get_remote_desktop_enabled(self) -> bool:
        """Returns True if GNOME Remote Desktop (RDP) server is enabled."""
        return self._get_bool(self._remote_rdp_settings, SCHEMA_REMOTE_RDP, "enable", False)

    def set_remote_desktop_enabled(self, enabled: bool) -> bool:
        """Enables or disables GNOME Remote Desktop server and starts/stops systemd user unit."""
        res = self._set_bool(self._remote_rdp_settings, SCHEMA_REMOTE_RDP, "enable", bool(enabled))
        try:
            action = "start" if enabled else "stop"
            subprocess.run(["systemctl", "--user", action, "gnome-remote-desktop.service"], check=False, timeout=2)
        except Exception:
            pass
        return res

    def is_remote_desktop_service_active(self) -> bool:
        """Checks if gnome-remote-desktop systemd user service is currently running."""
        try:
            res = subprocess.run(["systemctl", "--user", "is-active", "gnome-remote-desktop.service"], capture_output=True, text=True, timeout=1)
            return res.stdout.strip() == "active"
        except Exception:
            return False

    def is_remote_control_view_only(self) -> bool:
        """Returns True if remote connection is View Only, False if Full Control."""
        return self._get_bool(self._remote_rdp_settings, SCHEMA_REMOTE_RDP, "view-only", True)

    def set_remote_control_view_only(self, view_only: bool) -> bool:
        """Sets remote desktop control mode (True = View Only, False = Full Control)."""
        return self._set_bool(self._remote_rdp_settings, SCHEMA_REMOTE_RDP, "view-only", bool(view_only))

    def get_screen_share_mode(self) -> str:
        """Returns screen share mode ('mirror-primary' or 'extend')."""
        return self._get_string(self._remote_rdp_settings, SCHEMA_REMOTE_RDP, "screen-share-mode", "mirror-primary")

    def set_screen_share_mode(self, mode: str) -> bool:
        """Sets screen share mode ('mirror-primary' or 'extend')."""
        return self._set_string(self._remote_rdp_settings, SCHEMA_REMOTE_RDP, "screen-share-mode", mode)

    def get_rdp_port(self) -> int:
        """Returns the configured RDP port (default: 3389)."""
        return self._get_int(self._remote_rdp_settings, SCHEMA_REMOTE_RDP, "port", 3389)

    def get_pipewire_version(self) -> str:
        """Returns PipeWire and WirePlumber version string from the system."""
        try:
            res = subprocess.run(['wpctl', 'status'], capture_output=True, text=True, timeout=1)
            for line in res.stdout.splitlines():
                if "PipeWire" in line:
                    # e.g. "PipeWire 'pipewire-0' [1.6.8, ...]"
                    if "[" in line and "]" in line:
                        v = line.split("[")[1].split(",")[0].strip()
                        return f"PipeWire {v} / WirePlumber"
        except Exception:
            pass
        return "PipeWire / WirePlumber"

    def get_device_security_status(self) -> str:
        """Returns human-readable device USB protection status based on real settings."""
        if not self.get_usb_protection_enabled():
            return "Disabled (All USB Allowed)"
        lvl = self.get_usb_protection_level()
        if lvl == "always":
            return "Protected (Always Block New USB)"
        return "Protected (Block at Lock Screen)"

    # -------------------------------------------------------------------------
    # 5. History & Recent Files Tracking
    # -------------------------------------------------------------------------
    def get_remember_recent_files(self) -> bool:
        """Returns True if recent document/file history tracking is enabled."""
        return self._get_bool(self._privacy_settings, SCHEMA_PRIVACY, "remember-recent-files", True)

    def set_remember_recent_files(self, enabled: bool) -> bool:
        """Enables or disables recent file tracking in GTK/Nautilus/GNOME."""
        return self._set_bool(self._privacy_settings, SCHEMA_PRIVACY, "remember-recent-files", bool(enabled))

    def get_remember_app_usage(self) -> bool:
        """Returns True if app launch frequency tracking is enabled."""
        return self._get_bool(self._privacy_settings, SCHEMA_PRIVACY, "remember-app-usage", True)

    def set_remember_app_usage(self, enabled: bool) -> bool:
        """Enables or disables app usage tracking in GNOME Shell and search."""
        return self._set_bool(self._privacy_settings, SCHEMA_PRIVACY, "remember-app-usage", bool(enabled))

    def clear_recent_files_history(self) -> bool:
        """Safely purges ~/.local/share/recently-used.xbel and Gtk.RecentManager history."""
        success = False
        # 1. Purge via Gtk.RecentManager if available
        try:
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            manager = Gtk.RecentManager.get_default()
            if manager:
                manager.purge_items()
                success = True
        except Exception:
            pass

        # 2. Also directly truncate ~/.local/share/recently-used.xbel
        try:
            xbel_path = os.path.expanduser("~/.local/share/recently-used.xbel")
            if os.path.exists(xbel_path):
                # Write empty valid XML container
                with open(xbel_path, "w", encoding="utf-8") as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<xbel version="1.0"\n      xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"\n      xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info"\n></xbel>\n')
                success = True
        except Exception:
            pass

        return success

    # -------------------------------------------------------------------------
    # Overview / Security Summary
    # -------------------------------------------------------------------------
    def get_privacy_summary(self) -> dict:
        """Returns high-level status for the Hero Card."""
        loc = self.get_location_enabled()
        cam = self.get_camera_access()
        mic = self.get_microphone_access()
        rdp = self.get_remote_desktop_enabled()
        
        active_count = sum([loc, cam, mic, rdp])
        return {
            "location_enabled": loc,
            "camera_access": cam,
            "microphone_access": mic,
            "remote_desktop_enabled": rdp,
            "active_services_count": active_count,
            "status_text": "Protected" if not rdp else "Remote Sharing Active"
        }
