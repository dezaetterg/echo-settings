from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath
from theme.manager import ThemeManager

class MicLevelIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(12)
        self.setMinimumWidth(200)
        self._level = 0.0
        self._display_level = 0.0
        self._peak_level = 0.0
        self._peak_hold_ticks = 0
        
        self.anim = QPropertyAnimation(self, b"display_level")
        self.anim.setDuration(100) 
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.peak_timer = QTimer(self)
        self.peak_timer.timeout.connect(self._decay_peak)
        self.peak_timer.start(30)
        
    def get_display_level(self):
        return self._display_level
        
    def set_display_level(self, val):
        self._display_level = val
        self.update()
        
    display_level = Property(float, get_display_level, set_display_level)
        
    def set_level(self, val):
        val = max(0.0, min(1.0, val))
        
        if val >= self._peak_level:
            self._peak_level = val
            self._peak_hold_ticks = 20 # Hold peak for ~600ms
            
        if abs(val - self._level) > 0.01 or val == 0.0:
            self._level = val
            self.anim.stop()
            self.anim.setEndValue(val)
            self.anim.start()
            
    def _decay_peak(self):
        if self._peak_hold_ticks > 0:
            self._peak_hold_ticks -= 1
        else:
            if self._peak_level > 0:
                self._peak_level = max(0.0, self._peak_level - 0.03)
                self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        is_dark = ThemeManager.is_dark
        w = self.width()
        h = self.height()
        
        num_segments = 40
        gap = 2
        seg_w = (w - (num_segments - 1) * gap) / num_segments
        
        color_low = QColor("#34C759")   # Green
        color_mid = QColor("#FFCC00")   # Yellow
        color_high = QColor("#FF3B30")  # Red
        
        bg_inactive = QColor(255, 255, 255, 20) if is_dark else QColor(0, 0, 0, 15)
        
        active_segs = int(self._display_level * num_segments)
        peak_seg = int(self._peak_level * num_segments)
        
        for i in range(num_segments):
            x = i * (seg_w + gap)
            rect = QRectF(x, 0, seg_w, h)
            
            pct = i / float(num_segments)
            if pct < 0.65:
                base_color = color_low
            elif pct < 0.85:
                base_color = color_mid
            else:
                base_color = color_high
                
            path = QPainterPath()
            path.addRoundedRect(rect, 1.5, 1.5)
            
            if i < active_segs:
                p.fillPath(path, base_color)
            elif i == peak_seg and peak_seg > 0:
                p.fillPath(path, base_color)
            else:
                p.fillPath(path, bg_inactive)

