import os
import shutil
import subprocess
import platform
import socket
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QWidget, QLabel, 
    QScrollArea, QStackedWidget, QPushButton
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath

from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from components.settings_group import SettingsGroup

class ReportSidebarItem(QWidget):
    clicked = Signal(str)
    
    def __init__(self, text, icon_name, parent=None):
        super().__init__(parent)
        self.text = text
        self.icon_name = icon_name
        self.setFixedHeight(30)
        self.setCursor(Qt.PointingHandCursor)
        
        self.is_selected = False
        self.is_hovered = False
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 6, 10, 6)
        self.layout.setSpacing(10)
        
        # We will draw the icon directly in paintEvent to colorize it easily
        self.text_label = QLabel(text)
        self.text_label.setTextInteractionFlags(Qt.NoTextInteraction)
        self.text_label.setStyleSheet(f"font-size: 13px; font-weight: 500; background: transparent; border: none;")
        
        # Disable focus to prevent any dotted borders or cursors
        self.setFocusPolicy(Qt.NoFocus)
        
        # We use a dummy widget for spacing the icon since we draw it on self
        self.icon_spacer = QWidget()
        self.icon_spacer.setFixedSize(18, 18)
        self.icon_spacer.setStyleSheet("background: transparent;")
        
        self.layout.addWidget(self.icon_spacer)
        self.layout.addWidget(self.text_label)
        self.layout.addStretch()
        
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)
        
    def update_style(self, _is_dark=False):
        if self.is_selected:
            self.text_label.setStyleSheet(f"color: #FFFFFF; font-size: 13px; font-weight: 500; background: transparent; border: none;")
        else:
            self.text_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: 500; background: transparent; border: none;")
        self.update()

    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.text)
            
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Background
        if self.is_selected:
            p.setBrush(QColor("#007AFF"))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(self.rect(), 6, 6)
        elif self.is_hovered:
            is_dark = ThemeManager.is_dark
            p.setBrush(QColor(255, 255, 255, 13) if is_dark else QColor(0, 0, 0, 13))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(self.rect(), 6, 6)
            
        # Draw Icon (18x18) centered in the spacer area
        # spacer is at layout left margin (10), top margin (6)
        # So center of icon is x=10+9=19, y=6+9=15
        icon_color = Qt.white if self.is_selected else QColor(Colors.TEXT_PRIMARY)
        
        p.setPen(QPen(icon_color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        
        cx, cy = 19, 15
        
        if self.icon_name == "Hardware":
            p.setPen(QPen(icon_color, 2.0))
            p.drawEllipse(cx-3, cy-3, 6, 6)
            p.setPen(QPen(icon_color, 1.5))
            for i in range(8):
                p.save()
                p.translate(cx, cy)
                p.rotate(45 * i)
                p.drawLine(0, -3, 0, -5)
                p.restore()
                
        elif self.icon_name == "Graphics":
            p.drawRoundedRect(cx-6, cy-5, 12, 8, 1, 1)
            p.drawLine(cx-3, cy+5, cx+3, cy+5)
            p.drawLine(cx, cy+3, cx, cy+5)
            
        elif self.icon_name == "Storage":
            p.drawRoundedRect(cx-5, cy-6, 10, 12, 2, 2)
            p.drawEllipse(cx-3, cy-3, 6, 6)
            
        elif self.icon_name == "USB Devices":
            p.drawLine(cx, cy-5, cx, cy+5)
            p.drawLine(cx, cy-5, cx+4, cy-2)
            p.drawLine(cx+4, cy-2, cx-3, cy+3)
            p.drawLine(cx, cy+5, cx+4, cy+2)
            p.drawLine(cx+4, cy+2, cx-3, cy-3)
            
        elif self.icon_name == "Network":
            p.drawEllipse(cx-5, cy-5, 10, 10)
            p.drawEllipse(cx-2, cy-5, 4, 10)
            p.drawLine(cx-5, cy, cx+5, cy)

# -----------------
# Utility Functions
# -----------------

def get_cpu_info():
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":")[1].strip()
    except:
        pass
    return platform.processor()

def get_mem_info():
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    kb = int(line.split()[1])
                    gb = round(kb / (1024 * 1024), 1)
                    return f"{gb} GB"
    except:
        pass
    return "Unknown"

def get_dmi_info(filename):
    try:
        with open(f"/sys/class/dmi/id/{filename}", "r") as f:
            return f.read().strip()
    except:
        return "Unknown"

def get_lspci_info():
    if shutil.which("lspci"):
        try:
            out = subprocess.check_output(r"lspci | grep -i 'vga\|3d\|display'", shell=True, text=True)
            return [line.split(":")[-1].strip() for line in out.strip().split('\n') if line]
        except:
            pass
    return []

def get_lsusb_info():
    if shutil.which("lsusb"):
        try:
            out = subprocess.check_output("lsusb", shell=True, text=True)
            usbs = []
            for line in out.strip().split('\n'):
                if not line: continue
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    name_parts = parts[-1].strip().split(" ", 1)
                    vendor = name_parts[0]
                    name = name_parts[1] if len(name_parts) > 1 else vendor
                    if len(name) > 30:
                        name = name[:27] + "..."
                    usbs.append((name, vendor))
            return usbs
        except:
            pass
    return []

def get_storage_info():
    if shutil.which("lsblk"):
        try:
            out = subprocess.check_output("lsblk -d -o NAME,MODEL,SIZE,TYPE -n", shell=True, text=True)
            drives = []
            for line in out.strip().split('\n'):
                if not line: continue
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0]
                    if any(x in name for x in ['loop', 'ram', 'zram']):
                        continue
                    size = parts[-2]
                    drv_type = parts[-1]
                    model = " ".join(parts[1:-2])
                    
                    type_str = "SATA SSD/HDD"
                    if "nvme" in name: type_str = "NVMe Storage"
                    if "usb" in name or drv_type == "usb": type_str = "USB Storage"
                    
                    drives.append((type_str, f"{model} ({size})"))
            return drives
        except:
            pass
    return []

def get_network_ip():
    try:
        # Get actual active IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unknown"

class SystemReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Report")
        self.setFixedSize(700, 520)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Base rounded container
        self.container = QWidget()
        self.container.setObjectName("Container")
        is_dark = ThemeManager.is_dark
        bg = Colors.WINDOW_BG
        border = Colors.CARD_BORDER
        
        self.container.setStyleSheet(f"""
            QWidget#Container {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
        """)
        
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar_container = QWidget()
        self.sidebar_container.setObjectName("SidebarContainer")
        self.sidebar_container.setFixedWidth(190)
        
        sidebar_bg = Colors.SIDEBAR_BG
        sidebar_border = Colors.CARD_BORDER
        
        self.sidebar_container.setStyleSheet(f"""
            QWidget#SidebarContainer {{
                background-color: {sidebar_bg};
                border-right: 1px solid {sidebar_border};
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            }}
        """)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar_container)
        self.sidebar_layout.setContentsMargins(15, 15, 15, 15)
        self.sidebar_layout.setSpacing(2)
        self.sidebar_layout.setAlignment(Qt.AlignTop)
        
        container_layout.addWidget(self.sidebar_container)
        
        self.sidebar_items = []
        
        categories = [
            ("Hardware", "Hardware"),
            ("Graphics", "Graphics"),
            ("Storage", "Storage"),
            ("USB Devices", "USB Devices"),
            ("Network", "Network")
        ]
        
        for name, icon_name in categories:
            item = ReportSidebarItem(name, icon_name)
            item.clicked.connect(self._on_sidebar_clicked)
            self.sidebar_layout.addWidget(item)
            self.sidebar_items.append(item)
        
        # Content Stack
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: transparent;")
        
        self.pages = {}
        for name, _ in categories:
            page = self._create_page(name)
            self.content_stack.addWidget(page)
            self.pages[name] = page
            
        container_layout.addWidget(self.content_stack)
        
        # Close button overlay
        self.close_btn = QPushButton("Close", self.container)
        self.close_btn.setFixedSize(72, 28)
        
        btn_bg = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.05)"
        btn_hover = "rgba(255, 255, 255, 0.15)" if is_dark else "rgba(0, 0, 0, 0.1)"
        btn_border = "rgba(255, 255, 255, 0.15)" if is_dark else "rgba(0, 0, 0, 0.1)"
        
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_bg};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {btn_border};
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
            }}
        """)
        self.close_btn.clicked.connect(self.accept)
        
        main_layout.addWidget(self.container)
        
        if self.sidebar_items:
            self._on_sidebar_clicked(categories[0][0])

    def _on_sidebar_clicked(self, text):
        for idx, item in enumerate(self.sidebar_items):
            if item.text == text:
                item.set_selected(True)
                self.content_stack.setCurrentIndex(idx)
                self._load_data(text)
            else:
                item.set_selected(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.close_btn.move(self.width() - 92, self.height() - 48)

    def _create_page(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 80)
        content_layout.setSpacing(24)
        content_layout.setAlignment(Qt.AlignTop)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 24px; font-weight: bold;")
        content_layout.addWidget(lbl_title)
        
        group = SettingsGroup()
        content_layout.addWidget(group)
        
        # Empty State
        empty_state = QLabel("Information Unavailable")
        empty_state.setStyleSheet("color: #8E8E93; font-size: 13px;")
        empty_state.setAlignment(Qt.AlignCenter)
        empty_state.hide()
        content_layout.addWidget(empty_state)
        
        page.group = group
        page.empty_state = empty_state
        page.loaded = False
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        return page

    def _add_row(self, group, key, val, show_separator=True):
        from components.settings_row import SettingsRow
        val_lbl = QLabel(val)
        val_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        sr = SettingsRow(key, val_lbl, show_separator=show_separator, is_interactive=False)
        group.add_row(sr)

    def _show_empty(self, page, text="Information Unavailable"):
        page.group.hide()
        page.empty_state.setText(text)
        page.empty_state.show()

    def _load_data(self, cat):
        page = self.pages[cat]
        if page.loaded: return
        
        group = page.group
        
        if cat == "Hardware":
            self._add_row(group, "Processor", get_cpu_info())
            self._add_row(group, "Memory", get_mem_info())
            self._add_row(group, "Product Name", get_dmi_info("product_name"))
            self._add_row(group, "System Vendor", get_dmi_info("sys_vendor"))
            self._add_row(group, "OS Platform", platform.platform(), show_separator=False)
            
        elif cat == "Graphics":
            gpus = get_lspci_info()
            if gpus:
                for i, gpu in enumerate(gpus):
                    self._add_row(group, f"Display {i+1}", gpu, show_separator=(i < len(gpus)-1))
            else:
                self._show_empty(page)
                
        elif cat == "Storage":
            drives = get_storage_info()
            if drives:
                for i, d in enumerate(drives):
                    self._add_row(group, d[0], d[1], show_separator=(i < len(drives)-1))
            else:
                self._show_empty(page, "No Connected Storage Found")
                
        elif cat == "USB Devices":
            usbs = get_lsusb_info()
            if usbs:
                for i, u in enumerate(usbs):
                    self._add_row(group, u[0], u[1], show_separator=(i < len(usbs)-1))
            else:
                self._show_empty(page, "No Connected USB Devices Found")
                
        elif cat == "Network":
            self._add_row(group, "Hostname", socket.gethostname())
            self._add_row(group, "IPv4", get_network_ip(), show_separator=False)
            
        page.loaded = True

