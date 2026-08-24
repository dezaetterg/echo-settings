import subprocess
import ast
import os

class NotificationsBackend:
    def __init__(self):
        pass

    def get_dnd(self):
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.desktop.notifications", "show-banners"], capture_output=True, text=True)
            return res.stdout.strip() == "false"
        except:
            return False

    def set_dnd(self, val):
        try:
            val_str = "false" if val else "true"
            subprocess.run(["gsettings", "set", "org.gnome.desktop.notifications", "show-banners", val_str])
        except:
            pass

    def get_show_in_lock_screen(self):
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.desktop.notifications", "show-in-lock-screen"], capture_output=True, text=True)
            return res.stdout.strip() == "true"
        except:
            return True

    def set_show_in_lock_screen(self, val):
        try:
            val_str = "true" if val else "false"
            subprocess.run(["gsettings", "set", "org.gnome.desktop.notifications", "show-in-lock-screen", val_str])
        except:
            pass

    def get_app_info(self, app_id):
        search_names = [f"{app_id}.desktop", f"{app_id.replace('-', '.')}.desktop"]
        
        dirs = [
            os.path.expanduser("~/.local/share/applications"),
            "/usr/share/applications",
            "/var/lib/flatpak/exports/share/applications",
            "/snap/current/usr/share/applications"
        ]
        
        for d in dirs:
            for sn in search_names:
                path = os.path.join(d, sn)
                if os.path.exists(path):
                    return self._parse_desktop_file(path)
                    
        return None

    def _parse_desktop_file(self, path):
        name = None
        icon = None
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("Name=") and not name:
                        name = line.strip().split("=", 1)[1]
                    elif line.startswith("Icon=") and not icon:
                        icon = line.strip().split("=", 1)[1]
                    if name and icon:
                        break
        except:
            pass
        return {"name": name, "icon": icon}

    def get_applications(self):
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.desktop.notifications", "application-children"], capture_output=True, text=True)
            apps = ast.literal_eval(res.stdout.strip())
        except:
            return []
            
        # Fast single-pass dconf dump
        dconf_data = {}
        try:
            d_res = subprocess.run(['dconf', 'dump', '/org/gnome/desktop/notifications/application/'], capture_output=True, text=True)
            cur_section = None
            for line in d_res.stdout.splitlines():
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    cur_section = line[1:-1]
                    dconf_data[cur_section] = {}
                elif '=' in line and cur_section:
                    k, v = line.split('=', 1)
                    dconf_data[cur_section][k.strip()] = v.strip()
        except Exception:
            dconf_data = {}

        app_list = []
        for app_id in apps:
            info = self.get_app_info(app_id)
            if info and info["name"]:
                name = info["name"]
                icon = info["icon"] or "application-x-executable"
            else:
                name = app_id.replace("-", " ").title()
                icon = "application-x-executable"
                
            app_cfg = dconf_data.get(app_id, {})
            
            def get_app_key(key, default=True):
                if key in app_cfg:
                    return app_cfg[key].lower() == "true"
                # Fallback to gsettings if dconf dump was empty
                if not dconf_data:
                    try:
                        path = f"/org/gnome/desktop/notifications/application/{app_id}/"
                        r = subprocess.run(["gsettings", "get", "org.gnome.desktop.notifications.application:" + path, key], capture_output=True, text=True)
                        return r.stdout.strip() == "true"
                    except:
                        return default
                return default
                    
            app_list.append({
                "id": app_id,
                "name": name,
                "icon": icon,
                "enable": get_app_key("enable", True),
                "banners": get_app_key("show-banners", True),
                "sounds": get_app_key("enable-sound-alerts", True),
                "lock_screen": get_app_key("show-in-lock-screen", False)
            })
            
        return sorted(app_list, key=lambda x: x["name"].lower())

    def set_app_key(self, app_id, key, val):
        try:
            path = f"/org/gnome/desktop/notifications/application/{app_id}/"
            val_str = "true" if val else "false"
            subprocess.run(["gsettings", "set", "org.gnome.desktop.notifications.application:" + path, key, val_str])
        except:
            pass
