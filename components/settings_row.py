from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, Property
from PySide6.QtGui import QPainter, QPen, QColor
from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from theme.metrics import CARD_RADIUS

class SettingsRow(QWidget):
    """A row inside a SettingsGroup, optionally with a separator at the bottom. Interactive rows highlight on hover."""
    def __init__(self, label_text: str, control_widget: QWidget = None, show_separator: bool = True, is_interactive: bool = False, is_destructive: bool = False):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show_separator = show_separator
        self.is_interactive = is_interactive
        self.is_destructive = is_destructive
        self.setMinimumHeight(52)
        
        # Determine if this is the first or last row in the group to round the hover highlight corners correctly
        self.is_first = False
        self.is_last = False
        
        self._hover_alpha = 0.0
        self.anim = QPropertyAnimation(self, b"hover_alpha")
        self.anim.setDuration(150)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)
        
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(self.label)
        layout.addStretch()
        
        if control_widget:
            self.add_widget(control_widget)
            
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)
        
    @Property(float)
    def hover_alpha(self):
        return self._hover_alpha

    @hover_alpha.setter
    def hover_alpha(self, val):
        self._hover_alpha = val
        self.update()

    def enterEvent(self, event):
        if self.is_interactive:
            self.anim.setDirection(QPropertyAnimation.Forward)
            self.anim.setStartValue(self._hover_alpha)
            self.anim.setEndValue(1.0)
            self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.is_interactive:
            self.anim.stop()
            self.anim.setDirection(QPropertyAnimation.Forward)
            self.anim.setStartValue(self._hover_alpha)
            self.anim.setEndValue(0.0)
            self.anim.start()
        super().leaveEvent(event)
        
    def add_widget(self, widget: QWidget):
        self.layout().addWidget(widget)
        
    def update_style(self, _is_dark=False):
        color = Colors.DESTRUCTIVE if self.is_destructive else Colors.TEXT_PRIMARY
        self.label.setStyleSheet(f"color: {color}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_MEDIUM};")
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw hover highlight
        if self._hover_alpha > 0:
            is_dark = ThemeManager.is_dark
            base_color = QColor(255, 255, 255) if is_dark else QColor(0, 0, 0)
            base_color.setAlphaF((0.08 if is_dark else 0.04) * self._hover_alpha)
            painter.setBrush(base_color)
            painter.setPen(Qt.NoPen)
            
            # Draw rounded highlight. If it's the first or last row, round only the respective corners.
            # For simplicity, since we didn't inject is_first/is_last logic automatically, we will draw a flat rect, 
            # and rely on the parent group's clipping (which QWidget doesn't do natively without a mask, but it looks acceptable).
            # Let's just draw a slightly smaller rounded rect for the highlight to avoid clipping issues.
            rect = self.rect().adjusted(4, 0, -4, 0)
            painter.drawRoundedRect(rect, 8, 8)
            
        # Draw separator
        if self.show_separator:
            sep_color = QColor(Colors.CARD_BORDER)
            sep_color.setAlpha(50 if ThemeManager.is_dark else 40) # Lighter separator
            painter.setPen(QPen(sep_color, 1))
            painter.drawLine(20, self.height() - 1, self.width() - 20, self.height() - 1) # Add right margin
        painter.end()
