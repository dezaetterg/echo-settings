from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from theme.colors import Colors
from theme.manager import ThemeManager
from components.settings_row import SettingsRow
import re

class _ClickToScrollComboBox(QComboBox):
    """QComboBox that ignores wheel events until the user explicitly
    clicks it. This prevents accidental font changes while scrolling."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scroll_enabled = False
        # Lose scroll-focus when the popup closes
        self.view().installEventFilter(self)

    def mousePressEvent(self, event):
        self._scroll_enabled = True
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        if self._scroll_enabled:
            super().wheelEvent(event)
        else:
            event.ignore()  # pass to parent scroll area

    def leaveEvent(self, event):
        self._scroll_enabled = False
        super().leaveEvent(event)

    def hidePopup(self):
        super().hidePopup()
        self._scroll_enabled = False

class FontPreviewCard(QWidget):
    def __init__(self, font_name: str, font_size: int = 11):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 20, 24, 24)
        self.layout.setSpacing(4)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.CARD_BG};
                border-radius: 12px;
                border: 1px solid {Colors.CARD_BORDER};
            }}
        """)
        
        self.lbl_aa = QLabel("Aa")
        self.lbl_aa.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; border: none; background: transparent;")
        
        self.lbl_en_up = QLabel("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.lbl_en_up.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; border: none; background: transparent;")
        self.lbl_en_low = QLabel("abcdefghijklmnopqrstuvwxyz")
        self.lbl_en_low.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; border: none; background: transparent;")
        
        self.lbl_ru_up = QLabel("АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩ")
        self.lbl_ru_up.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; border: none; background: transparent;")
        self.lbl_ru_low = QLabel("абвгдежзийклмнопрстуфхцчшщ")
        self.lbl_ru_low.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; border: none; background: transparent;")
        
        self.lbl_num = QLabel("0123456789")
        self.lbl_num.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; border: none; background: transparent;")
        
        self.lbl_sent = QLabel("The quick brown fox jumps over the lazy dog.\nСъешь ещё этих мягких французских булок.")
        self.lbl_sent.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; border: none; background: transparent;")
        
        self.labels = [self.lbl_en_up, self.lbl_en_low, self.lbl_ru_up, self.lbl_ru_low, self.lbl_num, self.lbl_sent]
        for lbl in self.labels:
            lbl.setWordWrap(True)
            
        self.layout.addWidget(self.lbl_aa)
        self.layout.addSpacing(16)
        self.layout.addWidget(self.lbl_en_up)
        self.layout.addWidget(self.lbl_en_low)
        self.layout.addSpacing(12)
        self.layout.addWidget(self.lbl_ru_up)
        self.layout.addWidget(self.lbl_ru_low)
        self.layout.addSpacing(12)
        self.layout.addWidget(self.lbl_num)
        self.layout.addSpacing(16)
        self.layout.addWidget(self.lbl_sent)
        
        self.set_font(font_name, font_size)
        
    def set_font(self, full_font_string: str, base_size: int):
        match = re.search(r'(.+?)\s+(\d+)$', full_font_string)
        family = match.group(1).strip() if match else full_font_string.strip()
            
        f_base = QFont(family)
        f_base.setPointSize(base_size)
        
        f_aa = QFont(family)
        f_aa.setPointSize(42)
        
        self.lbl_aa.setFont(f_aa)
        for lbl in self.labels:
            lbl.setFont(f_base)

class FontPicker(QWidget):
    font_changed = Signal(str)
    
    def __init__(self, title, installed_fonts, current_font_str, is_monospace=False, show_separator=False):
        super().__init__()
        self.installed_fonts = installed_fonts
        self.is_monospace = is_monospace
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(16) # More spacing between combobox and preview
        
        # Parse current font string (e.g. "Ubuntu 11")
        match = re.search(r'(.+?)\s+(\d+)$', current_font_str)
        if match:
            self.current_family = match.group(1).strip()
            self.current_size = match.group(2).strip()
        else:
            self.current_family = current_font_str.strip()
            self.current_size = "11"
            
        # Combo box — using custom class to prevent accidental wheel-scroll
        self.combo = _ClickToScrollComboBox()
        self.combo.setFixedSize(200, 26)
        self.combo.setCursor(Qt.PointingHandCursor)
        self._apply_combo_style()
        ThemeManager.theme_changed.connect(lambda _: self._apply_combo_style())
        
        # Add items and select current
        self.combo.addItems(self.installed_fonts)
        index = self.combo.findText(self.current_family, Qt.MatchContains)
        if index >= 0:
            self.combo.setCurrentIndex(index)
            
        self.combo.currentTextChanged.connect(self._on_combo_changed)
        
        # We need a SettingsRow-like header
        self.row = SettingsRow(title, self.combo, show_separator=show_separator, is_interactive=False)
        self.layout.addWidget(self.row)
        
        # Preview card
        self.preview = FontPreviewCard(current_font_str, int(self.current_size))
        self.layout.addWidget(self.preview)
        
        # Add a little bottom margin if there is a separator so it doesn't touch the separator tightly
        if show_separator:
            self.layout.setContentsMargins(0, 0, 0, 10)
        
    def _apply_combo_style(self):
        is_dark = ThemeManager.is_dark
        hover_bg = "rgba(255,255,255,0.08)" if is_dark else "rgba(0,0,0,0.06)"
        self.combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {Colors.CARD_BG};
                border: 1px solid {Colors.CARD_BORDER};
                border-radius: 6px;
                padding: 4px 28px 4px 12px;
                color: {Colors.TEXT_PRIMARY};
                font-size: 13px;
            }}
            QComboBox:hover {{
                background-color: {hover_bg};
                border: 1px solid {Colors.CARD_BORDER};
                border-radius: 6px;
            }}
            QComboBox:focus {{
                border: 1.5px solid {Colors.ACCENT_BLUE};
                border-radius: 6px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0px;
                height: 0px;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {Colors.TEXT_SECONDARY};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {Colors.CARD_BG};
                color: {Colors.TEXT_PRIMARY};
                selection-background-color: {Colors.ACCENT_BLUE};
                selection-color: white;
                border: 1px solid {Colors.CARD_BORDER};
                border-radius: 8px;
                outline: none;
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 24px;
            }}
        """)

    def _on_combo_changed(self, new_family):
        new_val = f"{new_family} {self.current_size}"
        self.preview.set_font(new_val, int(self.current_size))
        self.font_changed.emit(new_val)
