import subprocess
import socket
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QScrollArea, 
    QPushButton, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtSvgWidgets import QSvgWidget

from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from theme.styler import fix_label_styles
from components.settings_group import SettingsGroup
from components.switch import Switch

class BluetoothDeviceRow(QWidget):
    def __init__(self, name, status, icon="bluetooth", connected=False, show_separator=True):
        super().__init__()
        self.setMinimumHeight(64)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show_separator = show_separator
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(16)
        
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(32, 32)
        icon_bg = Colors.ACCENT_BLUE if connected else (Colors.CARD_BORDER if ThemeManager.is_dark else "#E5E5EA")
        icon_lbl.setStyleSheet(f"background-color: {icon_bg}; border-radius: 16px;")
        layout.addWidget(icon_lbl)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.lbl_name = QLabel(name)
        self.lbl_name.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_MEDIUM};")
        
        self.lbl_status = QLabel(status)
        status_color = "#34C759" if connected else Colors.TEXT_SECONDARY
        self.lbl_status.setStyleSheet(f"color: {status_color}; font-size: {Typography.SIZE_SMALL}px;")
        
        text_layout.addWidget(self.lbl_name)
        text_layout.addWidget(self.lbl_status)
        layout.addLayout(text_layout)
        
        layout.addStretch()
        
        self.btn = QPushButton("Disconnect" if connected else "Connect")
        self.btn.setFixedSize(90, 28)
        
        is_dark = ThemeManager.is_dark
        btn_bg = "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.05)"
        btn_hover = "rgba(255, 255, 255, 0.15)" if is_dark else "rgba(0, 0, 0, 0.1)"
        
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_bg};
                color: {Colors.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
            }}
        """)
        layout.addWidget(self.btn)
        
    def paintEvent(self, event):
        if self.show_separator:
            p = QPainter(self)
            sep_color = QColor(Colors.CARD_BORDER)
            sep_color.setAlpha(50 if ThemeManager.is_dark else 40)
            p.setPen(QPen(sep_color, 1))
            p.drawLine(68, self.height() - 1, self.width() - 20, self.height() - 1)

class BluetoothPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("BluetoothPage")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.viewport().setAutoFillBackground(False)
        scroll.setStyleSheet("QScrollArea { background: transparent; } QWidget#scrollContent { background: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scrollContent")
        
        self.layout = QVBoxLayout(self.scroll_content)
        self.layout.setContentsMargins(24, 20, 24, 32)
        self.layout.setSpacing(24)
        self.layout.setAlignment(Qt.AlignTop)
        
        self._build_ui()
        
        scroll.setWidget(self.scroll_content)
        main_layout.addWidget(scroll)
        
        fix_label_styles(self)
        ThemeManager.theme_changed.connect(self._on_theme_changed)

    def check_bluetooth_available(self):
        try:
            out = subprocess.check_output("bluetoothctl show", shell=True, stderr=subprocess.STDOUT, timeout=1).decode()
            if "No default controller available" in out or not out.strip():
                return False
            return True
        except Exception:
            return False

    def get_real_devices(self):
        try:
            out = subprocess.check_output("bluetoothctl devices", shell=True, stderr=subprocess.STDOUT, timeout=2).decode()
            devices = []
            for line in out.split('\\n'):
                if line.startswith("Device "):
                    parts = line.split(" ", 2)
                    if len(parts) == 3:
                        devices.append(parts[2].strip())
            return devices
        except Exception:
            return []

    def _create_section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_SMALL}px; font-weight: {Typography.WEIGHT_SEMIBOLD}; letter-spacing: 0.5px;")
        lbl.setContentsMargins(8, 8, 8, 0)
        return lbl

    def _build_ui(self):
        from localization import t
        # 0. Header Title
        title_hdr = QLabel(t("nav.bluetooth", "Bluetooth"))
        title_hdr.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};")
        self.layout.addWidget(title_hdr)

        has_bt = self.check_bluetooth_available()
        
        # 1. Main Card
        self.main_card = SettingsGroup()
        
        top_row = QWidget()
        top_row.setMinimumHeight(60)
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(20, 12, 20, 12)
        
        text_v = QVBoxLayout()
        text_v.setSpacing(4)
        
        title = QLabel("Bluetooth")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: {Typography.WEIGHT_BOLD};")
        
        try:
            hostname = socket.gethostname()
        except:
            hostname = "PikaOS"
            
        sub = QLabel(f"Discoverable as '{hostname}'" if has_bt else "Bluetooth is unavailable")
        sub.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        
        text_v.addWidget(title)
        text_v.addWidget(sub)
        top_layout.addLayout(text_v)
        top_layout.addStretch()
        
        self.sw_bt = Switch(checked=has_bt)
        self.sw_bt.setEnabled(has_bt)
        self.sw_bt.toggled.connect(self._on_bt_toggled)
        top_layout.addWidget(self.sw_bt)
        
        self.main_card.layout.addWidget(top_row)
        self.layout.addWidget(self.main_card)
        
        if not has_bt:
            self._build_empty_state()
            return
            
        # 2. My Devices (Real Data)
        self.lbl_my_dev = self._create_section_label("MY DEVICES")
        self.layout.addWidget(self.lbl_my_dev)
        
        self.grp_my_dev = SettingsGroup()
        devices = self.get_real_devices()
        
        if devices:
            for i, dev in enumerate(devices):
                is_last = (i == len(devices) - 1)
                self.grp_my_dev.layout.addWidget(BluetoothDeviceRow(dev, "Not Connected", connected=False, show_separator=not is_last))
        else:
            lbl_no_dev = QLabel("No paired devices found")
            lbl_no_dev.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 20px;")
            self.grp_my_dev.layout.addWidget(lbl_no_dev)
            
        self.layout.addWidget(self.grp_my_dev)
        
        # 3. Nearby Devices (Placeholder for future scan)
        self.lbl_nearby = self._create_section_label("NEARBY DEVICES")
        self.layout.addWidget(self.lbl_nearby)
        
        self.grp_nearby = SettingsGroup()
        self.grp_nearby.layout.addWidget(BluetoothDeviceRow("Searching...", "Scanning for devices", connected=False, show_separator=False))
        self.layout.addWidget(self.grp_nearby)
        
    def _build_empty_state(self):
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(12)
        empty_layout.setContentsMargins(0, 80, 0, 0)
        
        svg_str = '''<svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6.5 7.5L17.5 16.5L12 22V2L17.5 7.5L6.5 16.5" stroke="#8E8E93" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        
        icon = QSvgWidget()
        icon.load(svg_str.encode('utf-8'))
        icon.setFixedSize(64, 64)
        op = QGraphicsOpacityEffect()
        op.setOpacity(0.4)
        icon.setGraphicsEffect(op)
        
        lbl_title = QLabel("No Bluetooth Adapter Found")
        lbl_title.setStyleSheet("color: #8E8E93; font-size: 16px; font-weight: bold;")
        
        lbl_desc = QLabel("Connect a Bluetooth dongle or enable Bluetooth in system BIOS.")
        lbl_desc.setStyleSheet("color: #6E6E73; font-size: 13px;")
        
        empty_layout.addWidget(icon, 0, Qt.AlignCenter)
        empty_layout.addWidget(lbl_title, 0, Qt.AlignCenter)
        empty_layout.addWidget(lbl_desc, 0, Qt.AlignCenter)
        
        self.layout.addWidget(empty_widget)

    def _on_bt_toggled(self, is_on):
        if hasattr(self, 'grp_my_dev'):
            self.grp_my_dev.setDisabled(not is_on)
            self.grp_nearby.setDisabled(not is_on)
            op1 = 1.0 if is_on else 0.5
            op2 = 1.0 if is_on else 0.3
            self.grp_my_dev.setStyleSheet(f"opacity: {op1};")
            self.grp_nearby.setStyleSheet(f"opacity: {op2};")
        
    def _on_theme_changed(self):
        fix_label_styles(self)
        self.update()

    def get_search_target(self, target_id: str) -> QWidget | None:
        targets = {
            "bluetooth.toggle": getattr(self, "main_card", None),
            "bluetooth.devices": getattr(self, "grp_my_dev", None) or getattr(self, "main_card", None),
        }
        return targets.get(target_id)
