from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QStackedWidget, QPushButton
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from components.shortcut_input import ShortcutInput

from theme.colors import Colors
from theme.typography import Typography
from theme.metrics import CARD_RADIUS
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from components.switch import Switch
from components.slider import Slider
from components.segmented_control import SegmentedControl
from components.spotlight_hero import SpotlightHero
from theme.manager import ThemeManager

from services.spotlight_service import SpotlightSettingsService


class SpotlightPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = SpotlightSettingsService()
        
        self.stack = QStackedWidget(self)
        
        # 1. Full Settings View (when installed)
        self.settings_scroll = self._build_settings_view()
        self.stack.addWidget(self.settings_scroll)
        
        # 2. Promo / Download View (when NOT installed)
        self.uninstalled_scroll = self._build_uninstalled_view()
        self.stack.addWidget(self.uninstalled_scroll)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)
        
        ThemeManager.theme_changed.connect(self.update_style)
        self.update_style()
        self.refresh_install_status()

    def _build_settings_view(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 30, 40, 40)
        self.layout.setSpacing(16)
        self.layout.setAlignment(Qt.AlignTop)
        
        from localization import t
        self.title_lbl_installed = QLabel(t("nav.search", "Echo Search"))
        self.title_lbl_installed.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};")
        self.layout.addWidget(self.title_lbl_installed)

        self.hero_card = SpotlightHero(self.service)
        self.layout.addWidget(self.hero_card)
        self.layout.addSpacing(10)
        
        self._build_general_section()
        self._build_search_section()
        self._build_appearance_section()
        self._build_preview_section()
        self._build_modes_section()
        
        self.layout.addStretch()
        scroll.setWidget(self.content)
        return scroll

    def _build_uninstalled_view(self) -> QScrollArea:
        from localization import t
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        un_content = QWidget()
        un_content.setStyleSheet("background: transparent;")
        un_layout = QVBoxLayout(un_content)
        un_layout.setContentsMargins(40, 30, 40, 40)
        un_layout.setSpacing(18)
        un_layout.setAlignment(Qt.AlignTop)
        
        # Header Title
        self.title_lbl_uninstalled = QLabel(t("nav.search", "Echo Search"))
        self.title_lbl_uninstalled.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};")
        un_layout.addWidget(self.title_lbl_uninstalled)
        
        # Promo Hero Card
        self.promo_card = SettingsGroup()
        promo_inner = QVBoxLayout()
        promo_inner.setContentsMargins(28, 26, 28, 26)
        promo_inner.setSpacing(16)
        
        # Icon + Text row
        header_row = QHBoxLayout()
        header_row.setSpacing(18)
        
        self.promo_icon = QLabel("🔍")
        self.promo_icon.setFixedSize(54, 54)
        self.promo_icon.setAlignment(Qt.AlignCenter)
        header_row.addWidget(self.promo_icon, 0, Qt.AlignTop)
        
        header_text = QVBoxLayout()
        header_text.setSpacing(6)
        
        self.promo_title = QLabel(t("search.not_installed_title", "Echo Search is not installed"))
        self.promo_desc = QLabel(t("search.not_installed_desc", "Echo Search delivers instant search for applications, files, clipboard history, and system actions in Apple Liquid Glass aesthetics. Install Echo Search to unlock unified search capabilities and access all configuration options."))
        self.promo_desc.setWordWrap(True)
        
        header_text.addWidget(self.promo_title)
        header_text.addWidget(self.promo_desc)
        header_row.addLayout(header_text, 1)
        
        promo_inner.addLayout(header_row)
        
        # Button bar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addSpacing(72)  # align with text
        
        self.btn_download = QPushButton(t("search.btn_download", "Download Echo Search"))
        self.btn_download.setCursor(Qt.PointingHandCursor)
        self.btn_download.setFixedHeight(34)
        self.btn_download.clicked.connect(self._open_download_page)
        btn_layout.addWidget(self.btn_download)
        
        self.btn_check_again = QPushButton("↻ " + t("search.btn_check_again", "Check Again"))
        self.btn_check_again.setCursor(Qt.PointingHandCursor)
        self.btn_check_again.setFixedHeight(34)
        self.btn_check_again.clicked.connect(self.refresh_install_status)
        btn_layout.addWidget(self.btn_check_again)
        
        btn_layout.addStretch()
        promo_inner.addLayout(btn_layout)
        
        self.promo_card.layout.addLayout(promo_inner)
        un_layout.addWidget(self.promo_card)
        
        # Feature Group Section
        un_layout.addSpacing(10)
        self.lbl_features = QLabel(t("search.sec_modes", "SEARCH CAPABILITIES"))
        un_layout.addWidget(self.lbl_features)
        
        self.group_features = SettingsGroup()
        
        lbl_f1 = QLabel("⚡")
        lbl_f1.setStyleSheet("font-size: 16px; margin-right: 6px;")
        self.group_features.add_row(SettingsRow(t("search.feature_instant", "Instant applications, files, and math search"), lbl_f1, show_separator=True))
        
        lbl_f2 = QLabel("📋")
        lbl_f2.setStyleSheet("font-size: 16px; margin-right: 6px;")
        self.group_features.add_row(SettingsRow(t("search.feature_clipboard", "Smart clipboard manager & emoji picker"), lbl_f2, show_separator=True))
        
        lbl_f3 = QLabel("💎")
        lbl_f3.setStyleSheet("font-size: 16px; margin-right: 6px;")
        self.group_features.add_row(SettingsRow(t("search.feature_glass", "Native Apple Liquid Glass blurred overlay"), lbl_f3, show_separator=False))
        
        un_layout.addWidget(self.group_features)
        
        un_layout.addStretch()
        scroll.setWidget(un_content)
        return scroll

    def _open_download_page(self):
        from localization import t
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl, QThread, Signal
        try:
            from installer.installer_engine import InstallationEngine
        except Exception:
            InstallationEngine = None

        if not InstallationEngine:
            QDesktopServices.openUrl(QUrl("https://github.com/echo-desktop/echo-search"))
            return

        self.btn_download.setEnabled(False)
        self.btn_download.setText("⏳ " + t("search.installing", "Installing Echo Search..."))

        class QuickInstallThread(QThread):
            completed = Signal(bool)
            def run(self):
                try:
                    res = InstallationEngine.install_echo_search(scope="user")
                    self.completed.emit(res)
                except Exception:
                    self.completed.emit(False)

        self._quick_install_thread = QuickInstallThread(self)

        def _on_finished(success: bool):
            self.btn_download.setEnabled(True)
            if success:
                self.btn_download.setText("✓ " + t("search.installed", "Installed"))
                self.refresh_install_status()
            else:
                self.btn_download.setText(t("search.btn_download", "Download Echo Search"))
                QDesktopServices.openUrl(QUrl("https://github.com/echo-desktop/echo-search"))

        self._quick_install_thread.completed.connect(_on_finished)
        self._quick_install_thread.start()

    def refresh_install_status(self):
        installed = self.service.is_installed()
        if installed:
            if self.stack.currentIndex() != 0:
                self.stack.setCurrentIndex(0)
            self.load_settings()
        else:
            if self.stack.currentIndex() != 1:
                self.stack.setCurrentIndex(1)
        self.update_style()

    def _create_section_label(self, text):
        lbl = QLabel(text)
        self.layout.addWidget(lbl)
        return lbl

    def _build_general_section(self):
        from localization import t
        self.lbl_general = self._create_section_label(t("search.sec_general", "GENERAL"))
        
        self.group_general = SettingsGroup()
        
        # Launch at Login
        self.sw_autostart = Switch()
        self.sw_autostart.setChecked(self.service.get("launch_at_login") is True)
        self.sw_autostart.toggled.connect(lambda v: self.service.set("launch_at_login", v))
        self.group_general.add_row(SettingsRow(t("search.launch_login", "Launch at Login"), self.sw_autostart, show_separator=True))
        
        # Launch Shortcut
        self.edit_shortcut = ShortcutInput()
        self.edit_shortcut.set_shortcut(self.service.get("launch_shortcut") or "<Super>space")
        self.edit_shortcut.setFixedWidth(150)
        self.edit_shortcut.shortcutChanged.connect(lambda v: (self.service.set("launch_shortcut", v), self.hero_card.update()))
        self.group_general.add_row(SettingsRow(t("search.launch_shortcut", "Launch Shortcut"), self.edit_shortcut, show_separator=True))
        
        # Search History
        self.sw_history = Switch()
        self.sw_history.setChecked(self.service.get("search_history") is not False)
        self.sw_history.toggled.connect(lambda v: self.service.set("search_history", v))
        self.group_general.add_row(SettingsRow(t("search.history", "Search History"), self.sw_history, show_separator=True))
        
        # Show Recent when Empty
        self.sw_recent = Switch()
        self.sw_recent.setChecked(self.service.get("recent_when_empty") is not False)
        self.sw_recent.toggled.connect(lambda v: self.service.set("recent_when_empty", v))
        self.group_general.add_row(SettingsRow(t("search.recent_empty", "Show Recent when Empty"), self.sw_recent, show_separator=False))
        
        self.layout.addWidget(self.group_general)

    def _build_search_section(self):
        from localization import t
        self.layout.addSpacing(25)
        self.lbl_search = self._create_section_label(t("search.sec_search", "SEARCH LIMITS"))
        
        self.group_search = SettingsGroup()
        
        # Results Limit
        self.slider_limit = Slider(Qt.Horizontal)
        self.slider_limit.setRange(5, 50)
        self.slider_limit.setValue(self.service.get("results_limit") or 20)
        self.slider_limit.valueChanged.connect(lambda v: self.service.set("results_limit", v))
        self.slider_limit.setFixedWidth(150)
        
        limit_layout = QHBoxLayout()
        limit_layout.setSpacing(10)
        limit_layout.addWidget(self.slider_limit)
        self.lbl_limit_val = QLabel(str(self.slider_limit.value()))
        self.lbl_limit_val.setFixedWidth(40)
        self.lbl_limit_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.slider_limit.valueChanged.connect(lambda v: self.lbl_limit_val.setText(str(v)))
        limit_layout.addWidget(self.lbl_limit_val)
        
        limit_widget = QWidget()
        limit_widget.setFixedWidth(200)
        limit_widget.setLayout(limit_layout)
        limit_layout.setContentsMargins(0,0,0,0)
        self.group_search.add_row(SettingsRow(t("search.results_limit", "Results Limit"), limit_widget, show_separator=False))
        
        self.layout.addWidget(self.group_search)

    def _build_appearance_section(self):
        from localization import t
        self.layout.addSpacing(25)
        self.lbl_appearance = self._create_section_label(t("search.sec_appearance", "APPEARANCE"))
        
        self.group_appearance = SettingsGroup()
        
        # Theme
        opts = [
            ("system", t("appearance.auto", "Auto")),
            ("light", t("appearance.light", "Light")),
            ("dark", t("appearance.dark", "Dark"))
        ]
        current_theme = self.service.get("theme") or "system"
        self.seg_theme = SegmentedControl(opts, current_theme)
        self.seg_theme.setFixedWidth(260)
        self.seg_theme.valueChanged.connect(lambda v: self.service.set("theme", v))
        self.group_appearance.add_row(SettingsRow(t("search.theme", "Theme"), self.seg_theme, show_separator=True))
        
        # Transparency
        self.slider_trans = Slider(Qt.Horizontal)
        self.slider_trans.setRange(0, 100)
        trans_val = self.service.get("transparency")
        if trans_val is None: trans_val = 0.7
        self.slider_trans.setValue(int(trans_val * 100))
        self.slider_trans.valueChanged.connect(lambda v: self.service.set("transparency", v / 100.0))
        self.slider_trans.setFixedWidth(150)
        
        trans_layout = QHBoxLayout()
        trans_layout.setSpacing(10)
        trans_layout.addWidget(self.slider_trans)
        self.lbl_trans_val = QLabel(f"{self.slider_trans.value()}%")
        self.lbl_trans_val.setFixedWidth(40)
        self.lbl_trans_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.slider_trans.valueChanged.connect(lambda v: self.lbl_trans_val.setText(f"{v}%"))
        trans_layout.addWidget(self.lbl_trans_val)
        
        trans_widget = QWidget()
        trans_widget.setFixedWidth(200)
        trans_widget.setLayout(trans_layout)
        trans_layout.setContentsMargins(0,0,0,0)
        
        self.group_appearance.add_row(SettingsRow(t("search.transparency", "Transparency"), trans_widget, show_separator=True))
        
        # Animations
        self.sw_anim = Switch()
        self.sw_anim.setChecked(self.service.get("animations") is not False)
        self.sw_anim.toggled.connect(lambda v: self.service.set("animations", v))
        self.group_appearance.add_row(SettingsRow(t("search.animations", "Animations"), self.sw_anim, show_separator=False))
        
        self.layout.addWidget(self.group_appearance)

    def _build_preview_section(self):
        from localization import t
        self.layout.addSpacing(25)
        self.lbl_preview = self._create_section_label(t("search.sec_preview", "PREVIEW PANEL"))
        
        self.group_preview = SettingsGroup()
        
        # Preview Enabled
        self.sw_preview = Switch()
        self.sw_preview.setChecked(self.service.get("preview_enabled") is not False)
        self.sw_preview.toggled.connect(lambda v: self.service.set("preview_enabled", v))
        self.group_preview.add_row(SettingsRow(t("search.preview_panel", "Preview Panel"), self.sw_preview, show_separator=True))
        
        # Preview Width
        self.slider_width = Slider(Qt.Horizontal)
        self.slider_width.setRange(200, 800)
        self.slider_width.setValue(self.service.get("preview_width") or 420)
        self.slider_width.valueChanged.connect(lambda v: self.service.set("preview_width", v))
        self.slider_width.setFixedWidth(150)
        
        width_layout = QHBoxLayout()
        width_layout.setSpacing(10)
        width_layout.addWidget(self.slider_width)
        self.lbl_width_val = QLabel(f"{self.slider_width.value()}px")
        self.lbl_width_val.setFixedWidth(45)
        self.lbl_width_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.slider_width.valueChanged.connect(lambda v: self.lbl_width_val.setText(f"{v}px"))
        width_layout.addWidget(self.lbl_width_val)
        
        width_widget = QWidget()
        width_widget.setFixedWidth(205)
        width_widget.setLayout(width_layout)
        width_layout.setContentsMargins(0,0,0,0)
        
        self.group_preview.add_row(SettingsRow(t("search.preview_width", "Preview Width"), width_widget, show_separator=False))
        
        self.layout.addWidget(self.group_preview)

    def _build_modes_section(self):
        from localization import t
        self.layout.addSpacing(25)
        self.lbl_modes = self._create_section_label(t("search.sec_modes", "SEARCH CATEGORIES"))
        
        self.group_modes = SettingsGroup()
        
        modes = [
            ("apps", t("search.mode_apps", "Applications")),
            ("files", t("search.mode_files", "Files & Documents")),
            ("clipboard", t("search.mode_clipboard", "Clipboard History")),
            ("emoji", t("search.mode_emoji", "Symbols & Emoji"))
        ]
        
        self.mode_switches = {}
        current_modes = self.service.get("enabled_modes") or []
        for i, (mode_key, label) in enumerate(modes):
            sw = Switch()
            sw.setChecked(mode_key in current_modes)
            sw.toggled.connect(lambda v, m=mode_key: self._toggle_mode(m, v))
            show_sep = i < len(modes) - 1
            self.group_modes.add_row(SettingsRow(label, sw, show_separator=show_sep))
            self.mode_switches[mode_key] = sw
            
        self.layout.addWidget(self.group_modes)
        
    def _toggle_mode(self, mode_key, enabled):
        current_modes = list(self.service.get("enabled_modes") or [])
        if enabled and mode_key not in current_modes:
            current_modes.append(mode_key)
        elif not enabled and mode_key in current_modes:
            current_modes.remove(mode_key)
        self.service.set("enabled_modes", current_modes)
        self.hero_card.update()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_install_status()

    def reset_to_root(self):
        self.refresh_install_status()

    def load_settings(self):
        self.service.load()
        
        if hasattr(self, 'sw_autostart'):
            self.sw_autostart.blockSignals(True)
            self.sw_autostart.setChecked(self.service.get("launch_at_login") is True)
            self.sw_autostart.blockSignals(False)

        if hasattr(self, 'edit_shortcut'):
            self.edit_shortcut.blockSignals(True)
            self.edit_shortcut.set_shortcut(self.service.get("launch_shortcut") or "<Super>space")
            self.edit_shortcut.blockSignals(False)

        if hasattr(self, 'sw_history'):
            self.sw_history.blockSignals(True)
            self.sw_history.setChecked(self.service.get("search_history") is not False)
            self.sw_history.blockSignals(False)

        if hasattr(self, 'sw_recent'):
            self.sw_recent.blockSignals(True)
            self.sw_recent.setChecked(self.service.get("recent_when_empty") is not False)
            self.sw_recent.blockSignals(False)
            
        if hasattr(self, 'sw_anim'):
            self.sw_anim.blockSignals(True)
            self.sw_anim.setChecked(self.service.get("animations") is not False)
            self.sw_anim.blockSignals(False)

        if hasattr(self, 'slider_limit'):
            self.slider_limit.blockSignals(True)
            self.slider_limit.setValue(self.service.get("results_limit") or 20)
            self.lbl_limit_val.setText(str(self.slider_limit.value()))
            self.slider_limit.blockSignals(False)

        if hasattr(self, 'seg_theme'):
            self.seg_theme.blockSignals(True)
            current_theme = self.service.get("theme") or "system"
            opts = [("system", "System"), ("light", "Light"), ("dark", "Dark")]
            idx = next((i for i, opt in enumerate(opts) if opt[0] == current_theme), 0)
            self.seg_theme.set_active_index(idx)
            self.seg_theme.blockSignals(False)

        if hasattr(self, 'slider_trans'):
            self.slider_trans.blockSignals(True)
            trans_val = self.service.get("transparency")
            if trans_val is None: trans_val = 0.7
            self.slider_trans.setValue(int(trans_val * 100))
            self.lbl_trans_val.setText(f"{self.slider_trans.value()}%")
            self.slider_trans.blockSignals(False)

        if hasattr(self, 'sw_preview'):
            self.sw_preview.blockSignals(True)
            self.sw_preview.setChecked(self.service.get("preview_enabled") is not False)
            self.sw_preview.blockSignals(False)

        if hasattr(self, 'slider_width'):
            self.slider_width.blockSignals(True)
            self.slider_width.setValue(self.service.get("preview_width") or 420)
            self.lbl_width_val.setText(f"{self.slider_width.value()}px")
            self.slider_width.blockSignals(False)

        if hasattr(self, 'mode_switches'):
            current_modes = self.service.get("enabled_modes") or []
            for mode_key, sw in self.mode_switches.items():
                sw.blockSignals(True)
                sw.setChecked(mode_key in current_modes)
                sw.blockSignals(False)
                
        if hasattr(self, 'hero_card'):
            self.hero_card.update()

    def update_style(self, _is_dark=False):
        is_dark = ThemeManager.is_dark
        style = f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; font-size: {Typography.SIZE_SMALL}px; margin-left: 20px; letter-spacing: 0.5px; text-transform: uppercase;"
        
        if hasattr(self, 'lbl_general'): self.lbl_general.setStyleSheet(style)
        if hasattr(self, 'lbl_appearance'): self.lbl_appearance.setStyleSheet(style)
        if hasattr(self, 'lbl_search'): self.lbl_search.setStyleSheet(style)
        if hasattr(self, 'lbl_preview'): self.lbl_preview.setStyleSheet(style)
        if hasattr(self, 'lbl_modes'): self.lbl_modes.setStyleSheet(style)
        if hasattr(self, 'lbl_features'): self.lbl_features.setStyleSheet(style)
        
        lbl_style = f"color: {Colors.TEXT_PRIMARY}; font-family: '{Typography.FONT_FAMILY}';"
        if hasattr(self, 'lbl_limit_val'): self.lbl_limit_val.setStyleSheet(lbl_style)
        if hasattr(self, 'lbl_trans_val'): self.lbl_trans_val.setStyleSheet(lbl_style)
        if hasattr(self, 'lbl_width_val'): self.lbl_width_val.setStyleSheet(lbl_style)
        
        # Uninstalled promo state styling
        if hasattr(self, 'promo_title'):
            self.promo_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: {Typography.WEIGHT_BOLD};")
        if hasattr(self, 'promo_desc'):
            self.promo_desc.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; line-height: 1.4;")
        if hasattr(self, 'promo_icon'):
            icon_bg = "rgba(10, 132, 255, 0.15)" if is_dark else "rgba(0, 122, 255, 0.1)"
            icon_color = "#0A84FF" if is_dark else "#007AFF"
            self.promo_icon.setStyleSheet(f"background: {icon_bg}; color: {icon_color}; border-radius: 14px; font-size: 26px;")
            
        if hasattr(self, 'btn_download'):
            btn_primary_bg = Colors.ACCENT_BLUE
            self.btn_download.setStyleSheet(f"""
                QPushButton {{
                    background: {btn_primary_bg};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 0 16px;
                }}
                QPushButton:hover {{
                    background: #0062cc;
                }}
            """)
            
        if hasattr(self, 'btn_check_again'):
            btn_sec_bg = "rgba(120, 120, 128, 0.18)" if is_dark else "rgba(120, 120, 128, 0.12)"
            btn_sec_hover = "rgba(120, 120, 128, 0.28)" if is_dark else "rgba(120, 120, 128, 0.20)"
            self.btn_check_again.setStyleSheet(f"""
                QPushButton {{
                    background: {btn_sec_bg};
                    color: {Colors.TEXT_PRIMARY};
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                    padding: 0 16px;
                }}
                QPushButton:hover {{
                    background: {btn_sec_hover};
                }}
            """)
        
        self.update()

    def get_search_target(self, target_id: str) -> QWidget | None:
        targets = {
            "spotlight.shortcut": getattr(self, "group_general", None),
            "spotlight.modes": getattr(self, "group_modes", None),
            "spotlight.preview": getattr(self, "group_preview", None),
        }
        return targets.get(target_id)
