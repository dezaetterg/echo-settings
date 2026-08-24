from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout
from PySide6.QtCore import Qt
from theme.colors import Colors
from theme.typography import Typography
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from components.switch import Switch
from components.popup_button import PopupButton
from components.segmented_control import SegmentedControl
from services.power_service import PowerService
from theme.manager import ThemeManager
from theme.styler import fix_label_styles

class PowerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = PowerService()
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 30, 40, 40)
        self.layout.setSpacing(24)
        self.layout.setAlignment(Qt.AlignTop)
        
        self._build_ui()
        
        self.layout.addStretch()
        
        scroll.setWidget(self.content)
        self.main_layout.addWidget(scroll)
        
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def update_style(self, _is_dark=False):
        fix_label_styles(self)
        self.update()

    def _build_ui(self):
        from localization import t
        # 0. Header Title
        title = QLabel(t("power.title", "Power"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};")
        self.layout.addWidget(title)

        bat_info = self.service.get_battery_info()
        
        # --- Battery Info ---
        self.bat_group = None
        if bat_info and bat_info.get('present'):
            lbl = QLabel("Battery")
            lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; letter-spacing: 0.5px;")
            self.layout.addWidget(lbl)
            
            self.bat_group = SettingsGroup()
            
            p_lbl = QLabel(f"{bat_info['percentage']}%")
            p_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_TITLE}px;")
            self.bat_group.add_row(SettingsRow("Current Charge", p_lbl, show_separator=True, is_interactive=False))
            
            s_lbl = QLabel(bat_info['state'].title())
            s_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px;")
            self.bat_group.add_row(SettingsRow("Status", s_lbl, show_separator=bat_info['time_to_full'] is not None or bat_info['time_to_empty'] is not None, is_interactive=False))
            
            if bat_info.get('time_to_full'):
                t_lbl = QLabel(bat_info['time_to_full'])
                t_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px;")
                self.bat_group.add_row(SettingsRow("Time to Full", t_lbl, show_separator=False, is_interactive=False))
            elif bat_info.get('time_to_empty'):
                t_lbl = QLabel(bat_info['time_to_empty'])
                t_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px;")
                self.bat_group.add_row(SettingsRow("Time to Empty", t_lbl, show_separator=False, is_interactive=False))
                
            self.layout.addWidget(self.bat_group)
            
        # --- Power Mode ---
        pm_lbl = QLabel(t("power.mode", "Power Mode"))
        pm_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;")
        self.layout.addWidget(pm_lbl)
        
        self.pm_group = SettingsGroup()
        
        prof = self.service.get_power_profile() or "balanced"
        options = [
            ("power-saver", t("power.saver", "Power Saver")),
            ("balanced", t("power.balanced", "Balanced")),
            ("performance", t("power.performance", "Performance"))
        ]
        
        prof_seg = SegmentedControl(options, prof)
        prof_seg.setMinimumWidth(380)
        
        def on_prof_changed(opt_id):
            self.service.set_power_profile(opt_id)
            
        prof_seg.valueChanged.connect(on_prof_changed)
        self.pm_group.add_row(SettingsRow(t("power.mode", "Power Profile"), prof_seg, show_separator=True, is_interactive=False))
            
        lp_sw = Switch()
        lp_sw.setChecked(self.service.get_low_power_mode())
        lp_sw.toggled.connect(self.service.set_low_power_mode)
        self.pm_group.add_row(SettingsRow(t("power.saver", "Low Power Mode"), lp_sw, show_separator=False, is_interactive=False))
        
        self.layout.addWidget(self.pm_group)
        
        # --- Display & Sleep ---
        disp_lbl = QLabel(t("power.screen_blank", "Display & Sleep"))
        disp_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;")
        self.layout.addWidget(disp_lbl)
        
        self.disp_group = SettingsGroup()
        
        # Display Sleep
        d_options = self.service.get_display_sleep_options()
        d_current = self.service.get_display_sleep()
        
        d_btn = PopupButton(d_options, d_current)
        d_btn.setMinimumWidth(150)
            
        def on_display_sleep(sec):
            self.service.set_display_sleep(sec)
            
        d_btn.valueChanged.connect(on_display_sleep)
        self.disp_group.add_row(SettingsRow(t("power.screen_blank", "Turn display off after"), d_btn, show_separator=True, is_interactive=False))
        
        # Computer Sleep
        c_current = self.service.get_computer_sleep()
        c_btn = PopupButton(d_options, c_current)
        c_btn.setMinimumWidth(150)
            
        def on_computer_sleep(sec):
            self.service.set_computer_sleep(sec)
            
        c_btn.valueChanged.connect(on_computer_sleep)
        self.disp_group.add_row(SettingsRow(t("power.auto_suspend", "Put computer to sleep after"), c_btn, show_separator=True, is_interactive=False))
        
        pb_options = self.service.get_power_button_options()
        pb_current = self.service.get_power_button_action()
        
        pb_btn = PopupButton(pb_options, pb_current)
        pb_btn.setMinimumWidth(150)
            
        def on_pb_action(action):
            self.service.set_power_button_action(action)
            
        pb_btn.valueChanged.connect(on_pb_action)
        self.disp_group.add_row(SettingsRow(t("power.button_action", "Power button action"), pb_btn, show_separator=False, is_interactive=False))
        self.layout.addWidget(self.disp_group)

    def get_search_target(self, target_id: str) -> QWidget | None:
        targets = {
            "power.battery": getattr(self, "bat_group", None) or getattr(self, "pm_group", None),
            "power.profile": getattr(self, "pm_group", None),
            "power.low_power": getattr(self, "pm_group", None),
            "power.screen_sleep": getattr(self, "disp_group", None),
            "power.sleep": getattr(self, "disp_group", None),
        }
        return targets.get(target_id)
