from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QScrollArea, 
    QStackedWidget, QPushButton, QGraphicsOpacityEffect, QGridLayout
)
from PySide6.QtCore import Qt, QPropertyAnimation, Property, QEasingCurve, Signal, QTimer, QRectF, QThread
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QConicalGradient

from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from theme.styler import fix_label_styles
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from components.switch import Switch
from services.wifi_service import WiFiService
from pages.network_details import NetworkDetailsPage

CARD_RADIUS = 12

# ─── Painted Icons ───────────────────────────────────────────────

class WiFiSignalIcon(QWidget):
    """Paints concentric Wi-Fi arcs proportional to signal strength."""
    def __init__(self, signal: int = 0, size: int = 16, parent=None):
        super().__init__(parent)
        self.signal = signal
        self.setFixedSize(size, size)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(Colors.TEXT_PRIMARY)
        dim_color = QColor(Colors.TEXT_SECONDARY)
        dim_color.setAlpha(60)
        
        w, h = self.width(), self.height()
        cx, cy = w / 2, h * 0.85
        
        # Number of bars to fill (0-3)
        bars = 0
        if self.signal >= 75: bars = 3
        elif self.signal >= 50: bars = 2
        elif self.signal >= 25: bars = 1
        
        pen_width = max(1.5, w / 10)
        
        # Draw 3 arcs (outer to inner)
        for i in range(3):
            radius = w * (0.85 - i * 0.25)
            rect = QRectF(cx - radius / 2, cy - radius / 2, radius, radius)
            arc_color = color if (2 - i) < bars else dim_color
            p.setPen(QPen(arc_color, pen_width, Qt.SolidLine, Qt.RoundCap))
            p.setBrush(Qt.NoBrush)
            p.drawArc(rect, 45 * 16, 90 * 16)
        
        # Bottom dot
        dot_r = max(1.5, w / 8)
        dot_color = color if bars > 0 else dim_color
        p.setPen(Qt.NoPen)
        p.setBrush(dot_color)
        p.drawEllipse(QRectF(cx - dot_r, cy - dot_r, dot_r * 2, dot_r * 2))
        p.end()

class LockIcon(QWidget):
    """Simple padlock icon."""
    def __init__(self, size: int = 14, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(Colors.TEXT_SECONDARY)
        w, h = self.width(), self.height()
        
        # Shackle (arc at top)
        p.setPen(QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        shackle_rect = QRectF(w * 0.25, h * 0.05, w * 0.5, h * 0.5)
        p.drawArc(shackle_rect, 0, 180 * 16)
        
        # Body (rounded rect)
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        body = QRectF(w * 0.15, h * 0.4, w * 0.7, h * 0.55)
        p.drawRoundedRect(body, 2, 2)
        p.end()

class InfoCircleButton(QPushButton):
    """Painted (i) button, consistent across fonts."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 22)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")
        self._hovered = False
        
    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(Colors.ACCENT_BLUE) if not self._hovered else QColor(Colors.TEXT_PRIMARY)
        
        w, h = self.width(), self.height()
        # Circle
        p.setPen(QPen(color, 1.2))
        p.setBrush(Qt.NoBrush)
        margin = 2
        p.drawEllipse(QRectF(margin, margin, w - margin * 2, h - margin * 2))
        
        # "i" letter
        p.setPen(QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap))
        cx = w / 2
        # dot
        p.drawPoint(int(cx), int(h * 0.33))
        # stem
        p.drawLine(int(cx), int(h * 0.45), int(cx), int(h * 0.72))
        p.end()

class ChevronLabel(QLabel):
    """A simple "›" rendered in the secondary text color."""
    def __init__(self, parent=None):
        super().__init__("›", parent)
        self.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_TITLE}px; font-weight: {Typography.WEIGHT_NORMAL};")
        self.setFixedWidth(12)
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

# ─── Cards ───────────────────────────────────────────────────────

class BaseCardWidget(QWidget):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        is_dark = ThemeManager.is_dark
        
        shadow_alpha = 40 if is_dark else 15
        shadow_color = QColor(0, 0, 0, shadow_alpha)
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(2, 4, -2, -2), CARD_RADIUS, CARD_RADIUS)
        p.fillPath(path, shadow_color)
        
        bg_color = QColor(Colors.CARD_BG)
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect().adjusted(0, 0, 0, -4), CARD_RADIUS, CARD_RADIUS)
        p.fillPath(bg_path, bg_color)
        
        border_color = QColor(Colors.CARD_BORDER)
        border_color.setAlpha(30 if is_dark else 50)
        p.setPen(QPen(border_color, 1))
        p.drawPath(bg_path)

class WiFiTopCard(BaseCardWidget):
    def __init__(self, is_enabled: bool, switch_callback, active_net, details, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 28)
        layout.setSpacing(20)
        
        # Header: title + switch
        from localization import t
        top_layout = QHBoxLayout()
        title = QLabel(t("nav.wifi", "Wi-Fi"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_SEMIBOLD}; letter-spacing: -0.5px;")
        
        self.switch = Switch(checked=is_enabled)
        self.switch.toggled.connect(switch_callback)
        
        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(self.switch)
        layout.addLayout(top_layout)
        
        if is_enabled and active_net:
            ssid = active_net['ssid']
            sig = active_net['signal']
            
            # SSID row with Wi-Fi icon
            ssid_layout = QHBoxLayout()
            ssid_layout.setSpacing(10)
            
            wifi_icon = WiFiSignalIcon(signal=sig, size=22)
            ssid_layout.addWidget(wifi_icon)
            
            net_title = QLabel(ssid)
            net_title.setStyleSheet(f"color: {Colors.ACCENT_BLUE}; font-size: 22px; font-weight: {Typography.WEIGHT_SEMIBOLD};")
            ssid_layout.addWidget(net_title)
            ssid_layout.addStretch()
            layout.addLayout(ssid_layout)
            
            sub_lbl = QLabel(f"Connected • Signal: {sig}%")
            sub_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_TITLE}px; font-weight: {Typography.WEIGHT_MEDIUM};")
            layout.addWidget(sub_lbl)
            
            # Subtle separator
            sep = QWidget()
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background-color: {Colors.CARD_BORDER}; max-height: 1px;")
            layout.addWidget(sep)
            
            # Detail grid with breathing room
            grid = QGridLayout()
            grid.setSpacing(16)
            grid.setContentsMargins(0, 6, 0, 0)
            
            def add_item(r, c, k, v):
                lbl_k = QLabel(k)
                lbl_k.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_SMALL}px; font-weight: {Typography.WEIGHT_SEMIBOLD}; letter-spacing: 0.5px;")
                lbl_v = QLabel(v)
                lbl_v.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_BODY}px;")
                w = QWidget()
                l = QVBoxLayout(w)
                l.setContentsMargins(0,0,0,0)
                l.setSpacing(3)
                l.addWidget(lbl_k)
                l.addWidget(lbl_v)
                grid.addWidget(w, r, c)
                
            ip = details.ipv4 if details else "—"
            mac = details.mac_address if details else "—"
            spd = details.link_speed if details else "—"
            sec = active_net['security'] or "Open"
            
            add_item(0, 0, "IP ADDRESS", ip)
            add_item(0, 1, "MAC ADDRESS", mac)
            add_item(1, 0, "LINK SPEED", spd)
            add_item(1, 1, "SECURITY", sec)
            
            layout.addLayout(grid)
        elif not is_enabled:
            lbl = QLabel("Wi-Fi is turned off. Turn it on to scan for networks.")
            lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px;")
            layout.addWidget(lbl)
        else:
            lbl = QLabel("Not connected to any network.")
            lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px;")
            layout.addWidget(lbl)

# ─── Network Row ─────────────────────────────────────────────────

class NetworkRow(QWidget):
    details_clicked = Signal(str)

    def __init__(self, ssid, security, signal, active, show_separator=True):
        super().__init__()
        self.ssid = ssid
        self.show_separator = show_separator
        self.setMinimumHeight(52)
        self.setCursor(Qt.PointingHandCursor)
        
        self._hover_alpha = 0.0
        self.hover_anim = QPropertyAnimation(self, b"hover_alpha")
        self.hover_anim.setDuration(150)
        self.hover_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignVCenter)
        
        # Wi-Fi signal icon
        wifi_icon = WiFiSignalIcon(signal=signal, size=16)
        layout.addWidget(wifi_icon)
        
        # SSID
        name_label = QLabel(ssid)
        name_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_MEDIUM};")
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # Lock icon (painted)
        if security != "":
            lock = LockIcon(size=14)
            layout.addWidget(lock)
            
        # Info button (painted)
        info_btn = InfoCircleButton()
        info_btn.clicked.connect(lambda: self.details_clicked.emit(self.ssid))
        layout.addWidget(info_btn)
        
    @Property(float)
    def hover_alpha(self):
        return self._hover_alpha
        
    @hover_alpha.setter
    def hover_alpha(self, alpha):
        self._hover_alpha = alpha
        self.update()
        
    def enterEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setDirection(QPropertyAnimation.Forward)
        self.hover_anim.setStartValue(self._hover_alpha)
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setDirection(QPropertyAnimation.Forward)
        self.hover_anim.setStartValue(self._hover_alpha)
        self.hover_anim.setEndValue(0.0)
        self.hover_anim.start()
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self._hover_alpha > 0:
            hover_color = QColor(255, 255, 255, int(15 * self._hover_alpha)) if ThemeManager.is_dark else QColor(0, 0, 0, int(10 * self._hover_alpha))
            path = QPainterPath()
            path.addRoundedRect(self.rect().adjusted(4, 2, -4, -2), 8, 8)
            painter.fillPath(path, hover_color)
            
        if self.show_separator:
            sep_color = QColor(Colors.CARD_BORDER)
            sep_color.setAlpha(120 if ThemeManager.is_dark else 80) 
            painter.setPen(QPen(sep_color, 1))
            painter.drawLine(16, self.height() - 1, self.width(), self.height() - 1)

# ─── Empty State ─────────────────────────────────────────────────

class EmptyStateWidget(QWidget):
    rescan_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(280)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        
        # Painted Wi-Fi icon instead of emoji
        icon = WiFiSignalIcon(signal=0, size=64)
        
        title = QLabel("No Networks Available")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_TITLE}px; font-weight: {Typography.WEIGHT_SEMIBOLD};")
        title.setAlignment(Qt.AlignCenter)
        
        desc = QLabel("Make sure you are in range of a Wi-Fi network.")
        desc.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px;")
        desc.setAlignment(Qt.AlignCenter)
        
        btn = QPushButton("Retry Search")
        btn.setFixedSize(140, 36)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_BLUE};
                color: white;
                border-radius: 8px;
                font-size: {Typography.SIZE_BODY}px;
                font-weight: {Typography.WEIGHT_MEDIUM};
            }}
            QPushButton:hover {{
                background-color: #0066CC;
            }}
        """)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.rescan_requested.emit)
        
        layout.addWidget(icon, 0, Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(btn, 0, Qt.AlignCenter)

# ─── Main WiFi List Page ─────────────────────────────────────────

class WiFiScanThread(QThread):
    networks_ready = Signal(list, object)

    def __init__(self, service: WiFiService, parent=None):
        super().__init__(parent)
        self.service = service

    def run(self):
        try:
            nets = self.service.get_networks()
            active_net = next((n for n in nets if n.get('active')), None)
            details = None
            if active_net:
                try:
                    details = self.service.get_network_details(active_net['ssid'])
                except Exception:
                    details = None
        except Exception:
            nets = []
            details = None
        self.networks_ready.emit(nets, details)


class WiFiListPage(QWidget):
    details_requested = Signal(str)
    
    def __init__(self, service: WiFiService):
        super().__init__()
        self.service = service
        self.is_wifi_on = self.service.is_enabled()
        self._scan_thread = None
        self._cached_networks = []
        self._cached_details = None
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 30, 40, 40)
        self.layout.setSpacing(24)
        self.layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(scroll)
        
        self.entrance_anim_group = []
        self.refresh_networks()
        ThemeManager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, _is_dark=False):
        fix_label_styles(self)
        if self._cached_networks:
            self._display_networks(self._cached_networks, self._cached_details)
        else:
            self.refresh_networks()
        
    def on_wifi_toggled(self, state):
        self.service.set_enabled(state)
        self.is_wifi_on = state
        self._cached_networks = []
        self._cached_details = None
        self.refresh_networks()
        
    def refresh_networks(self):
        self.entrance_anim_group.clear()
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if not self.is_wifi_on:
            top_card = WiFiTopCard(False, self.on_wifi_toggled, None, None)
            self.layout.addWidget(top_card)
            self.layout.addStretch()
            return
            
        if self._cached_networks:
            self._display_networks(self._cached_networks, self._cached_details)
        else:
            top_card = WiFiTopCard(True, self.on_wifi_toggled, None, None)
            self.layout.addWidget(top_card)
            self.layout.addStretch()

        if self._scan_thread and self._scan_thread.isRunning():
            return
        self._scan_thread = WiFiScanThread(self.service, self)
        self._scan_thread.networks_ready.connect(self._on_scan_finished)
        self._scan_thread.start()

    def _on_scan_finished(self, networks, details):
        self._cached_networks = networks
        self._cached_details = details
        self._display_networks(networks, details)

    def _display_networks(self, networks, details=None):
        self.entrance_anim_group.clear()
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.animated_widgets = []
                
        active_net = next((n for n in networks if n.get('active')), None)
        other_networks = [n for n in networks if not n.get('active')]
        
        if details is None and active_net:
            details = getattr(self, '_cached_details', None)
            
        top_card = WiFiTopCard(self.is_wifi_on, self.on_wifi_toggled, active_net, details)
        self.layout.addWidget(top_card)
        self.animated_widgets.append(top_card)

        
        if self.is_wifi_on:
            if other_networks:
                lbl_avail = QLabel("OTHER NETWORKS")
                lbl_avail.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_SMALL}px; font-weight: {Typography.WEIGHT_NORMAL}; letter-spacing: 0.5px; margin-left: 8px;")
                self.layout.addWidget(lbl_avail)
                self.animated_widgets.append(lbl_avail)
                
                networks_group = SettingsGroup()
                for i, net in enumerate(other_networks):
                    show_sep = i < len(other_networks) - 1
                    row = NetworkRow(net['ssid'], net['security'], net['signal'], False, show_sep)
                    row.details_clicked.connect(self.details_requested.emit)
                    networks_group.layout.addWidget(row)
                self.layout.addWidget(networks_group)
                self.animated_widgets.append(networks_group)
            elif not active_net:
                empty = EmptyStateWidget()
                empty.rescan_requested.connect(self.refresh_networks)
                self.layout.addWidget(empty)
                self.animated_widgets.append(empty)
                
            # Quick Actions — only "Scan for Networks" is functional
            qa_group = SettingsGroup()
            
            scan_row = SettingsRow("Scan for Networks", ChevronLabel(), show_separator=True)
            scan_row.setCursor(Qt.PointingHandCursor)
            scan_row.mousePressEvent = lambda e: self.refresh_networks()
            qa_group.add_row(scan_row)
            
            hidden_row = SettingsRow("Join Hidden Network...", ChevronLabel(), show_separator=False)
            qa_group.add_row(hidden_row)
            
            self.layout.addWidget(qa_group)
            self.animated_widgets.append(qa_group)
            
        self.layout.addStretch()
        
        # Entrance animations
        delay = 0
        for w in self.animated_widgets:
            eff = QGraphicsOpacityEffect(w)
            eff.setOpacity(0.0)
            w.setGraphicsEffect(eff)
            
            anim = QPropertyAnimation(eff, b"opacity")
            anim.setDuration(300)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            
            QTimer.singleShot(delay, anim.start)
            self.entrance_anim_group.append(anim)
            delay += 40

    def cleanup(self):
        if self._scan_thread and self._scan_thread.isRunning():
            self._scan_thread.quit()
            self._scan_thread.wait(500)

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)

class WiFiPage(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.service = WiFiService()
        
        self.list_page = WiFiListPage(self.service)
        self.list_page.details_requested.connect(self.show_details)
        
        self.addWidget(self.list_page)
        self.current_details_page = None
        
    def show_details(self, ssid):
        details = self.service.get_network_details(ssid)
        if self.current_details_page:
            self.removeWidget(self.current_details_page)
            self.current_details_page.deleteLater()
            
        self.current_details_page = NetworkDetailsPage(details, parent_page_name="Wi-Fi")
        self.current_details_page.back_requested.connect(self.show_list)
        self.addWidget(self.current_details_page)
        self.setCurrentWidget(self.current_details_page)
        
    def show_list(self):
        self.setCurrentWidget(self.list_page)

    def reset_to_root(self):
        self.show_list()

    def showEvent(self, event):
        super().showEvent(event)
        self.show_list()

    def cleanup(self):
        if hasattr(self, 'list_page'):
            self.list_page.cleanup()

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)

    def get_search_target(self, target_id: str) -> QWidget | None:
        self.setCurrentWidget(self.list_page)
        targets = {
            "wifi.toggle": getattr(self.list_page, "top_card", None),
            "wifi.networks": getattr(self.list_page, "top_card", None),
        }
        return targets.get(target_id)

