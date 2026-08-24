import os
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QEasingCurve, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QLinearGradient, QPen, QFont
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from theme.colors import Colors
from theme.typography import Typography

class ThemePreviewCard(QWidget):
    clicked = Signal()

    def __init__(self, title: str, is_dark: bool = False, is_auto: bool = False, is_selected: bool = False):
        super().__init__()
        self.setFixedSize(140, 115)
        self.setCursor(Qt.PointingHandCursor)
        self.title = title
        self.is_dark = is_dark
        self.is_auto = is_auto
        self.is_selected = is_selected
        self.accent_color = QColor(Colors.ACCENT_BLUE)
        self._scale = 1.0
        self._active_alpha = 1.0 if is_selected else 0.0

        self.hover_anim = QPropertyAnimation(self, b"scale_factor")
        self.hover_anim.setDuration(180)
        self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Add shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(12)
        self.shadow.setColor(QColor(0, 0, 0, 12)) # Permanent soft shadow
        self.shadow.setOffset(0, 3)
        self.setGraphicsEffect(self.shadow)
        
        self.shadow_anim = QPropertyAnimation(self.shadow, b"color")
        self.shadow_anim.setDuration(180)
        
        self.active_anim = QPropertyAnimation(self, b"active_alpha")
        self.active_anim.setDuration(180)
        self.active_anim.setEasingCurve(QEasingCurve.OutCubic)

    def set_selected(self, selected: bool):
        if self.is_selected == selected:
            return
        self.is_selected = selected
        
        self.active_anim.stop()
        self.active_anim.setDirection(QPropertyAnimation.Forward)
        self.active_anim.setStartValue(self._active_alpha)
        self.active_anim.setEndValue(1.0 if selected else 0.0)
        self.active_anim.start()
        self.update()

    @Property(float)
    def scale_factor(self):
        return self._scale

    @scale_factor.setter
    def scale_factor(self, s):
        self._scale = s
        self.update()
        
    @Property(float)
    def active_alpha(self):
        return self._active_alpha
        
    @active_alpha.setter
    def active_alpha(self, a):
        self._active_alpha = a
        self.update()

    def enterEvent(self, event):
        if not self.is_selected:
            self.hover_anim.setDirection(QPropertyAnimation.Forward)
            self.hover_anim.setStartValue(self._scale)
            self.hover_anim.setEndValue(1.03)
            self.hover_anim.start()
            
            self.shadow_anim.setDirection(QPropertyAnimation.Forward)
            self.shadow_anim.setStartValue(QColor(0, 0, 0, 12))
            self.shadow_anim.setEndValue(QColor(0, 0, 0, 40))
            self.shadow_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_anim.setDirection(QPropertyAnimation.Backward)
        self.hover_anim.setStartValue(self._scale)
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()
        
        self.shadow_anim.setDirection(QPropertyAnimation.Backward)
        self.shadow_anim.setStartValue(QColor(0, 0, 0, 12))
        self.shadow_anim.setEndValue(QColor(0, 0, 0, 40))
        self.shadow_anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            event.accept()
        else:
            super().mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        
        # Base rect for the image area (centered)
        card_rect = QRectF(10, 6, self.width() - 20, self.height() - 34)
        
        # Scale logic for hover
        center = card_rect.center()
        p.translate(center)
        p.scale(self._scale, self._scale)
        p.translate(-center)

        # 1. Draw rounded card preview
        path = QPainterPath()
        path.addRoundedRect(card_rect, 8, 8)
        p.setClipPath(path)
        
        # Background
        if self.is_auto:
            grad = QLinearGradient(card_rect.topLeft(), card_rect.bottomRight())
            grad.setColorAt(0.0, QColor("#8E44AD"))
            grad.setColorAt(0.5, QColor("#3498DB"))
            grad.setColorAt(0.51, QColor("#2C3E50"))
            p.fillPath(path, grad)
        else:
            # Tahoe default wallpaper colors
            grad = QLinearGradient(card_rect.topLeft(), card_rect.bottomRight())
            if self.is_dark:
                grad.setColorAt(0.0, QColor("#002244"))
                grad.setColorAt(1.0, QColor("#004488"))
            else:
                grad.setColorAt(0.0, QColor("#007AFF"))
                grad.setColorAt(1.0, QColor("#66CCFF"))
            p.fillPath(path, grad)
            
        # Draw Mini Windows
        def draw_window(r: QRectF, dark: bool):
            actual_r = QRectF(card_rect.x() + r.x(), card_rect.y() + r.y(), r.width(), r.height())
            win_path = QPainterPath()
            win_path.addRoundedRect(actual_r, 5, 5)
            
            # Content bg
            win_color = QColor(30, 30, 30, 240) if dark else QColor(255, 255, 255, 240)
            p.fillPath(win_path, win_color)
            
            # Sidebar
            sidebar_rect = QRectF(actual_r.x(), actual_r.y(), actual_r.width() * 0.3, actual_r.height())
            sidebar_path = QPainterPath()
            sidebar_path.addRoundedRect(sidebar_rect, 5, 5)
            # Flatten right side of sidebar
            p.fillPath(sidebar_path, QColor(40, 40, 40, 220) if dark else QColor(240, 240, 240, 220))
            
            # Traffic light buttons
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#FF5F56") if not dark else QColor(80,80,80))
            p.drawEllipse(QRectF(actual_r.x() + 4, actual_r.y() + 4, 3, 3))
            p.setBrush(QColor("#FFBD2E") if not dark else QColor(80,80,80))
            p.drawEllipse(QRectF(actual_r.x() + 9, actual_r.y() + 4, 3, 3))
            p.setBrush(QColor("#27C93F") if not dark else QColor(80,80,80))
            p.drawEllipse(QRectF(actual_r.x() + 14, actual_r.y() + 4, 3, 3))
            
            # Border
            p.setPen(QPen(QColor(0,0,0, 40), 1))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(actual_r, 5, 5)

        if self.is_auto:
            draw_window(QRectF(10, 8, 50, 32), False)
            draw_window(QRectF(35, 20, 68, 42), True)
        else:
            draw_window(QRectF(10, 8, 50, 32), self.is_dark)
            draw_window(QRectF(35, 20, 68, 42), self.is_dark)
            
        # Draw Dock
        dock_w = 48
        dock_h = 5
        dock_rect = QRectF(card_rect.x() + (card_rect.width() - dock_w)/2, card_rect.bottom() - 8, dock_w, dock_h)
        dock_path = QPainterPath()
        dock_path.addRoundedRect(dock_rect, dock_h/2, dock_h/2)
        p.fillPath(dock_path, QColor(255, 255, 255, 120))
        
        p.setClipping(False)
        
        # Draw card border & selection
        # Base border
        p.setPen(QPen(QColor(0, 0, 0, 35), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(card_rect, 8, 8)
        
        if self._active_alpha > 0:
            active_color = QColor(Colors.ACCENT_BLUE)
            active_color.setAlphaF(self._active_alpha)
            p.setPen(QPen(active_color, 2.5))
            p.drawRoundedRect(card_rect, 8, 8)
            
            # Draw checkmark badge inside card bottom right
            badge_r = 8
            badge_rect = QRectF(card_rect.right() - badge_r*2 - 3, card_rect.bottom() - badge_r*2 - 3, badge_r*2, badge_r*2)
            
            # Animate checkmark scale and opacity
            p.translate(badge_rect.center())
            p.scale(self._active_alpha, self._active_alpha)
            p.translate(-badge_rect.center())
            
            p.setPen(Qt.NoPen)
            p.setBrush(active_color)
            p.drawEllipse(badge_rect)
            
            # Checkmark
            icon_color = QColor(255, 255, 255)
            icon_color.setAlphaF(self._active_alpha)
            p.setPen(QPen(icon_color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawLine(badge_rect.x() + 4.5, badge_rect.y() + 8, badge_rect.x() + 7, badge_rect.y() + 10.5)
            p.drawLine(badge_rect.x() + 7, badge_rect.y() + 10.5, badge_rect.x() + 11.5, badge_rect.y() + 5.5)
            
            p.translate(badge_rect.center())
            p.scale(1.0/self._active_alpha if self._active_alpha > 0 else 1.0, 1.0/self._active_alpha if self._active_alpha > 0 else 1.0)
            p.translate(-badge_rect.center())

        p.resetTransform()

        # Draw Title below the card
        p.setPen(QColor(Colors.TEXT_PRIMARY))
        font = p.font()
        font.setPixelSize(12)
        from PySide6.QtGui import QFont
        font.setWeight(QFont.Weight(Typography.WEIGHT_MEDIUM))
        p.setFont(font)
        
        title_rect = QRectF(0, self.height() - 24, self.width(), 20)
        p.drawText(title_rect, Qt.AlignCenter, self.title)
        
        p.end()
