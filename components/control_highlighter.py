from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPropertyAnimation, Property, QEasingCurve, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath
from theme.colors import Colors
from theme.metrics import CARD_RADIUS

class PulseOverlay(QWidget):
    """
    Temporary animated glow overlay rendered directly over a target widget
    to highlight a found setting without altering any stylesheets.
    """
    def __init__(self, target_widget: QWidget, parent: QWidget = None):
        super().__init__(parent or target_widget.window())
        self.target_widget = target_widget
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        self._alpha = 1.0
        self.update_geometry()
        
        self.anim = QPropertyAnimation(self, b"glow_alpha")
        self.anim.setDuration(1600)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.finished.connect(self.deleteLater)
        self.anim.start()

    def update_geometry(self):
        if not self.target_widget or not self.target_widget.isVisible():
            return
        # Map target rect to overlay parent coordinates
        top_left = self.target_widget.mapTo(self.parentWidget(), QPoint(0, 0))
        w = self.target_widget.width()
        h = self.target_widget.height()
        # Add slight padding for elegant outer glow
        pad = 4
        self.setGeometry(top_left.x() - pad, top_left.y() - pad, w + pad * 2, h + pad * 2)

    @Property(float)
    def glow_alpha(self) -> float:
        return self._alpha

    @glow_alpha.setter
    def glow_alpha(self, val: float):
        self._alpha = val
        self.update()

    def paintEvent(self, event):
        if self._alpha <= 0.001:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        rect = QRectF(self.rect()).adjusted(3, 3, -3, -3)
        radius = min(14.0, rect.height() / 2.0)

        # 1. Soft accent background fill glow
        fill_alpha = int(45 * self._alpha)
        p.setBrush(QColor(0, 122, 255, fill_alpha))
        p.setPen(Qt.NoPen)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        p.fillPath(path, QColor(0, 122, 255, fill_alpha))

        # 2. Glowing accent border
        border_alpha = int(220 * self._alpha)
        pen = QPen(QColor(0, 122, 255, border_alpha), 2.5)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(rect, radius, radius)
        
        p.end()


class ControlHighlighter:
    """Helper to pulse-highlight any control widget."""
    @staticmethod
    def pulse(target_widget: QWidget):
        if not target_widget or not target_widget.isVisible():
            return None
        window = target_widget.window()
        overlay = PulseOverlay(target_widget, parent=window)
        overlay.show()
        overlay.raise_()
        return overlay
