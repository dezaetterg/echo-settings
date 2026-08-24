import subprocess

class KeyboardBackend:
    def __init__(self):
        pass

    def get_repeat_enabled(self):
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.desktop.peripherals.keyboard", "repeat"], capture_output=True, text=True)
            return res.stdout.strip() == "true"
        except:
            return True

    def set_repeat_enabled(self, val):
        for schema in ("org.gnome.desktop.peripherals.keyboard", "org.cinnamon.desktop.peripherals.keyboard"):
            try:
                subprocess.Popen(["gsettings", "set", schema, "repeat", "true" if val else "false"])
            except:
                pass

    def get_delay(self):
        for schema in ("org.gnome.desktop.peripherals.keyboard", "org.cinnamon.desktop.peripherals.keyboard"):
            try:
                res = subprocess.run(["gsettings", "get", schema, "delay"], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    return int(res.stdout.strip().replace("uint32", "").strip())
            except:
                pass
        return 500

    def set_delay(self, val):
        for schema in ("org.gnome.desktop.peripherals.keyboard", "org.cinnamon.desktop.peripherals.keyboard"):
            try:
                subprocess.Popen(["gsettings", "set", schema, "delay", str(val)])
            except:
                pass

    def get_interval(self):
        for schema in ("org.gnome.desktop.peripherals.keyboard", "org.cinnamon.desktop.peripherals.keyboard"):
            try:
                res = subprocess.run(["gsettings", "get", schema, "repeat-interval"], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    return int(res.stdout.strip().replace("uint32", "").strip())
            except:
                pass
        return 30

    def set_interval(self, val):
        for schema in ("org.gnome.desktop.peripherals.keyboard", "org.cinnamon.desktop.peripherals.keyboard"):
            try:
                subprocess.Popen(["gsettings", "set", schema, "repeat-interval", str(val)])
            except:
                pass

    def get_input_sources(self):
        try:
            import ast
            res = subprocess.run(["gsettings", "get", "org.gnome.desktop.input-sources", "sources"], capture_output=True, text=True)
            val = res.stdout.strip()
            return ast.literal_eval(val)
        except:
            return []

    def get_current_input_source(self):
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.desktop.input-sources", "current"], capture_output=True, text=True)
            return int(res.stdout.strip().replace("uint32", "").strip())
        except:
            return 0

    def set_current_input_source(self, index):
        try:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.input-sources", "current", str(index)])
        except:
            pass

    def get_cursor_blink(self):
        for schema in ("org.gnome.desktop.interface", "org.cinnamon.desktop.interface"):
            try:
                res = subprocess.run(["gsettings", "get", schema, "cursor-blink"], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip() == "true"
            except:
                pass
        return True

    def set_cursor_blink(self, val):
        for schema in ("org.gnome.desktop.interface", "org.cinnamon.desktop.interface"):
            try:
                subprocess.Popen(
                    ["gsettings", "set", schema, "cursor-blink", "true" if val else "false"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except:
                pass

    def get_disable_while_typing(self):
        for schema in ("org.gnome.desktop.peripherals.touchpad", "org.cinnamon.desktop.peripherals.touchpad"):
            try:
                res = subprocess.run(["gsettings", "get", schema, "disable-while-typing"], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip() == "true"
            except:
                pass
        return True

    def set_disable_while_typing(self, val):
        for schema in ("org.gnome.desktop.peripherals.touchpad", "org.cinnamon.desktop.peripherals.touchpad"):
            try:
                subprocess.Popen(
                    ["gsettings", "set", schema, "disable-while-typing", "true" if val else "false"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except:
                pass

    def get_sticky_keys(self):
        for schema in ("org.gnome.desktop.a11y.keyboard", "org.cinnamon.desktop.a11y.keyboard"):
            try:
                res = subprocess.run(["gsettings", "get", schema, "stickykeys-enable"], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip() == "true"
            except:
                pass
        return False

    def set_sticky_keys(self, val):
        for schema in ("org.gnome.desktop.a11y.keyboard", "org.cinnamon.desktop.a11y.keyboard"):
            try:
                subprocess.Popen(["gsettings", "set", schema, "stickykeys-enable", "true" if val else "false"])
            except:
                pass

    def get_lock_state(self, lock_type):
        import glob
        paths = glob.glob(f"/sys/class/leds/*::{lock_type}/brightness")
        for path in paths:
            try:
                with open(path, "r") as f:
                    if f.read().strip() == "1":
                        return True
            except:
                pass
        return False

    def open_shortcuts(self):
        import shutil
        tools = ["cinnamon-settings keyboard", "gnome-control-center keyboard", "xfce4-keyboard-settings", "systemsettings kcm_keys"]
        for tool in tools:
            binary = tool.split()[0]
            if shutil.which(binary):
                try:
                    subprocess.Popen(tool.split())
                    return
                except:
                    pass

    def get_primary_keyboard_info(self):
        try:
            with open("/proc/bus/input/devices", "r") as f:
                content = f.read()
                
            blocks = content.split("\n\n")
            best_kb = None
            for block in blocks:
                if "Handlers=" in block and "kbd" in block:
                    if "BRLTTY" in block or "Virtual" in block:
                        continue
                    
                    name_line = [l for l in block.split("\n") if l.startswith("N: Name=")]
                    phys_line = [l for l in block.split("\n") if l.startswith("P: Phys=")]
                    
                    if name_line:
                        name = name_line[0].split("=")[1].strip('"').strip()
                        phys = phys_line[0].split("=")[1] if phys_line else ""
                        
                        
                        ignore_names = ["power button", "sleep button", "video bus", "pc speaker", "microphone", "headphone", "audio", "camera", "hdmi"]
                        if any(ign in name.lower() for ign in ignore_names):
                            continue
                            
                        conn_type = "Internal"
                        if "usb" in phys.lower():
                            conn_type = "USB"
                        elif "bluetooth" in phys.lower() or "0005:" in block:
                            conn_type = "Bluetooth"
                            
                        clean_name = name.replace(" Consumer Control", "").replace(" System Control", "").strip()
                        if "Control" not in name and "Mouse" not in name:
                            return {"name": clean_name, "type": conn_type, "status": "Connected"}
                            
                        if best_kb is None:
                            best_kb = {"name": clean_name, "type": conn_type, "status": "Connected"}
            if best_kb:
                return best_kb
        except:
            pass
            
        return {"name": "Built-in Keyboard", "type": "Internal", "status": "Active"}
