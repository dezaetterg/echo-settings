from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu, QApplication
from PySide6.QtCore import Qt, QPropertyAnimation, Property, QEasingCurve, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QFont, QAction
from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from theme.metrics import CARD_RADIUS
from theme.glass_shimmer import GlassShimmerHelper

class BaseNetworkCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self.shimmer = GlassShimmerHelper(self)
        self.setMinimumHeight(60)

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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Soft shadow
        is_dark = ThemeManager.is_dark
        shadow_color = QColor(0, 0, 0, 40 if is_dark else 15)
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(2, 4, -2, -2), CARD_RADIUS, CARD_RADIUS)
        painter.fillPath(path, shadow_color)
        
        # Background
        bg_color = QColor(Colors.CARD_BG)
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect().adjusted(0, 0, 0, -4), CARD_RADIUS, CARD_RADIUS)
        painter.fillPath(bg_path, bg_color)
        
        # Border
        border_color = QColor(Colors.CARD_BORDER)
        border_color.setAlpha(30 if is_dark else 50)
        painter.setPen(QPen(border_color, 1))
        painter.drawPath(bg_path)

        # Dynamic specular edge sheen and ambient surface spotlight
        self.shimmer.paint_shimmer(painter, QRectF(self.rect().adjusted(0, 0, 0, -4)), CARD_RADIUS, is_dark)

class SummaryIcon(QWidget):
    def __init__(self, icon_type, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.icon_type = icon_type
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        icon_color = QColor(Colors.TEXT_SECONDARY)
        p.setPen(QPen(icon_color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        
        if self.icon_type == "wifi":
            p.drawArc(2, 4, 16, 16, 45 * 16, 90 * 16)
            p.drawArc(5, 7, 10, 10, 45 * 16, 90 * 16)
            p.drawArc(8, 10, 4, 4, 45 * 16, 90 * 16)
            p.setBrush(icon_color)
            p.drawEllipse(9, 13, 2, 2)
        elif self.icon_type == "ethernet":
            p.drawRoundedRect(3, 4, 14, 12, 2, 2)
            p.drawLine(7, 16, 13, 16)
            p.drawLine(10, 16, 10, 18)
            p.drawLine(6, 8, 8, 8)
            p.drawLine(9, 8, 11, 8)
            p.drawLine(12, 8, 14, 8)

class NetworkSummaryCard(BaseNetworkCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 16, 20, 20)
        self.layout.setSpacing(16)
        
        self.icon_widget = SummaryIcon("wifi", self)
        self.layout.addWidget(self.icon_widget)
        
        from localization import t
        self.status_lbl = QLabel(t("network.connected_wifi", "Connected to Wi-Fi"))
        self.status_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_MEDIUM};")
        self.layout.addWidget(self.status_lbl)
        
        self.layout.addStretch()
        
        ThemeManager.theme_changed.connect(self.update_style)
        
    def update_style(self, _is_dark=False):
        self.status_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_MEDIUM};")
        self.update()
        
    def set_status(self, is_connected: bool, is_wifi: bool = True, network_name: str = ""):
        self.icon_widget.icon_type = "wifi" if is_wifi else "ethernet"
        self.icon_widget.update()
        
        from localization import t
        if is_connected:
            if network_name:
                self.status_lbl.setText(network_name)
            else:
                self.status_lbl.setText(t("network.connected_wifi", "Connected to Wi-Fi") if is_wifi else t("network.connected_eth", "Connected to Ethernet"))
        else:
            self.status_lbl.setText(t("network.not_connected", "Not Connected"))

class GearButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(28, 28)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._hover_alpha = 0.0
        self.anim = QPropertyAnimation(self, b"hover_alpha")
        self.anim.setDuration(120)
        
    @Property(float)
    def hover_alpha(self):
        return self._hover_alpha
        
    @hover_alpha.setter
    def hover_alpha(self, val):
        self._hover_alpha = val
        self.update()
        
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self._hover_alpha)
        self.anim.setEndValue(1.0)
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self._hover_alpha)
        self.anim.setEndValue(0.0)
        self.anim.start()
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        if self._hover_alpha > 0:
            is_dark = ThemeManager.is_dark
            bg = QColor(255, 255, 255, int(25 * self._hover_alpha)) if is_dark else QColor(0, 0, 0, int(15 * self._hover_alpha))
            p.setBrush(bg)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(self.rect(), 6, 6)
            
        icon_color = QColor(Colors.TEXT_SECONDARY)
        p.setPen(QPen(icon_color, 1.3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        r_inner = 3.0
        r_outer = 5.5
        
        p.drawEllipse(QPointF(center_x, center_y), r_inner, r_inner)
        
        import math
        for i in range(6):
            angle = i * (math.pi / 3.0)
            x1 = center_x + math.cos(angle) * (r_inner + 0.5)
            y1 = center_y + math.sin(angle) * (r_inner + 0.5)
            x2 = center_x + math.cos(angle) * r_outer
            y2 = center_y + math.sin(angle) * r_outer
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

class IconWidget(QWidget):
    def __init__(self, is_wifi=True, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.is_wifi = is_wifi
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        bg_color = QColor(Colors.ACCENT_BLUE)
        p.setBrush(bg_color)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 8, 8)
        
        p.setPen(QPen(Qt.white, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        
        if self.is_wifi:
            p.drawArc(10, 12, 16, 16, 45 * 16, 90 * 16)
            p.drawArc(13, 15, 10, 10, 45 * 16, 90 * 16)
            p.drawArc(16, 18, 4, 4, 45 * 16, 90 * 16)
            p.setBrush(Qt.white)
            p.drawEllipse(17, 21, 2, 2)
        else:
            p.drawRoundedRect(11, 12, 14, 12, 2, 2)
            p.drawLine(15, 24, 21, 24)
            p.drawLine(18, 24, 18, 26)
            p.drawLine(14, 16, 16, 16)
            p.drawLine(17, 16, 19, 16)
            p.drawLine(20, 16, 22, 16)

class InterfaceCard(BaseNetworkCard):
    def __init__(self, is_wifi: bool = True, parent=None):
        super().__init__(parent)
        self.is_wifi = is_wifi
        self.menu_actions = []
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 12, 16, 16)
        self.layout.setSpacing(14)
        
        self.icon_widget = IconWidget(is_wifi=self.is_wifi, parent=self)
        self.layout.addWidget(self.icon_widget)
        
        self.info_layout = QVBoxLayout()
        self.info_layout.setSpacing(2)
        self.info_layout.setAlignment(Qt.AlignVCenter)
        
        self.name_lbl = QLabel("Wi-Fi" if is_wifi else "Ethernet")
        self.name_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_MEDIUM};")
        
        self.status_container = QHBoxLayout()
        self.status_container.setSpacing(6)
        self.status_container.setAlignment(Qt.AlignLeft)
        
        class DotWidget(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setFixedSize(8, 8)
                self.color = QColor(Colors.ACCENT_GREEN)
            def paintEvent(self, event):
                p = QPainter(self)
                p.setRenderHint(QPainter.Antialiasing)
                p.setBrush(self.color)
                p.setPen(Qt.NoPen)
                p.drawEllipse(0, 0, 8, 8)
                
        self.dot = DotWidget(self)
        self.status_lbl = QLabel("Connected")
        self.status_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;")
        
        self.status_container.addWidget(self.dot)
        self.status_container.addWidget(self.status_lbl)
        
        self.info_layout.addWidget(self.name_lbl)
        self.info_layout.addLayout(self.status_container)
        
        self.layout.addLayout(self.info_layout)
        self.layout.addStretch()
        
        self.gear_btn = GearButton(self)
        self.gear_btn.clicked.connect(self._show_details_menu)
        self.layout.addWidget(self.gear_btn)
        
        ThemeManager.theme_changed.connect(self.update_style)
        
    def update_style(self, _is_dark=False):
        self.name_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_MEDIUM};")
        self.status_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;")
        self.update()
        
    def set_status(self, is_connected: bool, status_text: str = ""):
        self.dot.color = QColor(Colors.ACCENT_GREEN) if is_connected else QColor(Colors.TEXT_SECONDARY)
        self.dot.update()
        
        from localization import t
        if status_text:
            self.status_lbl.setText(status_text)
        else:
            self.status_lbl.setText(t("network.connected", "Connected") if is_connected else t("network.not_connected", "Not Connected"))
            
    def _show_details_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {Colors.CARD_BG};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.CARD_BORDER};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 16px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {Colors.ACCENT_BLUE};
                color: white;
            }}
        """)
        
        from localization import t
        copy_action = menu.addAction(t("network.copy_ip", "Copy IPv4 Address"))
        details_action = menu.addAction(t("network.details", "Details..."))
        
        copy_action.triggered.connect(self._copy_ip)
        details_action.triggered.connect(self._open_network_settings)
        
        menu.exec(self.gear_btn.mapToGlobal(QPointF(0, self.gear_btn.height()).toPoint()))
        
    def _copy_ip(self):
        import subprocess
        try:
            out = subprocess.check_output(["hostname", "-I"], text=True).strip()
            ip = out.split()[0] if out else "127.0.0.1"
            QApplication.clipboard().setText(ip)
        except Exception:
            pass

    def _open_network_settings(self):
        import subprocess, shutil
        for cmd in ["gnome-control-center wifi", "gnome-control-center network", "cinnamon-settings network", "nm-connection-editor"]:
            binary = cmd.split()[0]
            if shutil.which(binary):
                subprocess.Popen(cmd.split())
                break
