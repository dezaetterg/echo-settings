from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QGridLayout
from PySide6.QtCore import Qt, Signal, QThread, QObject
from theme.colors import Colors
from theme.typography import Typography
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from components.switch import Switch
from components.popup_button import PopupButton
from components.hero_card import HeroCard
from components.action_card import ActionGridCard, SimpleActionCard
from services.general_service import GeneralService
from theme.manager import ThemeManager
from theme.styler import fix_label_styles

import threading

class UpdateCheckThread(QObject):
    finished = Signal(int)
    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service
        self._is_stopped = False

    def start(self):
        def _worker():
            try:
                count = self.service.check_updates()
                if not self._is_stopped:
                    self.finished.emit(count)
            except Exception:
                pass
        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def quit(self): self._is_stopped = True
    def requestInterruption(self): self._is_stopped = True
    def wait(self, timeout=None): pass
    def isRunning(self): return False

class OptionsLoaderThread(QObject):
    locales_ready = Signal(dict)
    timezones_ready = Signal(dict)

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service
        self._is_stopped = False

    def start(self):
        def _worker():
            try:
                locs = self.service.get_locales()
                if locs and not self._is_stopped:
                    self.locales_ready.emit(locs)
            except Exception:
                pass

            try:
                from PySide6.QtCore import QTimeZone, QDateTime
                tzs = self.service.get_all_timezones()
                tz_dict = {}
                now = QDateTime.currentDateTime()
                for tz in tzs:
                    if self._is_stopped:
                        return
                    try:
                        qtz = QTimeZone(tz.encode('utf-8'))
                        offset = qtz.offsetFromUtc(now) // 3600
                        sign = "+" if offset >= 0 else ""
                        city = tz.split("/")[-1].replace("_", " ")
                        tz_dict[tz] = f"{city} (UTC{sign}{offset})"
                    except Exception:
                        tz_dict[tz] = tz
                if tz_dict and not self._is_stopped:
                    self.timezones_ready.emit(tz_dict)
            except Exception:
                pass

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def quit(self): self._is_stopped = True
    def requestInterruption(self): self._is_stopped = True
    def wait(self, timeout=None): pass
    def isRunning(self): return False


class ClickableRow(SettingsRow):
    clicked = Signal()
    def __init__(self, title, widget=None, **kwargs):
        super().__init__(title, widget, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

class GeneralPage(QWidget):
    request_page = Signal(str) # To navigate to other pages
    
    def __init__(self):
        super().__init__()
        self.service = GeneralService()
        self._dev_value_labels: dict[str, QLabel] = {}  # key -> QLabel for live updates
        self._hero: HeroCard | None = None
        self._options_loader = None
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 30, 40, 40)
        self.layout.setSpacing(32)
        self.layout.setAlignment(Qt.AlignTop)
        
        self._build_ui()
        
        self.layout.addStretch()
        
        scroll.setWidget(self.content)
        self.main_layout.addWidget(scroll)
        
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

        # Background load full locales and timezones
        self._options_loader = OptionsLoaderThread(self.service, parent=self)
        self._options_loader.locales_ready.connect(self._on_full_locales_ready)
        self._options_loader.timezones_ready.connect(self._on_full_timezones_ready)
        self._options_loader.start()


    def _on_full_locales_ready(self, full_locales: dict):
        if hasattr(self, 'lang_btn') and self.lang_btn:
            self.lang_btn.update_options(full_locales)
        if hasattr(self, 'region_btn') and self.region_btn:
            self.region_btn.update_options(full_locales)

    def _on_full_timezones_ready(self, full_tzs: dict):
        if hasattr(self, 'tz_btn') and self.tz_btn:
            self.tz_btn.update_options(full_tzs)

    def update_style(self, _is_dark=False):
        fix_label_styles(self)
        self.update()
        
    def _create_section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #6E6E73; font-size: 13px; font-weight: 600; margin-left: 8px; margin-bottom: 4px;")
        return lbl

    def _build_ui(self):
        from localization import t
        # 0. Header Title
        title = QLabel(t("general.title", "General"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};")
        self.layout.addWidget(title)

        # 1. Hero Card
        self._hero = HeroCard()
        self.layout.addWidget(self._hero)
        
        # 2. Device Information
        self.layout.addWidget(self._create_section_label(t("general.dev_info", "Device Information")))
        dev_info = self.service.get_device_info()
        self.dev_group = SettingsGroup()
        
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(20, 16, 20, 16)
        grid.setSpacing(16)
        
        dev_key_map = {
            "Hostname": "general.device_name",
            "CPU": "general.processor",
            "GPU": "general.graphics",
            "RAM": "general.memory",
            "Disk": "general.disk_capacity",
            "Kernel": "general.os_name",
            "Architecture": "general.processor"
        }
        
        row, col = 0, 0
        for key, val in dev_info.items():
            item_layout = QVBoxLayout()
            item_layout.setSpacing(4)
            
            translated_k = t(dev_key_map.get(key, key), key)
            k_lbl = QLabel(translated_k)
            k_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; font-weight: 500;")
            
            v_lbl = QLabel(val)
            v_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px;")
            v_lbl.setWordWrap(True)
            
            # Store reference for live refresh
            self._dev_value_labels[key] = v_lbl
            
            item_layout.addWidget(k_lbl)
            item_layout.addWidget(v_lbl)
            
            grid.addLayout(item_layout, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        self.dev_group.layout.addWidget(grid_widget)
        self.layout.addWidget(self.dev_group)
        
        # 3. Startup
        self.layout.addWidget(self._create_section_label(t("general.startup", "Startup")))
        self.start_group = SettingsGroup()
        
        sw_start = Switch(checked=self.service.get_startup())
        sw_start.toggled.connect(self.service.set_startup)
        self.start_group.add_row(SettingsRow(t("general.start_at_login", "Start Settings at Login"), sw_start, show_separator=False))
        self.layout.addWidget(self.start_group)
        
        # 4. Updates
        self.layout.addWidget(self._create_section_label(t("general.updates", "Updates")))
        self.upd_group = SettingsGroup()
        
        # Build custom row for Updates without SettingsRow
        upd_widget = QWidget()
        upd_widget.setMinimumHeight(60)
        upd_layout = QHBoxLayout(upd_widget)
        upd_layout.setContentsMargins(20, 12, 20, 12)
        
        upd_text = QVBoxLayout()
        upd_text.setSpacing(4)
        
        self.lbl_update_title = QLabel(t("general.system_up_to_date", "System is up to date"))
        self.lbl_update_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 15px; font-weight: 500;")
        self.lbl_update_sub = QLabel(t("general.last_checked", "Last checked: Today"))
        self.lbl_update_sub.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        
        upd_text.addWidget(self.lbl_update_title)
        upd_text.addWidget(self.lbl_update_sub)
        upd_layout.addLayout(upd_text)
        upd_layout.addStretch()
        
        self.btn_check_update = QPushButton(t("general.check_updates", "Check for Updates"))
        self.btn_check_update.setFixedSize(160, 32)
        self.btn_check_update.setStyleSheet(f"QPushButton {{ background-color: {Colors.ACCENT_BLUE}; color: white; border: none; border-radius: 6px; font-weight: 500; }} QPushButton:hover {{ background-color: #0066CC; }} QPushButton:disabled {{ background-color: #333333; color: #888888; }}")
        self.btn_check_update.clicked.connect(self._start_update_check)
        upd_layout.addWidget(self.btn_check_update)
        
        self.upd_group.layout.addWidget(upd_widget)
        self.layout.addWidget(self.upd_group)
        
        # 5. Default Applications
        self.layout.addWidget(self._create_section_label(t("general.default_apps", "Default Applications")))
        self.app_group = SettingsGroup()
        
        browsers = self.service.get_installed_browsers()
        if not browsers:
            browsers = {"xdg-open": "System Default"}
            
        cur_browser = self.service.get_default_browser()
        if cur_browser not in browsers and cur_browser != "Unknown":
            browsers[cur_browser] = cur_browser.replace(".desktop", "").title()
            
        browser_btn = PopupButton(browsers, cur_browser if cur_browser in browsers else list(browsers.keys())[0])
        browser_btn.valueChanged.connect(self.service.set_default_browser)
        self.app_group.add_row(SettingsRow(t("general.browser", "Web Browser"), browser_btn, show_separator=False))
        
        self.layout.addWidget(self.app_group)
        
        # 6. Language & Region
        self.layout.addWidget(self._create_section_label(t("general.lang_region", "Language & Region")))
        self.lang_group = SettingsGroup()
        
        from localization import i18n, SUPPORTED_LANGUAGES
        app_lang_options = {code: f"{meta['native']} ({meta['name']})" for code, meta in SUPPORTED_LANGUAGES.items()}
        self.app_lang_btn = PopupButton(app_lang_options, i18n.current_language)
        self.app_lang_btn.valueChanged.connect(lambda val: i18n.set_language(val))
        self.lang_group.add_row(SettingsRow(t("general.app_language", "Echo Settings Language"), self.app_lang_btn, show_separator=True))
        
        cur_locale = self.service.get_current_locale()
        init_locales = {
            cur_locale: "Russian (Russia)" if "ru" in cur_locale else "English (United States)" if "en" in cur_locale else cur_locale,
            "en_US.UTF-8": "English (United States)",
            "ru_RU.UTF-8": "Russian (Russia)"
        }
            
        self.lang_btn = PopupButton(init_locales, cur_locale)
        self.lang_btn.valueChanged.connect(self.service.set_locale)
        self.lang_group.add_row(SettingsRow(t("general.system_language", "System Display Language"), self.lang_btn, show_separator=True))
        
        cur_region = self.service.get_region()
        if cur_region not in init_locales:
            init_locales[cur_region] = cur_region
            
        self.region_btn = PopupButton(init_locales, cur_region)
        self.region_btn.valueChanged.connect(self.service.set_region)
        self.lang_group.add_row(SettingsRow(t("general.region", "Region"), self.region_btn, show_separator=True))
        
        days_opts = {"mon": t("general.monday", "Monday"), "sun": t("general.sunday", "Sunday")}
        self.lang_group.add_row(SettingsRow(t("general.first_day", "First Day of Week"), PopupButton(days_opts, "mon"), show_separator=False))
        self.layout.addWidget(self.lang_group)
        
        # 7. Date & Time
        self.layout.addWidget(self._create_section_label(t("general.date_time", "Date & Time")))
        time_group = SettingsGroup()
        
        sw_ntp = Switch(checked=self.service.get_ntp())
        sw_ntp.toggled.connect(self.service.set_ntp)
        time_group.add_row(SettingsRow(t("general.auto_time", "Set Time Automatically"), sw_ntp, show_separator=True))
        
        cur_tz = self.service.get_timezone()
        init_tz_dict = {
            cur_tz: cur_tz.split("/")[-1].replace("_", " "),
            "UTC": "UTC",
            "Europe/Moscow": "Moscow (UTC+3)",
            "America/New_York": "New York (UTC-5)",
            "Europe/London": "London (UTC+0)",
            "Asia/Tokyo": "Tokyo (UTC+9)"
        }
            
        self.tz_btn = PopupButton(init_tz_dict, cur_tz)
        self.tz_btn.valueChanged.connect(self.service.set_timezone)
        
        time_group.add_row(SettingsRow(t("general.timezone", "Timezone"), self.tz_btn, show_separator=True))
        
        sw_24h_2 = Switch(checked=self.service.get_24_hour())
        sw_24h_2.toggled.connect(self.service.set_24_hour)
        time_group.add_row(SettingsRow(t("general.use_24h", "Use 24-hour clock"), sw_24h_2, show_separator=False))
        self.layout.addWidget(time_group)
        
        # 8. Quick Shortcuts
        self.layout.addWidget(self._create_section_label(t("general.quick_shortcuts", "Quick Shortcuts")))
        sc_group = SettingsGroup()
        
        shortcut_items = [
            ("Storage", "nav.storage"),
            ("Power", "nav.power"),
            ("Network", "nav.network"),
            ("Display", "nav.display"),
            ("Wi-Fi", "nav.wifi")
        ]
        for name, key in shortcut_items:
            row = ClickableRow(f"{t(key, name)}  →", is_interactive=True, show_separator=(name != "Wi-Fi"))
            row.clicked.connect(lambda n=name: self.request_page.emit(n))
            sc_group.add_row(row)
            
        self.layout.addWidget(sc_group)
        
        # 9. Session
        self.layout.addWidget(self._create_section_label(t("general.session", "Session")))
        session_group = SettingsGroup()
        
        row_lock = ClickableRow(t("general.lock_screen", "Lock Screen"), show_separator=True, is_destructive=True)
        row_lock.clicked.connect(self.service.lock_screen)
        session_group.add_row(row_lock)
        
        row_logout = ClickableRow(t("general.log_out", "Log Out"), show_separator=True, is_destructive=True)
        row_logout.clicked.connect(self.service.log_out)
        session_group.add_row(row_logout)
        
        row_restart = ClickableRow(t("general.restart", "Restart..."), show_separator=True, is_destructive=True)
        row_restart.clicked.connect(self.service.restart)
        session_group.add_row(row_restart)
        
        row_power = ClickableRow(t("general.power_off", "Shut Down..."), show_separator=False, is_destructive=True)
        row_power.clicked.connect(self.service.power_off)
        session_group.add_row(row_power)
        
        self.layout.addWidget(session_group)

    def _start_update_check(self):
        self.btn_check_update.setEnabled(False)
        self.btn_check_update.setText("Checking...")
        self.lbl_update_title.setText("Checking for updates...")
        
        self.update_thread = UpdateCheckThread(self.service)
        self.update_thread.finished.connect(self._on_update_check_finished)
        self.update_thread.start()
        
    def _on_update_check_finished(self, count):
        self.btn_check_update.setEnabled(True)
        self.btn_check_update.setText("Check for Updates")
        
        from datetime import datetime
        now = datetime.now().strftime("%I:%M %p")
        self.lbl_update_sub.setText(f"Last checked: Today at {now}")
        
        if count > 0:
            self.lbl_update_title.setText(f"{count} Updates Available")
            self.lbl_update_title.setStyleSheet(f"color: #FF9F0A; font-size: 15px; font-weight: 500;")
        else:
            self.lbl_update_title.setText("System is up to date")
            self.lbl_update_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 15px; font-weight: 500;")

    # ------------------------------------------------------------------
    # Live system info refresh (called by SystemInfoWatcher)
    # ------------------------------------------------------------------
    def refresh_system_info(self, info: dict):
        """Update UI when system info has changed without rebuilding widgets."""
        # Map backend keys to what GeneralService returns
        key_map = {
            "Hostname": info.get("hostname", ""),
            "CPU": info.get("cpu", ""),
            "GPU": info.get("gpu", ""),
            "RAM": info.get("ram", ""),
            "Kernel": info.get("kernel", ""),
            "Architecture": info.get("architecture", ""),
            "Disk": info.get("disk", ""),
        }
        for label_key, new_val in key_map.items():
            if label_key in self._dev_value_labels and new_val:
                self._dev_value_labels[label_key].setText(new_val)

        # Update HeroCard
        if self._hero:
            self._hero.refresh(info)

    def cleanup(self):
        if hasattr(self, '_options_loader') and self._options_loader:
            try:
                if self._options_loader.isRunning():
                    self._options_loader.requestInterruption()
                    self._options_loader.quit()
                    self._options_loader.wait(500)
            except Exception:
                pass
        if hasattr(self, 'update_thread') and self.update_thread:
            try:
                if self.update_thread.isRunning():
                    self.update_thread.requestInterruption()
                    self.update_thread.quit()
                    self.update_thread.wait(500)
            except Exception:
                pass

    def __del__(self):
        try:
            self.cleanup()
        except Exception:
            pass

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)

    def get_search_target(self, target_id: str) -> QWidget | None:
        targets = {
            "general.about": getattr(self, "_hero", None) or getattr(self, "dev_group", None),
            "general.name": getattr(self, "dev_group", None),
            "general.startup": getattr(self, "start_group", None),
            "general.updates": getattr(self, "upd_group", None),
            "general.default_browser": getattr(self, "app_group", None),
            "general.language": getattr(self, "lang_group", None),
        }
        return targets.get(target_id)


