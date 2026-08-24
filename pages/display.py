from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath
from theme.colors import Colors
from theme.typography import Typography
from theme.metrics import CARD_RADIUS
from theme.manager import ThemeManager
from theme.styler import fix_label_styles
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from components.segmented_control import SegmentedControl
from components.switch import Switch
from components.popup_button import PopupButton
from components.slider import Slider
from services.display_service import DisplayService
from components.monitor_arrangement import MonitorArrangementWidget
from components.display_monitor_view import DisplayStageWidget
from components.display_summary_card import DisplaySummaryCard
from localization import Localization, t


class MonitorArrangementDialog(QDialog):
    """Modal dialog sheet for arranging multiple display positions."""
    def __init__(self, service: DisplayService, parent=None):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle(t("display.arrange_btn", "Arrange Displays"))
        self.setFixedSize(620, 440)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel(t("display.arrange_btn", "Arrange Displays"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: {Typography.WEIGHT_BOLD};")
        layout.addWidget(title)

        desc = QLabel(t("display.subtitle", "Drag displays to rearrange their physical alignment."))
        desc.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(desc)

        monitors = self.service.get_monitors()
        self.arrangement_widget = MonitorArrangementWidget(monitors, parent=self)
        self.arrangement_widget.arrangement_changed.connect(self.service.update_arrangement)
        layout.addWidget(self.arrangement_widget)

        button_box = QHBoxLayout()
        button_box.addStretch()
        self.done_btn = QPushButton(t("common.done", "Done"))
        self.done_btn.setFixedSize(100, 32)
        self.done_btn.setCursor(Qt.PointingHandCursor)
        self.done_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #007AFF;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #0062CC;
            }}
        """)
        self.done_btn.clicked.connect(self.accept)
        button_box.addWidget(self.done_btn)
        layout.addLayout(button_box)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        is_dark = ThemeManager.is_dark
        bg_color = QColor(28, 28, 30) if is_dark else QColor(245, 245, 247)
        p.fillRect(self.rect(), bg_color)


class DisplayPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = DisplayService()
        self.summary_cards: list[DisplaySummaryCard] = []

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        self.scroll.viewport().setStyleSheet("background: transparent;")

        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 30, 40, 40)
        self.layout.setSpacing(20)
        self.layout.setAlignment(Qt.AlignTop)

        self._build_ui()
        self.layout.addStretch()

        self.scroll.setWidget(self.content)
        self.main_layout.addWidget(self.scroll)

        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def update_style(self, _is_dark=False):
        fix_label_styles(self)
        if hasattr(self, 'arrange_btn'):
            self._apply_arrange_btn_style()
        if hasattr(self, 'title_lbl'):
            self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD}; background: transparent;")
        if hasattr(self, 'subtitle_lbl'):
            self.subtitle_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px; background: transparent;")
        self.update()

    def _apply_arrange_btn_style(self):
        if not hasattr(self, 'arrange_btn') or self.arrange_btn is None:
            return
        is_dark = ThemeManager.is_dark
        if is_dark:
            bg = "rgba(120, 120, 128, 0.24)"
            bg_hover = "rgba(120, 120, 128, 0.38)"
            color = "#AEAEB2"
            border = "rgba(120, 120, 128, 0.4)"
        else:
            bg = "rgba(100, 100, 100, 0.08)"
            bg_hover = "rgba(100, 100, 100, 0.16)"
            color = Colors.TEXT_PRIMARY
            border = Colors.CARD_BORDER
        self.arrange_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                border: 1px solid {border};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
            }}
        """)

    def _create_section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; "
            f"font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px; background: transparent;"
        )
        return lbl

    def _build_ui(self):
        self._widgets = []

        def keep(widget):
            self._widgets.append(widget)
            return widget

        # ── 1. Header Title & Subtitle ──
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        header_layout.setContentsMargins(0, 0, 0, 4)

        self.title_lbl = keep(QLabel(t("nav.display", "Display")))
        self.title_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD}; background: transparent;"
        )
        header_layout.addWidget(self.title_lbl)

        self.subtitle_lbl = keep(QLabel(t("display.subtitle", "Manage your connected displays, resolution, refresh rate and color settings.")))
        self.subtitle_lbl.setWordWrap(True)
        self.subtitle_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px; background: transparent;"
        )
        header_layout.addWidget(self.subtitle_lbl)
        self.layout.addLayout(header_layout)

        monitors = self.service.get_monitors()
        if not monitors:
            lbl = keep(QLabel(t("display.no_displays", "No displays found.")))
            lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 14px; padding: 20px;")
            self.layout.addWidget(lbl)
            return

        active_id = self.service.active_monitor_id or monitors[0].id

        # ── 2. Hardware 3D Monitor Stage ──
        self.stage_widget = keep(DisplayStageWidget(monitors, active_id=active_id))
        self.stage_widget.monitor_selected.connect(self._on_monitor_selected)
        self.layout.addWidget(self.stage_widget)

        # ── 3. Connected Displays Summary Cards Strip ──
        if len(monitors) >= 2:
            self.cards_layout = QHBoxLayout()
            self.cards_layout.setSpacing(16)
        else:
            self.cards_layout = QVBoxLayout()
            self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.summary_cards = []

        hdr_supp = self.service.has_hdr() if hasattr(self.service, "has_hdr") else False
        for mon in monitors:
            card = keep(DisplaySummaryCard(mon, is_selected=(mon.id == active_id), hdr_supported=hdr_supp))
            card.clicked.connect(self._on_monitor_selected)
            self.cards_layout.addWidget(card)
            self.summary_cards.append(card)

        self.layout.addLayout(self.cards_layout)

        # ── 4. Arrange Displays Action ──
        self.arrange_btn = keep(QPushButton(t("display.arrange_btn", "Arrange Displays...")))
        self.arrange_btn.setMinimumSize(180, 32)
        self.arrange_btn.setCursor(Qt.PointingHandCursor)
        self._apply_arrange_btn_style()
        self.arrange_btn.clicked.connect(self._open_arrangement_dialog)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 4, 0, 8)
        btn_layout.addStretch()
        btn_layout.addWidget(self.arrange_btn)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

        # ── 5. Detail Controls: Layout & Position ──
        self.layout_section_lbl = keep(self._create_section_label(t("display.layout_position", "LAYOUT & POSITION")))
        self.layout.addWidget(self.layout_section_lbl)
        self.geom_group = keep(SettingsGroup())

        # Resolution
        res_options = self.service.get_resolution_options()
        res_current = self.service.get_current_resolution()
        self.res_btn = keep(PopupButton(res_options, res_current))
        self.res_btn.setMinimumWidth(160)
        self.res_btn.valueChanged.connect(self._on_resolution_changed)
        self.res_row = keep(SettingsRow(t("display.resolution", "Resolution"), self.res_btn, show_separator=True, is_interactive=False))
        self.geom_group.add_row(self.res_row)

        # Refresh Rate
        rr_options = self.service.get_refresh_rate_options()
        rr_current = self.service.get_current_refresh_rate()
        self.rr_btn = keep(PopupButton(rr_options, rr_current))
        self.rr_btn.setMinimumWidth(160)
        self.rr_btn.valueChanged.connect(self._on_refresh_rate_changed)
        self.rr_row = keep(SettingsRow(t("display.refresh_rate", "Refresh Rate"), self.rr_btn, show_separator=True, is_interactive=False))
        self.geom_group.add_row(self.rr_row)

        # Orientation
        orient_current = self.service.get_current_orientation()
        orient_opts = {
            "0": t("display.orient_std", "Standard (0°)"),
            "1": t("display.orient_90r", "90° Right"),
            "3": t("display.orient_90l", "90° Left"),
            "2": t("display.orient_180", "180°")
        }
        self.orient_btn = keep(PopupButton(orient_opts, orient_current))
        self.orient_btn.setMinimumWidth(160)
        self.orient_btn.valueChanged.connect(self.service.set_orientation)
        self.orient_row = keep(SettingsRow(t("display.orientation", "Orientation"), self.orient_btn, show_separator=True, is_interactive=False))
        self.geom_group.add_row(self.orient_row)

        # Make Main Display
        self.main_disp_sw = keep(Switch())
        self.main_disp_sw.setChecked(self.service.is_primary())
        self.main_disp_sw.toggled.connect(self._on_primary_toggled)
        self.main_disp_row = keep(SettingsRow(t("display.use_as_main", "Use as Main Display"), self.main_disp_sw, show_separator=True, is_interactive=False))
        self.geom_group.add_row(self.main_disp_row)

        # Scale
        scale_list = [("1.0", "100%"), ("1.25", "125%"), ("1.5", "150%"), ("2.0", "200%")]
        scale_current = self.service.get_current_scale()
        if scale_current not in dict(scale_list):
            scale_current = "1.0"
        self.scale_seg = keep(SegmentedControl(scale_list, scale_current))
        self.scale_seg.valueChanged.connect(self.service.set_scale)
        self.scale_row = keep(SettingsRow(t("display.scale", "Scale"), self.scale_seg, show_separator=False, is_interactive=False))
        self.geom_group.add_row(self.scale_row)

        self.layout.addWidget(self.geom_group)

        self.scale_desc = keep(QLabel(t("display.scale_desc", "Larger text may reduce available space on screen.")))
        self.scale_desc.setWordWrap(True)
        self.scale_desc.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: -16px; margin-bottom: 12px;"
        )
        self.layout.addWidget(self.scale_desc)

        # ── 6. Detail Controls: Brightness & Display ──
        self.bright_section_lbl = keep(self._create_section_label(t("display.brightness", "BRIGHTNESS")))
        self.layout.addWidget(self.bright_section_lbl)
        self.color_group = keep(SettingsGroup())

        # Display Brightness
        self.bright_slider = keep(Slider(Qt.Horizontal))
        self.bright_slider.setRange(1, 100)
        self.bright_slider.setValue(self.service.get_brightness())
        self.bright_slider.valueChanged.connect(self.service.set_brightness)
        self.bright_row = keep(SettingsRow(t("display.brightness", "Brightness"), self.bright_slider, show_separator=True, is_interactive=False))
        self.color_group.add_row(self.bright_row)

        # High Dynamic Range (HDR)
        self.hdr_sw = keep(Switch())
        self.hdr_sw.setChecked(self.service.is_hdr_enabled())
        self.hdr_sw.toggled.connect(self.service.set_hdr_enabled)
        self.hdr_row = keep(SettingsRow(t("display.enable_hdr", "High Dynamic Range (HDR)"), self.hdr_sw, show_separator=False, is_interactive=False))
        self.color_group.add_row(self.hdr_row)

        self.layout.addWidget(self.color_group)

        # ── 7. Detail Controls: Gaming & Performance ──
        self.game_section_lbl = keep(self._create_section_label(t("display.gaming_perf", "GAMING & PERFORMANCE")))
        self.layout.addWidget(self.game_section_lbl)
        self.game_group = keep(SettingsGroup())

        # VRR
        vrr_opts = {
            "off": t("display.vrr_off", "Off"),
            "always": t("display.vrr_always", "Always"),
            "fullscreen": t("display.vrr_fullscreen", "Fullscreen Only")
        }
        self.vrr_btn = keep(PopupButton(vrr_opts, self.service.get_vrr_mode()))
        self.vrr_btn.setMinimumWidth(160)
        self.vrr_btn.valueChanged.connect(self.service.set_vrr_mode)
        self.vrr_row = keep(SettingsRow(t("display.vrr", "Variable Refresh Rate"), self.vrr_btn, show_separator=True, is_interactive=False))
        self.game_group.add_row(self.vrr_row)

        # V-Sync
        self.vsync_sw = keep(Switch())
        self.vsync_sw.setChecked(self.service.is_vsync_enabled())
        self.vsync_sw.toggled.connect(self.service.set_vsync_enabled)
        self.vsync_row = keep(SettingsRow(t("display.vsync", "V-Sync / TearFree"), self.vsync_sw, show_separator=True, is_interactive=False))
        self.game_group.add_row(self.vsync_row)

        # Response Time
        resp_opts = {
            "normal": t("display.resp_normal", "Normal"),
            "fast": t("display.resp_fast", "Fast"),
            "faster": t("display.resp_faster", "Faster")
        }
        self.resp_btn = keep(PopupButton(resp_opts, self.service.get_response_time()))
        self.resp_btn.setMinimumWidth(160)
        self.resp_btn.valueChanged.connect(self.service.set_response_time)
        self.resp_row = keep(SettingsRow(t("display.response_time", "Response Time"), self.resp_btn, show_separator=False, is_interactive=False))
        self.game_group.add_row(self.resp_row)

        self.layout.addWidget(self.game_group)

        # ── 8. Detail Controls: Display Protection ──
        self.prot_section_lbl = keep(self._create_section_label(t("display.protection", "DISPLAY PROTECTION")))
        self.layout.addWidget(self.prot_section_lbl)
        self.prot_group = keep(SettingsGroup())

        # Night Shift
        self.ns_sw = keep(Switch())
        self.ns_sw.setChecked(self.service.is_night_shift_enabled())
        self.ns_sw.toggled.connect(self.service.set_night_shift_enabled)
        self.ns_row = keep(SettingsRow(t("display.night_shift", "Night Shift"), self.ns_sw, show_separator=True, is_interactive=False))
        self.prot_group.add_row(self.ns_row)

        # Night Shift Schedule
        sched_options = self.service.get_night_shift_schedule_options()
        sched_current = self.service.get_night_shift_schedule()
        self.sched_btn = keep(PopupButton(sched_options, sched_current))
        self.sched_btn.setMinimumWidth(160)
        self.sched_btn.valueChanged.connect(self.service.set_night_shift_schedule)
        self.sched_row = keep(SettingsRow(t("display.schedule", "Schedule"), self.sched_btn, show_separator=True, is_interactive=False))
        self.prot_group.add_row(self.sched_row)

        # Screen Dim
        dim_opts = {
            "5m": t("power.5m", "5 minutes"),
            "15m": t("power.15m", "15 minutes"),
            "never": t("power.never", "Never")
        }
        self.dim_btn = keep(PopupButton(dim_opts, self.service.get_idle_delay()))
        self.dim_btn.setMinimumWidth(160)
        self.dim_btn.valueChanged.connect(self.service.set_idle_delay)
        self.dim_row = keep(SettingsRow(t("display.dim_sleep", "Screen Dim / Sleep"), self.dim_btn, show_separator=False, is_interactive=False))
        self.prot_group.add_row(self.dim_row)

        self.layout.addWidget(self.prot_group)

    def _open_arrangement_dialog(self):
        dlg = MonitorArrangementDialog(self.service, parent=self.window())
        dlg.exec()
        # Refresh state after arrangement dialog closed
        self._refresh_monitors_ui()

    def _on_monitor_selected(self, monitor_id: str):
        self.service.set_active_monitor(monitor_id)
        if hasattr(self, 'stage_widget'):
            self.stage_widget.set_active_monitor(monitor_id)
        for card in self.summary_cards:
            card.set_selected(card.monitor.id == monitor_id)
        self._sync_active_controls()

    def _on_resolution_changed(self, res: str):
        self.service.set_resolution(res)
        # Update refresh rate options for newly selected resolution
        rr_opts = self.service.get_refresh_rate_options(resolution=res)
        current_rr = self.service.get_current_refresh_rate()
        self.rr_btn.set_options(rr_opts, current_rr)
        self._refresh_monitors_ui()

    def _on_refresh_rate_changed(self, rate: str):
        self.service.set_refresh_rate(rate)
        self._refresh_monitors_ui()

    def _on_primary_toggled(self, checked: bool):
        self.service.set_primary(checked)
        self._refresh_monitors_ui()

    def _refresh_monitors_ui(self):
        monitors = self.service.get_monitors()
        active_id = self.service.active_monitor_id
        hdr_supp = self.service.has_hdr() if hasattr(self.service, "has_hdr") else False
        if hasattr(self, 'stage_widget'):
            self.stage_widget.update_monitors(monitors, active_id)
        for i, card in enumerate(self.summary_cards):
            if i < len(monitors):
                card.update_monitor(monitors[i], hdr_supported=hdr_supp)
                card.set_selected(monitors[i].id == active_id)
        self._sync_active_controls()

    def _sync_active_controls(self):
        # Update Resolution dropdown
        res_opts = self.service.get_resolution_options()
        current_res = self.service.get_current_resolution()
        self.res_btn.set_options(res_opts, current_res)

        # Update Refresh Rate dropdown
        rr_opts = self.service.get_refresh_rate_options()
        current_rr = self.service.get_current_refresh_rate()
        self.rr_btn.set_options(rr_opts, current_rr)

        # Update Orientation
        orient = self.service.get_current_orientation()
        self.orient_btn.set_value(orient)

        # Update Primary Switch
        self.main_disp_sw.blockSignals(True)
        self.main_disp_sw.setChecked(self.service.is_primary())
        self.main_disp_sw.blockSignals(False)

        # Update Scale
        scale = self.service.get_current_scale()
        self.scale_seg.set_value(scale)

        # Update Brightness & HDR
        self.bright_slider.blockSignals(True)
        self.bright_slider.setValue(self.service.get_brightness())
        self.bright_slider.blockSignals(False)

        self.hdr_sw.blockSignals(True)
        self.hdr_sw.setChecked(self.service.is_hdr_enabled())
        self.hdr_sw.blockSignals(False)

    def get_search_target(self, target_id: str) -> QWidget | None:
        targets = {
            "display.resolution": getattr(self, "geom_group", None),
            "display.refresh_rate": getattr(self, "geom_group", None),
            "display.scale": getattr(self, "geom_group", None),
            "display.arrange": getattr(self, "arrange_btn", None) or getattr(self, "geom_group", None),
            "display.night_shift": getattr(self, "prot_group", None),
        }
        return targets.get(target_id)
