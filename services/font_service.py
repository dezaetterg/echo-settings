import subprocess

class FontService:
    def __init__(self):
        self.installed_fonts = self._get_installed_fonts()

    def _get_installed_fonts(self):
        try:
            # Get list of font families from fc-list
            # fc-list : family
            result = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, check=True)
            families = set()
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                # Sometimes families are comma separated like "Ubuntu,Ubuntu Light"
                parts = line.split(',')
                for p in parts:
                    clean_name = p.strip()
                    if clean_name:
                        families.add(clean_name)
            return sorted(list(families))
        except Exception as e:
            print(f"Error getting fonts: {e}")
            return []

    def _get_gsetting(self, schema, key):
        try:
            result = subprocess.run(["gsettings", "get", schema, key], capture_output=True, text=True)
            if result.returncode == 0:
                val = result.stdout.strip().strip("'").strip('"')
                return val
        except Exception:
            pass
        return None

    def _set_gsetting(self, schema, key, value):
        try:
            subprocess.run(["gsettings", "set", schema, key, f"'{value}'"], check=True)
            return True
        except Exception:
            return False

    def is_supported(self):
        # Check if gsettings and org.gnome.desktop.interface exists
        val = self._get_gsetting("org.gnome.desktop.interface", "font-name")
        return val is not None

    def get_interface_font(self):
        return self._get_gsetting("org.gnome.desktop.interface", "font-name")

    def set_interface_font(self, font_name):
        return self._set_gsetting("org.gnome.desktop.interface", "font-name", font_name)

    def get_document_font(self):
        return self._get_gsetting("org.gnome.desktop.interface", "document-font-name")

    def set_document_font(self, font_name):
        return self._set_gsetting("org.gnome.desktop.interface", "document-font-name", font_name)

    def get_monospace_font(self):
        return self._get_gsetting("org.gnome.desktop.interface", "monospace-font-name")

    def set_monospace_font(self, font_name):
        return self._set_gsetting("org.gnome.desktop.interface", "monospace-font-name", font_name)
