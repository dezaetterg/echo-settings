from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton,
    QStackedWidget, QApplication
)
from PySide6.QtCore import Qt, QRectF, QTimer, Signal, QPropertyAnimation, Property
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath

from theme.colors import Colors
from theme.typography import Typography
from components.settings_group import SettingsGroup
from components.settings_row import SettingsRow
from components.segmented_control import SegmentedControl
from components.switch import Switch
from backends.privacy_backend import PrivacyBackend
from theme.manager import ThemeManager
from theme.styler import fix_label_styles
from localization import t, i18n

# =============================================================================
# Vector Icon Widgets
# =============================================================================

class PrivacyHeroIconWidget(QWidget):
    """Echo Lock/Shield hero icon with vector lock motif."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(96, 96)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Background squircle (Accent Blue)
        p.setBrush(QColor(Colors.ACCENT_BLUE))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 24, 24)

        cx, cy = self.width() / 2, self.height() / 2

        # Draw Padlock Shackle
        p.setBrush(Qt.NoBrush)
        pen = QPen(QColor(255, 255, 255), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)

        shackle_rect = QRectF(cx - 14, cy - 26, 28, 28)
        p.drawArc(shackle_rect, 0, 180 * 16)
        p.drawLine(cx - 14, cy - 12, cx - 14, cy - 6)
        p.drawLine(cx + 14, cy - 12, cx + 14, cy - 6)

        # Padlock Body
        p.setBrush(QColor(255, 255, 255))
        p.setPen(Qt.NoPen)
        body_rect = QRectF(cx - 20, cy - 8, 40, 32)
        p.drawRoundedRect(body_rect, 8, 8)

        # Keyhole
        p.setBrush(QColor(Colors.ACCENT_BLUE))
        p.drawEllipse(cx - 3.5, cy + 2, 7, 7)
        key_path = QPainterPath()
        key_path.moveTo(cx - 2.5, cy + 6)
        key_path.lineTo(cx + 2.5, cy + 6)
        key_path.lineTo(cx + 3.5, cy + 15)
        key_path.lineTo(cx - 3.5, cy + 15)
        key_path.closeSubpath()
        p.drawPath(key_path)

        p.end()

class PrivacyRowIcon(QWidget):
    """Compact 30x30 squircle with crisp vector iconography for Privacy rows."""
    def __init__(self, icon_type: str, bg_color: str, parent=None):
        super().__init__(parent)
        self.icon_type = icon_type
        self.bg_color = bg_color
        self.setFixedSize(30, 30)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Background squircle
        p.setBrush(QColor(self.bg_color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 7.5, 7.5)

        cx, cy = self.width() / 2.0, self.height() / 2.0
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255))

        if self.icon_type == "lock":
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255), 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawArc(cx - 3.5, cy - 7, 7, 7, 0, 180 * 16)
            p.drawLine(cx - 3.5, cy - 3.5, cx - 3.5, cy - 1.5)
            p.drawLine(cx + 3.5, cy - 3.5, cx + 3.5, cy - 1.5)
            p.setBrush(QColor(255, 255, 255))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(cx - 5.5, cy - 2, 11, 8.5), 2, 2)
            p.setBrush(QColor(self.bg_color))
            p.drawEllipse(cx - 1, cy + 1, 2, 2)

        elif self.icon_type == "location":
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255), 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            pin_path = QPainterPath()
            pin_path.moveTo(cx, cy + 6.5)
            pin_path.quadTo(cx - 5, cy + 0.5, cx - 5, cy - 2.5)
            pin_path.arcTo(cx - 5, cy - 7.5, 10, 10, 180, -180)
            pin_path.quadTo(cx + 5, cy + 0.5, cx, cy + 6.5)
            p.drawPath(pin_path)
            p.setBrush(QColor(255, 255, 255))
            p.setPen(Qt.NoPen)
            p.drawEllipse(cx - 1.8, cy - 2.5 - 1.8, 3.6, 3.6)

        elif self.icon_type == "history":
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255), 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawEllipse(QRectF(cx - 6, cy - 6, 12, 12))
            p.drawLine(cx, cy, cx, cy - 3.5)
            p.drawLine(cx, cy, cx + 3, cy)

        elif self.icon_type == "camera":
            p.setBrush(QColor(255, 255, 255))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(cx - 6.5, cy - 4, 13, 9.5), 2, 2)
            top_notch = QPainterPath()
            top_notch.moveTo(cx - 3, cy - 4)
            top_notch.lineTo(cx - 2, cy - 6)
            top_notch.lineTo(cx + 2, cy - 6)
            top_notch.lineTo(cx + 3, cy - 4)
            top_notch.closeSubpath()
            p.drawPath(top_notch)
            p.setBrush(QColor(self.bg_color))
            p.drawEllipse(cx - 2.5, cy + 0.75 - 2.5, 5, 5)

        elif self.icon_type == "mic":
            p.setBrush(QColor(255, 255, 255))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(cx - 2.5, cy - 6.5, 5, 8.5), 2.5, 2.5)
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255), 1.5, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(QRectF(cx - 4.5, cy - 4, 9, 8), 0, -180 * 16)
            p.drawLine(cx, cy + 4, cx, cy + 6.5)
            p.drawLine(cx - 3, cy + 6.5, cx + 3, cy + 6.5)

        elif self.icon_type == "shield":
            shield_path = QPainterPath()
            shield_path.moveTo(cx, cy - 6.5)
            shield_path.lineTo(cx + 5.5, cy - 4.5)
            shield_path.quadTo(cx + 5.5, cy + 2.5, cx, cy + 6.5)
            shield_path.quadTo(cx - 5.5, cy + 2.5, cx - 5.5, cy - 4.5)
            shield_path.closeSubpath()
            p.fillPath(shield_path, QColor(255, 255, 255))
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(self.bg_color), 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            check_path = QPainterPath()
            check_path.moveTo(cx - 2.5, cy - 0.5)
            check_path.lineTo(cx - 0.5, cy + 1.8)
            check_path.lineTo(cx + 2.8, cy - 2)
            p.drawPath(check_path)

        elif self.icon_type == "remote":
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255), 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawRoundedRect(QRectF(cx - 6.5, cy - 5.5, 13, 9), 2, 2)
            p.drawLine(cx, cy + 3.5, cx, cy + 6)
            p.drawLine(cx - 3.5, cy + 6, cx + 3.5, cy + 6)

        elif self.icon_type == "control":
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255), 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawRoundedRect(QRectF(cx - 6.5, cy - 4, 13, 8), 3, 3)
            # D-pad
            p.drawLine(cx - 3.5, cy, cx - 1.5, cy)
            p.drawLine(cx - 2.5, cy - 1, cx - 2.5, cy + 1)
            # Buttons
            p.setBrush(QColor(255, 255, 255))
            p.setPen(Qt.NoPen)
            p.drawEllipse(cx + 2.5, cy - 1, 1.5, 1.5)
            p.drawEllipse(cx + 1, cy + 1, 1.5, 1.5)

        p.end()

class ChevronWidget(QWidget):
    """Right-facing chevron `>` indicator for list items."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(8, 13)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        is_dark = ThemeManager.is_dark
        chevron_color = QColor(255, 255, 255, 75) if is_dark else QColor(60, 60, 67, 75)
        p.setPen(QPen(chevron_color, 1.75, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawLine(1.5, 2.0, 6.0, 6.5)
        p.drawLine(6.0, 6.5, 1.5, 11.0)
        p.end()

# =============================================================================
# Interactive Navigation Row
# =============================================================================

class PrivacyNavigationRow(QWidget):
    """Interactive Navigation Row with squircle icon, title, subtitle, optional value, and chevron."""
    clicked = Signal(str)

    def __init__(
        self,
        route_id: str,
        icon_type: str,
        icon_color: str,
        title: str,
        subtitle: str,
        detail_value: str = "",
        show_separator: bool = True,
        parent=None
    ):
        super().__init__(parent)
        self.route_id = route_id
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.PointingHandCursor)
        self.show_separator = show_separator
        self.setMinimumHeight(56)

        self._hover_alpha = 0.0
        self.anim = QPropertyAnimation(self, b"hover_alpha")
        self.anim.setDuration(150)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(14)

        # 1. Leading Squircle Icon
        self.icon_widget = PrivacyRowIcon(icon_type, icon_color, self)
        layout.addWidget(self.icon_widget, 0, Qt.AlignVCenter)

        # 2. Text Stack
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        text_layout.setAlignment(Qt.AlignVCenter)

        self.title_lbl = QLabel(title)
        text_layout.addWidget(self.title_lbl)

        self.subtitle_lbl = QLabel(subtitle)
        text_layout.addWidget(self.subtitle_lbl)

        layout.addLayout(text_layout)
        layout.addStretch()

        # 3. Optional detail value label (e.g. "View Only")
        self.value_lbl = QLabel(detail_value)
        if detail_value:
            layout.addWidget(self.value_lbl, 0, Qt.AlignVCenter)
        else:
            self.value_lbl.hide()

        # 4. Trailing Chevron
        self.chevron = ChevronWidget(self)
        layout.addWidget(self.chevron, 0, Qt.AlignVCenter)

        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    @Property(float)
    def hover_alpha(self):
        return self._hover_alpha

    @hover_alpha.setter
    def hover_alpha(self, val):
        self._hover_alpha = val
        self.update()

    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setEndValue(1.0)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setEndValue(0.0)
        self.anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.route_id)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def update_texts(self, title: str, subtitle: str, detail_value: str = None):
        self.title_lbl.setText(title)
        self.subtitle_lbl.setText(subtitle)
        if detail_value is not None:
            self.set_value(detail_value)

    def set_value(self, text: str):
        self.value_lbl.setText(text)
        if text:
            self.value_lbl.show()
        else:
            self.value_lbl.hide()

    def update_style(self, _is_dark=False):
        self.title_lbl.setStyleSheet(
            f"font-size: 14px; font-weight: {Typography.WEIGHT_MEDIUM}; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;"
        )
        self.subtitle_lbl.setStyleSheet(
            f"font-size: 12px; font-weight: {Typography.WEIGHT_NORMAL}; color: {Colors.TEXT_SECONDARY}; background: transparent; border: none;"
        )
        self.value_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: {Typography.WEIGHT_NORMAL}; color: {Colors.TEXT_SECONDARY}; background: transparent; border: none; margin-right: 4px;"
        )
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Hover highlight
        if self._hover_alpha > 0:
            is_dark = ThemeManager.is_dark
            base_color = QColor(255, 255, 255) if is_dark else QColor(0, 0, 0)
            base_color.setAlphaF((0.08 if is_dark else 0.04) * self._hover_alpha)
            p.setBrush(base_color)
            p.setPen(Qt.NoPen)
            rect = self.rect().adjusted(4, 0, -4, 0)
            p.drawRoundedRect(rect, 8, 8)

        # Separator line
        if self.show_separator:
            sep_color = QColor(Colors.CARD_BORDER)
            sep_color.setAlpha(45 if ThemeManager.is_dark else 35)
            p.setPen(QPen(sep_color, 1))
            p.drawLine(60, self.height() - 1, self.width() - 16, self.height() - 1)
        p.end()

# =============================================================================
# Hero Card
# =============================================================================

class PrivacyHeroCard(QWidget):
    """Hero Card with Echo lock icon, title, and live security status."""
    def __init__(self, backend: PrivacyBackend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.setFixedHeight(132)

        self.bg = QWidget(self)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.bg)

        layout = QHBoxLayout(self.bg)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(24)

        self.icon_widget = PrivacyHeroIconWidget()
        layout.addWidget(self.icon_widget)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        info_layout.setAlignment(Qt.AlignVCenter)

        self.title_lbl = QLabel(t("privacy.title", "Privacy & Security"))
        info_layout.addWidget(self.title_lbl)

        self.subtitle_lbl = QLabel()
        info_layout.addWidget(self.subtitle_lbl)

        layout.addLayout(info_layout)
        layout.addStretch()

        self.update_info()
        ThemeManager.theme_changed.connect(self.update_style)

    def retranslate_ui(self):
        self.title_lbl.setText(t("privacy.title", "Privacy & Security"))
        self.update_info()

    def update_info(self):
        summary = self.backend.get_privacy_summary()
        count = summary["active_services_count"]
        status_key = "privacy.status_protected" if summary.get("is_protected", True) else "privacy.status_standard"
        status = t(status_key, summary["status_text"])
        services_text = t("privacy.hero_active", "Services Active")
        self.subtitle_lbl.setText(f"{status} · {count} {services_text}")
        self.update_style()

    def update_style(self, _is_dark=False):
        self.bg.setStyleSheet(
            f"background-color: {Colors.CARD_BG}; border-radius: 16px; border: 1px solid {Colors.CARD_BORDER};"
        )
        self.title_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 22px; font-weight: {Typography.WEIGHT_BOLD}; border: none; background: transparent;"
        )
        self.subtitle_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 14px; font-weight: {Typography.WEIGHT_MEDIUM}; border: none; background: transparent;"
        )

# =============================================================================
# Action Buttons & Helpers
# =============================================================================

class ClearHistoryButton(QPushButton):
    """Clean action button to purge recent file history with visual confirmation."""
    def __init__(self, backend: PrivacyBackend, parent=None):
        super().__init__(t("privacy.clear_btn", "Clear File History..."), parent)
        self.backend = backend
        self.setFixedSize(160, 30)
        self.setCursor(Qt.PointingHandCursor)

        self._reset_timer = QTimer(self)
        self._reset_timer.setSingleShot(True)
        self._reset_timer.setInterval(1200)
        self._reset_timer.timeout.connect(self._reset_state)

        self.clicked.connect(self._on_clear_clicked)
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def _on_clear_clicked(self):
        self.backend.clear_recent_files_history()
        self.setText(t("privacy.cleared", "✓ Cleared"))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_BLUE};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }}
        """)
        self._reset_timer.start()

    def _reset_state(self):
        self.setText(t("privacy.clear_btn", "Clear File History..."))
        self.update_style()

    def retranslate_ui(self):
        self.setText(t("privacy.clear_btn", "Clear File History..."))

    def update_style(self, _is_dark=False):
        is_dark = ThemeManager.is_dark
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
                padding: 4px 10px;
            }}
            QPushButton:hover {{
                background-color: {'rgba(120, 120, 128, 0.35)' if is_dark else 'rgba(0, 0, 0, 0.1)'};
            }}
        """)

# =============================================================================
# Base Detail Page Template
# =============================================================================

class BasePrivacyDetailPage(QWidget):
    """Standard Detail Page with Back button (`‹ Privacy & Security`), title, description, and settings."""
    back_requested = Signal()

    def __init__(self, title_key: str, default_title: str, desc_key: str, default_desc: str, backend: PrivacyBackend, parent=None):
        super().__init__(parent)
        self.title_key = title_key
        self.default_title = default_title
        self.desc_key = desc_key
        self.default_desc = default_desc
        self.backend = backend

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        self.scroll.viewport().setStyleSheet("background: transparent;")

        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.scroll.setWidget(self.content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)

        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 24, 40, 40)
        self.layout.setSpacing(16)
        self.layout.setAlignment(Qt.AlignTop)

        # Back Button
        self.back_btn = QPushButton(t("privacy.back_btn", "‹ Privacy & Security"))
        self.back_btn.setStyleSheet(
            f"color: {Colors.ACCENT_BLUE}; font-size: 14px; font-weight: {Typography.WEIGHT_MEDIUM}; "
            f"border: none; background: transparent; text-align: left; padding: 0px;"
        )
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.layout.addWidget(self.back_btn, 0, Qt.AlignLeft)

        # Title
        self.title_lbl = QLabel(t(self.title_key, self.default_title))
        self.title_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 24px; font-weight: {Typography.WEIGHT_BOLD}; margin-top: 4px;"
        )
        self.layout.addWidget(self.title_lbl)

        # Description
        self.desc_lbl = QLabel(t(self.desc_key, self.default_desc))
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; font-weight: {Typography.WEIGHT_NORMAL}; margin-bottom: 6px;"
        )
        self.layout.addWidget(self.desc_lbl)

        self._build_detail_ui()
        self.layout.addStretch()

        ThemeManager.theme_changed.connect(self.update_style)
        self.update_style()

    def _create_section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_MEDIUM}; "
            f"font-size: 11px; margin-left: 12px; margin-top: 6px; letter-spacing: 0.6px;"
        )
        return lbl

    def _build_detail_ui(self):
        pass

    def _retranslate_detail_ui(self):
        pass

    def retranslate_ui(self):
        self.back_btn.setText(t("privacy.back_btn", "‹ Privacy & Security"))
        self.title_lbl.setText(t(self.title_key, self.default_title))
        self.desc_lbl.setText(t(self.desc_key, self.default_desc))
        self._retranslate_detail_ui()

    def refresh_settings(self):
        pass

    def update_style(self, _is_dark=False):
        fix_label_styles(self)
        self.back_btn.setStyleSheet(
            f"color: {Colors.ACCENT_BLUE}; font-size: 14px; font-weight: {Typography.WEIGHT_MEDIUM}; "
            f"border: none; background: transparent; text-align: left; padding: 0px;"
        )
        self.title_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 24px; font-weight: {Typography.WEIGHT_BOLD}; margin-top: 4px; border: none; background: transparent;"
        )
        self.desc_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; font-weight: {Typography.WEIGHT_NORMAL}; margin-bottom: 6px; border: none; background: transparent;"
        )
        self.update()

# =============================================================================
# 1. Screen Lock Detail Page
# =============================================================================

class ScreenLockDetailPage(BasePrivacyDetailPage):
    def __init__(self, backend: PrivacyBackend, parent=None):
        super().__init__(
            title_key="privacy.screen_lock",
            default_title="Screen Lock",
            desc_key="privacy.screen_lock_desc",
            default_desc="Automatic screen locking helps protect your device and privacy when you step away.",
            backend=backend,
            parent=parent
        )

    def _build_detail_ui(self):
        self.group1 = SettingsGroup()

        self.lock_switch = Switch()
        self.lock_switch.setChecked(self.backend.get_screen_lock_enabled())
        self.lock_switch.toggled.connect(self.backend.set_screen_lock_enabled)
        self.row_lock = SettingsRow(t("privacy.screen_lock_row", "Screen Lock"), self.lock_switch, show_separator=True, is_interactive=False)
        self.group1.add_row(self.row_lock)

        self.notif_switch = Switch()
        self.notif_switch.setChecked(self.backend.get_lock_screen_notifications())
        self.notif_switch.toggled.connect(self.backend.set_lock_screen_notifications)
        self.row_notif = SettingsRow(t("privacy.lock_notif", "Show Notifications on Lock Screen"), self.notif_switch, show_separator=False, is_interactive=False)
        self.group1.add_row(self.row_notif)
        self.layout.addWidget(self.group1)

        self.lbl_sec_timeouts = self._create_section_label(t("privacy.sec_timeouts", "TIMEOUTS & DELAYS"))
        self.layout.addWidget(self.lbl_sec_timeouts)
        self.group2 = SettingsGroup()

        # Idle delay options: 0s (Never), 300s (5 min), 900s (15 min), 1800s (30 min)
        cur_idle = self.backend.get_idle_delay()
        idle_map = {0: "never", 300: "5m", 900: "15m", 1800: "30m"}
        idle_active = idle_map.get(cur_idle, "never")
        idle_opts = [
            ("never", t("privacy.never", "Never")),
            ("5m", t("privacy.5m", "5 min")),
            ("15m", t("privacy.15m", "15 min")),
            ("30m", t("privacy.30m", "30 min"))
        ]
        self.idle_seg = SegmentedControl(idle_opts, idle_active)
        self.idle_seg.setMinimumWidth(320)
        self.idle_seg.valueChanged.connect(self._on_idle_changed)
        self.row_idle = SettingsRow(t("privacy.turn_off_screen", "Turn Screen Off"), self.idle_seg, show_separator=True, is_interactive=False)
        self.group2.add_row(self.row_idle)

        # Lock delay: 0s (Immediately), 5s, 60s (1 min), 300s (5 min)
        cur_delay = self.backend.get_lock_delay()
        delay_map = {0: "0s", 5: "5s", 60: "1m", 300: "5m"}
        delay_active = delay_map.get(cur_delay, "0s")
        delay_opts = [
            ("0s", t("privacy.immediately", "Immediately")),
            ("5s", t("privacy.5s", "5 sec")),
            ("1m", t("privacy.1m", "1 min")),
            ("5m", t("privacy.5m", "5 min"))
        ]
        self.delay_seg = SegmentedControl(delay_opts, delay_active)
        self.delay_seg.setMinimumWidth(320)
        self.delay_seg.valueChanged.connect(self._on_delay_changed)
        self.row_delay = SettingsRow(t("privacy.lock_delay", "Lock Delay after Screen Off"), self.delay_seg, show_separator=False, is_interactive=False)
        self.group2.add_row(self.row_delay)

        self.layout.addWidget(self.group2)

    def _retranslate_detail_ui(self):
        if hasattr(self, 'row_lock'):
            self.row_lock.label.setText(t("privacy.screen_lock_row", "Screen Lock"))
        if hasattr(self, 'row_notif'):
            self.row_notif.label.setText(t("privacy.lock_notif", "Show Notifications on Lock Screen"))
        if hasattr(self, 'lbl_sec_timeouts'):
            self.lbl_sec_timeouts.setText(t("privacy.sec_timeouts", "TIMEOUTS & DELAYS"))
        if hasattr(self, 'row_idle'):
            self.row_idle.label.setText(t("privacy.turn_off_screen", "Turn Screen Off"))
        if hasattr(self, 'row_delay'):
            self.row_delay.label.setText(t("privacy.lock_delay", "Lock Delay after Screen Off"))
        if hasattr(self, 'idle_seg'):
            self.idle_seg.set_segments([
                ("never", t("privacy.never", "Never")),
                ("5m", t("privacy.5m", "5 min")),
                ("15m", t("privacy.15m", "15 min")),
                ("30m", t("privacy.30m", "30 min"))
            ])
        if hasattr(self, 'delay_seg'):
            self.delay_seg.set_segments([
                ("0s", t("privacy.immediately", "Immediately")),
                ("5s", t("privacy.5s", "5 sec")),
                ("1m", t("privacy.1m", "1 min")),
                ("5m", t("privacy.5m", "5 min"))
            ])

    def _on_idle_changed(self, val_id: str):
        sec_map = {"never": 0, "5m": 300, "15m": 900, "30m": 1800}
        self.backend.set_idle_delay(sec_map.get(val_id, 0))

    def _on_delay_changed(self, val_id: str):
        sec_map = {"0s": 0, "5s": 5, "1m": 60, "5m": 300}
        self.backend.set_lock_delay(sec_map.get(val_id, 0))

    def refresh_settings(self):
        if hasattr(self, 'lock_switch'):
            cur = self.backend.get_screen_lock_enabled()
            if self.lock_switch.isChecked() != cur:
                self.lock_switch.setChecked(cur)

        if hasattr(self, 'notif_switch'):
            cur_notif = self.backend.get_lock_screen_notifications()
            if self.notif_switch.isChecked() != cur_notif:
                self.notif_switch.setChecked(cur_notif)

# =============================================================================
# 2. Location Services Detail Page
# =============================================================================

class LocationServicesDetailPage(BasePrivacyDetailPage):
    def __init__(self, backend: PrivacyBackend, parent=None):
        super().__init__(
            title_key="privacy.location",
            default_title="Location Services",
            desc_key="privacy.location_desc",
            default_desc="Location Services allows apps and system services to determine your approximate geographic location using GeoClue2.",
            backend=backend,
            parent=parent
        )

    def _build_detail_ui(self):
        self.group = SettingsGroup()

        is_avail = self.backend.is_location_available()
        self.loc_switch = Switch()
        if is_avail:
            self.loc_switch.setChecked(self.backend.get_location_enabled())
            self.loc_switch.toggled.connect(self.backend.set_location_enabled)
        else:
            self.loc_switch.setChecked(False)
            self.loc_switch.setEnabled(False)

        self.row_loc = SettingsRow(t("privacy.location", "Location Services"), self.loc_switch, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_loc)

        # Accuracy
        cur_acc = self.backend.get_location_accuracy()
        acc_opts = [
            ("exact", t("privacy.exact", "Exact")),
            ("city", t("privacy.city", "City")),
            ("country", t("privacy.country", "Country"))
        ]
        self.acc_seg = SegmentedControl(acc_opts, cur_acc)
        self.acc_seg.setEnabled(is_avail)
        self.acc_seg.valueChanged.connect(self.backend.set_location_accuracy)
        self.row_acc = SettingsRow(t("privacy.accuracy", "Accuracy Level"), self.acc_seg, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_acc)

        daemon_txt = "GeoClue2 (" + t("privacy.active", "Active") + ")" if is_avail else t("privacy.inactive", "Not Installed")
        self.daemon_status = QLabel(daemon_txt)
        self.daemon_status.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        self.row_daemon = SettingsRow(t("privacy.system_daemon", "System Daemon"), self.daemon_status, show_separator=False, is_interactive=False)
        self.group.add_row(self.row_daemon)

        self.layout.addWidget(self.group)

    def _retranslate_detail_ui(self):
        if hasattr(self, 'row_loc'):
            self.row_loc.label.setText(t("privacy.location", "Location Services"))
        if hasattr(self, 'row_acc'):
            self.row_acc.label.setText(t("privacy.accuracy", "Accuracy Level"))
        if hasattr(self, 'acc_seg'):
            self.acc_seg.set_segments([
                ("exact", t("privacy.exact", "Exact")),
                ("city", t("privacy.city", "City")),
                ("country", t("privacy.country", "Country"))
            ])
        if hasattr(self, 'row_daemon'):
            self.row_daemon.label.setText(t("privacy.system_daemon", "System Daemon"))
        if hasattr(self, 'daemon_status'):
            is_avail = self.backend.is_location_available()
            daemon_txt = "GeoClue2 (" + t("privacy.active", "Active") + ")" if is_avail else t("privacy.inactive", "Not Installed")
            self.daemon_status.setText(daemon_txt)

    def refresh_settings(self):
        if hasattr(self, 'loc_switch') and self.backend.is_location_available():
            cur = self.backend.get_location_enabled()
            if self.loc_switch.isChecked() != cur:
                self.loc_switch.setChecked(cur)

# =============================================================================
# 3. File & Recent History Detail Page
# =============================================================================

class RecentHistoryDetailPage(BasePrivacyDetailPage):
    def __init__(self, backend: PrivacyBackend, parent=None):
        super().__init__(
            title_key="privacy.history",
            default_title="File & Recent History",
            desc_key="privacy.history_desc",
            default_desc="Manage document tracking and application usage history across the system.",
            backend=backend,
            parent=parent
        )

    def _build_detail_ui(self):
        self.group1 = SettingsGroup()

        self.recent_switch = Switch()
        self.recent_switch.setChecked(self.backend.get_remember_recent_files())
        self.recent_switch.toggled.connect(self.backend.set_remember_recent_files)
        self.row_recent = SettingsRow(t("privacy.remember_recent", "Remember Recent Files"), self.recent_switch, show_separator=True, is_interactive=False)
        self.group1.add_row(self.row_recent)

        self.usage_switch = Switch()
        self.usage_switch.setChecked(self.backend.get_remember_app_usage())
        self.usage_switch.toggled.connect(self.backend.set_remember_app_usage)
        self.row_usage = SettingsRow(t("privacy.remember_usage", "Remember App Usage Frequency"), self.usage_switch, show_separator=False, is_interactive=False)
        self.group1.add_row(self.row_usage)
        self.layout.addWidget(self.group1)

        self.lbl_sec_cleanup = self._create_section_label(t("privacy.sec_cleanup", "CLEANUP & RETENTION"))
        self.layout.addWidget(self.lbl_sec_cleanup)
        self.group2 = SettingsGroup()

        self.clear_btn = ClearHistoryButton(self.backend)
        self.row_clear = SettingsRow(t("privacy.clear_history", "Clear File History"), self.clear_btn, show_separator=False, is_interactive=False)
        self.group2.add_row(self.row_clear)
        self.layout.addWidget(self.group2)

    def _retranslate_detail_ui(self):
        if hasattr(self, 'row_recent'):
            self.row_recent.label.setText(t("privacy.remember_recent", "Remember Recent Files"))
        if hasattr(self, 'row_usage'):
            self.row_usage.label.setText(t("privacy.remember_usage", "Remember App Usage Frequency"))
        if hasattr(self, 'lbl_sec_cleanup'):
            self.lbl_sec_cleanup.setText(t("privacy.sec_cleanup", "CLEANUP & RETENTION"))
        if hasattr(self, 'row_clear'):
            self.row_clear.label.setText(t("privacy.clear_history", "Clear File History"))
        if hasattr(self, 'clear_btn'):
            self.clear_btn.retranslate_ui()

    def refresh_settings(self):
        if hasattr(self, 'recent_switch'):
            cur_r = self.backend.get_remember_recent_files()
            if self.recent_switch.isChecked() != cur_r:
                self.recent_switch.setChecked(cur_r)

        if hasattr(self, 'usage_switch'):
            cur_u = self.backend.get_remember_app_usage()
            if self.usage_switch.isChecked() != cur_u:
                self.usage_switch.setChecked(cur_u)

# =============================================================================
# 4. Camera Detail Page
# =============================================================================

class CameraDetailPage(BasePrivacyDetailPage):
    def __init__(self, backend: PrivacyBackend, parent=None):
        super().__init__(
            title_key="privacy.camera",
            default_title="Camera",
            desc_key="privacy.camera_desc",
            default_desc="Control global camera hardware access for applications and browser portals.",
            backend=backend,
            parent=parent
        )

    def _build_detail_ui(self):
        self.group = SettingsGroup()

        is_present = self.backend.is_camera_present()
        self.cam_switch = Switch()
        if is_present:
            self.cam_switch.setChecked(self.backend.get_camera_access())
            self.cam_switch.toggled.connect(self.backend.set_camera_access)
        else:
            self.cam_switch.setChecked(False)
            self.cam_switch.setEnabled(False)

        self.row_cam = SettingsRow(t("privacy.camera_access", "Camera Access"), self.cam_switch, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_cam)

        hw_txt = t("privacy.connected", "Connected") if is_present else t("privacy.no_cam", "No Camera Connected")
        self.hw_status = QLabel(hw_txt)
        self.hw_status.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        self.row_hw = SettingsRow(t("privacy.camera_hw", "Camera Hardware"), self.hw_status, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_hw)

        pipe_txt = "PipeWire Video Source" if is_present else "PipeWire Video Source (" + t("privacy.inactive", "Inactive") + ")"
        self.pipe_cam_lbl = QLabel(pipe_txt)
        self.pipe_cam_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        self.row_pipe = SettingsRow(t("privacy.capture_pipe", "Capture Pipeline"), self.pipe_cam_lbl, show_separator=False, is_interactive=False)
        self.group.add_row(self.row_pipe)

        self.layout.addWidget(self.group)

    def _retranslate_detail_ui(self):
        if hasattr(self, 'row_cam'):
            self.row_cam.label.setText(t("privacy.camera_access", "Camera Access"))
        if hasattr(self, 'row_hw'):
            self.row_hw.label.setText(t("privacy.camera_hw", "Camera Hardware"))
        if hasattr(self, 'hw_status'):
            is_present = self.backend.is_camera_present()
            self.hw_status.setText(t("privacy.connected", "Connected") if is_present else t("privacy.no_cam", "No Camera Connected"))
        if hasattr(self, 'row_pipe'):
            self.row_pipe.label.setText(t("privacy.capture_pipe", "Capture Pipeline"))

    def refresh_settings(self):
        if hasattr(self, 'cam_switch'):
            is_present = self.backend.is_camera_present()
            if is_present:
                cur = self.backend.get_camera_access()
                if self.cam_switch.isChecked() != cur:
                    self.cam_switch.setChecked(cur)
                if not self.cam_switch.isEnabled():
                    self.cam_switch.setEnabled(True)
            else:
                if self.cam_switch.isChecked():
                    self.cam_switch.setChecked(False)
                if self.cam_switch.isEnabled():
                    self.cam_switch.setEnabled(False)

            if hasattr(self, 'hw_status'):
                self.hw_status.setText(t("privacy.connected", "Connected") if is_present else t("privacy.no_cam", "No Camera Connected"))
            if hasattr(self, 'pipe_cam_lbl'):
                self.pipe_cam_lbl.setText("PipeWire Video Source" if is_present else "PipeWire Video Source (" + t("privacy.inactive", "Inactive") + ")")

# =============================================================================
# 5. Microphone Detail Page
# =============================================================================

class MicrophoneDetailPage(BasePrivacyDetailPage):
    def __init__(self, backend: PrivacyBackend, parent=None):
        super().__init__(
            title_key="privacy.microphone",
            default_title="Microphone",
            desc_key="privacy.microphone_desc",
            default_desc="Control global microphone input and audio capture permissions across PipeWire.",
            backend=backend,
            parent=parent
        )

    def _build_detail_ui(self):
        self.group = SettingsGroup()

        is_present = self.backend.is_microphone_present()
        self.mic_switch = Switch()
        if is_present:
            self.mic_switch.setChecked(self.backend.get_microphone_access())
            self.mic_switch.toggled.connect(self.backend.set_microphone_access)
        else:
            self.mic_switch.setChecked(False)
            self.mic_switch.setEnabled(False)

        self.row_mic = SettingsRow(t("privacy.mic_access", "Microphone Access"), self.mic_switch, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_mic)

        dev_name = self.backend.get_default_microphone_name()
        self.dev_lbl = QLabel(dev_name)
        self.dev_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        self.row_dev = SettingsRow(t("privacy.default_input", "Default Input Device"), self.dev_lbl, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_dev)

        self.pipe_mic_lbl = QLabel(self.backend.get_pipewire_version())
        self.pipe_mic_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        self.row_pipe = SettingsRow(t("privacy.audio_server", "Audio Server"), self.pipe_mic_lbl, show_separator=False, is_interactive=False)
        self.group.add_row(self.row_pipe)

        self.layout.addWidget(self.group)

    def _retranslate_detail_ui(self):
        if hasattr(self, 'row_mic'):
            self.row_mic.label.setText(t("privacy.mic_access", "Microphone Access"))
        if hasattr(self, 'row_dev'):
            self.row_dev.label.setText(t("privacy.default_input", "Default Input Device"))
        if hasattr(self, 'row_pipe'):
            self.row_pipe.label.setText(t("privacy.audio_server", "Audio Server"))

    def refresh_settings(self):
        if hasattr(self, 'mic_switch'):
            cur = self.backend.get_microphone_access()
            if self.mic_switch.isChecked() != cur:
                self.mic_switch.setChecked(cur)

        if hasattr(self, 'dev_lbl'):
            self.dev_lbl.setText(self.backend.get_default_microphone_name())
        if hasattr(self, 'pipe_mic_lbl'):
            self.pipe_mic_lbl.setText(self.backend.get_pipewire_version())

# =============================================================================
# 6. Device Security Detail Page
# =============================================================================

class DeviceSecurityDetailPage(BasePrivacyDetailPage):
    def __init__(self, backend: PrivacyBackend, parent=None):
        super().__init__(
            title_key="privacy.device_security",
            default_title="Device Security",
            desc_key="privacy.device_security_desc",
            default_desc="View device security status and restrict unauthorized physical USB access.",
            backend=backend,
            parent=parent
        )

    def _build_detail_ui(self):
        self.group = SettingsGroup()

        self.usb_switch = Switch()
        self.usb_switch.setChecked(self.backend.get_usb_protection_enabled())
        self.usb_switch.toggled.connect(self._on_usb_toggled)
        self.row_usb = SettingsRow(t("privacy.usb_protection", "USB Device Protection"), self.usb_switch, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_usb)

        cur_lvl = self.backend.get_usb_protection_level()
        lvl_opts = [
            ("lockscreen", t("privacy.lockscreen_opt", "Lock Screen")),
            ("always", t("privacy.always_opt", "Always"))
        ]
        self.lvl_seg = SegmentedControl(lvl_opts, cur_lvl)
        self.lvl_seg.valueChanged.connect(self._on_lvl_changed)
        self.row_lvl = SettingsRow(t("privacy.protection_lvl", "Protection Level"), self.lvl_seg, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_lvl)

        self.sec_lbl = QLabel(self._get_sec_status_text())
        self.sec_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        self.row_status = SettingsRow(t("privacy.security_status", "Security Status"), self.sec_lbl, show_separator=False, is_interactive=False)
        self.group.add_row(self.row_status)

        self.layout.addWidget(self.group)

    def _get_sec_status_text(self) -> str:
        if not self.backend.get_usb_protection_enabled():
            return t("privacy.status_usb_disabled", "Disabled (All USB Allowed)")
        lvl = self.backend.get_usb_protection_level()
        if lvl == "always":
            return t("privacy.status_usb_always", "Protected (Always Block New USB)")
        return t("privacy.status_usb_lock", "Protected (Block at Lock Screen)")

    def _retranslate_detail_ui(self):
        if hasattr(self, 'row_usb'):
            self.row_usb.label.setText(t("privacy.usb_protection", "USB Device Protection"))
        if hasattr(self, 'row_lvl'):
            self.row_lvl.label.setText(t("privacy.protection_lvl", "Protection Level"))
        if hasattr(self, 'lvl_seg'):
            self.lvl_seg.set_segments([
                ("lockscreen", t("privacy.lockscreen_opt", "Lock Screen")),
                ("always", t("privacy.always_opt", "Always"))
            ])
        if hasattr(self, 'row_status'):
            self.row_status.label.setText(t("privacy.security_status", "Security Status"))
        if hasattr(self, 'sec_lbl'):
            self.sec_lbl.setText(self._get_sec_status_text())

    def _on_usb_toggled(self, checked: bool):
        self.backend.set_usb_protection_enabled(checked)
        if hasattr(self, 'sec_lbl'):
            self.sec_lbl.setText(self._get_sec_status_text())

    def _on_lvl_changed(self, lvl: str):
        self.backend.set_usb_protection_level(lvl)
        if hasattr(self, 'sec_lbl'):
            self.sec_lbl.setText(self._get_sec_status_text())

    def refresh_settings(self):
        if hasattr(self, 'usb_switch'):
            cur = self.backend.get_usb_protection_enabled()
            if self.usb_switch.isChecked() != cur:
                self.usb_switch.setChecked(cur)

        if hasattr(self, 'lvl_seg'):
            cur_lvl = self.backend.get_usb_protection_level()
            if self.lvl_seg.active_id != cur_lvl:
                self.lvl_seg.set_active_id(cur_lvl, emit_signal=False)

        if hasattr(self, 'sec_lbl'):
            self.sec_lbl.setText(self._get_sec_status_text())

# =============================================================================
# 7. Remote Desktop Detail Page
# =============================================================================

class RemoteDesktopDetailPage(BasePrivacyDetailPage):
    def __init__(self, backend: PrivacyBackend, parent=None):
        super().__init__(
            title_key="privacy.remote_desktop",
            default_title="Remote Desktop",
            desc_key="privacy.remote_desktop_desc",
            default_desc="Manage remote desktop connections to this machine using GNOME Remote Desktop (RDP).",
            backend=backend,
            parent=parent
        )

    def _build_detail_ui(self):
        self.group = SettingsGroup()

        is_rdp = self.backend.get_remote_desktop_enabled()
        self.rdp_switch = Switch()
        self.rdp_switch.setChecked(is_rdp)
        self.rdp_switch.toggled.connect(self._on_rdp_toggled)
        self.row_rdp = SettingsRow(t("privacy.rdp_toggle", "Remote Desktop (RDP)"), self.rdp_switch, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_rdp)

        cur_mode = self.backend.get_screen_share_mode()
        share_opts = [
            ("mirror-primary", t("privacy.mirror_primary", "Mirror Primary")),
            ("extend", t("privacy.extend_disp", "Extend Display"))
        ]
        self.share_seg = SegmentedControl(share_opts, cur_mode)
        self.share_seg.setEnabled(is_rdp)
        self.share_seg.valueChanged.connect(self.backend.set_screen_share_mode)
        self.row_share = SettingsRow(t("privacy.share_mode", "Screen Share Mode"), self.share_seg, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_share)

        port = self.backend.get_rdp_port()
        self.port_lbl = QLabel(f"{port} (" + t("privacy.std_rdp", "Standard RDP") + ")")
        self.port_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        self.row_port = SettingsRow(t("privacy.port", "Port"), self.port_lbl, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_port)

        svc_txt = t("privacy.active", "Active") if self.backend.is_remote_desktop_service_active() else t("privacy.inactive", "Inactive")
        self.svc_lbl = QLabel(svc_txt)
        self.svc_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        self.row_svc = SettingsRow(t("privacy.service_status", "Service Status"), self.svc_lbl, show_separator=False, is_interactive=False)
        self.group.add_row(self.row_svc)

        self.layout.addWidget(self.group)

    def _retranslate_detail_ui(self):
        if hasattr(self, 'row_rdp'):
            self.row_rdp.label.setText(t("privacy.rdp_toggle", "Remote Desktop (RDP)"))
        if hasattr(self, 'row_share'):
            self.row_share.label.setText(t("privacy.share_mode", "Screen Share Mode"))
        if hasattr(self, 'share_seg'):
            self.share_seg.set_segments([
                ("mirror-primary", t("privacy.mirror_primary", "Mirror Primary")),
                ("extend", t("privacy.extend_disp", "Extend Display"))
            ])
        if hasattr(self, 'row_port'):
            self.row_port.label.setText(t("privacy.port", "Port"))
        if hasattr(self, 'port_lbl'):
            port = self.backend.get_rdp_port()
            self.port_lbl.setText(f"{port} (" + t("privacy.std_rdp", "Standard RDP") + ")")
        if hasattr(self, 'row_svc'):
            self.row_svc.label.setText(t("privacy.service_status", "Service Status"))
        if hasattr(self, 'svc_lbl'):
            self.svc_lbl.setText(t("privacy.active", "Active") if self.backend.is_remote_desktop_service_active() else t("privacy.inactive", "Inactive"))

    def _on_rdp_toggled(self, checked: bool):
        self.backend.set_remote_desktop_enabled(checked)
        if hasattr(self, 'share_seg'):
            self.share_seg.setEnabled(checked)
        if hasattr(self, 'svc_lbl'):
            self.svc_lbl.setText(t("privacy.active", "Active") if self.backend.is_remote_desktop_service_active() else t("privacy.inactive", "Inactive"))

    def refresh_settings(self):
        if hasattr(self, 'rdp_switch'):
            cur = self.backend.get_remote_desktop_enabled()
            if self.rdp_switch.isChecked() != cur:
                self.rdp_switch.setChecked(cur)
            if hasattr(self, 'share_seg'):
                self.share_seg.setEnabled(cur)
                cur_mode = self.backend.get_screen_share_mode()
                if self.share_seg.active_id != cur_mode:
                    self.share_seg.set_active_id(cur_mode, emit_signal=False)
            if hasattr(self, 'port_lbl'):
                port = self.backend.get_rdp_port()
                self.port_lbl.setText(f"{port} (" + t("privacy.std_rdp", "Standard RDP") + ")")
            if hasattr(self, 'svc_lbl'):
                self.svc_lbl.setText(t("privacy.active", "Active") if self.backend.is_remote_desktop_service_active() else t("privacy.inactive", "Inactive"))


# =============================================================================
# 8. Remote Control Detail Page
# =============================================================================

class RemoteControlDetailPage(BasePrivacyDetailPage):
    def __init__(self, backend: PrivacyBackend, parent=None):
        super().__init__(
            title_key="privacy.remote_control",
            default_title="Remote Control",
            desc_key="privacy.remote_control_desc",
            default_desc="Configure remote input permissions for keyboard, mouse, and touch events over remote connections.",
            backend=backend,
            parent=parent
        )

    def _build_detail_ui(self):
        self.group = SettingsGroup()

        cur_mode = "view" if self.backend.is_remote_control_view_only() else "control"
        control_opts = [
            ("view", t("privacy.view_only", "View Only")),
            ("control", t("privacy.full_control", "Full Control"))
        ]
        self.control_seg = SegmentedControl(control_opts, cur_mode)
        self.control_seg.valueChanged.connect(self._on_mode_changed)
        self.row_mode = SettingsRow(t("privacy.control_mode", "Remote Control Mode"), self.control_seg, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_mode)

        self.input_lbl = QLabel(t("privacy.supported_input_val", "Keyboard, Pointer, Touchscreen"))
        self.input_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        self.row_input = SettingsRow(t("privacy.supported_input", "Supported Input"), self.input_lbl, show_separator=True, is_interactive=False)
        self.group.add_row(self.row_input)

        self.eis_lbl = QLabel("Mutter EIS (Wayland Native)")
        self.eis_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        self.row_emul = SettingsRow(t("privacy.input_emulation", "Input Emulation"), self.eis_lbl, show_separator=False, is_interactive=False)
        self.group.add_row(self.row_emul)

        self.layout.addWidget(self.group)

    def _retranslate_detail_ui(self):
        if hasattr(self, 'row_mode'):
            self.row_mode.label.setText(t("privacy.control_mode", "Remote Control Mode"))
        if hasattr(self, 'control_seg'):
            self.control_seg.set_segments([
                ("view", t("privacy.view_only", "View Only")),
                ("control", t("privacy.full_control", "Full Control"))
            ])
        if hasattr(self, 'row_input'):
            self.row_input.label.setText(t("privacy.supported_input", "Supported Input"))
        if hasattr(self, 'input_lbl'):
            self.input_lbl.setText(t("privacy.supported_input_val", "Keyboard, Pointer, Touchscreen"))
        if hasattr(self, 'row_emul'):
            self.row_emul.label.setText(t("privacy.input_emulation", "Input Emulation"))

    def _on_mode_changed(self, mode_id: str):
        is_view_only = (mode_id == "view")
        self.backend.set_remote_control_view_only(is_view_only)

    def refresh_settings(self):
        if hasattr(self, 'control_seg'):
            cur_mode = "view" if self.backend.is_remote_control_view_only() else "control"
            if self.control_seg.active_id != cur_mode:
                self.control_seg.set_active_id(cur_mode, emit_signal=False)

# =============================================================================
# Main Privacy Hub Page (Overview & Navigation Hub)
# =============================================================================

class PrivacyHubPage(QWidget):
    """
    Main Overview Hub with Header, Hero Card, and Grouped Navigation Rows (Chevrons).
    """
    navigate_to_detail = Signal(str)

    def __init__(self, backend: PrivacyBackend, parent=None):
        super().__init__(parent)
        self.backend = backend

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        self.scroll.viewport().setStyleSheet("background: transparent;")

        self.content = QWidget()
        self.content.setObjectName("PrivacyContent")
        self.content.setStyleSheet("background: transparent;")
        self.scroll.setWidget(self.content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)

        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(40, 30, 40, 40)
        self.layout.setSpacing(18)
        self.layout.setAlignment(Qt.AlignTop)

        self._build_ui()
        self.layout.addStretch()

        ThemeManager.theme_changed.connect(self.update_style)
        self.update_style()

    def _create_section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_MEDIUM}; "
            f"font-size: 11px; margin-left: 12px; margin-top: 6px; letter-spacing: 0.6px;"
        )
        return lbl

    def _build_ui(self):
        # 0. Header Title
        self.title_lbl = QLabel(t("privacy.title", "Privacy & Security"))
        self.title_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};"
        )
        self.layout.addWidget(self.title_lbl)

        # 1. Hero Card
        self.hero_card = PrivacyHeroCard(self.backend)
        self.layout.addWidget(self.hero_card)

        # =========================================================================
        # 2. SYSTEM GROUP
        # =========================================================================
        self.lbl_system = self._create_section_label(t("privacy.sec_system", "SYSTEM"))
        self.layout.addWidget(self.lbl_system)
        group_system = SettingsGroup()

        self.row_lock = PrivacyNavigationRow(
            route_id="screen_lock",
            icon_type="lock",
            icon_color="#8E8E93",
            title=t("privacy.screen_lock", "Screen Lock"),
            subtitle=t("privacy.screen_lock_sub", "Manage screen timeout and automatic locking"),
            show_separator=True
        )
        self.row_lock.clicked.connect(self.navigate_to_detail.emit)
        group_system.add_row(self.row_lock)

        self.row_location = PrivacyNavigationRow(
            route_id="location",
            icon_type="location",
            icon_color="#007AFF",
            title=t("privacy.location", "Location Services"),
            subtitle=t("privacy.location_sub", "Control location access for apps and services"),
            show_separator=True
        )
        self.row_location.clicked.connect(self.navigate_to_detail.emit)
        group_system.add_row(self.row_location)

        self.row_history = PrivacyNavigationRow(
            route_id="history",
            icon_type="history",
            icon_color="#AF52DE",
            title=t("privacy.history", "File & Recent History"),
            subtitle=t("privacy.history_sub", "Manage recent files and clear history"),
            show_separator=False
        )
        self.row_history.clicked.connect(self.navigate_to_detail.emit)
        group_system.add_row(self.row_history)
        self.layout.addWidget(group_system)

        # =========================================================================
        # 3. DEVICES GROUP
        # =========================================================================
        self.lbl_devices = self._create_section_label(t("privacy.sec_devices", "DEVICES"))
        self.layout.addWidget(self.lbl_devices)
        group_devices = SettingsGroup()

        self.row_camera = PrivacyNavigationRow(
            route_id="camera",
            icon_type="camera",
            icon_color="#34C759",
            title=t("privacy.camera", "Camera"),
            subtitle=t("privacy.camera_sub", "Manage camera access for apps and services"),
            show_separator=True
        )
        self.row_camera.clicked.connect(self.navigate_to_detail.emit)
        group_devices.add_row(self.row_camera)

        self.row_mic = PrivacyNavigationRow(
            route_id="microphone",
            icon_type="mic",
            icon_color="#FF3B30",
            title=t("privacy.microphone", "Microphone"),
            subtitle=t("privacy.microphone_sub", "Manage microphone access for apps and services"),
            show_separator=True
        )
        self.row_mic.clicked.connect(self.navigate_to_detail.emit)
        group_devices.add_row(self.row_mic)

        self.row_usb = PrivacyNavigationRow(
            route_id="device_security",
            icon_type="shield",
            icon_color="#007AFF",
            title=t("privacy.device_security", "Device Security"),
            subtitle=t("privacy.device_security_sub", "View device security status and trusted devices"),
            show_separator=False
        )
        self.row_usb.clicked.connect(self.navigate_to_detail.emit)
        group_devices.add_row(self.row_usb)
        self.layout.addWidget(group_devices)

        # =========================================================================
        # 4. REMOTE ACCESS GROUP
        # =========================================================================
        self.lbl_remote = self._create_section_label(t("privacy.sec_remote", "REMOTE ACCESS"))
        self.layout.addWidget(self.lbl_remote)
        group_remote = SettingsGroup()

        self.row_rdp = PrivacyNavigationRow(
            route_id="remote_desktop",
            icon_type="remote",
            icon_color="#5856D6",
            title=t("privacy.remote_desktop", "Remote Desktop"),
            subtitle=t("privacy.remote_desktop_sub", "Manage remote desktop access to this device"),
            show_separator=True
        )
        self.row_rdp.clicked.connect(self.navigate_to_detail.emit)
        group_remote.add_row(self.row_rdp)

        control_detail = t("privacy.view_only", "View Only") if self.backend.is_remote_control_view_only() else t("privacy.full_control", "Full Control")
        self.row_control = PrivacyNavigationRow(
            route_id="remote_control",
            icon_type="control",
            icon_color="#FF9500",
            title=t("privacy.remote_control", "Remote Control Mode"),
            subtitle=t("privacy.remote_control_sub", "Allow this device to be controlled remotely"),
            detail_value=control_detail,
            show_separator=False
        )
        self.row_control.clicked.connect(self.navigate_to_detail.emit)
        group_remote.add_row(self.row_control)
        self.layout.addWidget(group_remote)

    def retranslate_ui(self):
        self.title_lbl.setText(t("privacy.title", "Privacy & Security"))
        if hasattr(self, 'lbl_system'):
            self.lbl_system.setText(t("privacy.sec_system", "SYSTEM"))
        if hasattr(self, 'lbl_devices'):
            self.lbl_devices.setText(t("privacy.sec_devices", "DEVICES"))
        if hasattr(self, 'lbl_remote'):
            self.lbl_remote.setText(t("privacy.sec_remote", "REMOTE ACCESS"))

        if hasattr(self, 'row_lock'):
            self.row_lock.update_texts(t("privacy.screen_lock", "Screen Lock"), t("privacy.screen_lock_sub", "Manage screen timeout and automatic locking"))
        if hasattr(self, 'row_location'):
            self.row_location.update_texts(t("privacy.location", "Location Services"), t("privacy.location_sub", "Control location access for apps and services"))
        if hasattr(self, 'row_history'):
            self.row_history.update_texts(t("privacy.history", "File & Recent History"), t("privacy.history_sub", "Manage recent files and clear history"))
        if hasattr(self, 'row_camera'):
            self.row_camera.update_texts(t("privacy.camera", "Camera"), t("privacy.camera_sub", "Manage camera access for apps and services"))
        if hasattr(self, 'row_mic'):
            self.row_mic.update_texts(t("privacy.microphone", "Microphone"), t("privacy.microphone_sub", "Manage microphone access for apps and services"))
        if hasattr(self, 'row_usb'):
            self.row_usb.update_texts(t("privacy.device_security", "Device Security"), t("privacy.device_security_sub", "View device security status and trusted devices"))
        if hasattr(self, 'row_rdp'):
            self.row_rdp.update_texts(t("privacy.remote_desktop", "Remote Desktop"), t("privacy.remote_desktop_sub", "Manage remote desktop access to this device"))
        if hasattr(self, 'row_control'):
            control_detail = t("privacy.view_only", "View Only") if self.backend.is_remote_control_view_only() else t("privacy.full_control", "Full Control")
            self.row_control.update_texts(t("privacy.remote_control", "Remote Control Mode"), t("privacy.remote_control_sub", "Allow this device to be controlled remotely"), control_detail)

        if hasattr(self, 'hero_card'):
            self.hero_card.retranslate_ui()

    def refresh_settings(self):
        if hasattr(self, 'hero_card'):
            self.hero_card.update_info()
        if hasattr(self, 'row_control'):
            val = t("privacy.view_only", "View Only") if self.backend.is_remote_control_view_only() else t("privacy.full_control", "Full Control")
            self.row_control.set_value(val)

    def update_style(self, _is_dark=False):
        fix_label_styles(self)
        if hasattr(self, 'hero_card'):
            self.hero_card.update_style()
        self.update()

# =============================================================================
# Root Privacy Page (QStackedWidget with Hub + 8 Detail Pages)
# =============================================================================

class PrivacyPage(QStackedWidget):
    """
    Root Container with QStackedWidget for seamless internal navigation
    between Privacy Hub and all 8 Category Detail Pages.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backend = PrivacyBackend()

        # 0. Hub Page
        self.hub_page = PrivacyHubPage(self.backend)
        self.hub_page.navigate_to_detail.connect(self.open_detail_page)
        self.addWidget(self.hub_page)

        # 1..8 Detail Pages
        self.detail_pages = {
            "screen_lock": ScreenLockDetailPage(self.backend),
            "location": LocationServicesDetailPage(self.backend),
            "history": RecentHistoryDetailPage(self.backend),
            "camera": CameraDetailPage(self.backend),
            "microphone": MicrophoneDetailPage(self.backend),
            "device_security": DeviceSecurityDetailPage(self.backend),
            "remote_desktop": RemoteDesktopDetailPage(self.backend),
            "remote_control": RemoteControlDetailPage(self.backend)
        }

        for page in self.detail_pages.values():
            page.back_requested.connect(self.open_hub_page)
            self.addWidget(page)

        # Background sync timer
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(1000)
        self._poll_timer.timeout.connect(self.refresh_settings)
        self._poll_timer.start()

        i18n.language_changed.connect(self.retranslate_ui)

    def open_detail_page(self, route_id: str):
        if route_id in self.detail_pages:
            page = self.detail_pages[route_id]
            page.refresh_settings()
            self.setCurrentWidget(page)

    def reset_to_root(self):
        self.open_hub_page()

    def open_hub_page(self):
        self.hub_page.refresh_settings()
        self.setCurrentWidget(self.hub_page)

    def showEvent(self, event):
        super().showEvent(event)
        self.open_hub_page()

    def refresh_settings(self):
        curr = self.currentWidget()
        if hasattr(curr, 'refresh_settings'):
            curr.refresh_settings()
        self.hub_page.refresh_settings()

    def retranslate_ui(self):
        self.hub_page.retranslate_ui()
        for page in self.detail_pages.values():
            if hasattr(page, 'retranslate_ui'):
                page.retranslate_ui()

    def cleanup(self):
        if hasattr(self, '_poll_timer'):
            self._poll_timer.stop()

    def update_style(self, _is_dark=False):
        for i in range(self.count()):
            w = self.widget(i)
            if hasattr(w, 'update_style'):
                w.update_style()

    def get_search_target(self, target_id: str) -> QWidget | None:
        self.setCurrentWidget(self.hub_page)
        targets = {
            "privacy.lock": getattr(self.hub_page, "row_lock", None),
            "privacy.location": getattr(self.hub_page, "row_location", None),
            "privacy.camera": getattr(self.hub_page, "row_camera", None),
            "privacy.mic": getattr(self.hub_page, "row_mic", None),
            "privacy.history": getattr(self.hub_page, "row_history", None),
            "privacy.remote": getattr(self.hub_page, "row_rdp", None),
        }
        return targets.get(target_id)
