from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton, QApplication
from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath

from theme.colors import Colors
from theme.typography import Typography
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from components.segmented_control import SegmentedControl
from components.switch import Switch
from components.slider import Slider
from backends.mouse_backend import MouseBackend
from theme.manager import ThemeManager
from theme.styler import fix_label_styles

class MouseIconWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(96, 96)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Background rounded box
        bg_color = QColor(Colors.ACCENT_BLUE)
        p.setBrush(bg_color)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 24, 24)

        # Draw white mouse silhouette
        p.setBrush(Qt.NoBrush)
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(3)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)

        # Mouse body outline
        mouse_rect = QRectF(32, 22, 32, 52)
        p.drawRoundedRect(mouse_rect, 16, 16)

        # Divider between left/right buttons
        p.drawLine(48, 22, 48, 38)

        # Scroll wheel
        wheel_rect = QRectF(45.5, 30, 5, 11)
        p.setBrush(QColor(255, 255, 255))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(wheel_rect, 2.5, 2.5)

        p.end()

class MouseHeroCard(QWidget):
    def __init__(self, backend: MouseBackend, parent=None):
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

        self.icon_widget = MouseIconWidget()
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
        info = self.backend.get_primary_mouse_info()
        self.title_lbl.setText(info["name"])
        self.subtitle_lbl.setText(f"{info['type']} • {info['status']}")
        self.update_style()

    def update_style(self, _is_dark=False):
        self.bg.setStyleSheet(
            f"background-color: {Colors.CARD_BG}; border-radius: 18px; border: 1px solid {Colors.CARD_BORDER};"
        )
        self.title_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 24px; font-weight: {Typography.WEIGHT_BOLD}; border: none; background: transparent;"
        )
        self.subtitle_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 15px; font-weight: {Typography.WEIGHT_MEDIUM}; border: none; background: transparent;"
        )

class DoubleClickTestButton(QPushButton):
    """Minimalist test area for checking configured double-click responsiveness."""
    def __init__(self, parent=None):
        from localization import t
        super().__init__(t("mouse.test_click", "Double-Click Here"), parent)
        self.setFixedSize(160, 28)
        self.setCursor(Qt.PointingHandCursor)
        self.is_success = False

        self._reset_timer = QTimer(self)
        self._reset_timer.setSingleShot(True)
        self._reset_timer.setInterval(1000)
        self._reset_timer.timeout.connect(self._reset_state)

        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def mouseDoubleClickEvent(self, event):
        from localization import t
        if event.button() == Qt.LeftButton:
            self.is_success = True
            self.setText(t("mouse.test_recognized", "✓ Recognized!"))
            self.update_style()
            self._reset_timer.start()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def _reset_state(self):
        from localization import t
        self.is_success = False
        self.setText(t("mouse.test_click", "Double-Click Here"))
        self.update_style()

    def update_style(self, _is_dark=False):
        is_dark = ThemeManager.is_dark
        if self.is_success:
            bg = Colors.ACCENT_BLUE
            text_color = "#FFFFFF"
            border = "none"
        else:
            if is_dark:
                bg = "rgba(120, 120, 128, 0.24)"
                text_color = Colors.TEXT_PRIMARY
                border = "1px solid rgba(120, 120, 128, 0.4)"
            else:
                bg = "rgba(0, 0, 0, 0.06)"
                text_color = Colors.TEXT_PRIMARY
                border = f"1px solid {Colors.CARD_BORDER}"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border: {border};
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_BLUE if self.is_success else ('rgba(120, 120, 128, 0.35)' if is_dark else 'rgba(0, 0, 0, 0.1)')};
            }}
        """)

class MousePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backend = MouseBackend()

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        self.scroll.viewport().setStyleSheet("background: transparent;")

        self.content = QWidget()
        self.content.setObjectName("MouseContent")
        self.content.setStyleSheet("background: transparent;")
        self.scroll.setWidget(self.content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)

        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 30, 40, 40)
        self.layout.setSpacing(20)
        self.layout.setAlignment(Qt.AlignTop)

        self._build_ui()
        self.layout.addStretch()

        # Real-time synchronization timer to detect external GSettings changes
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(1000) # Check every 1s
        self._poll_timer.timeout.connect(self.refresh_settings)
        self._poll_timer.start()

        ThemeManager.theme_changed.connect(self.update_style)
        self.update_style()

    def _create_section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_MEDIUM}; "
            f"font-size: {Typography.SIZE_SMALL}px; margin-left: 15px; margin-top: 10px; letter-spacing: 0.5px;"
        )
        return lbl

    def _make_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: 500;")
        return lbl

    def _build_ui(self):
        from localization import t
        # 0. Page Title Header
        title = QLabel(t("nav.mouse", "Mouse"))
        title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};"
        )
        self.layout.addWidget(title)

        # 1. Hero Card
        self.hero_card = MouseHeroCard(self.backend)
        self.layout.addWidget(self.hero_card)

        # 2. Primary Button Section (Left / Right)
        self.layout.addWidget(self._create_section_label(t("mouse.primary_btn", "PRIMARY BUTTON")))
        self.group_primary = SettingsGroup()
        
        active_primary = self.backend.get_primary_button() # "left" or "right"
        self.primary_control = SegmentedControl([("left", t("mouse.left", "Left")), ("right", t("mouse.right", "Right"))], active_primary)
        self.primary_control.valueChanged.connect(self._on_primary_button_changed)
        self.group_primary.add_row(SettingsRow(t("mouse.primary_mouse_btn", "Primary Mouse Button"), self.primary_control, show_separator=False, is_interactive=False))
        self.layout.addWidget(self.group_primary)

        # 3. Pointer Speed Section (Smooth Slider)
        self.layout.addWidget(self._create_section_label(t("mouse.speed", "POINTER SPEED")))
        self.group_speed = SettingsGroup()

        speed_layout = QHBoxLayout()
        speed_layout.setContentsMargins(0, 0, 0, 0)
        self.speed_slider = Slider(Qt.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(100)
        
        # Map [-1.0 .. 1.0] to [0 .. 100]
        cur_speed = self.backend.get_pointer_speed()
        slider_val = int(round((cur_speed + 1.0) * 50))
        self.speed_slider.setValue(slider_val)
        self.speed_slider.valueChanged.connect(self._on_speed_slider_changed)
        self.speed_slider.sliderReleased.connect(self._on_speed_slider_released)

        speed_layout.addWidget(self._make_label(t("mouse.slow", "Slow")), 0, Qt.AlignVCenter)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self._make_label(t("mouse.fast", "Fast")), 0, Qt.AlignVCenter)

        speed_widget = QWidget()
        speed_widget.setLayout(speed_layout)
        self.group_speed.add_row(SettingsRow(t("mouse.tracking_speed", "Tracking Speed"), speed_widget, show_separator=False, is_interactive=False))
        self.layout.addWidget(self.group_speed)

        # 4. Scrolling Section (Natural Scrolling)
        self.layout.addWidget(self._create_section_label(t("mouse.scrolling", "SCROLLING")))
        self.group_scroll = SettingsGroup()

        self.natural_switch = Switch()
        self.natural_switch.setChecked(self.backend.get_natural_scroll())
        self.natural_switch.toggled.connect(self._on_natural_scroll_toggled)
        self.group_scroll.add_row(SettingsRow(t("mouse.natural_scroll", "Natural Scrolling"), self.natural_switch, show_separator=False, is_interactive=False))
        self.layout.addWidget(self.group_scroll)

        # 5. Double-Click Speed Section with Interactive Test Button
        self.layout.addWidget(self._create_section_label(t("mouse.double_click_speed", "DOUBLE-CLICK SPEED")))
        self.group_dc = SettingsGroup()

        dc_layout = QHBoxLayout()
        dc_layout.setContentsMargins(0, 0, 0, 0)
        self.dc_slider = Slider(Qt.Horizontal)
        self.dc_slider.setMinimum(100)
        self.dc_slider.setMaximum(1000)
        self.dc_slider.setInvertedAppearance(True) # Right is faster (smaller ms)
        
        initial_dc = self.backend.get_double_click()
        self.dc_slider.setValue(initial_dc)
        self._sync_qt_double_click(initial_dc)
        
        self.dc_slider.valueChanged.connect(self._on_dc_slider_changed)
        self.dc_slider.sliderReleased.connect(self._on_dc_slider_released)

        dc_layout.addWidget(self._make_label(t("mouse.slow", "Slow")), 0, Qt.AlignVCenter)
        dc_layout.addWidget(self.dc_slider)
        dc_layout.addWidget(self._make_label(t("mouse.fast", "Fast")), 0, Qt.AlignVCenter)

        dc_widget = QWidget()
        dc_widget.setLayout(dc_layout)
        self.group_dc.add_row(SettingsRow(t("mouse.double_click_speed", "Double-Click Speed"), dc_widget, show_separator=True, is_interactive=False))

        self.test_btn = DoubleClickTestButton()
        self.group_dc.add_row(SettingsRow(t("mouse.test_double_click", "Test Double-Click"), self.test_btn, show_separator=False, is_interactive=False))
        self.layout.addWidget(self.group_dc)

        # 6. Pointer Acceleration Section (Supported on GNOME Wayland via accel-profile)
        self.layout.addWidget(self._create_section_label(t("mouse.acceleration", "POINTER ACCELERATION")))
        self.group_accel = SettingsGroup()

        self.accel_switch = Switch()
        self.accel_switch.setChecked(self.backend.is_acceleration_enabled())
        self.accel_switch.toggled.connect(self._on_accel_toggled)
        self.group_accel.add_row(SettingsRow(t("mouse.acceleration", "Pointer Acceleration"), self.accel_switch, show_separator=False, is_interactive=False))
        self.layout.addWidget(self.group_accel)

    # -------------------------------------------------------------------------
    # UI Event Handlers
    # -------------------------------------------------------------------------
    def _sync_qt_double_click(self, ms: int):
        app_inst = QApplication.instance()
        if app_inst:
            app_inst.setDoubleClickInterval(ms)

    def _on_primary_button_changed(self, val: str):
        """Immediately change primary button setting in GNOME Mutter."""
        self.backend.set_primary_button(val)

    def _on_speed_slider_changed(self, val: int):
        """Real-time smooth speed adjustment during dragging."""
        speed = round((val / 50.0) - 1.0, 2)
        self.backend.set_pointer_speed(speed)

    def _on_speed_slider_released(self):
        """Ensure final position is saved when slider is released."""
        val = self.speed_slider.value()
        speed = round((val / 50.0) - 1.0, 2)
        self.backend.set_pointer_speed(speed)

    def _on_natural_scroll_toggled(self, checked: bool):
        self.backend.set_natural_scroll(checked)

    def _on_dc_slider_changed(self, val: int):
        self.backend.set_double_click(val)
        self._sync_qt_double_click(val)

    def _on_dc_slider_released(self):
        ms = self.dc_slider.value()
        self.backend.set_double_click(ms)
        self._sync_qt_double_click(ms)

    def _on_accel_toggled(self, checked: bool):
        self.backend.set_acceleration_enabled(checked)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_settings()

    def refresh_settings(self):
        """Syncs all controls with the latest system GSettings state."""
        # 1. Primary button
        active_primary = self.backend.get_primary_button()
        if hasattr(self, 'primary_control') and self.primary_control.active_id != active_primary:
            self.primary_control.set_active_id(active_primary, emit_signal=False)
        
        # 2. Pointer speed
        if hasattr(self, 'speed_slider') and not self.speed_slider.isSliderDown():
            cur_speed = self.backend.get_pointer_speed()
            slider_val = int(round((cur_speed + 1.0) * 50))
            if abs(self.speed_slider.value() - slider_val) > 1:
                self.speed_slider.setValue(slider_val)

        # 3. Natural scroll
        if hasattr(self, 'natural_switch'):
            cur_nat = self.backend.get_natural_scroll()
            if self.natural_switch.isChecked() != cur_nat:
                self.natural_switch.setChecked(cur_nat)

        # 4. Double click
        if hasattr(self, 'dc_slider') and not self.dc_slider.isSliderDown():
            cur_dc = self.backend.get_double_click()
            if abs(self.dc_slider.value() - cur_dc) > 5:
                self.dc_slider.setValue(cur_dc)
                self._sync_qt_double_click(cur_dc)

        # 5. Pointer acceleration
        if hasattr(self, 'accel_switch'):
            cur_accel = self.backend.is_acceleration_enabled()
            if self.accel_switch.isChecked() != cur_accel:
                self.accel_switch.setChecked(cur_accel)

    def cleanup(self):
        """Stops background timers when window closes."""
        if hasattr(self, '_poll_timer'):
            self._poll_timer.stop()

    def update_style(self, _is_dark=False):
        fix_label_styles(self)
        if hasattr(self, 'hero_card'):
            self.hero_card.update_style()
        if hasattr(self, 'test_btn'):
            self.test_btn.update_style()
        self.update()

    def get_search_target(self, target_id: str) -> QWidget | None:
        targets = {
            "mouse.primary_button": getattr(self, "group_primary", None),
            "mouse.speed": getattr(self, "group_speed", None),
            "mouse.natural_scroll": getattr(self, "group_scroll", None),
            "mouse.double_click": getattr(self, "group_dc", None),
            "mouse.acceleration": getattr(self, "group_accel", None),
        }
        return targets.get(target_id)
