from PySide6.QtWidgets import QLineEdit
from theme.colors import Colors
from theme.typography import Typography
from theme.metrics import SEARCH_HEIGHT

class SearchBar(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(SEARCH_HEIGHT)
        self.setFixedWidth(160)
        self.setPlaceholderText("Search")
        from theme.manager import ThemeManager
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)
        
    def update_style(self, _is_dark=False):
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.SEARCH_BG};
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 0 8px;
                font-size: {Typography.SIZE_BODY}px;
                color: {Colors.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border: 1px solid {Colors.SEARCH_BORDER_FOCUS};
                background-color: {Colors.CARD_BG};
            }}
        """)
