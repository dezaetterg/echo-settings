import sys
import os
import logging

candidate_paths = [
    os.path.expanduser("~/.local/share/echo-search"),
    os.path.expanduser("~/echo_search"),
    os.path.expanduser("~/spotlight_liquidglass"),
    os.path.expanduser("~/.local/share/spotlight-glass"),
    "/usr/share/echo-search",
    "/usr/local/share/echo-search",
    "/usr/local/share/spotlight-glass",
    "/usr/share/spotlight-glass"
]
for p in candidate_paths:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)


try:
    from config_manager import ConfigManager
except ImportError as e:
    logging.error(f"Could not import Spotlight ConfigManager: {e}")
    class ConfigManager:
        def get(self, key): return None
        def set(self, key, value): pass
        def load(self): pass
        def save(self): pass

class SpotlightSettingsService:
    def __init__(self):
        self._config = ConfigManager()
        
    def is_installed(self) -> bool:
        """Checks if Echo Search is genuinely installed and executable on the system."""
        import shutil
        # 1. Check PATH binary
        if shutil.which("echo-search"):
            return True
        # 2. Check standard installation binaries
        binary_candidates = [
            os.path.expanduser("~/.local/bin/echo-search"),
            "/usr/bin/echo-search",
            "/usr/local/bin/echo-search",
            os.path.expanduser("~/.local/share/echo-search/main.py"),
            os.path.expanduser("~/echo_search/main.py"),
            os.path.expanduser("~/.local/share/spotlight-glass/main.py"),
            "/usr/share/echo-search/main.py",
            "/usr/share/spotlight-glass/main.py",
            "/usr/local/share/spotlight-glass/main.py"
        ]
        for path in binary_candidates:
            if os.path.isfile(path) and (os.access(path, os.X_OK) or path.endswith('.py')):
                return True
        return False
        
    def load(self):
        self._config.load()
        
    def save(self):
        self._config.save()
        
    def get(self, key: str):
        if key == "enabled_modes":
            # Map ConfigManager's Capitalized mode strings to lowercase for UI
            modes = self._config.get("enabled_modes") or []
            return [m.lower() for m in modes]
        return self._config.get(key)
        
    def set(self, key: str, value):
        if key == "enabled_modes":
            self._config.set("applications", "apps" in value)
            self._config.set("files", "files" in value)
            self._config.set("clipboard", "clipboard" in value)
            self._config.set("emoji", "emoji" in value)
        else:
            self._config.set(key, value)
