from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen
from theme.colors import Colors
from theme.manager import ThemeManager
from theme.metrics import CARD_RADIUS
from theme.glass_shimmer import GlassShimmerHelper

class OutputHeroCard(QWidget):
    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self.shimmer = GlassShimmerHelper(self)
        self.setMinimumHeight(120)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 24, 30, 24)
        main_layout.setSpacing(24)
        
        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(72, 72)
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setStyleSheet(f"background-color: {Colors.ACCENT_BLUE}; color: white; font-size: 32px; border-radius: 36px;")
        main_layout.addWidget(self.icon_lbl)
        
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignVCenter)
        info_layout.setSpacing(4)
        
        self.title_lbl = QLabel("Unknown Device")
        self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: bold;")
        
        self.subtitle_lbl = QLabel("Connection • Status")
        self.subtitle_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        
        info_layout.addWidget(self.title_lbl)
        info_layout.addWidget(self.subtitle_lbl)
        main_layout.addLayout(info_layout)
        
        ThemeManager.theme_changed.connect(self.update_style)

    def enterEvent(self, event):
        self.shimmer.handle_enter(event)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shimmer.handle_leave(event)
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        self.shimmer.handle_mouse_move(event)
        super().mouseMoveEvent(event)
        
    def update_style(self, _=False):
        self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: bold;")
        self.subtitle_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        self.update()

    def update_info(self, info, default_name):
        if info:
            name = info.get("Name", default_name)
            self.title_lbl.setText(name)
            conn = info.get("Connection", "")
            state = info.get("State", "")
            self.subtitle_lbl.setText(f"{conn}  •  {state}")
            
            if "Bluetooth" in conn:
                icon_text = "🎧" 
            elif "HDMI" in conn:
                icon_text = "📺"
            elif "USB" in conn:
                icon_text = "🔌"
            else:
                icon_text = "🔊"
                
            self.icon_lbl.setText(icon_text)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        is_dark = ThemeManager.is_dark
        shadow_color = QColor(0, 0, 0, 40 if is_dark else 15)
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(2, 4, -2, -2), CARD_RADIUS, CARD_RADIUS)
        painter.fillPath(path, shadow_color)
        
        bg_color = QColor(Colors.CARD_BG)
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect().adjusted(0, 0, 0, -4), CARD_RADIUS, CARD_RADIUS)
        painter.fillPath(bg_path, bg_color)
        
        border_color = QColor(Colors.CARD_BORDER)
        border_color.setAlpha(30 if is_dark else 50)
        painter.setPen(QPen(border_color, 1))
        painter.drawPath(bg_path)

        # Dynamic specular edge sheen and ambient surface spotlight
        self.shimmer.paint_shimmer(painter, QRectF(self.rect().adjusted(0, 0, 0, -4)), CARD_RADIUS, is_dark)
