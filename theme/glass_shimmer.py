from PySide6.QtCore import Qt, QObject, QPointF, Property, QPropertyAnimation, QEasingCurve, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QPainterPath

class GlassShimmerHelper(QObject):
    """
    Adds interactive optical refraction / specular light sheen along the 1px border
    of glass widgets, dynamically tracking cursor position.
    """
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.widget = parent_widget
        self._hover_pos = QPointF(-100, -100)
        self._hover_opacity = 0.0

        self.anim = QPropertyAnimation(self, b"hover_opacity")
        self.anim.setDuration(220)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    @Property(float)
    def hover_opacity(self):
        return self._hover_opacity

    @hover_opacity.setter
    def hover_opacity(self, val):
        self._hover_opacity = val
        self.widget.update()

    def _extract_pos(self, event):
        if hasattr(event, "position"):
            return event.position()
        elif hasattr(event, "pos"):
            return QPointF(event.pos())
        return QPointF(0, 0)

    def handle_enter(self, event):
        self._hover_pos = self._extract_pos(event)
        self.anim.stop()
        self.anim.setStartValue(self._hover_opacity)
        self.anim.setEndValue(1.0)
        self.anim.start()

    def handle_leave(self, event):
        self.anim.stop()
        self.anim.setStartValue(self._hover_opacity)
        self.anim.setEndValue(0.0)
        self.anim.start()

    def handle_mouse_move(self, event):
        self._hover_pos = self._extract_pos(event)
        if self._hover_opacity > 0:
            self.widget.update()

    def paint_shimmer(self, painter: QPainter, rect: QRectF, radius: float = 12.0, is_dark: bool = True):
        if self._hover_opacity <= 0.01:
            return

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Base delicate border
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        # 2. Dynamic Specular Sheen centered at cursor position
        cx = self._hover_pos.x()
        cy = self._hover_pos.y()
        shimmer_radius = max(80.0, rect.width() * 0.45)

        grad = QRadialGradient(cx, cy, shimmer_radius)
        if is_dark:
            sheen_color = QColor(255, 255, 255, int(120 * self._hover_opacity))
            mid_color = QColor(140, 200, 255, int(40 * self._hover_opacity))
        else:
            sheen_color = QColor(255, 255, 255, int(200 * self._hover_opacity))
            mid_color = QColor(0, 122, 255, int(45 * self._hover_opacity))

        grad.setColorAt(0.0, sheen_color)
        grad.setColorAt(0.5, mid_color)
        grad.setColorAt(1.0, QColor(255, 255, 255, 0))

        shimmer_pen = QPen(grad, 1.2)
        painter.setPen(shimmer_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        painter.restore()
