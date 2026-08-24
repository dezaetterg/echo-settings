from PySide6.QtCore import QObject, Signal

class _ThemeManager(QObject):
    theme_changed = Signal(bool) # emits True if dark mode

    def __init__(self):
        super().__init__()
        self._is_dark = False

    @property
    def is_dark(self):
        return self._is_dark

    def set_dark_mode(self, is_dark: bool):
        if self._is_dark != is_dark:
            self._is_dark = is_dark
            self.theme_changed.emit(is_dark)

    set_theme = set_dark_mode

# Singleton instance
ThemeManager = _ThemeManager()
