from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, Property
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QIcon, QImage, QPixmap
from theme.colors import Colors
from theme.manager import ThemeManager
from theme.typography import Typography
from components.settings_group import SettingsGroup

class DeviceRow(QWidget):
    clicked = Signal(str)
    
    def __init__(self, device_id, device_info, is_active=False, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(56)
        
        self.is_active = is_active
        self._hover_alpha = 0.0
        self.hover_anim = QPropertyAnimation(self, b"hover_alpha")
        self.hover_anim.setDuration(150)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        
        # Icon
        icon_name = device_info.get("icon", "audio-card-symbolic")
        icon = QIcon.fromTheme(icon_name)
        if icon.isNull():
            icon = QIcon.fromTheme(icon_name.replace("-symbolic", ""))
        pixmap = icon.pixmap(24, 24)
        if ThemeManager.is_dark:
            img = pixmap.toImage().convertToFormat(QImage.Format_ARGB32)
            p = QPainter(img)
            p.setCompositionMode(QPainter.CompositionMode_SourceIn)
            p.fillRect(img.rect(), QColor(255, 255, 255))
            p.end()
            img.setDevicePixelRatio(pixmap.devicePixelRatio())
            pixmap = QPixmap.fromImage(img)
            
        icon_lbl = QLabel()
        icon_lbl.setPixmap(pixmap)
        layout.addWidget(icon_lbl)
        
        # Text Layout
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setAlignment(Qt.AlignVCenter)
        
        label_text = device_info.get("label", str(device_id))
        self.name_lbl = QLabel(label_text)
        
        font_weight = Typography.WEIGHT_MEDIUM if is_active else Typography.WEIGHT_NORMAL
        color = Colors.ACCENT_BLUE if is_active else Colors.TEXT_PRIMARY
        
        self.name_lbl.setStyleSheet(f"color: {color}; font-size: {Typography.SIZE_BODY}px; font-weight: {font_weight}; background: transparent;")
        text_layout.addWidget(self.name_lbl)
        
        if is_active:
            state_str = device_info.get("state", "").upper()
            is_muted = device_info.get("muted", False)
            
            status_parts = []
            if state_str == "RUNNING":
                status_parts.append("Active")
            elif state_str == "SUSPENDED":
                status_parts.append("Suspended")
            elif state_str == "IDLE":
                status_parts.append("Connected")
                
            if is_muted:
                status_parts.append("Muted")
                
            status_text = " • ".join(status_parts) if status_parts else "Default Device"
            
            self.status_lbl = QLabel(status_text)
            self.status_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: 500; background: transparent;")
            text_layout.addWidget(self.status_lbl)
            
        layout.addLayout(text_layout)
        
        layout.addStretch()
        
        # Active Checkmark
        if is_active:
            check_icon = QIcon.fromTheme("object-select-symbolic")
            if check_icon.isNull():
                check_lbl = QLabel("Active")
                check_lbl.setStyleSheet(f"color: {Colors.ACCENT_BLUE}; font-size: {Typography.SIZE_SMALL}px; font-weight: bold; background: transparent;")
                layout.addWidget(check_lbl)
            else:
                check_lbl = QLabel()
                check_lbl.setPixmap(check_icon.pixmap(16, 16))
                layout.addWidget(check_lbl)
                
    @Property(float)
    def hover_alpha(self): return self._hover_alpha
    
    @hover_alpha.setter
    def hover_alpha(self, val):
        self._hover_alpha = val
        self.update()
        
    def enterEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setEndValue(0.0)
        self.hover_anim.start()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.device_id)
        super().mousePressEvent(event)
        
    def paintEvent(self, event):
        if self._hover_alpha > 0:
            p = QPainter(self)
            is_dark = ThemeManager.is_dark
            c = QColor(255, 255, 255, int(15 * self._hover_alpha)) if is_dark else QColor(0, 0, 0, int(10 * self._hover_alpha))
            p.fillRect(self.rect(), c)

class DeviceSelector(SettingsGroup):
    deviceSelected = Signal(str)
    
    def __init__(self, devices: dict, active_id: str, parent=None):
        super().__init__(parent)
        self.devices = devices
        self.active_id = active_id
        self._build_list()
        ThemeManager.theme_changed.connect(self._on_theme_changed)
        
    def _on_theme_changed(self, _is_dark=False):
        self._build_list()
        
    def set_devices(self, devices, active_id):
        self.devices = devices
        self.active_id = active_id
        self._build_list()
        
    def _build_list(self):
        # Clear existing rows
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
                w.setParent(None)
                w.deleteLater()
                
        keys = list(self.devices.keys())
        for i, key in enumerate(keys):
            is_active = (key == self.active_id)
            row = DeviceRow(key, self.devices[key], is_active)
            row.clicked.connect(self.deviceSelected.emit)
            self.layout.addWidget(row)
            
            # separator
            if i < len(keys) - 1:
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet(f"background-color: {Colors.CARD_BORDER}; max-height: 1px; border: none;")
                self.layout.addWidget(sep)
                
        self.updateGeometry()
