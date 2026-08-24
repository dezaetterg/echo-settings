from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QScrollArea
from PySide6.QtCore import Qt, Signal
from theme.colors import Colors
from theme.typography import Typography
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from models.network_details import NetworkDetailsModel
from theme.manager import ThemeManager
from theme.styler import fix_label_styles

class ReadOnlyValue(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px;")
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

class NetworkDetailsPage(QWidget):
    back_requested = Signal()
    
    def __init__(self, details: NetworkDetailsModel, parent_page_name="Network"):
        super().__init__()
        self.details = details
        self.parent_page_name = parent_page_name
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 30, 40, 40)
        self.layout.setSpacing(24)
        self.layout.setAlignment(Qt.AlignTop)
        
        self._build_header()
        
        # TCP/IP Group
        ip_label = QLabel("TCP/IP")
        ip_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; font-size: {Typography.SIZE_BODY}px; margin-left: 15px;")
        self.layout.addWidget(ip_label)
        
        ip_group = SettingsGroup()
        ip_group.add_row(SettingsRow("IPv4 Address", ReadOnlyValue(self.details.ipv4), show_separator=True))
        ip_group.add_row(SettingsRow("Router", ReadOnlyValue(self.details.gateway), show_separator=True))
        ip_group.add_row(SettingsRow("IPv6 Address", ReadOnlyValue(self.details.ipv6), show_separator=False))
        self.layout.addWidget(ip_group)
        
        # DNS Group
        dns_label = QLabel("DNS")
        dns_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; font-size: {Typography.SIZE_BODY}px; margin-left: 15px;")
        self.layout.addWidget(dns_label)
        
        dns_group = SettingsGroup()
        dns_text = ", ".join(self.details.dns) if self.details.dns else "Unavailable"
        dns_group.add_row(SettingsRow("DNS Servers", ReadOnlyValue(dns_text), show_separator=False))
        self.layout.addWidget(dns_group)
        
        # Hardware Group
        hw_label = QLabel("Hardware")
        hw_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; font-size: {Typography.SIZE_BODY}px; margin-left: 15px;")
        self.layout.addWidget(hw_label)
        
        hw_group = SettingsGroup()
        hw_group.add_row(SettingsRow("MAC Address", ReadOnlyValue(self.details.mac_address), show_separator=True))
        hw_group.add_row(SettingsRow("Interface", ReadOnlyValue(self.details.interface), show_separator=True))
        hw_group.add_row(SettingsRow("Link Speed", ReadOnlyValue(self.details.link_speed), show_separator=True))
        hw_group.add_row(SettingsRow("Driver", ReadOnlyValue(self.details.driver), show_separator=True))
        hw_group.add_row(SettingsRow("MTU", ReadOnlyValue(self.details.mtu), show_separator=False))
        self.layout.addWidget(hw_group)
        
        self.layout.addStretch()
        scroll.setWidget(self.content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(scroll)
        
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def update_style(self, _is_dark=False):
        fix_label_styles(self)
        self.update()

    def _build_header(self):
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        back_btn = QPushButton(f"〈 {self.parent_page_name}")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {Colors.ACCENT_BLUE};
                font-size: {Typography.SIZE_TITLE}px;
                
                text-align: left;
            }}
            QPushButton:hover {{
                color: {Colors.ACCENT_BLUE};
                text-decoration: underline;
            }}
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        
        title_label = QLabel(self.details.ssid)
        title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_SUBHEADER}px; font-weight: {Typography.WEIGHT_SEMIBOLD};")
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Invisible spacer to balance the back button
        spacer = QWidget()
        spacer.setFixedWidth(back_btn.sizeHint().width())
        header_layout.addWidget(spacer)
        
        self.layout.addLayout(header_layout)
