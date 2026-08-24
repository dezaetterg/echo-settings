from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen
from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from theme.metrics import CARD_RADIUS

class SimpleActionCard(QWidget):
    def __init__(self, label: str, is_destructive=False, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.is_destructive = is_destructive
        self._hover = False
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        
        self.lbl = QLabel(label)
        if is_destructive:
            self.lbl.setStyleSheet(f"color: {Colors.DESTRUCTIVE}; font-size: {Typography.SIZE_BODY}px; font-weight: 500;")
        else:
            self.lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_BODY}px; font-weight: 500;")
        
        layout.addWidget(self.lbl, 0, Qt.AlignCenter)
        
    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect().adjusted(0, 0, 0, -1)
        
        is_dark = ThemeManager.is_dark
        
        if self._hover:
            bg_color = QColor(Colors.HOVER_BG)
            path = QPainterPath()
            path.addRoundedRect(rect, 6, 6)
            p.fillPath(path, bg_color)
            
class ActionGridCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        from PySide6.QtWidgets import QGridLayout
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(8)
        self.items_count = 0
        
    def add_action(self, widget):
        row = self.items_count // 2
        col = self.items_count % 2
        self.layout.addWidget(widget, row, col)
        self.items_count += 1

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        is_dark = ThemeManager.is_dark
        shadow_color = QColor(0, 0, 0, 40 if is_dark else 15)
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(2, 4, -2, -2), CARD_RADIUS, CARD_RADIUS)
        painter.fillPath(path, shadow_color)
        
        bg_color = QColor(Colors.CARD_BG)
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect().adjusted(0, 0, 0, -4), CARD_RADIUS, CARD_RADIUS)
        painter.fillPath(bg_path, bg_color)
        
        border_color = QColor(Colors.CARD_BORDER)
        border_color.setAlpha(30 if is_dark else 50)
        painter.setPen(QPen(border_color, 1))
        painter.drawPath(bg_path)
