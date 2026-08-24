from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QDialog
from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QEasingCurve, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QConicalGradient, QImage
from theme.colors import Colors
from theme.manager import ThemeManager

class ColorButton(QPushButton):
    def __init__(self, color_hex, color_name, is_selected=False):
        super().__init__()
        self.color_hex = color_hex
        self.color_name = color_name
        self.setFixedSize(28, 28)
        self.setCursor(Qt.PointingHandCursor)
        self.is_selected = is_selected
        
        self._scale = 1.08 if is_selected else 1.0
        self._active_alpha = 1.0 if is_selected else 0.0
        
        self.hover_anim = QPropertyAnimation(self, b"scale_factor")
        self.hover_anim.setDuration(180)
        self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.active_anim = QPropertyAnimation(self, b"active_alpha")
        self.active_anim.setDuration(180)
        self.active_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
        """)

    @Property(float)
    def scale_factor(self): return self._scale
    @scale_factor.setter
    def scale_factor(self, s):
        self._scale = s
        self.update()
        
    @Property(float)
    def active_alpha(self): return self._active_alpha
    @active_alpha.setter
    def active_alpha(self, a):
        self._active_alpha = a
        self.update()

    def enterEvent(self, event):
        if not self.is_selected:
            self.hover_anim.setDirection(QPropertyAnimation.Forward)
            self.hover_anim.setStartValue(self._scale)
            self.hover_anim.setEndValue(1.08)
            self.hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setDirection(QPropertyAnimation.Forward)
        self.hover_anim.setStartValue(self._scale)
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()
        super().leaveEvent(event)

    def set_selected(self, selected):
        if self.is_selected == selected:
            return
            
        self.is_selected = selected
        
        self.hover_anim.stop()
        self.hover_anim.setDirection(QPropertyAnimation.Forward)
        self.hover_anim.setStartValue(self._scale)
        self.hover_anim.setEndValue(1.1 if selected else 1.0)
        self.hover_anim.start()
        
        self.active_anim.stop()
        self.active_anim.setDirection(QPropertyAnimation.Forward)
        self.active_anim.setStartValue(self._active_alpha)
        self.active_anim.setEndValue(1.0 if selected else 0.0)
        self.active_anim.start()
        
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setClipRect(self.rect())
        
        target_scale = self._scale
            
        center = QPointF(self.width() / 2.0, self.height() / 2.0)
        painter.translate(center)
        painter.scale(target_scale, target_scale)
        painter.translate(-center)
        
        circle_size = 20
        c_rect = QRectF(center.x() - circle_size/2, center.y() - circle_size/2, circle_size, circle_size)
        
        if self.color_name == "multicolor":
            grad = QConicalGradient(c_rect.center(), 0)
            grad.setColorAt(0.0, QColor("#FF3B30"))
            grad.setColorAt(0.16, QColor("#FF9500"))
            grad.setColorAt(0.33, QColor("#FFCC00"))
            grad.setColorAt(0.5, QColor("#34C759"))
            grad.setColorAt(0.66, QColor("#007AFF"))
            grad.setColorAt(0.83, QColor("#AF52DE"))
            grad.setColorAt(1.0, QColor("#FF3B30"))
            painter.setBrush(grad)
        else:
            painter.setBrush(QColor(self.color_hex))
            
        # Draw border for very light colors
        painter.setPen(Qt.NoPen)
        if self.color_name != "multicolor" and QColor(self.color_hex).name().lower() == "#ffffff":
            painter.setPen(QPen(QColor(0,0,0, 30), 1))
            
        painter.drawEllipse(c_rect)
            
        if self._active_alpha > 0:
            icon_color = QColor(255, 255, 255)
            icon_color.setAlphaF(self._active_alpha)
            
            if self.color_name != "multicolor" and QColor(self.color_hex).name().lower() == "#ffffff":
                icon_color = QColor(0, 0, 0)
                icon_color.setAlphaF(self._active_alpha)
                
            painter.translate(center)
            painter.scale(self._active_alpha, self._active_alpha)
            painter.translate(-center)
            
            painter.setPen(QPen(icon_color, 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
            cx = center.x()
            cy = center.y()
            
            painter.drawLine(cx - 3.5, cy + 0.5, cx - 1, cy + 3)
            painter.drawLine(cx - 1, cy + 3, cx + 4, cy - 2.5)
            
            painter.translate(center)
            painter.scale(1.0/self._active_alpha if self._active_alpha > 0 else 1.0, 1.0/self._active_alpha if self._active_alpha > 0 else 1.0)
            painter.translate(-center)
            
        painter.resetTransform()
        painter.end()

class ColorPicker(QWidget):
    color_changed = Signal(str)

    def __init__(self, colors_dict, initial_color):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(7)
        
        self.buttons = []
        for name, hex_code in colors_dict.items():
            btn = ColorButton(hex_code, name, is_selected=(name == initial_color))
            btn.clicked.connect(lambda checked=False, b=btn: self._on_color_clicked(b))
            self.layout.addWidget(btn)
            self.buttons.append(btn)
            
        self.layout.addStretch()

    def _closest_gnome_color(self, hex_color):
        from PySide6.QtGui import QColor
        # Must use exact GNOME accent-color enum values
        gnome_colors = {
            'blue':   '#007AFF',
            'teal':   '#5AC8FA',
            'green':  '#28CD41',
            'yellow': '#FFCC00',
            'orange': '#FF9500',
            'red':    '#FF3B30',
            'pink':   '#FF2D55',
            'purple': '#AF52DE',
            'slate':  '#8E8E93',
        }
        
        target = QColor(hex_color)
        best_name = 'blue'
        min_dist = float('inf')
        
        for name, hex_code in gnome_colors.items():
            c = QColor(hex_code)
            dist = (target.red()-c.red())**2 + (target.green()-c.green())**2 + (target.blue()-c.blue())**2
            if dist < min_dist:
                min_dist = dist
                best_name = name
                
        return best_name

    def _on_color_clicked(self, clicked_btn):
        if clicked_btn.color_name == "multicolor":
            dialog = MinimalColorPicker(self)
            
            def on_color(hex_code):
                closest_name = self._closest_gnome_color(hex_code)
                for btn in self.buttons:
                    btn.set_selected(btn.color_name == closest_name)
                self.color_changed.emit(closest_name)
                
            dialog.color_selected.connect(on_color)
            
            # Position it below the button
            pos = clicked_btn.mapToGlobal(clicked_btn.rect().bottomLeft())
            dialog.move(pos.x(), pos.y() + 8)
            dialog.exec()
            return

        for btn in self.buttons:
            btn.set_selected(btn == clicked_btn)
        self.color_changed.emit(clicked_btn.color_name)

class WheelWidget(QWidget):
    colorChanged = Signal(str)
    
    SIZE = 140
    RADIUS = 60
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setCursor(Qt.CrossCursor)
        self.current_color = QColor("#007AFF")
        self.current_pos = QPointF(self.SIZE / 2, self.SIZE / 2)
        self._wheel_image = self._build_wheel_image()

    def _build_wheel_image(self):
        """
        Paint an HSV colour wheel into a QImage pixel-by-pixel.
        Hue = angle, Saturation = distance-from-center, Value = 1.
        Alpha is blended smoothly at the edge (1-pixel anti-alias).
        """
        import math
        size = self.SIZE
        r = self.RADIUS
        cx = cy = size / 2.0

        img = QImage(size, size, QImage.Format_ARGB32)
        img.fill(Qt.transparent)

        for y in range(size):
            for x in range(size):
                dx = x - cx
                dy = y - cy
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > r + 1:
                    continue
                angle = math.degrees(math.atan2(dy, dx))
                if angle < 0:
                    angle += 360
                hue = angle / 360.0
                sat = min(dist / r, 1.0)
                c = QColor()
                c.setHsvF(hue, sat, 1.0)
                # Smooth alpha fade in the last 1px near the edge
                if dist > r - 1:
                    alpha = max(0.0, r - dist + 1)  # goes 1→0
                    c.setAlphaF(alpha)
                img.setPixelColor(x, y, c)

        return img

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawImage(0, 0, self._wheel_image)
        
        # Selection indicator
        painter.setPen(QPen(QColor(255, 255, 255), 2.5))
        painter.setBrush(self.current_color)
        painter.drawEllipse(self.current_pos, 6, 6)
        painter.end()

    def _update_color(self, pos):
        import math
        cx = cy = self.SIZE / 2.0
        dx = pos.x() - cx
        dy = pos.y() - cy
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > self.RADIUS:
            dx = dx / dist * self.RADIUS
            dy = dy / dist * self.RADIUS
            dist = self.RADIUS

        self.current_pos = QPointF(cx + dx, cy + dy)

        # Sample DIRECTLY from the wheel image — always matches visual
        px = int(round(cx + dx))
        py = int(round(cy + dy))
        px = max(0, min(self.SIZE - 1, px))
        py = max(0, min(self.SIZE - 1, py))
        self.current_color = QColor(self._wheel_image.pixel(px, py))
        self.colorChanged.emit(self.current_color.name())
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._update_color(event.position())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self._update_color(event.position())

class MinimalColorPicker(QDialog):
    color_selected = Signal(str)
    
    def __init__(self, parent=None):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QWidget
        from PySide6.QtCore import Qt
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        container = QWidget()
        container.setObjectName("container")
        self.layout.addWidget(container)
        
        v_lay = QVBoxLayout(container)
        v_lay.setContentsMargins(12, 12, 12, 12)
        v_lay.setSpacing(12)
        
        self.wheel = WheelWidget()
        v_lay.addWidget(self.wheel, 0, Qt.AlignCenter)
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setFixedHeight(28)
        self.apply_btn.setCursor(Qt.PointingHandCursor)
        self.apply_btn.clicked.connect(self._on_apply)
        v_lay.addWidget(self.apply_btn)
        
        # Track selected
        self.selected_hex = self.wheel.current_color.name()
        self.wheel.colorChanged.connect(self._on_color_changed)
        
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)
        
    def _on_color_changed(self, hex_code):
        self.selected_hex = hex_code
        self.update_style()
        
    def _on_apply(self):
        self.color_selected.emit(self.selected_hex)
        self.accept()
        
    def update_style(self, _is_dark=False):
        is_dark = ThemeManager.is_dark
        bg_color = Colors.CARD_BG
        border = Colors.CARD_BORDER
        text = Colors.TEXT_PRIMARY
        
        self.setStyleSheet(f"""
            QWidget#container {{
                background-color: {bg_color};
                border: 1px solid {border};
                border-radius: 12px;
            }}
            QPushButton {{
                background-color: {self.selected_hex};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        self.update()
