from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QPixmap

class ThemeTransitionOverlay(QWidget):
    def __init__(self, parent, old_pixmap: QPixmap):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.old_pixmap = old_pixmap
        self.opacity = 1.0
        self.setGeometry(parent.rect())
        
        self.anim = QPropertyAnimation(self, b"opacity_val")
        self.anim.setDuration(250)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.finished.connect(self.deleteLater)
        
    @Property(float)
    def opacity_val(self):
        return self.opacity
        
    @opacity_val.setter
    def opacity_val(self, val):
        self.opacity = val
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setOpacity(self.opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()
