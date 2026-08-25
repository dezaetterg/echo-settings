from PySide6.QtCore import Qt, QObject, QPointF, Property, QPropertyAnimation, QEasingCurve, QRectF, QEvent
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QPainterPath, QCursor
from PySide6.QtWidgets import QWidget

class GlassShimmerHelper(QObject):
    """
    Adds interactive optical refraction / specular light sheen and ambient surface spotlight
    along cards and widgets, dynamically tracking cursor position seamlessly across all child elements.
    """
    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)
        self.widget = parent_widget
        self._hover_pos = QPointF(-100, -100)
        self._hover_opacity = 0.0
        self._is_hovered = False

        self.anim = QPropertyAnimation(self, b"hover_opacity")
        self.anim.setDuration(220)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

        if self.widget:
            self.widget.setMouseTracking(True)
            self._install_recursive(self.widget)

    def _install_recursive(self, w: QWidget):
        if not w:
            return
        w.setMouseTracking(True)
        w.installEventFilter(self)
        for child in w.findChildren(QWidget):
            child.setMouseTracking(True)
            child.installEventFilter(self)

    @Property(float)
    def hover_opacity(self):
        return self._hover_opacity

    @hover_opacity.setter
    def hover_opacity(self, val):
        self._hover_opacity = val
        if self.widget:
            self.widget.update()

    def _extract_pos(self, event=None) -> QPointF:
        if self.widget:
            # mapFromGlobal is always authoritative and continuous across child boundaries
            return QPointF(self.widget.mapFromGlobal(QCursor.pos()))
        if event is not None:
            if hasattr(event, "position"):
                return event.position()
            elif hasattr(event, "pos"):
                return QPointF(event.pos())
        return QPointF(0, 0)

    def _start_fade(self, target: float):
        self._is_hovered = (target > 0.5)
        self.anim.stop()
        self.anim.setStartValue(self._hover_opacity)
        self.anim.setEndValue(target)
        self.anim.start()

    def handle_enter(self, event=None):
        self._hover_pos = self._extract_pos(event)
        self._start_fade(1.0)

    def handle_leave(self, event=None):
        if self.widget:
            cur_pos = self.widget.mapFromGlobal(QCursor.pos())
            if self.widget.rect().contains(cur_pos):
                # Mouse is still inside card boundaries (e.g. over a child widget)
                return
        self._start_fade(0.0)

    def handle_mouse_move(self, event=None):
        self._hover_pos = self._extract_pos(event)
        if self._hover_opacity > 0 and self.widget:
            self.widget.update()

    def eventFilter(self, watched, event):
        etype = event.type()
        if etype in (QEvent.MouseMove, QEvent.HoverMove):
            if self.widget and self.widget.isVisible():
                cur_pos = self.widget.mapFromGlobal(QCursor.pos())
                if self.widget.rect().contains(cur_pos):
                    self._hover_pos = QPointF(cur_pos)
                    if not self._is_hovered or self._hover_opacity < 0.99:
                        self._start_fade(1.0)
                    else:
                        self.widget.update()
                else:
                    if self._is_hovered or self._hover_opacity > 0.01:
                        self._start_fade(0.0)

        elif etype == QEvent.Enter:
            if self.widget and self.widget.isVisible():
                cur_pos = self.widget.mapFromGlobal(QCursor.pos())
                if self.widget.rect().contains(cur_pos):
                    self._hover_pos = QPointF(cur_pos)
                    self._start_fade(1.0)

        elif etype == QEvent.Leave:
            if self.widget and self.widget.isVisible():
                cur_pos = self.widget.mapFromGlobal(QCursor.pos())
                if not self.widget.rect().contains(cur_pos):
                    self._start_fade(0.0)

        elif etype == QEvent.ChildAdded:
            child = getattr(event, "child", lambda: None)()
            if child and isinstance(child, QWidget):
                self._install_recursive(child)

        return super().eventFilter(watched, event)

    def paint_shimmer(self, painter: QPainter, rect: QRectF, radius: float = 12.0, is_dark: bool = True):
        if self._hover_opacity <= 0.01:
            return

        # Ensure fresh mouse coordinates whenever rendering
        if self.widget:
            cur_pos = self.widget.mapFromGlobal(QCursor.pos())
            if rect.contains(QPointF(cur_pos)):
                self._hover_pos = QPointF(cur_pos)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        cx = self._hover_pos.x()
        cy = self._hover_pos.y()

        # 1. Subtle Surface Ambient Spotlight (Illuminates the center / body of the card)
        surface_radius = max(160.0, rect.width() * 0.48, rect.height() * 0.95)
        surface_grad = QRadialGradient(cx, cy, surface_radius)

        if is_dark:
            # Delicate physical ambient glow in dark mode
            surface_grad.setColorAt(0.0, QColor(255, 255, 255, int(24 * self._hover_opacity)))
            surface_grad.setColorAt(0.35, QColor(170, 215, 255, int(11 * self._hover_opacity)))
            surface_grad.setColorAt(0.7, QColor(110, 170, 255, int(3 * self._hover_opacity)))
            surface_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        else:
            # Crisp luminous sheen in light mode
            surface_grad.setColorAt(0.0, QColor(255, 255, 255, int(130 * self._hover_opacity)))
            surface_grad.setColorAt(0.35, QColor(240, 248, 255, int(55 * self._hover_opacity)))
            surface_grad.setColorAt(0.7, QColor(210, 230, 255, int(15 * self._hover_opacity)))
            surface_grad.setColorAt(1.0, QColor(255, 255, 255, 0))

        painter.setPen(Qt.NoPen)
        painter.setBrush(surface_grad)
        painter.drawPath(path)

        # 2. Specular Glass Edge Refraction (Illuminates the 1px/1.2px card perimeter)
        shimmer_radius = max(110.0, rect.width() * 0.42)
        edge_grad = QRadialGradient(cx, cy, shimmer_radius)

        if is_dark:
            edge_grad.setColorAt(0.0, QColor(255, 255, 255, int(160 * self._hover_opacity)))
            edge_grad.setColorAt(0.3, QColor(170, 220, 255, int(80 * self._hover_opacity)))
            edge_grad.setColorAt(0.7, QColor(110, 180, 255, int(20 * self._hover_opacity)))
            edge_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        else:
            edge_grad.setColorAt(0.0, QColor(255, 255, 255, int(240 * self._hover_opacity)))
            edge_grad.setColorAt(0.35, QColor(210, 235, 255, int(110 * self._hover_opacity)))
            edge_grad.setColorAt(0.75, QColor(160, 210, 255, int(30 * self._hover_opacity)))
            edge_grad.setColorAt(1.0, QColor(255, 255, 255, 0))

        edge_pen = QPen(edge_grad, 1.2)
        painter.setPen(edge_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        painter.restore()
