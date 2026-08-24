from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, Property, QEasingCurve, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen
from theme.colors import Colors

class MacOSProgressBar(QWidget):
    def __init__(self, height=14):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(height)
        self._target_percent = 0.0
        self._animated_percent = 0.0
        
        self.anim = QPropertyAnimation(self, b"animated_percent")
        self.anim.setDuration(600)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    @Property(float)
    def animated_percent(self):
        return self._animated_percent

    @animated_percent.setter
    def animated_percent(self, val):
        self._animated_percent = val
        self.update()

    def set_percent(self, percent):
        self._target_percent = max(0, min(100, percent))
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(self._target_percent)
        self.anim.start()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        radius = rect.height() / 2.0

        bg_path = QPainterPath()
        bg_path.addRoundedRect(QRectF(rect), radius, radius)
        
        from theme.manager import ThemeManager
        is_dark = ThemeManager.is_dark
        track_color = QColor(255, 255, 255, 20) if is_dark else QColor(0, 0, 0, 15)
        painter.fillPath(bg_path, track_color)

        if self._animated_percent > 0:
            painter.setClipPath(bg_path)
            
            fill_width = rect.width() * (self._animated_percent / 100)
            fill_rect = QRectF(rect.x(), rect.y(), fill_width, rect.height())
            
            painter.fillRect(fill_rect, QColor(Colors.ACCENT_BLUE))
            
            painter.setClipping(False)
            
        painter.end()
