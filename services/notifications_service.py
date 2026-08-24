import sys
if "/usr/lib/python3/dist-packages" not in sys.path:
    sys.path.append("/usr/lib/python3/dist-packages")

import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio

def _get_safe_schema(schema_id: str, path: str = None):
    try:
        source = Gio.SettingsSchemaSource.get_default()
        if source and source.lookup(schema_id, True):
            if path:
                return Gio.Settings.new_with_path(schema_id, path)
            return Gio.Settings.new(schema_id)
    except Exception:
        pass
    return None

class NotificationsService:
    def __init__(self):
        self.settings = _get_safe_schema("org.gnome.desktop.notifications")

    def _safe_get_bool(self, settings_obj, key):
        if settings_obj and key in settings_obj.list_keys():
            return settings_obj.get_boolean(key)
        return "Not Supported"

    def _safe_set_bool(self, settings_obj, key, val):
        if settings_obj and key in settings_obj.list_keys():
            settings_obj.set_boolean(key, val)

    def get_dnd(self):
        val = self._safe_get_bool(self.settings, "show-banners")
        if val == "Not Supported": return "Not Supported"
        return not val

    def set_dnd(self, val):
        if val != "Not Supported":
            self._safe_set_bool(self.settings, "show-banners", not val)

    def get_show_in_lock_screen(self):
        return self._safe_get_bool(self.settings, "show-in-lock-screen")

    def set_show_in_lock_screen(self, val):
        self._safe_set_bool(self.settings, "show-in-lock-screen", val)

    def get_applications(self):
        if not self.settings or "application-children" not in self.settings.list_keys():
            return []
            
        apps = self.settings.get_strv("application-children")
        app_list = []
        seen_names = set()
        for app_id in apps:
            app_info = self._get_desktop_info(app_id)
            name = app_info["name"] if app_info and app_info["name"] else app_id.replace("-", " ").title()
            
            if name in seen_names:
                continue
            seen_names.add(name)
            
            icon = app_info["icon"] if app_info and app_info["icon"] else "application-x-executable"
            
            path = f"/org/gnome/desktop/notifications/application/{app_id}/"
            app_settings = _get_safe_schema("org.gnome.desktop.notifications.application", path)
                
            app_list.append({
                "id": app_id,
                "name": name,
                "icon": icon,
                "enable": self._safe_get_bool(app_settings, "enable"),
                "banners": self._safe_get_bool(app_settings, "show-banners"),
                "sounds": self._safe_get_bool(app_settings, "enable-sound-alerts"),
                "lock_screen": self._safe_get_bool(app_settings, "show-in-lock-screen"),
                "priority": "Not Supported"
            })
            
        return sorted(app_list, key=lambda x: x["name"].lower())

    def set_app_key(self, app_id, key, val):
        path = f"/org/gnome/desktop/notifications/application/{app_id}/"
        app_settings = _get_safe_schema("org.gnome.desktop.notifications.application", path)
        if app_settings:
            self._safe_set_bool(app_settings, key, val)


    def _get_desktop_info(self, app_id):
        app_info = None
        try:
            app_info = Gio.DesktopAppInfo.new(f"{app_id}.desktop")
        except TypeError:
            pass
            
        if not app_info:
            try:
                app_info = Gio.DesktopAppInfo.new(f"{app_id.replace('-', '.')}.desktop")
            except TypeError:
                pass
                
        # Fallback to search through all desktop files (helps with Flatpak and mixed IDs)
        if not app_info:
            target = app_id.lower()
            target_dot = target.replace('-', '.')
            apps = Gio.DesktopAppInfo.get_all()
            
            # 1st pass: case-insensitive exact match
            for app in apps:
                aid = app.get_id().lower()
                if aid == f"{target}.desktop" or aid == f"{target_dot}.desktop":
                    app_info = app
                    break
                    
            # 2nd pass: fuzzy substring match
            if not app_info:
                for app in apps:
                    aid = app.get_id().lower().replace('.desktop', '')
                    if target in aid or target_dot in aid:
                        app_info = app
                        break
        
        if app_info:
            name = app_info.get_name()
            icon_obj = app_info.get_icon()
            icon_name = "application-x-executable"
            if icon_obj:
                if hasattr(icon_obj, 'get_names') and icon_obj.get_names():
                    icon_name = icon_obj.get_names()[0]
                elif hasattr(icon_obj, 'to_string'):
                    icon_name = icon_obj.to_string()
            return {"name": name, "icon": icon_name}
        return None
