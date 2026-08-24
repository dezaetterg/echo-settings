from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt
from theme.colors import Colors
from theme.typography import Typography
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from components.slider import Slider
from components.switch import Switch
from components.popup_button import PopupButton
from services.sound_service import SoundService
from theme.manager import ThemeManager
from theme.typography import Typography
from theme.colors import Colors
from theme.styler import fix_label_styles
from PySide6.QtWidgets import QHBoxLayout, QLabel
from components.animated_button import AnimatedButton
from components.device_selector import DeviceSelector
from PySide6.QtCore import QTimer
from pages.storage import InfoCard

class SoundPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = SoundService()
        
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

    def hideEvent(self, event):
        super().hideEvent(event)
        if hasattr(self, 'is_mic_testing') and self.is_mic_testing:
            self.is_mic_testing = False
            self.mic_test_btn.setText("Test")
            if hasattr(self, 'mic_monitor'):
                self.mic_monitor.stop()
            if hasattr(self, 'mic_indicator'):
                self.mic_indicator.set_level(0.0)

    def _build_ui(self):
        from localization import t
        # 0. Header Title
        title = QLabel(t("sound.title", "Sound"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};")
        self.layout.addWidget(title)

        # --- Output ---
        out_lbl = QLabel(t("sound.output", "OUTPUT"))
        out_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 4px; letter-spacing: 0.5px;")
        self.layout.addWidget(out_lbl)
        
        from components.output_hero import OutputHeroCard
        self.output_hero = OutputHeroCard(self.service)
        self.layout.addWidget(self.output_hero)
        
        out_devices = self.service.get_output_devices()
        active_out = self.service.get_active_output_device()
        self.out_selector = DeviceSelector(out_devices, active_out)
        
        def on_out_device_changed(name):
            self.service.set_active_output_device(name)
            QTimer.singleShot(300, lambda: self.out_selector.set_devices(self.service.get_output_devices(), name))
            QTimer.singleShot(300, self.update_device_info)
            
        self.out_selector.deviceSelected.connect(on_out_device_changed)
        self.layout.addWidget(self.out_selector)
        
        self.out_group = SettingsGroup()
        
        vol_slider = Slider()
        vol_slider.setValue(self.service.get_output_volume())
        vol_slider.setMinimumWidth(200)
        vol_slider.valueChanged.connect(self.service.set_output_volume)
        self.out_group.add_row(SettingsRow(t("sound.output_volume", "Output Volume"), vol_slider, show_separator=False, is_interactive=False))
        
        # Test Speakers Button
        self.test_speakers_btn = AnimatedButton(t("sound.test", "Test"))
        self.test_speakers_btn.setMinimumWidth(90)
        self.test_speakers_btn.clicked.connect(self.service.test_speakers)
        
        # Balance Slider
        bal_val = self.service.get_output_balance()
        if bal_val is not None:
            self.bal_slider = Slider()
            self.bal_slider.setMinimum(0)
            self.bal_slider.setMaximum(100)
            self.bal_slider.setValue(int(bal_val * 100))
            self.bal_slider.setMinimumWidth(180)
            
            def on_balance_change(val):
                self.service.set_output_balance(val / 100.0)
                
            self.bal_slider.valueChanged.connect(on_balance_change)
            
            bal_layout = QHBoxLayout()
            bal_layout.setContentsMargins(0, 0, 0, 0)
            l_lbl = QLabel("L")
            r_lbl = QLabel("R")
            for lbl in (l_lbl, r_lbl):
                lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: bold;")
            bal_layout.addWidget(l_lbl)
            bal_layout.addWidget(self.bal_slider)
            bal_layout.addWidget(r_lbl)
            
            bal_widget = QWidget()
            bal_widget.setLayout(bal_layout)
            
            self.out_group.add_row(SettingsRow(t("sound.balance", "Balance"), bal_widget, show_separator=True, is_interactive=False))
            
        self.out_group.add_row(SettingsRow(t("sound.test_speakers", "Test Speakers"), self.test_speakers_btn, show_separator=False, is_interactive=False))
        
        self.layout.addWidget(self.out_group)
        
        self.dev_info_card = InfoCard(t("sound.device_info", "Output Device Info"))
        self.dev_info_keys = ["Name", "Connection", "Channels", "Sample Rate", "State"]
        for k in self.dev_info_keys:
            self.dev_info_card.add_row(k, "—")
        self.layout.addWidget(self.dev_info_card)
        self.layout.addSpacing(10)
        
        self.update_device_info()
        
        # --- Input ---
        in_lbl = QLabel(t("sound.input", "INPUT"))
        in_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;")
        self.layout.addWidget(in_lbl)
        
        in_devices = self.service.get_input_devices()
        active_in = self.service.get_active_input_device()
        
        self.in_selector = DeviceSelector(in_devices, active_in)
        def on_in_device_changed(name):
            self.service.set_active_input_device(name)
            QTimer.singleShot(300, lambda: self.in_selector.set_devices(self.service.get_input_devices(), name))
            
        self.in_selector.deviceSelected.connect(on_in_device_changed)
        self.layout.addWidget(self.in_selector)
        
        in_group = SettingsGroup()
        
        mic_slider = Slider()
        mic_slider.setValue(self.service.get_input_volume())
        mic_slider.setMinimumWidth(200)
        mic_slider.valueChanged.connect(self.service.set_input_volume)
        in_group.add_row(SettingsRow(t("sound.input_volume", "Input Volume"), mic_slider, show_separator=True, is_interactive=False))
        
        from components.mic_level import MicLevelIndicator
        self.mic_indicator = MicLevelIndicator()
        
        self.mic_test_btn = AnimatedButton(t("sound.test", "Test"))
        self.mic_test_btn.setMinimumWidth(90)
        
        self.is_mic_testing = False
        def toggle_mic_test():
            self.is_mic_testing = not self.is_mic_testing
            if self.is_mic_testing:
                self.mic_test_btn.setText(t("sound.stop", "Stop"))
                if not hasattr(self, 'mic_monitor'):
                    from services.mic_monitor import MicMonitorThread
                    self.mic_monitor = MicMonitorThread(self)
                    self.mic_monitor.level_changed.connect(self.mic_indicator.set_level)
                self.mic_monitor.start()
            else:
                self.mic_test_btn.setText(t("sound.test", "Test"))
                if hasattr(self, 'mic_monitor'):
                    self.mic_monitor.stop()
                self.mic_indicator.set_level(0.0)
                
        self.mic_test_btn.clicked.connect(toggle_mic_test)
        
        mic_test_layout = QHBoxLayout()
        mic_test_layout.setContentsMargins(0, 0, 0, 0)
        mic_test_layout.addWidget(self.mic_indicator)
        mic_test_layout.addSpacing(15)
        mic_test_layout.addWidget(self.mic_test_btn)
        
        mic_test_widget = QWidget()
        mic_test_widget.setLayout(mic_test_layout)
        
        in_group.add_row(SettingsRow(t("sound.input_level", "Input Level"), mic_test_widget, show_separator=False, is_interactive=False))
        
        self.layout.addWidget(in_group)
        
        # --- System Sounds ---
        sys_lbl = QLabel(t("sound.system_sounds", "SYSTEM SOUNDS"))
        sys_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_NORMAL}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;")
        self.layout.addWidget(sys_lbl)
        
        self.sys_group = SettingsGroup()
        
        sys_switch = Switch(checked=self.service.get_system_sounds_enabled())
        sys_switch.toggled.connect(self.service.set_system_sounds_enabled)
        
        self.sys_group.add_row(SettingsRow(t("sound.ui_sounds", "Play User Interface Sounds"), sys_switch, show_separator=False, is_interactive=False))
        
        self.layout.addWidget(self.sys_group)

    def update_device_info(self):
        info = self.service.get_active_device_info()
        default_name = self.service.get_active_output_device()
        self.output_hero.update_info(info, default_name)
        
        if info:
            for i, k in enumerate(self.dev_info_keys):
                self.dev_info_card.update_row(i, str(info.get(k, "—")))
        else:
            for i, k in enumerate(self.dev_info_keys):
                self.dev_info_card.update_row(i, "—")

    def get_search_target(self, target_id: str) -> QWidget | None:
        targets = {
            "sound.output_volume": getattr(self, "out_group", None),
            "sound.device": getattr(self, "out_selector", None) or getattr(self, "output_hero", None),
            "sound.balance": getattr(self, "out_group", None),
            "sound.test_speakers": getattr(self, "out_group", None),
            "sound.effects": getattr(self, "sys_group", None),
        }
        return targets.get(target_id)
