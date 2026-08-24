from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from theme.colors import Colors
from theme.typography import Typography
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from components.switch import Switch
from components.color_picker import ColorPicker
from components.theme_preview_card import ThemePreviewCard
from components.wallpaper_gallery import WallpaperGallery
from components.font_picker import FontPicker
from components.stepper import NumberStepper
from components.workspace_widgets import (
    WorkspaceHeaderRow, RadioOptionItem, WorkspaceRadioRow, InlineRadioGroup
)
from components.live_accent_preview import LiveAccentPreviewCard
from services.appearance_service import AppearanceService
from services.font_service import FontService
from theme.manager import ThemeManager
from theme.styler import fix_label_styles

class AppearancePage(QWidget):
    theme_switched = Signal(str)

    def __init__(self):
        super().__init__()
        self.service = AppearanceService()
        self.font_service = FontService()
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        self.scroll.viewport().setStyleSheet("background: transparent;")
        
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(36, 24, 36, 36)
        self.layout.setSpacing(16)
        self.layout.setAlignment(Qt.AlignTop)
        
        from localization import t
        # 0. Header Title
        title = QLabel(t("appearance.title", "Appearance"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};")
        self.layout.addWidget(title)
        # =========================================================================
        # 1. THEME SECTION
        # =========================================================================
        self.theme_lbl = self._create_section_label(t("appearance.theme", "THEME"), is_first=True)
        self.layout.addWidget(self.theme_lbl)
        
        theme_layout = QHBoxLayout()
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(14)
        
        current = self.service.get_theme()
        light_preview = ThemePreviewCard(t("appearance.light", "Light"), is_dark=False, is_auto=False, is_selected=current == "default")
        light_preview.theme_type = "default"
        dark_preview = ThemePreviewCard(t("appearance.dark", "Dark"), is_dark=True, is_auto=False, is_selected=current == "prefer-dark")
        dark_preview.theme_type = "prefer-dark"
        auto_preview = ThemePreviewCard(t("appearance.auto", "Auto"), is_dark=False, is_auto=True, is_selected=current == "auto")
        auto_preview.theme_type = "auto"
        
        self.previews = [light_preview, dark_preview, auto_preview]
        
        for p in self.previews:
            p.clicked.connect(lambda checked=False, t=p.theme_type: self._on_theme_selected(t))
            theme_layout.addWidget(p)
            
        self.theme_container = QWidget()
        self.theme_container.setLayout(theme_layout)
        self.layout.addWidget(self.theme_container)
        
        # =========================================================================
        # 2. ACCENT COLOR SECTION
        # =========================================================================
        self.accent_lbl = self._create_section_label(t("appearance.accent_color", "ACCENT COLOR"))
        self.layout.addWidget(self.accent_lbl)
        
        ACCENT_COLORS = {
            "multicolor": "multicolor",
            "blue": "#007AFF",
            "purple": "#AF52DE",
            "pink": "#FF2D55",
            "red": "#FF3B30",
            "orange": "#FF9500",
            "yellow": "#FFCC00",
            "green": "#28CD41",
            "teal": "#5AC8FA",
            "slate": "#8E8E93"
        }
        
        current_accent = self.service.get_accent_color()
        self.accent_group = SettingsGroup()
        color_picker = ColorPicker(ACCENT_COLORS, current_accent)
        color_picker.color_changed.connect(self._on_accent_changed)
        self.accent_group.add_row(SettingsRow(t("appearance.system_accent", "System Accent"), color_picker, show_separator=False, is_interactive=False))
        self.layout.addWidget(self.accent_group)

        # =========================================================================
        # 3. WALLPAPER SECTION
        # =========================================================================
        self.wall_lbl = self._create_section_label("WALLPAPER")
        self.layout.addWidget(self.wall_lbl)
        
        self.gallery = WallpaperGallery(self.service)
        self.layout.addWidget(self.gallery)
        
        # =========================================================================
        # 4. SYSTEM FONTS SECTION
        # =========================================================================
        self.font_lbl = None
        if self.font_service.is_supported():
            self.font_lbl = self._create_section_label("SYSTEM FONTS")
            self.layout.addWidget(self.font_lbl)
            
            font_group = SettingsGroup()
            fonts = self.font_service.installed_fonts
            
            if self.font_service.get_interface_font():
                self.iface_picker = FontPicker("Interface Font", fonts, self.font_service.get_interface_font(), show_separator=True)
                self.iface_picker.font_changed.connect(self._on_interface_font_changed)
                font_group.add_row(self.iface_picker)
                
            if self.font_service.get_document_font():
                self.doc_picker = FontPicker("Document Font", fonts, self.font_service.get_document_font(), show_separator=True)
                self.doc_picker.font_changed.connect(self.font_service.set_document_font)
                font_group.add_row(self.doc_picker)
                
            if self.font_service.get_monospace_font():
                self.mono_picker = FontPicker("Monospace Font", fonts, self.font_service.get_monospace_font(), show_separator=False, is_monospace=True)
                self.mono_picker.font_changed.connect(self.font_service.set_monospace_font)
                font_group.add_row(self.mono_picker)
                
            self.layout.addWidget(font_group)

        # =========================================================================
        # 5. WORKSPACE & DESKTOP SECTION (GNOME / Supported DEs Only)
        # =========================================================================
        has_hc = self.service.is_hot_corners_supported()
        has_mt = self.service.is_multitasking_supported()

        if has_hc or has_mt:
            self.ws_section_lbl = self._create_section_label(t("appearance.workspace_desktop", "WORKSPACE & DESKTOP"))
            self.layout.addWidget(self.ws_section_lbl)

            # --- 5.1 Hot Corner Card ---
            if has_hc:
                self.hot_corner_group = SettingsGroup()
                is_hc_enabled = self.service.get_hot_corners_enabled()
                self.switch_hot_corner = Switch(checked=is_hc_enabled)
                self.switch_hot_corner.toggled.connect(self._on_hot_corner_toggled)

                hc_hdr = WorkspaceHeaderRow(
                    "hot_corners", "#007AFF", t("appearance.hot_corners", "Hot Corner"),
                    t("appearance.hot_corners_sub", "Open the Activities Overview by pushing the pointer to the top-left corner of the screen."),
                    right_widget=self.switch_hot_corner
                )
                self.hot_corner_group.layout.addWidget(hc_hdr)
                self.layout.addWidget(self.hot_corner_group)
            else:
                self.hot_corner_group = None

            # --- 5.2 Workspaces Card ---
            if has_mt:
                self.workspaces_group = SettingsGroup()
                ws_hdr = WorkspaceHeaderRow(
                    "workspaces", "#34C759", t("appearance.workspaces", "Workspaces"),
                    t("appearance.workspaces_dynamic_desc", "Manage how workspaces are created and displayed.")
                )
                self.workspaces_group.layout.addWidget(ws_hdr)

                is_dynamic = self.service.get_is_dynamic_workspaces()
                self.radio_dynamic = RadioOptionItem(
                    "dynamic",
                    t("appearance.workspaces_dynamic", "Dynamic Workspaces"),
                    t("appearance.workspaces_dynamic_desc", "Automatically remove empty workspaces."),
                    is_checked=is_dynamic
                )
                self.radio_dynamic.clicked.connect(lambda: self._set_workspace_mode("dynamic"))
                self.workspaces_group.layout.addWidget(WorkspaceRadioRow(self.radio_dynamic, show_separator=True))

                self.radio_fixed = RadioOptionItem(
                    "fixed",
                    t("appearance.workspaces_fixed", "Fixed Workspaces"),
                    t("appearance.workspaces_fixed_desc", "Use a fixed number of workspaces."),
                    is_checked=not is_dynamic
                )
                self.radio_fixed.clicked.connect(lambda: self._set_workspace_mode("fixed"))
                self.radio_fixed_row = WorkspaceRadioRow(self.radio_fixed, show_separator=not is_dynamic)
                self.workspaces_group.layout.addWidget(self.radio_fixed_row)

                cur_num_ws = self.service.get_num_workspaces()
                self.ws_stepper = NumberStepper(value=cur_num_ws, min_val=1, max_val=32)
                self.ws_stepper.valueChanged.connect(self._on_num_workspaces_changed)
                self.num_ws_row = SettingsRow(t("appearance.num_workspaces", "Number of Workspaces"), self.ws_stepper, show_separator=False, is_interactive=False)
                self.num_ws_row.setVisible(not is_dynamic)
                self.workspaces_group.add_row(self.num_ws_row)

                self.layout.addWidget(self.workspaces_group)

                # --- 5.3 Workspaces on Displays Card ---
                displays_group = SettingsGroup()
                is_primary_only = self.service.get_workspaces_only_on_primary()

                disp_hdr = WorkspaceHeaderRow(
                    "displays", "#FF9500", t("appearance.multiple_displays", "Multiple Displays"),
                    t("appearance.multiple_displays_sub", "Choose how workspaces are shown on multiple monitors.")
                )
                displays_group.layout.addWidget(disp_hdr)

                self.radio_disp_primary = RadioOptionItem(
                    "primary",
                    t("appearance.ws_primary_only", "Primary Display Only"),
                    t("appearance.ws_primary_only_desc", "Workspaces are only on the primary display."),
                    is_checked=is_primary_only
                )
                self.radio_disp_primary.clicked.connect(lambda: self._set_displays_mode("primary"))
                displays_group.layout.addWidget(WorkspaceRadioRow(self.radio_disp_primary, show_separator=True))

                self.radio_disp_all = RadioOptionItem(
                    "all",
                    t("appearance.ws_all_displays", "All Displays"),
                    t("appearance.ws_all_displays_desc", "Workspaces are on each display."),
                    is_checked=not is_primary_only
                )
                self.radio_disp_all.clicked.connect(lambda: self._set_displays_mode("all"))
                displays_group.layout.addWidget(WorkspaceRadioRow(self.radio_disp_all, show_separator=False))

                self.layout.addWidget(displays_group)

                # --- 5.4 Application Switching Card ---
                app_switch_group = SettingsGroup()
                is_current_only = self.service.get_app_switcher_current_workspace_only()

                app_hdr = WorkspaceHeaderRow(
                    "app_switching", "#32ADE6", t("appearance.app_switching", "Application Switching"),
                    t("appearance.app_switching_sub", "Choose which windows appear when switching between applications.")
                )
                app_switch_group.layout.addWidget(app_hdr)

                self.radio_app_all = RadioOptionItem(
                    "all",
                    t("appearance.app_all_ws", "All Workspaces"),
                    t("appearance.app_all_ws_desc", "Switching includes applications from all workspaces."),
                    is_checked=not is_current_only
                )
                self.radio_app_all.clicked.connect(lambda: self._set_app_switching_mode("all"))
                app_switch_group.layout.addWidget(WorkspaceRadioRow(self.radio_app_all, show_separator=True))

                self.radio_app_current = RadioOptionItem(
                    "current",
                    t("appearance.app_current_ws", "Current Workspace Only"),
                    t("appearance.app_current_ws_desc", "Switching only includes applications on the current workspace."),
                    is_checked=is_current_only
                )
                self.radio_app_current.clicked.connect(lambda: self._set_app_switching_mode("current"))
                app_switch_group.layout.addWidget(WorkspaceRadioRow(self.radio_app_current, show_separator=False))

                self.layout.addWidget(app_switch_group)
        else:
            self.ws_section_lbl = None
            self.hot_corner_group = None
            self.workspaces_group = None


        self.layout.addStretch()
        
        self.scroll.setWidget(self.content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)
        
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def _create_section_label(self, text: str, is_first: bool = False) -> QLabel:
        lbl = QLabel(text)
        top_margin = 4 if is_first else 28
        lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; "
            f"font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: {top_margin}px; letter-spacing: 0.5px;"
        )
        return lbl

    def update_style(self, _is_dark=False):
        for attr in ['theme_lbl', 'accent_lbl', 'wall_lbl', 'font_lbl', 'ws_section_lbl']:
            lbl = getattr(self, attr, None)
            if lbl:
                top_m = 4 if attr == 'theme_lbl' else 28
                lbl.setStyleSheet(
                    f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; "
                    f"font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: {top_m}px; letter-spacing: 0.5px;"
                )
            
        fix_label_styles(self)
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_settings()

    def refresh_settings(self):
        current_mode = self.service.get_theme_mode()
        for p in self.previews:
            p.set_selected(p.theme_type == current_mode)

    def _on_theme_selected(self, theme_name):
        for p in self.previews:
            p.set_selected(p.theme_type == theme_name)
        self.service.set_theme(theme_name)
        self.theme_switched.emit(theme_name)
        
    def _on_accent_changed(self, color_hex):
        self.service.set_accent_color(color_hex)
        
    def _on_interface_font_changed(self, new_font):
        self.font_service.set_interface_font(new_font)

    def _on_hot_corner_toggled(self, enabled: bool):
        self.service.set_hot_corners_enabled(enabled)

    def _set_workspace_mode(self, mode_id: str):
        is_dynamic = (mode_id == "dynamic")
        self.radio_dynamic.setChecked(is_dynamic)
        self.radio_fixed.setChecked(not is_dynamic)
        self.service.set_dynamic_workspaces(is_dynamic)
        self.radio_fixed_row.show_separator = not is_dynamic
        self.radio_fixed_row.update()
        self.num_ws_row.setVisible(not is_dynamic)

    def _on_num_workspaces_changed(self, val: int):
        self.service.set_num_workspaces(val)

    def _set_displays_mode(self, mode_id: str):
        is_primary_only = (mode_id == "primary")
        self.radio_disp_primary.setChecked(is_primary_only)
        self.radio_disp_all.setChecked(not is_primary_only)
        self.service.set_workspaces_only_on_primary(is_primary_only)

    def _set_app_switching_mode(self, scope_id: str):
        current_only = (scope_id == "current")
        self.radio_app_current.setChecked(current_only)
        self.radio_app_all.setChecked(not current_only)
        self.service.set_app_switcher_current_workspace_only(current_only)

    def get_search_target(self, target_id: str) -> QWidget | None:
        targets = {
            "appearance.theme": getattr(self, "theme_container", None),
            "appearance.accent": getattr(self, "accent_group", None),
            "appearance.contrast": getattr(self, "contrast_group", None),
            "appearance.hot_corners": getattr(self, "hot_corner_group", None),
            "appearance.workspaces": getattr(self, "workspaces_group", None),
        }
        return targets.get(target_id)
