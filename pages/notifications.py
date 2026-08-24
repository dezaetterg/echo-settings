from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QSizePolicy, QSpacerItem, QStackedWidget, QPushButton
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
from theme.colors import Colors
from theme.typography import Typography
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from components.switch import Switch
from services.notifications_service import NotificationsService
from theme.manager import ThemeManager
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath

def create_default_app_icon(size=32):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    
    p.setBrush(QColor("#8E8E93"))
    p.setPen(Qt.NoPen)
    radius = size * 0.22
    p.drawRoundedRect(0, 0, size, size, radius, radius)
    
    cx, cy = size / 2.0, size / 2.0
    scale = size / 32.0
    
    p.setPen(QPen(Qt.white, 1.5 * scale, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    
    p.drawArc(cx - 4*scale, cy - 5*scale, 8*scale, 8*scale, 0, 180*16)
    p.drawLine(cx - 4*scale, cy - 1*scale, cx - 6*scale, cy + 3*scale)
    p.drawLine(cx + 4*scale, cy - 1*scale, cx + 6*scale, cy + 3*scale)
    p.drawLine(cx - 7*scale, cy + 3*scale, cx + 7*scale, cy + 3*scale)
    
    p.setBrush(Qt.white)
    p.setPen(Qt.NoPen)
    p.drawEllipse(cx - 1.5*scale, cy + 4*scale, 3*scale, 3*scale)
    
    p.end()
    return pixmap

class AppNotificationRow(QWidget):
    clicked = Signal(object)
    
    def __init__(self, app_info, service, parent=None):
        super().__init__(parent)
        self.app_info = app_info
        self.service = service
        self.setFixedHeight(56)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        # Icon
        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(32, 32)
        icon_name = app_info["icon"]
        icon = QIcon.fromTheme(icon_name)
        if icon.isNull() or icon_name == "application-x-executable":
            self.icon_lbl.setPixmap(create_default_app_icon(32))
        else:
            self.icon_lbl.setPixmap(icon.pixmap(32, 32))
        layout.addWidget(self.icon_lbl)
        
        # Texts
        vbox = QVBoxLayout()
        vbox.setSpacing(2)
        vbox.setAlignment(Qt.AlignVCenter)
        
        self.name_lbl = QLabel(app_info["name"])
        self.name_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; font-weight: {Typography.WEIGHT_MEDIUM}; background: transparent;")
        vbox.addWidget(self.name_lbl)
        
        self.subtitle_lbl = QLabel()
        vbox.addWidget(self.subtitle_lbl)
        
        layout.addLayout(vbox)
        layout.addStretch()
        
        # Arrow instead of switch
        arrow = QLabel("›")
        arrow.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 24px; font-weight: 300; margin-bottom: 2px;")
        layout.addWidget(arrow)
        
        self.update_subtitle()
        ThemeManager.theme_changed.connect(self.update_style)
        
    def update_subtitle(self):
        from localization import t
        if self.app_info.get("enable") == False:
            text = t("notifications.off", "Off")
        else:
            items = []
            if self.app_info.get("banners") == True: items.append(t("notifications.sub_banners", "Banners"))
            if self.app_info.get("sounds") == True: items.append(t("notifications.sub_sounds", "Sounds"))
            if self.app_info.get("lock_screen") == True: items.append(t("notifications.sub_lock", "Lock Screen"))
            text = ", ".join(items) if items else t("notifications.sub_badges", "Badges")
            
        self.subtitle_lbl.setText(text)
        self.update_style()
        
    def update_style(self, _=None):
        self.subtitle_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; font-weight: {Typography.WEIGHT_NORMAL}; background: transparent;")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.app_info)
        super().mousePressEvent(event)

class AppNotificationsSubPage(QWidget):
    back_requested = Signal()
    
    def __init__(self, app_info, service, parent=None):
        super().__init__(parent)
        self.app_info = app_info
        self.service = service
        
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.content = QWidget()
        self.scroll.setWidget(self.content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)
        
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 20, 40, 40)
        self.layout.setSpacing(20)
        self.layout.setAlignment(Qt.AlignTop)
        
        # Back Button
        from localization import t
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        self.back_btn = QPushButton(t("notifications.back", "‹ Notifications"))
        self.back_btn.setStyleSheet(f"color: {Colors.ACCENT_BLUE}; font-size: 15px; border: none; background: transparent; text-align: left; font-weight: 500;")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        
        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)
        
        # App Info (Icon + Name)
        info_layout = QHBoxLayout()
        info_layout.setSpacing(16)
        
        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(64, 64)
        icon_name = app_info["icon"]
        icon = QIcon.fromTheme(icon_name)
        if icon.isNull() or icon_name == "application-x-executable":
            self.icon_lbl.setPixmap(create_default_app_icon(64))
        else:
            self.icon_lbl.setPixmap(icon.pixmap(64, 64))
        
        self.name_lbl = QLabel(app_info["name"])
        self.name_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 24px; font-weight: {Typography.WEIGHT_BOLD};")
        
        info_layout.addWidget(self.icon_lbl)
        info_layout.addWidget(self.name_lbl)
        info_layout.addStretch()
        self.layout.addLayout(info_layout)
        
        # Toggles
        group = SettingsGroup()
        
        if app_info.get("enable") != "Not Supported":
            self.enable_switch = Switch()
            self.enable_switch.setChecked(app_info["enable"])
            self.enable_switch.toggled.connect(self.on_enable_toggled)
            group.add_row(SettingsRow(t("notifications.allow", "Allow Notifications"), self.enable_switch, show_separator=True, is_interactive=False))
            
        if app_info.get("banners") != "Not Supported":
            self.banners_switch = Switch()
            self.banners_switch.setChecked(app_info["banners"])
            self.banners_switch.toggled.connect(lambda s: self.service.set_app_key(app_info["id"], "show-banners", s))
            group.add_row(SettingsRow(t("notifications.banners", "Show Banners"), self.banners_switch, show_separator=True, is_interactive=False))
            
        if app_info.get("sounds") != "Not Supported":
            self.sounds_switch = Switch()
            self.sounds_switch.setChecked(app_info["sounds"])
            self.sounds_switch.toggled.connect(lambda s: self.service.set_app_key(app_info["id"], "enable-sound-alerts", s))
            group.add_row(SettingsRow(t("notifications.sounds", "Play Sound Alerts"), self.sounds_switch, show_separator=True, is_interactive=False))
            
        if app_info.get("lock_screen") != "Not Supported":
            self.lock_switch = Switch()
            self.lock_switch.setChecked(app_info["lock_screen"])
            self.lock_switch.toggled.connect(lambda s: self.service.set_app_key(app_info["id"], "show-in-lock-screen", s))
            group.add_row(SettingsRow(t("notifications.lock_screen", "Show on Lock Screen"), self.lock_switch, show_separator=True, is_interactive=False))
            
        if group.layout.count() > 0:
            last_item = group.layout.itemAt(group.layout.count() - 1).widget()
            if isinstance(last_item, SettingsRow):
                last_item.show_separator = True
                last_item.update()
                
        pri_lbl = QLabel(t("notifications.not_supported", "Standard (System)"))
        pri_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 14px;")
        group.add_row(SettingsRow(t("notifications.priority", "Priority"), pri_lbl, show_separator=False, is_interactive=False))
        
        self.layout.addWidget(group)
        
    def on_enable_toggled(self, state):
        self.service.set_app_key(self.app_info["id"], "enable", state)
        self.app_info["enable"] = state

class NotificationsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = NotificationsService()
        
        self.stack = QStackedWidget(self)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)
        
        self.main_page = QWidget()
        self.stack.addWidget(self.main_page)
        
        self.scroll = QScrollArea(self.main_page)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.content = QWidget()
        self.scroll.setWidget(self.content)
        
        mp_layout = QVBoxLayout(self.main_page)
        mp_layout.setContentsMargins(0, 0, 0, 0)
        mp_layout.addWidget(self.scroll)
        
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)
        self.layout.setAlignment(Qt.AlignTop)
        
        from localization import t
        title = QLabel(t("nav.notifications", "Notifications"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};")
        self.layout.addWidget(title)
        
        # DND
        dnd_val = self.service.get_dnd()
        self.group_dnd = None
        if dnd_val != "Not Supported":
            self.group_dnd = SettingsGroup()
            self.dnd_switch = Switch()
            self.dnd_switch.setChecked(dnd_val)
            self.dnd_switch.toggled.connect(self.service.set_dnd)
            self.group_dnd.add_row(SettingsRow(t("notifications.dnd", "Do Not Disturb"), self.dnd_switch, show_separator=False, is_interactive=False))
            self.layout.addWidget(self.group_dnd)
        
        # Notification Center
        lock_val = self.service.get_show_in_lock_screen()
        self.group_lock = None
        if lock_val != "Not Supported":
            nc_lbl = QLabel(t("notifications.sec_center", "NOTIFICATION CENTER"))
            nc_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_MEDIUM}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;")
            self.layout.addWidget(nc_lbl)
            
            self.group_lock = SettingsGroup()
            self.lock_switch = Switch()
            self.lock_switch.setChecked(lock_val)
            self.lock_switch.toggled.connect(self.service.set_show_in_lock_screen)
            self.group_lock.add_row(SettingsRow(t("notifications.lock_previews", "Show Previews on Lock Screen"), self.lock_switch, show_separator=False, is_interactive=False))
            self.layout.addWidget(self.group_lock)
        
        # Apps
        apps = self.service.get_applications()
        if apps:
            apps_lbl = QLabel(t("notifications.sec_apps", "APPLICATION NOTIFICATIONS"))
            apps_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_MEDIUM}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;")
            self.layout.addWidget(apps_lbl)
            
            self.apps_group = SettingsGroup()
            for i, app in enumerate(apps):
                row = AppNotificationRow(app, self.service)
                row.clicked.connect(self.open_app_page)
                self.apps_group.layout.addWidget(row)
                if i < len(apps) - 1:
                    sep = QFrame()
                    sep.setFrameShape(QFrame.HLine)
                    sep.setStyleSheet(f"background-color: {Colors.CARD_BORDER}; max-height: 1px; border: none;")
                    self.apps_group.layout.addWidget(sep)
                    
            self.layout.addWidget(self.apps_group)
        else:
            self.apps_group = None
        
    def open_app_page(self, app_info):
        sub_page = AppNotificationsSubPage(app_info, self.service, self)
        sub_page.back_requested.connect(self.close_app_page)
        self.stack.addWidget(sub_page)
        self.stack.setCurrentWidget(sub_page)
        
    def close_app_page(self):
        current = self.stack.currentWidget()
        self.stack.setCurrentWidget(self.main_page)
        if current != self.main_page:
            self.stack.removeWidget(current)
            current.deleteLater()
            
        # Refresh subtitles on main page if apps group exists
        if self.apps_group:
            for i in range(self.apps_group.layout.count()):
                item = self.apps_group.layout.itemAt(i)
                if item:
                    w = item.widget()
                    if isinstance(w, AppNotificationRow):
                        w.update_subtitle()

    def reset_to_root(self):
        self.close_app_page()

    def showEvent(self, event):
        super().showEvent(event)
        self.close_app_page()

    def get_search_target(self, target_id: str) -> QWidget | None:
        targets = {
            "notifications.allow": getattr(self, "group_dnd", None),
            "notifications.dnd": getattr(self, "group_dnd", None),
            "notifications.lock_screen": getattr(self, "group_lock", None),
            "notifications.previews": getattr(self, "group_lock", None),
            "notifications.badges": getattr(self, "apps_group", None),
        }
        return targets.get(target_id)
