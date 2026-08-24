from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager

class NumberStepper(QWidget):
    valueChanged = Signal(int)

    def __init__(self, value: int = 4, min_val: int = 1, max_val: int = 32, suffix: str = "", parent=None):
        super().__init__(parent)
        self._val = value
        self.min_val = min_val
        self.max_val = max_val
        self.suffix = suffix
        self.setFixedHeight(32)
        self.setMinimumWidth(110)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.btn_minus = QPushButton("−")
        self.btn_minus.setFixedSize(30, 28)
        self.btn_minus.setCursor(Qt.PointingHandCursor)
        self.btn_minus.clicked.connect(self._on_minus)

        self.lbl_value = QLabel(self._format_text())
        self.lbl_value.setAlignment(Qt.AlignCenter)
        self.lbl_value.setMinimumWidth(36)

        self.btn_plus = QPushButton("+")
        self.btn_plus.setFixedSize(30, 28)
        self.btn_plus.setCursor(Qt.PointingHandCursor)
        self.btn_plus.clicked.connect(self._on_plus)

        layout.addWidget(self.btn_minus)
        layout.addWidget(self.lbl_value)
        layout.addWidget(self.btn_plus)

        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def _format_text(self) -> str:
        if self.suffix:
            return f"{self._val} {self.suffix}"
        return str(self._val)

    def value(self) -> int:
        return self._val

    def setValue(self, val: int):
        clamped = max(self.min_val, min(self.max_val, val))
        if clamped != self._val:
            self._val = clamped
            self.lbl_value.setText(self._format_text())
            self.btn_minus.setEnabled(self._val > self.min_val)
            self.btn_plus.setEnabled(self._val < self.max_val)
            self.valueChanged.emit(self._val)

    def _on_minus(self):
        self.setValue(self._val - 1)

    def _on_plus(self):
        self.setValue(self._val + 1)

    def update_style(self, _is_dark=False):
        is_dark = ThemeManager.is_dark
        bg_btn = "rgba(255, 255, 255, 0.10)" if is_dark else "rgba(0, 0, 0, 0.05)"
        bg_hover = "rgba(255, 255, 255, 0.18)" if is_dark else "rgba(0, 0, 0, 0.10)"
        border_color = "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(0, 0, 0, 0.10)"
        text_color = "#FFFFFF" if is_dark else "#000000"

        btn_style = f"""
            QPushButton {{
                background-color: {bg_btn};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
            }}
            QPushButton:disabled {{
                color: {Colors.TEXT_SECONDARY};
                opacity: 0.4;
            }}
        """
        self.btn_minus.setStyleSheet(btn_style)
        self.btn_plus.setStyleSheet(btn_style)
        self.lbl_value.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; font-weight: {Typography.WEIGHT_SEMIBOLD};")
        self.btn_minus.setEnabled(self._val > self.min_val)
        self.btn_plus.setEnabled(self._val < self.max_val)
