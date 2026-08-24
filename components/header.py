from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from theme.metrics import HEADER_HEIGHT
from theme.typography import Typography
from theme.colors import Colors
from theme.manager import ThemeManager
from components.searchbar import SearchBar

class Header(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(HEADER_HEIGHT)
        ThemeManager.theme_changed.connect(self.update_style)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Navigation buttons
        self.back_btn = QPushButton("<")
        self.back_btn.setFixedSize(30, 30)
        self.forward_btn = QPushButton(">")
        self.forward_btn.setFixedSize(30, 30)
        
        btn_style = f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                font-size: {Typography.SIZE_TITLE}px;
                color: {Colors.TEXT_SECONDARY};
            }}
            QPushButton:hover {{
                background-color: {Colors.MENU_ITEM_HOVER};
            }}
        """
        self.back_btn.setStyleSheet(btn_style)
        self.forward_btn.setStyleSheet(btn_style)
        
        layout.addWidget(self.back_btn)
        layout.addWidget(self.forward_btn)
        layout.addSpacing(20)
        
        # Title
        self.title_label = QLabel("Title")
        self.title_label.setStyleSheet(f"font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_SEMIBOLD}; letter-spacing: {Typography.LETTER_SPACING_HEADER}px; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(self.title_label)
        
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addSpacerItem(spacer)
        
        # self.search_box = SearchBar()
        # layout.addWidget(self.search_box)
        
    def set_title(self, title):
        self.title_label.setText(title)
        
    def update_style(self, _is_dark=False):
        btn_style = f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                font-size: {Typography.SIZE_TITLE}px;
                color: {Colors.TEXT_SECONDARY};
            }}
            QPushButton:hover {{
                background-color: {Colors.MENU_ITEM_HOVER};
            }}
        """
        self.back_btn.setStyleSheet(btn_style)
        self.forward_btn.setStyleSheet(btn_style)
        self.title_label.setStyleSheet(f"font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_SEMIBOLD}; letter-spacing: {Typography.LETTER_SPACING_HEADER}px; color: {Colors.TEXT_PRIMARY};")

