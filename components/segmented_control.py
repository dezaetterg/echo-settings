from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QEasingCurve, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QFont, QPen
from theme.colors import Colors
from theme.manager import ThemeManager

class SegmentedControl(QWidget):
    valueChanged = Signal(str)

    def __init__(self, options: list[tuple[str, str]], active_id: str):
        super().__init__()
        self.options = options  # [(id, label), ...]
        self.active_id = active_id
        
        self.setFixedHeight(34)
        
        # Calculate dynamic minimum width based on label text
        from PySide6.QtGui import QFontMetrics, QFont
        font = QFont()
        font.setPixelSize(12)
        font.setBold(True)
        fm = QFontMetrics(font)
        max_w = max([fm.horizontalAdvance(lbl) for _, lbl in self.options], default=60)
        calc_min_w = max(280, int((max_w + 28) * len(self.options)))
        self.setMinimumWidth(calc_min_w)
        self.setCursor(Qt.PointingHandCursor)
        
        self.active_index = 0
        for i, (opt_id, _) in enumerate(self.options):
            if opt_id == active_id:
                self.active_index = i
                break

        # Animation state for the sliding pill
        self._pill_pos = float(self.active_index)
        self.anim = QPropertyAnimation(self, b"pill_pos")
        self.anim.setDuration(200) # Soft 200ms animation
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.setMouseTracking(True)
        self.hover_index = -1
        
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def update_style(self, _is_dark=False):
        self.update()

    @Property(float)
    def pill_pos(self):
        return self._pill_pos

    @pill_pos.setter
    def pill_pos(self, val):
        self._pill_pos = val
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item_width = self.width() / len(self.options)
            index = int(event.position().x() // item_width)
            if 0 <= index < len(self.options):
                self.set_active_index(index)
            event.accept()
        else:
            super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        item_width = self.width() / len(self.options)
        index = int(event.position().x() // item_width)
        if index != self.hover_index and 0 <= index < len(self.options):
            self.hover_index = index
            self.update()
        super().mouseMoveEvent(event)
        
    def leaveEvent(self, event):
        self.hover_index = -1
        self.update()
        super().leaveEvent(event)

    def set_active_index(self, index, emit_signal=True):
        if 0 <= index < len(self.options):
            self.active_index = index
            self.active_id = self.options[index][0]
            self.anim.stop()
            self.anim.setStartValue(self._pill_pos)
            self.anim.setEndValue(float(index))
            self.anim.start()
            if emit_signal:
                self.valueChanged.emit(self.active_id)

    def set_active_id(self, active_id, emit_signal=True):
        for i, (opt_id, _) in enumerate(self.options):
            if opt_id == active_id:
                self.set_active_index(i, emit_signal)
                break

    def set_value(self, active_id, emit_signal=False):
        self.set_active_id(active_id, emit_signal)

    def set_options(self, options: list[tuple[str, str]]):
        self.options = options
        for i, (opt_id, _) in enumerate(self.options):
            if opt_id == self.active_id:
                self.active_index = i
                break
        self.update()

    def set_segments(self, options: list[tuple[str, str]]):
        self.set_options(options)


    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        
        # 1. Draw outer background (light gray container)
        # MacOS Segmented Control bg is very subtle
        is_dark = ThemeManager.is_dark
        bg_color = QColor(0, 0, 0, 30) if not is_dark else QColor(255, 255, 255, 20)
        path = QPainterPath()
        radius = 9 # Roughly matching 14-16px container requirement (radius ~ 9-12)
        path.addRoundedRect(QRectF(rect), radius, radius)
        p.fillPath(path, bg_color)
        
        # Inner shadow simulation (optional but looks good)
        p.setPen(QPen(QColor(0, 0, 0, 20), 1))
        p.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        if not self.options:
            return

        item_width = rect.width() / len(self.options)
        padding = 3
        pill_radius = radius - 2
        
        # 2. Draw hover effect if not on selected
        if self.hover_index != -1 and self.hover_index != self.active_index:
            hover_rect = QRectF(self.hover_index * item_width + padding, padding, item_width - padding*2, rect.height() - padding*2)
            h_path = QPainterPath()
            h_path.addRoundedRect(hover_rect, pill_radius, pill_radius)
            p.fillPath(h_path, QColor(0, 0, 0, 15) if not is_dark else QColor(255, 255, 255, 15))

        # 3. Draw sliding active pill
        pill_rect = QRectF(self._pill_pos * item_width + padding, padding, item_width - padding*2, rect.height() - padding*2)
        pill_path = QPainterPath()
        pill_path.addRoundedRect(pill_rect, pill_radius, pill_radius)
        
        # Pill shadow
        p.setPen(Qt.NoPen)
        shadow_rect = pill_rect.translated(0, 1)
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(shadow_rect, pill_radius, pill_radius)
        p.fillPath(shadow_path, QColor(0, 0, 0, 35 if not is_dark else 70)) # Soft shadow
        
        # Pill color (White selected segment)
        pill_color = QColor(255, 255, 255) if not is_dark else QColor(80, 80, 80)
        p.fillPath(pill_path, pill_color)
        
        # Pill border
        p.setPen(QPen(QColor(0, 0, 0, 10 if not is_dark else 40), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(pill_rect, pill_radius, pill_radius)

        # 4. Draw text
        font = p.font()
        font.setPixelSize(11)
        
        for i, (_, label) in enumerate(self.options):
            text_rect = QRectF(i * item_width, 0, item_width, rect.height())
            
            is_active = (i == self.active_index)
            font.setBold(is_active)
            p.setFont(font)
            
            p.setPen(QColor(Colors.TEXT_PRIMARY))
            p.drawText(text_rect, Qt.AlignCenter, label)
