from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu, QApplication
from PySide6.QtCore import Qt, QPropertyAnimation, Property, QEasingCurve, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QFont, QAction
from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from theme.metrics import CARD_RADIUS

class BaseNetworkCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumHeight(60)
        
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

class SummaryIcon(QWidget):
    def __init__(self, icon_type, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.icon_type = icon_type
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(Colors.TEXT_SECONDARY)
        p.setPen(QPen(color, 1.5))
        p.setBrush(Qt.NoBrush)
        
        cx, cy = self.width()/2, self.height()/2
        if self.icon_type == 'Active Connection':
            p.drawEllipse(cx-6, cy-6, 12, 12)
            p.drawEllipse(cx-2, cy-2, 4, 4)
        elif self.icon_type == 'Local IPv4':
            p.drawRect(cx-7, cy-5, 14, 10)
            p.drawLine(cx-3, cy+5, cx-3, cy+7)
            p.drawLine(cx+3, cy+5, cx+3, cy+7)
            p.drawLine(cx-5, cy+7, cx+5, cy+7)
        elif self.icon_type == 'Internet Status':
            p.drawArc(cx-8, cy-2, 16, 16, 45*16, 90*16)
            p.drawArc(cx-5, cy+1, 10, 10, 45*16, 90*16)
            p.setBrush(color)
            p.drawEllipse(cx-1, cy+5, 2, 2)
        elif self.icon_type == 'VPN Status':
            p.drawRoundedRect(cx-5, cy-2, 10, 7, 2, 2)
            p.drawArc(cx-3, cy-6, 6, 8, 0, 180*16)

class NetworkSummaryCard(BaseNetworkCard):
    def __init__(self, status: dict, parent=None):
        super().__init__(parent)
        from localization import t
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 28, 24, 28)
        layout.setSpacing(20)
        
        title = QLabel(t("network.summary", "Network Summary"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_TITLE}px; font-weight: {Typography.WEIGHT_SEMIBOLD};")
        layout.addWidget(title)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(16)
        
        self._add_row(info_layout, "Active Connection", t("network.active_conn", "Active Connection"), status.get("active_connection", "None"))
        self._add_row(info_layout, "Local IPv4", t("network.local_ip", "Local IPv4"), status.get("local_ip", "Unavailable"))
        
        internet = status.get("internet", "Unknown")
        int_color = Colors.ACCENT_BLUE if internet == "Full" else Colors.TEXT_PRIMARY
        self._add_row(info_layout, "Internet Status", t("network.internet_status", "Internet Status"), internet, val_color=int_color)
        
        is_vpn = status.get("vpn_active", False)
        vpn = t("network.connected", "Connected") if is_vpn else t("network.not_connected", "Not Connected")
        vpn_color = Colors.ACCENT_BLUE if is_vpn else Colors.TEXT_PRIMARY
        self._add_row(info_layout, "VPN Status", t("network.vpn_status", "VPN Status"), vpn, val_color=vpn_color)
        
        layout.addLayout(info_layout)
        
    def _add_row(self, layout, icon_type, label_text, val_text, val_color=None):
        if val_color is None:
            val_color = Colors.TEXT_PRIMARY
        row = QHBoxLayout()
        row.setSpacing(12)
        
        icon = SummaryIcon(icon_type)
        row.addWidget(icon)
        
        lbl = QLabel(label_text.upper())
        lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_SMALL}px; font-weight: {Typography.WEIGHT_SEMIBOLD}; letter-spacing: 0.5px;")
        
        val = QLabel(val_text)
        val.setStyleSheet(f"color: {val_color}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_NORMAL};")
        val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        layout.addLayout(row)

class GearButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.setCursor(Qt.PointingHandCursor)
        self._hover_alpha = 0.0
        self.anim = QPropertyAnimation(self, b"hover_alpha")
        self.anim.setDuration(150)

    @Property(float)
    def hover_alpha(self):
        return self._hover_alpha
        
    @hover_alpha.setter
    def hover_alpha(self, v):
        self._hover_alpha = v
        self.update()

    def enterEvent(self, event):
        self.anim.setDirection(QPropertyAnimation.Forward)
        self.anim.setStartValue(self._hover_alpha)
        self.anim.setEndValue(1.0)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.setDirection(QPropertyAnimation.Backward)
        self.anim.setStartValue(self._hover_alpha)
        self.anim.setEndValue(0.0)
        self.anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        if self._hover_alpha > 0:
            bg_c = QColor(128, 128, 128, int(30 * self._hover_alpha))
            p.setBrush(bg_c)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(self.rect(), 8, 8)
            
        color = QColor(Colors.TEXT_SECONDARY)
        if self._hover_alpha > 0:
            color = QColor(Colors.TEXT_PRIMARY)
            
        p.setPen(QPen(color, 1.5))
        p.setBrush(Qt.NoBrush)
        
        cx, cy = self.rect().center().x(), self.rect().center().y()
        
        # Apply slight scale on hover for micro-interaction
        scale = 1.0 + (0.05 * self._hover_alpha)
        if self.isDown(): scale = 0.95
        p.translate(cx, cy)
        p.scale(scale, scale)
        p.translate(-cx, -cy)
        
        p.drawEllipse(cx-4, cy-4, 8, 8)
        p.setPen(QPen(color, 1.5, Qt.DashLine))
        p.drawEllipse(cx-6, cy-6, 12, 12)

class IconWidget(QWidget):
    def __init__(self, icon_type, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.icon_type = icon_type
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(Colors.TEXT_PRIMARY)
        p.setPen(QPen(color, 1.5))
        p.setBrush(Qt.NoBrush)
        
        cx, cy = self.width()/2, self.height()/2
        
        if self.icon_type == 'ethernet':
            p.drawRect(cx-9, cy-7, 18, 12)
            p.drawLine(cx-4, cy+5, cx-4, cy+10)
            p.drawLine(cx+4, cy+5, cx+4, cy+10)
            p.drawLine(cx-7, cy+10, cx+7, cy+10)
        elif self.icon_type == 'wifi':
            p.drawArc(cx-12, cy-5, 24, 24, 45*16, 90*16)
            p.drawArc(cx-8, cy-1, 16, 16, 45*16, 90*16)
            p.drawArc(cx-4, cy+3, 8, 8, 45*16, 90*16)
            p.setBrush(color)
            p.drawEllipse(cx-2, cy+7, 4, 4)
        else:
            p.drawRoundedRect(cx-7, cy-2, 14, 9, 2, 2)
            p.drawArc(cx-5, cy-8, 10, 12, 0, 180*16)

class InterfaceCard(BaseNetworkCard):
    details_clicked = Signal(str, str) # interface, name

    def __init__(self, interface: str, name: str, active: bool, ipv4: str, speed: str, icon_type: str, mac: str = "Unavailable", parent=None):
        super().__init__(parent)
        self.interface = interface
        self.name = name
        self.ipv4 = ipv4
        self.mac = mac
        self.setCursor(Qt.PointingHandCursor)
        
        self._hover_alpha = 0.0
        self.hover_anim = QPropertyAnimation(self, b"hover_alpha")
        self.hover_anim.setDuration(150)
        self.hover_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)
        
        # Icon
        layout.addWidget(IconWidget(icon_type))
        
        # Middle text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        text_layout.setAlignment(Qt.AlignVCenter)
        
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_TITLE}px; font-weight: {Typography.WEIGHT_MEDIUM};")
        text_layout.addWidget(name_lbl)
        
        nic_type = icon_type.title() if icon_type else "Connection"
        info_str = f"IPv4 • {ipv4}"
        if speed != "Unavailable":
            info_str += f"   {speed} {nic_type}"
            
        info_lbl = QLabel(info_str)
        info_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px; font-weight: 400;")
        text_layout.addWidget(info_lbl)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Right Side (Status + Gear)
        right_layout = QHBoxLayout()
        right_layout.setSpacing(12)
        
        # Green/Gray dot + Status
        status_layout = QHBoxLayout()
        status_layout.setSpacing(6)
        
        class DotWidget(QWidget):
            def __init__(self, active):
                super().__init__()
                self.setFixedSize(8, 8)
                self.active = active
            def paintEvent(self, e):
                p = QPainter(self)
                p.setRenderHint(QPainter.Antialiasing)
                p.setPen(Qt.NoPen)
                color = QColor(Colors.SWITCH_ON) if self.active else QColor(Colors.TEXT_SECONDARY)
                if not self.active: color.setAlpha(100)
                p.setBrush(color)
                p.drawEllipse(self.rect())
                
        if active:
            status_layout.addWidget(DotWidget(active))
            
        status_text = QLabel("Connected" if active else "Not Connected")
        s_col = Colors.SWITCH_ON if active else Colors.TEXT_SECONDARY
        status_text.setStyleSheet(f"color: {s_col}; font-size: {Typography.SIZE_SECONDARY}px; font-weight: {Typography.WEIGHT_NORMAL};")
        status_layout.addWidget(status_text)
        
        right_layout.addLayout(status_layout)
        
        gear = GearButton()
        gear.clicked.connect(lambda checked=False: self.details_clicked.emit(self.interface, self.name))
        right_layout.addWidget(gear)
        
        layout.addLayout(right_layout)
        
    def _show_context_menu(self, pos):
        menu = QMenu(self)
        
        # Styling macOS like menu
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {Colors.WINDOW_BG};
                border: 1px solid {Colors.CARD_BORDER};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.SIZE_BODY}px;
            }}
            QMenu::item:selected {{
                background-color: {Colors.ACCENT_BLUE};
                color: white;
            }}
            QMenu::item:disabled {{
                color: {Colors.TEXT_SECONDARY};
            }}
        """)
        
        copy_ip = QAction("Copy IP Address", self)
        if self.ipv4 == "Unavailable":
            copy_ip.setEnabled(False)
        else:
            copy_ip.triggered.connect(lambda: QApplication.clipboard().setText(self.ipv4))
        menu.addAction(copy_ip)
        
        copy_mac = QAction("Copy MAC Address", self)
        if self.mac == "Unavailable":
            copy_mac.setEnabled(False)
        else:
            copy_mac.triggered.connect(lambda: QApplication.clipboard().setText(self.mac))
        menu.addAction(copy_mac)
        
        menu.addSeparator()
        
        open_details = QAction("Open Connection Details...", self)
        open_details.triggered.connect(lambda: self.details_clicked.emit(self.interface, self.name))
        menu.addAction(open_details)
        
        renew_dhcp = QAction("Renew DHCP Lease", self)
        renew_dhcp.setEnabled(False)
        menu.addAction(renew_dhcp)
        
        menu.exec_(self.mapToGlobal(pos))
        
    @Property(float)
    def hover_alpha(self):
        return self._hover_alpha
        
    @hover_alpha.setter
    def hover_alpha(self, alpha):
        self._hover_alpha = alpha
        self.update()
        
    def enterEvent(self, event):
        self.hover_anim.setDirection(QPropertyAnimation.Forward)
        self.hover_anim.setStartValue(self._hover_alpha)
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.hover_anim.setDirection(QPropertyAnimation.Backward)
        self.hover_anim.setStartValue(self._hover_alpha)
        self.hover_anim.setEndValue(0.0)
        self.hover_anim.start()
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        # Only hover shadow and bg, no scaling for macOS authenticity
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Soft shadow
        is_dark = ThemeManager.is_dark
        shadow_color = QColor(0, 0, 0, 40 if is_dark else 15)
        if self._hover_alpha > 0:
            shadow_color = QColor(0, 0, 0, int(40 + 15 * self._hover_alpha) if is_dark else int(15 + 10 * self._hover_alpha))
            
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(2, 4, -2, -2), CARD_RADIUS, CARD_RADIUS)
        p.fillPath(path, shadow_color)
        
        # Background
        bg_color = QColor(Colors.CARD_BG)
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect().adjusted(0, 0, 0, -4), CARD_RADIUS, CARD_RADIUS)
        p.fillPath(bg_path, bg_color)
        
        # Border
        border_color = QColor(Colors.CARD_BORDER)
        border_color.setAlpha(30 if is_dark else 50)
        p.setPen(QPen(border_color, 1))
        p.drawPath(bg_path)
        
        # Hover Overlay
        if self._hover_alpha > 0:
            hover_color = QColor(255, 255, 255, int(15 * self._hover_alpha)) if is_dark else QColor(0, 0, 0, int(8 * self._hover_alpha))
            p.fillPath(bg_path, hover_color)
