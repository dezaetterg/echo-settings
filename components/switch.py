from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, Signal
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen
from theme.colors import Colors
from theme.manager import ThemeManager

class Switch(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(44, 24)
        self.setCursor(Qt.PointingHandCursor)
        self._checked = checked
        self._position = 22.0 if checked else 2.0
        
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(200)
        
        self._hover_progress = 0.0
        self.hover_anim = QPropertyAnimation(self, b"hover_progress")
        self.hover_anim.setDuration(150)
        
    @Property(float)
    def hover_progress(self):
        return self._hover_progress
        
    @hover_progress.setter
    def hover_progress(self, val):
        self._hover_progress = val
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
        
    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self.animation.setStartValue(self._position)
            self.animation.setEndValue(22.0 if checked else 2.0) 
            self.animation.start()
        
    @Property(float)
    def position(self):
        return self._position
        
    @position.setter
    def position(self, pos):
        self._position = pos
        self.update()
        
    def mousePressEvent(self, event):
        if not self.isEnabled():
            return
        if event.button() == Qt.LeftButton:
            event.accept()
        else:
            super().mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        if not self.isEnabled():
            return
        if event.button() == Qt.LeftButton:
            self.setChecked(not self._checked)
            self.toggled.emit(self._checked)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
            
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.35)
        
        is_dark = ThemeManager.is_dark
        bg_color = QColor(Colors.SWITCH_ON) if self._checked else QColor(Colors.SEARCH_BG)
        
        # In dark mode, if OFF, Apple makes it slightly lighter than background
        if not self._checked and is_dark:
            bg_color = QColor(255, 255, 255, 25)
            
        # Add hover bright/dark overlay
        if self._hover_progress > 0:
            hover_r = 255 if is_dark else 0
            hover_a = int(self._hover_progress * 15)
            overlay = QColor(hover_r, hover_r, hover_r, hover_a)
            # blend bg_color and overlay
            r = (bg_color.red() * (255 - hover_a) + overlay.red() * hover_a) // 255
            g = (bg_color.green() * (255 - hover_a) + overlay.green() * hover_a) // 255
            b = (bg_color.blue() * (255 - hover_a) + overlay.blue() * hover_a) // 255
            a = max(bg_color.alpha(), hover_a)
            bg_color = QColor(r, g, b, a)
            
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.height()/2, self.height()/2)
        p.fillPath(path, bg_color)
        
        # Border
        if not self._checked:
            p.setPen(QPen(QColor(Colors.CARD_BORDER), 1))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)
            
        # Knob setup
        knob_size = self.height() - 4
        knob_y = 2
        
        # Fake soft shadow for knob
        shadow_color = QColor(0, 0, 0, 20 if not is_dark else 50)
        p.setPen(Qt.NoPen)
        p.setBrush(shadow_color)
        p.drawEllipse(int(self._position), knob_y + 1, knob_size, knob_size)
        p.drawEllipse(int(self._position), knob_y + 2, knob_size, knob_size)
        
        # Circle
        p.setBrush(QColor("#FFFFFF") if not is_dark else QColor("#D1D1D1"))
        p.setPen(QPen(QColor(0, 0, 0, 15), 1))
        p.drawEllipse(int(self._position), knob_y, knob_size, knob_size)
        p.end()
