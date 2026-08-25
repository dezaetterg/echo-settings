from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from theme.colors import Colors
from theme.typography import Typography
from theme.metrics import CARD_RADIUS
from theme.manager import ThemeManager
from theme.glass_shimmer import GlassShimmerHelper

class SettingsGroup(QWidget):
    """A white/dark rounded card to group settings rows. Identical in style to ModularCard."""
    def __init__(self, title=None):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self.shimmer = GlassShimmerHelper(self)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        if title:
            self.title_lbl = QLabel(title)
            self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_TITLE}px; font-weight: {Typography.WEIGHT_SEMIBOLD}; letter-spacing: {Typography.LETTER_SPACING_HEADER}px; padding: 16px 20px 8px 20px;")
            self.layout.addWidget(self.title_lbl)
            
    def add_row(self, row_widget):
        self.layout.addWidget(row_widget)
        if hasattr(self, 'shimmer') and self.shimmer:
            self.shimmer._install_recursive(row_widget)

    def enterEvent(self, event):
        self.shimmer.handle_enter(event)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shimmer.handle_leave(event)
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        self.shimmer.handle_mouse_move(event)
        super().mouseMoveEvent(event)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        is_dark = ThemeManager.is_dark
        
        # Exact same shadow as ModularCard
        shadow_alpha = 40 if is_dark else 15
        shadow_color = QColor(0, 0, 0, shadow_alpha)
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(2, 4, -2, -2), CARD_RADIUS, CARD_RADIUS)
        p.fillPath(path, shadow_color)
        
        # Background
        bg_color = QColor(Colors.CARD_BG)
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect(), CARD_RADIUS, CARD_RADIUS)
        p.fillPath(bg_path, bg_color)
        
        # Border
        border_color = QColor(Colors.CARD_BORDER)
        border_color.setAlpha(30 if is_dark else 50)
        p.setPen(QPen(border_color, 1))
        p.drawPath(bg_path)

        # Dynamic specular edge sheen and ambient surface spotlight
        self.shimmer.paint_shimmer(p, QRectF(self.rect()), CARD_RADIUS, is_dark)
