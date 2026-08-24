from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QRectF, QPointF, QPropertyAnimation, QEasingCurve, Property, QObject, Signal
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QFont
from models.monitor import MonitorModel
from theme.colors import Colors
from theme.manager import ThemeManager

class MonitorItem(QObject):
    def __init__(self, model: MonitorModel, parent=None):
        super().__init__(parent)
        self.model = model
        self._rect = QRectF()
        self.is_dragging = False

    def get_rect(self): return self._rect
    def set_rect(self, rect): 
        self._rect = rect
        if self.parent():
            self.parent().update()
            
    rect = Property(QRectF, get_rect, set_rect)


class MonitorArrangementWidget(QWidget):
    arrangement_changed = Signal(dict)

    def __init__(self, monitors: list[MonitorModel], parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.setMinimumWidth(400)
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.monitors = monitors
        self.items = []
        self.scale_factor = 1.0
        self.center_offset = QPointF(0, 0)
        
        self.drag_item = None
        self.drag_offset = QPointF(0, 0)
        
        self.animations = []
        
        self.setMouseTracking(True)
        self._init_layout()

    def _init_layout(self):
        if not self.monitors: return
        
        # Calculate bounding box of real physical space
        min_x = min(m.x for m in self.monitors)
        min_y = min(m.y for m in self.monitors)
        max_x = max(m.x + m.width for m in self.monitors)
        max_y = max(m.y + m.height for m in self.monitors)
        
        total_w = max_x - min_x
        total_h = max_y - min_y
        
        if total_w == 0 or total_h == 0:
            total_w, total_h = 1920, 1080
            
        # Target widget size (approx)
        target_w = 400
        target_h = 200
        
        scale_x = target_w / total_w
        scale_y = target_h / total_h
        self.scale_factor = min(scale_x, scale_y) * 0.8 # 80% to leave padding
        
        # Center offset
        self.center_offset = QPointF(
            (self.width() - (total_w * self.scale_factor)) / 2,
            (self.height() - (total_h * self.scale_factor)) / 2
        )
        
        for m in self.monitors:
            item = MonitorItem(m, self)
            w = m.width * self.scale_factor
            h = m.height * self.scale_factor
            x = (m.x - min_x) * self.scale_factor
            y = (m.y - min_y) * self.scale_factor
            item.set_rect(QRectF(x, y, w, h))
            self.items.append(item)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Recenter on resize
        if not self.items: return
        total_w = max(i.rect.right() for i in self.items) - min(i.rect.left() for i in self.items)
        total_h = max(i.rect.bottom() for i in self.items) - min(i.rect.top() for i in self.items)
        self.center_offset = QPointF(
            (self.width() - total_w) / 2,
            (self.height() - total_h) / 2
        )

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        is_dark = ThemeManager.is_dark
        bg_color = QColor(40, 40, 40) if is_dark else QColor(240, 240, 240)
        p.fillRect(self.rect(), bg_color)
        
        # Grid lines (optional, for macOS feeling)
        
        p.translate(self.center_offset)
        
        for item in self.items:
            path = QPainterPath()
            path.addRoundedRect(item.rect, 8, 8)
            
            # Shadow
            p.fillPath(path, QColor(0, 0, 0, 40))
            
            # Fill
            fill_col = QColor(Colors.ACCENT_BLUE) if item.model.is_primary else QColor(80, 80, 80)
            if item.is_dragging:
                fill_col.setAlpha(200)
            p.fillPath(path, fill_col)
            
            # Border
            p.setPen(QPen(QColor(0, 0, 0, 100), 1))
            p.drawPath(path)
            
            # macOS Menubar indicator
            if item.model.is_primary:
                bar_rect = QRectF(item.rect.x(), item.rect.y(), item.rect.width(), 12)
                bar_path = QPainterPath()
                bar_path.addRoundedRect(bar_rect, 8, 8)
                # Clip bottom to make it flat
                bar_clip = QRectF(item.rect.x(), item.rect.y(), item.rect.width(), 12)
                p.fillPath(bar_path, QColor(255, 255, 255, 200))
            
            # Label
            p.setPen(QColor(255, 255, 255))
            font = QFont("Inter", 10, QFont.Bold)
            p.setFont(font)
            p.drawText(item.rect, Qt.AlignCenter, str(self.items.index(item) + 1))

    def mousePressEvent(self, event):
        if len(self.items) <= 1: return
        pos = event.position() - self.center_offset
        
        for item in reversed(self.items):
            if item.rect.contains(pos):
                self.drag_item = item
                self.drag_item.is_dragging = True
                self.drag_offset = pos - item.rect.topLeft()
                
                # Bring to front
                self.items.remove(item)
                self.items.append(item)
                break
        self.update()

    def mouseMoveEvent(self, event):
        if self.drag_item:
            pos = event.position() - self.center_offset
            new_rect = QRectF(self.drag_item.rect)
            new_rect.moveTopLeft(pos - self.drag_offset)
            self.drag_item.set_rect(new_rect)
            self.update()

    def mouseReleaseEvent(self, event):
        if not self.drag_item: return
        
        # Implement snap logic
        snapped = False
        snap_threshold = 20
        target_rect = QRectF(self.drag_item.rect)
        
        # Very basic snap: if close to another rect, snap to it
        for target in self.items:
            if target == self.drag_item: continue
            
            dx = abs(self.drag_item.rect.center().x() - target.rect.center().x())
            dy = abs(self.drag_item.rect.center().y() - target.rect.center().y())
            
            # Mirror snap (auto-mirroring if overlapping)
            if dx < snap_threshold and dy < snap_threshold:
                target_rect.moveCenter(target.rect.center())
                snapped = True
                break
                
            # Edge snaps (Left/Right)
            if abs(self.drag_item.rect.right() - target.rect.left()) < snap_threshold:
                target_rect.moveRight(target.rect.left())
                if abs(self.drag_item.rect.top() - target.rect.top()) < snap_threshold:
                    target_rect.moveTop(target.rect.top())
                snapped = True
                break
            
        # Animate to target
        self.drag_item.is_dragging = False
        
        anim = QPropertyAnimation(self.drag_item, b"rect", self)
        anim.setDuration(250)
        anim.setStartValue(self.drag_item.rect)
        anim.setEndValue(target_rect)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        
        def on_anim_finished():
            self._emit_arrangement()
            
        anim.finished.connect(on_anim_finished)
        anim.start()
        
        self.animations.append(anim)
        self.drag_item = None

    def _emit_arrangement(self):
        # Calculate bounding box of items to normalize back to (0,0)
        min_x = min(item.rect.x() for item in self.items)
        min_y = min(item.rect.y() for item in self.items)
        
        positions = {}
        for item in self.items:
            # Map back to real coordinates
            real_x = int(round((item.rect.x() - min_x) / self.scale_factor))
            real_y = int(round((item.rect.y() - min_y) / self.scale_factor))
            
            # Snap to grid of 10 for safety
            real_x = round(real_x / 10) * 10
            real_y = round(real_y / 10) * 10
            
            positions[item.model.id] = {'x': real_x, 'y': real_y}
            
        self.arrangement_changed.emit(positions)
