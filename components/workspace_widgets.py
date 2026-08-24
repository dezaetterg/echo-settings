from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen

from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager

class WorkspaceIconWidget(QWidget):
    """30x30 Squircle vector icon for Workspace & Desktop settings."""
    def __init__(self, category: str, color_hex: str, parent=None):
        super().__init__(parent)
        self.category = category
        self.color_hex = color_hex
        self.setFixedSize(30, 30)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Background rounded rectangle
        p.setBrush(QColor(self.color_hex))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 7, 7)

        # Foreground vector symbol
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(Qt.white, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        cx, cy = self.width() / 2.0, self.height() / 2.0

        if self.category == "hot_corners":
            # 4 corner brackets
            p.drawPolyline([QPointF(cx - 7, cy - 3), QPointF(cx - 7, cy - 7), QPointF(cx - 3, cy - 7)])
            p.drawPolyline([QPointF(cx + 3, cy - 7), QPointF(cx + 7, cy - 7), QPointF(cx + 7, cy - 3)])
            p.drawPolyline([QPointF(cx - 7, cy + 3), QPointF(cx - 7, cy + 7), QPointF(cx - 3, cy + 7)])
            p.drawPolyline([QPointF(cx + 3, cy + 7), QPointF(cx + 7, cy + 7), QPointF(cx + 7, cy + 3)])

        elif self.category == "workspaces":
            # 2 overlapping workspace cards
            p.drawRoundedRect(QRectF(cx - 7, cy - 5.5, 9.5, 7.5), 1.5, 1.5)
            p.drawRoundedRect(QRectF(cx - 2.5, cy - 2, 9.5, 7.5), 1.5, 1.5)

        elif self.category == "displays":
            # Monitor with stand
            p.drawRoundedRect(QRectF(cx - 7.5, cy - 6.5, 15, 9.5), 1.5, 1.5)
            p.drawLine(QPointF(cx, cy + 3), QPointF(cx, cy + 6.5))
            p.drawLine(QPointF(cx - 4, cy + 6.5), QPointF(cx + 4, cy + 6.5))

        elif self.category == "app_switching":
            # Two switching application windows
            p.drawRoundedRect(QRectF(cx - 7, cy - 6, 8.5, 8.5), 1.5, 1.5)
            p.drawRoundedRect(QRectF(cx - 1.5, cy - 2.5, 8.5, 8.5), 1.5, 1.5)


class RadioIndicator(QWidget):
    """Native macOS-style 16x16 circular radio button indicator."""
    def __init__(self, is_checked: bool = False, parent=None):
        super().__init__(parent)
        self.is_checked = is_checked
        self.setFixedSize(16, 16)

    def setChecked(self, checked: bool):
        if self.is_checked != checked:
            self.is_checked = checked
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        is_dark = ThemeManager.is_dark

        if self.is_checked:
            p.setBrush(QColor("#007AFF"))
            p.setPen(Qt.NoPen)
            p.drawEllipse(rect.adjusted(1, 1, -1, -1))
            # inner white dot
            p.setBrush(Qt.white)
            p.drawEllipse(rect.center(), 2.4, 2.4)
        else:
            p.setBrush(Qt.NoBrush)
            border_color = QColor(255, 255, 255, 90) if is_dark else QColor(0, 0, 0, 70)
            p.setPen(QPen(border_color, 1.5))
            p.drawEllipse(rect.adjusted(1.5, 1.5, -1.5, -1.5))


class RadioOptionItem(QWidget):
    """Interactive radio option with title and optional description."""
    clicked = Signal()

    def __init__(self, option_id: str, title: str, subtitle: str = "", is_checked: bool = False, parent=None):
        super().__init__(parent)
        self.option_id = option_id
        self.is_checked = is_checked
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)

        self.indicator = RadioIndicator(is_checked)
        layout.addWidget(self.indicator, alignment=Qt.AlignVCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)

        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: {Typography.WEIGHT_MEDIUM};")
        text_layout.addWidget(self.title_lbl)

        if subtitle:
            self.sub_lbl = QLabel(subtitle)
            self.sub_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_SMALL}px;")
            text_layout.addWidget(self.sub_lbl)
        else:
            self.sub_lbl = None

        layout.addLayout(text_layout)

        ThemeManager.theme_changed.connect(self.update_style)

    def update_style(self, _is_dark=False):
        self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: {Typography.WEIGHT_MEDIUM};")
        if self.sub_lbl:
            self.sub_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_SMALL}px;")
        self.indicator.update()

    def setChecked(self, checked: bool):
        self.is_checked = checked
        self.indicator.setChecked(checked)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
        else:
            super().mousePressEvent(event)


class WorkspaceRadioRow(QWidget):
    """A row inside SettingsGroup containing a left-aligned radio option with separator support."""
    def __init__(self, option_item: RadioOptionItem, show_separator: bool = True, parent=None):
        super().__init__(parent)
        self.option_item = option_item
        self.show_separator = show_separator
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(64, 4, 20, 4)
        layout.addWidget(option_item)
        layout.addStretch()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.show_separator:
            painter = QPainter(self)
            sep_color = QColor(Colors.CARD_BORDER)
            sep_color.setAlpha(50 if ThemeManager.is_dark else 40)
            painter.setPen(QPen(sep_color, 1))
            painter.drawLine(64, self.height() - 1, self.width() - 20, self.height() - 1)
            painter.end()


class InlineRadioGroup(QWidget):
    """Horizontal inline radio buttons for row controls."""
    valueChanged = Signal(str)

    def __init__(self, options: list[tuple[str, str]], active_id: str, parent=None):
        super().__init__(parent)
        self.options = options  # [(id, label), ...]
        self.active_id = active_id
        self._items: dict[str, RadioOptionItem] = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        for opt_id, label in options:
            item = RadioOptionItem(opt_id, label, is_checked=(opt_id == active_id))
            item.clicked.connect(lambda o=opt_id: self.setActiveId(o))
            self._items[opt_id] = item
            layout.addWidget(item)

    def setActiveId(self, opt_id: str, emit_signal: bool = True):
        if self.active_id != opt_id or not emit_signal:
            self.active_id = opt_id
            for oid, item in self._items.items():
                item.setChecked(oid == opt_id)
            if emit_signal:
                self.valueChanged.emit(opt_id)


class WorkspaceHeaderRow(QWidget):
    """Card header row with squircle icon, bold title, and subtitle."""
    def __init__(self, icon_category: str, color_hex: str, title: str, subtitle: str, right_widget: QWidget = None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(14)

        self.icon_widget = WorkspaceIconWidget(icon_category, color_hex)
        layout.addWidget(self.icon_widget, alignment=Qt.AlignVCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 15px; font-weight: {Typography.WEIGHT_SEMIBOLD};")
        text_layout.addWidget(self.title_lbl)

        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        self.sub_lbl.setWordWrap(True)
        text_layout.addWidget(self.sub_lbl)

        layout.addLayout(text_layout, 1)

        if right_widget:
            layout.addWidget(right_widget, 0, alignment=Qt.AlignVCenter | Qt.AlignRight)

        ThemeManager.theme_changed.connect(self.update_style)

    def update_style(self, _is_dark=False):
        self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 15px; font-weight: {Typography.WEIGHT_SEMIBOLD};")
        self.sub_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
