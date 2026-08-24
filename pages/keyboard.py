from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QImage, QPainter, QColor
from theme.colors import Colors
from theme.typography import Typography
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from components.slider import Slider
from components.switch import Switch
from components.animated_button import AnimatedButton
from backends.keyboard_backend import KeyboardBackend
from theme.manager import ThemeManager

class KeyboardIconWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(96, 96)
        
    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QColor, QPen
        from PySide6.QtCore import Qt, QRectF
        from theme.manager import ThemeManager
        from theme.colors import Colors
        
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        bg_color = QColor(Colors.ACCENT_BLUE)
        p.setBrush(bg_color)
        p.setPen(Qt.NoPen)
        
        p.drawRoundedRect(self.rect(), 24, 24)
        
        p.setBrush(Qt.NoBrush)
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(3)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        
        kb_rect = QRectF(18, 32, 60, 32)
        p.drawRoundedRect(kb_rect, 6, 6)
        
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255))
        
        p.drawRoundedRect(QRectF(34, 52, 28, 4), 2, 2)
        
        for x in [24, 34, 44, 54, 64]:
            p.drawRoundedRect(QRectF(x, 39, 8, 4), 2, 2)
            
        for x in [27, 39, 49, 61]:
            if x not in (39, 49):
                p.drawRoundedRect(QRectF(x, 45.5, 8, 4), 2, 2)
                
        p.end()

class KeyboardHeroCard(QWidget):
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.setFixedHeight(140)
        
        self.bg = QWidget(self)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.bg)
        
        layout = QHBoxLayout(self.bg)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(28)
        
        self.icon_widget = KeyboardIconWidget()
        layout.addWidget(self.icon_widget)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        info_layout.setAlignment(Qt.AlignVCenter)
        
        self.title_lbl = QLabel()
        info_layout.addWidget(self.title_lbl)
        
        self.subtitle_lbl = QLabel()
        info_layout.addWidget(self.subtitle_lbl)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        self.update_info()
        ThemeManager.theme_changed.connect(self.update_style)
        
    def update_info(self):
        info = self.backend.get_primary_keyboard_info()
        self.title_lbl.setText(info["name"])
        self.subtitle_lbl.setText(f"{info['type']} • {info['status']}")
        self.update_style()
        
    def update_style(self, _is_dark=False):
        self.bg.setStyleSheet(f"background-color: {Colors.CARD_BG}; border-radius: 18px; border: 1px solid {Colors.CARD_BORDER};")
        self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 24px; font-weight: {Typography.WEIGHT_BOLD}; border: none; background: transparent;")
        self.subtitle_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 15px; font-weight: {Typography.WEIGHT_MEDIUM}; border: none; background: transparent;")

LANGUAGE_NAMES = {
    "us": "English (US)",
    "ru": "Russian",
    "uk": "English (UK)",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "pl": "Polish",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
}

class InputSourceRow(QWidget):
    def __init__(self, index, src_type, src_id, is_active, parent=None):
        super().__init__(parent)
        self.index = index
        self.setFixedHeight(44)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        code = src_id.split('+')[0].upper()
        if len(code) > 2:
            code = code[:2]
            
        badge = QLabel(code)
        badge.setFixedSize(28, 28)
        badge.setAlignment(Qt.AlignCenter)
        
        name = LANGUAGE_NAMES.get(src_id.split('+')[0], src_id.upper())
        if '+' in src_id:
            name += f" ({src_id.split('+')[1]})"
            
        lbl = QLabel(name)
        
        if is_active:
            badge_bg = Colors.ACCENT_BLUE
            badge_color = "white"
            lbl_color = Colors.ACCENT_BLUE
            font_weight = "bold"
        else:
            badge_bg = "rgba(120, 120, 120, 0.2)" if ThemeManager.is_dark else "rgba(120, 120, 120, 0.1)"
            badge_color = Colors.TEXT_SECONDARY
            lbl_color = Colors.TEXT_PRIMARY
            font_weight = "500"
            
        badge.setStyleSheet(f"""
            background-color: {badge_bg};
            color: {badge_color};
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        """)
        
        lbl.setStyleSheet(f"color: {lbl_color}; font-size: 14px; font-weight: {font_weight}; background: transparent;")
        
        layout.addWidget(badge)
        layout.addWidget(lbl)
        layout.addStretch()
        
        if is_active:
            check = QLabel("✓")
            check.setStyleSheet(f"color: {Colors.ACCENT_BLUE}; font-size: 18px; font-weight: bold; background: transparent;")
            layout.addWidget(check)

class InputSourcesList(SettingsGroup):
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.refresh()
        
    def refresh(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
                w.setParent(None)
                w.deleteLater()
                
        sources = self.backend.get_input_sources()
        current_idx = self.backend.get_current_input_source()
        
        for i, src in enumerate(sources):
            if len(src) == 2:
                src_type, src_id = src
            else:
                continue
                
            row = InputSourceRow(i, src_type, src_id, i == current_idx)
            self.layout.addWidget(row)
            
            if i < len(sources) - 1:
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet(f"background-color: {Colors.CARD_BORDER}; max-height: 1px; border: none;")
                self.layout.addWidget(sep)
        self.updateGeometry()

class KeyboardStatusList(SettingsGroup):
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        
        from localization import t
        self.caps_lbl = self._make_status_label()
        self.num_lbl = self._make_status_label()
        self.scroll_lbl = self._make_status_label()
        
        self.add_row(SettingsRow(t("keyboard.caps_lock", "Caps Lock"), self.caps_lbl, show_separator=True, is_interactive=False))
        self.add_row(SettingsRow(t("keyboard.num_lock", "Num Lock"), self.num_lbl, show_separator=True, is_interactive=False))
        self.add_row(SettingsRow(t("keyboard.scroll_lock", "Scroll Lock"), self.scroll_lbl, show_separator=False, is_interactive=False))
        
        from PySide6.QtCore import QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)
        self.update_status()
        
    def _make_status_label(self):
        lbl = QLabel()
        return lbl
        
    def update_status(self):
        self._set_status(self.caps_lbl, self.backend.get_lock_state("capslock"))
        self._set_status(self.num_lbl, self.backend.get_lock_state("numlock"))
        self._set_status(self.scroll_lbl, self.backend.get_lock_state("scrolllock"))
        
    def _set_status(self, lbl, is_on):
        from theme.colors import Colors
        from localization import t
        color = Colors.SWITCH_ON if is_on else Colors.TEXT_SECONDARY
        text = t("keyboard.enabled", "Enabled") if is_on else t("keyboard.disabled", "Disabled")
        lbl.setText(f"<span style='color: {color}; font-size: 14px;'>●</span> <span style='color: {Colors.TEXT_SECONDARY}; font-size: 13px;'>{text}</span>")
        lbl.setStyleSheet("background: transparent; border: none;")

class KeyboardPage(QWidget):
    def __init__(self):
        super().__init__()
        from theme.colors import Colors
        from localization import t
        self.backend = KeyboardBackend()
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        
        self.content = QWidget()
        self.content.setObjectName("KeyboardContent")
        self.scroll.setWidget(self.content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)
        
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)
        self.layout.setAlignment(Qt.AlignTop)
        
        title = QLabel(t("nav.keyboard", "Keyboard"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};")
        self.layout.addWidget(title)
        
        # Hero Card
        self.hero_card = KeyboardHeroCard(self.backend)
        self.layout.addWidget(self.hero_card)
        
        # Key Repeat toggle
        self.group_repeat = SettingsGroup()
        self.repeat_switch = Switch()
        self.repeat_switch.setChecked(self.backend.get_repeat_enabled())
        self.repeat_switch.toggled.connect(self.backend.set_repeat_enabled)
        self.group_repeat.add_row(SettingsRow(t("keyboard.repeat_keys", "Key Repeat"), self.repeat_switch, show_separator=False, is_interactive=False))
        self.layout.addWidget(self.group_repeat)
        
        # Keyboard Status
        status_lbl = QLabel(t("keyboard.status_sec", "KEYBOARD STATUS"))
        status_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_MEDIUM}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;")
        self.layout.addWidget(status_lbl)
        
        self.status_list = KeyboardStatusList(self.backend)
        self.layout.addWidget(self.status_list)
        
        # Typing Options
        opt_lbl = QLabel(t("keyboard.typing_options", "TYPING OPTIONS"))
        opt_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_MEDIUM}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;")
        self.layout.addWidget(opt_lbl)
        
        self.opt_group = SettingsGroup()
        
        self.blink_switch = Switch()
        self.blink_switch.setChecked(self.backend.get_cursor_blink())
        self.blink_switch.toggled.connect(self.backend.set_cursor_blink)
        self.opt_group.add_row(SettingsRow(t("keyboard.cursor_blink", "Cursor Blinking"), self.blink_switch, show_separator=True, is_interactive=False))
        
        self.dwt_switch = Switch()
        self.dwt_switch.setChecked(self.backend.get_disable_while_typing())
        self.dwt_switch.toggled.connect(self.backend.set_disable_while_typing)
        self.opt_group.add_row(SettingsRow(t("keyboard.dwt", "Disable Touchpad While Typing"), self.dwt_switch, show_separator=True, is_interactive=False))
        
        self.sticky_switch = Switch()
        self.sticky_switch.setChecked(self.backend.get_sticky_keys())
        self.sticky_switch.toggled.connect(self.backend.set_sticky_keys)
        self.opt_group.add_row(SettingsRow(t("keyboard.sticky_keys", "Sticky Keys"), self.sticky_switch, show_separator=False, is_interactive=False))
        
        self.layout.addWidget(self.opt_group)
        
        # Sliders group
        sliders_lbl = QLabel(t("keyboard.typing_sec", "TYPING"))
        sliders_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_MEDIUM}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;")
        self.layout.addWidget(sliders_lbl)
        
        self.group_sliders = SettingsGroup()
        
        def make_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: 500;")
            return lbl
        
        # Delay (Long to Short)
        delay_layout = QHBoxLayout()
        self.delay_slider = Slider(Qt.Horizontal)
        self.delay_slider.setMinimum(150)
        self.delay_slider.setMaximum(1000)
        self.delay_slider.setInvertedAppearance(True) # Right is shorter delay
        self.delay_slider.setValue(self.backend.get_delay())
        self.delay_slider.sliderReleased.connect(lambda: self.backend.set_delay(self.delay_slider.value()))
        
        delay_layout.addWidget(make_label(t("keyboard.long", "Long")), 0, Qt.AlignVCenter)
        delay_layout.addWidget(self.delay_slider)
        delay_layout.addWidget(make_label(t("keyboard.short", "Short")), 0, Qt.AlignVCenter)
        
        delay_widget = QWidget()
        delay_widget.setLayout(delay_layout)
        delay_layout.setContentsMargins(0, 0, 0, 0)
        
        self.group_sliders.add_row(SettingsRow(t("keyboard.delay", "Delay Until Repeat"), delay_widget, show_separator=True, is_interactive=False))
        
        # Rate (Slow to Fast)
        rate_layout = QHBoxLayout()
        self.rate_slider = Slider(Qt.Horizontal)
        self.rate_slider.setMinimum(10)
        self.rate_slider.setMaximum(100)
        self.rate_slider.setInvertedAppearance(True) # Right is smaller interval (faster)
        self.rate_slider.setValue(self.backend.get_interval())
        self.rate_slider.sliderReleased.connect(lambda: self.backend.set_interval(self.rate_slider.value()))
        
        rate_layout.addWidget(make_label(t("keyboard.slow", "Slow")), 0, Qt.AlignVCenter)
        rate_layout.addWidget(self.rate_slider)
        rate_layout.addWidget(make_label(t("keyboard.fast", "Fast")), 0, Qt.AlignVCenter)
        
        rate_widget = QWidget()
        rate_widget.setLayout(rate_layout)
        rate_layout.setContentsMargins(0, 0, 0, 0)
        
        self.group_sliders.add_row(SettingsRow(t("keyboard.speed", "Key Repeat Rate"), rate_widget, show_separator=False, is_interactive=False))
        
        self.layout.addWidget(self.group_sliders)
        
        # Input Sources
        input_lbl = QLabel(t("keyboard.input_sources", "INPUT SOURCES"))
        input_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_MEDIUM}; font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;")
        self.layout.addWidget(input_lbl)
        
        self.input_sources_list = InputSourcesList(self.backend)
        self.layout.addWidget(self.input_sources_list)
        
        ThemeManager.theme_changed.connect(self.update_style)
        self.update_style()
        
    def update_style(self, _is_dark=False):
        pass

    def get_search_target(self, target_id: str) -> QWidget | None:
        targets = {
            "keyboard.repeat_keys": getattr(self, "group_repeat", None),
            "keyboard.delay": getattr(self, "group_sliders", None),
            "keyboard.speed": getattr(self, "group_sliders", None),
            "keyboard.input_sources": getattr(self, "input_sources_list", None),
        }
        return targets.get(target_id)
