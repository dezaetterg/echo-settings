from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QPainterPath
from theme.manager import ThemeManager

class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(32)
        
        self._hover_progress = 0.0
        self._press_progress = 0.0
        
        self.hover_anim = QPropertyAnimation(self, b"hover_progress")
        self.hover_anim.setDuration(150)
        
        self.press_anim = QPropertyAnimation(self, b"press_progress")
        self.press_anim.setDuration(100)
        
    @Property(float)
    def hover_progress(self): return self._hover_progress
    
    @hover_progress.setter
    def hover_progress(self, val):
        self._hover_progress = val
        self.update()
        
    @Property(float)
    def press_progress(self): return self._press_progress
    
    @press_progress.setter
    def press_progress(self, val):
        self._press_progress = val
        self.update()
        
    def enterEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setEndValue(0.0)
        self.hover_anim.start()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        self.press_anim.stop()
        self.press_anim.setEndValue(1.0)
        self.press_anim.start()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self.press_anim.stop()
        self.press_anim.setEndValue(0.0)
        self.press_anim.start()
        super().mouseReleaseEvent(event)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        is_dark = ThemeManager.is_dark
        
        # Base colors (Mac style)
        base_r, base_g, base_b = (120, 120, 128)
        base_a = 46 if is_dark else 25 # 0.18 * 255 / 0.1 * 255
        
        # Hover target
        hov_r, hov_g, hov_b = (0, 122, 255)
        hov_a = 38 # 0.15 * 255
        
        # Interpolate background
        r = int(base_r + (hov_r - base_r) * self._hover_progress)
        g = int(base_g + (hov_g - base_g) * self._hover_progress)
        b = int(base_b + (hov_b - base_b) * self._hover_progress)
        a = int(base_a + (hov_a - base_a) * self._hover_progress)
        
        # Press effect (darken)
        if self._press_progress > 0:
            a = int(a + (60 - a) * self._press_progress)
            
        bg_color = QColor(r, g, b, a)
        
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 6, 6)
        p.fillPath(path, bg_color)
        
        # Text
        text_color = QColor("#007AFF")
        if self._press_progress > 0:
            text_color = QColor("#0056B3")
            
        p.setPen(text_color)
        font = self.font()
        font.setBold(True)
        font.setPixelSize(12)
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignCenter, self.text())
        
        p.end()
