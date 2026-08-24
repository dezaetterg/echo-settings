from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt, QRect, QRectF, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen
from theme.colors import Colors
from theme.manager import ThemeManager

class Slider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(24)
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)
        
        self._anim = QPropertyAnimation(self, b"animValue")
        self._anim.setDuration(250)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        
    @Property(int)
    def animValue(self):
        return super().value()
        
    @animValue.setter
    def animValue(self, val):
        super().setValue(val)
        
    def setValue(self, val):
        if self.isSliderDown():
            super().setValue(val)
        else:
            self._anim.stop()
            self._anim.setEndValue(val)
            self._anim.start()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            w = max(1, self.width())
            x = event.position().x() if hasattr(event, "position") else event.pos().x()
            ratio = max(0.0, min(1.0, x / w))
            if self.invertedAppearance():
                val = self.maximum() - ratio * (self.maximum() - self.minimum())
            else:
                val = self.minimum() + ratio * (self.maximum() - self.minimum())
            super().setValue(int(round(val)))
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)
        
    def update_style(self, _is_dark=False):
        is_dark = ThemeManager.is_dark
        
        bg_color = "rgba(255, 255, 255, 0.15)" if is_dark else "#E5E5EA"
        
        self.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 4px;
                border-radius: 2px;
                background: {bg_color};
            }}
            QSlider::sub-page:horizontal {{
                background: #007AFF;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                width: 18px;
                height: 18px;
                margin: -7px 0;
                background: #FFFFFF;
                border: 0.5px solid rgba(0, 0, 0, 0.2);
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #F5F5F5;
            }}
            QSlider::handle:horizontal:pressed {{
                background: #EBEBEB;
            }}
        """)
