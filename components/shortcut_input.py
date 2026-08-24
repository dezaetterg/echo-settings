from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QKeySequence

from theme.colors import Colors
from theme.typography import Typography

class ShortcutInput(QPushButton):
    shortcutChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.toggled.connect(self._on_toggled)
        self.current_shortcut = "<Super>space"
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()
        self.setText(self._format_for_display(self.current_shortcut))

    def _format_for_display(self, shortcut: str) -> str:
        if not shortcut: return ""
        s = shortcut
        s = s.replace("<Super>", "⌘ ")
        s = s.replace("<Ctrl>", "⌃ ")
        s = s.replace("<Alt>", "⌥ ")
        s = s.replace("<Shift>", "⇧ ")
        # Capitalize letters for display, e.g., 'space' -> 'Space', 'g' -> 'G'
        parts = s.split(" ")
        if len(parts) > 1:
            return f"{parts[0]} {parts[-1].capitalize()}"
        return s.capitalize()

    def _update_style(self, *args):
        checked = self.isChecked()
        bg = Colors.HOVER_BG if checked else Colors.CARD_BG
        border = Colors.ACCENT_BLUE if checked else Colors.CARD_BORDER
        style = f"""
            QPushButton {{
                background-color: {bg};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 6px 12px;
                font-family: '{Typography.FONT_FAMILY}';
                font-size: {Typography.SIZE_SMALL}px;
            }}
            QPushButton:hover {{
                background-color: {Colors.HOVER_BG};
            }}
        """
        self.setStyleSheet(style)

    def _on_toggled(self, checked):
        self._update_style()
        if checked:
            self.setText("Press Shortcut...")
        else:
            self.setText(self._format_for_display(self.current_shortcut))

    def keyPressEvent(self, event: QKeyEvent):
        if not self.isChecked():
            super().keyPressEvent(event)
            return

        key = event.key()
        modifiers = event.modifiers()
        
        # Ignore modifier-only presses until a real key is pressed
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            return 

        mod_str = ""
        if modifiers & Qt.ControlModifier:
            mod_str += "<Ctrl>"
        if modifiers & Qt.AltModifier:
            mod_str += "<Alt>"
        if modifiers & Qt.ShiftModifier:
            mod_str += "<Shift>"
        if modifiers & Qt.MetaModifier:
            mod_str += "<Super>"

        key_str = ""
        
        # Mapping Russian layout to English layout for GNOME parsing
        ru_to_en = {
            1049: 'q', 1062: 'w', 1059: 'e', 1050: 'r', 1045: 't', 1053: 'y', 
            1043: 'u', 1064: 'i', 1065: 'o', 1047: 'p', 1061: '[', 1066: ']', 
            1060: 'a', 1067: 's', 1042: 'd', 1040: 'f', 1055: 'g', 1056: 'h', 
            1054: 'j', 1051: 'k', 1044: 'l', 1046: ';', 1069: "'", 1071: 'z', 
            1063: 'x', 1057: 'c', 1052: 'v', 1048: 'b', 1058: 'n', 1068: 'm', 
            1041: ',', 1070: '.', 1025: '`' # Ё -> `
        }
        
        if key == Qt.Key_Space:
            key_str = "space"
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            key_str = "Return"
        elif key in ru_to_en:
            key_str = ru_to_en[key]
        elif Qt.Key_A <= key <= Qt.Key_Z:
            key_str = chr(key).lower()
        elif Qt.Key_0 <= key <= Qt.Key_9:
            key_str = chr(key)
        else:
            key_str = QKeySequence(key).toString().lower()

        if key_str:
            new_shortcut = mod_str + key_str
            self.current_shortcut = new_shortcut
            self.setChecked(False)
            self.shortcutChanged.emit(new_shortcut)

    def set_shortcut(self, shortcut: str):
        self.current_shortcut = shortcut or ""
        if not self.isChecked():
            self.setText(self._format_for_display(self.current_shortcut))
