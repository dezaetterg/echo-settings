from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QEasingCurve, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QLinearGradient, QRadialGradient

from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from localization import t

ACCENT_COLOR_DATA = {
    "multicolor": {"hex": "#007AFF", "loc_key": "appearance.color_multicolor"},
    "blue": {"hex": "#007AFF", "loc_key": "appearance.color_blue"},
    "purple": {"hex": "#AF52DE", "loc_key": "appearance.color_purple"},
    "pink": {"hex": "#FF2D55", "loc_key": "appearance.color_pink"},
    "red": {"hex": "#FF3B30", "loc_key": "appearance.color_red"},
    "orange": {"hex": "#FF9500", "loc_key": "appearance.color_orange"},
    "yellow": {"hex": "#FFCC00", "loc_key": "appearance.color_yellow"},
    "green": {"hex": "#28CD41", "loc_key": "appearance.color_green"},
    "teal": {"hex": "#5AC8FA", "loc_key": "appearance.color_teal"},
    "slate": {"hex": "#8E8E93", "loc_key": "appearance.color_slate"}
}

class InteractiveAccentSwitch(QWidget):
    """
    Miniature Apple-style toggle switch showing live accent styling with smooth animation.
    """
    def __init__(self, accent_hex: str = "#007AFF", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(40, 22)
        self.setCursor(Qt.PointingHandCursor)
        self.accent_hex = accent_hex
        self._checked = True
        self._position = 20.0

        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(180)

    @Property(float)
    def position(self):
        return self._position

    @position.setter
    def position(self, pos):
        self._position = pos
        self.update()

    def set_accent_hex(self, hex_code: str):
        self.accent_hex = hex_code
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._checked = not self._checked
            self.animation.stop()
            self.animation.setStartValue(self._position)
            self.animation.setEndValue(20.0 if self._checked else 2.0)
            self.animation.start()
            event.accept()
        else:
            super().mousePressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        is_dark = ThemeManager.is_dark

        # Background track
        if self._checked:
            bg_col = QColor(self.accent_hex)
        else:
            bg_col = QColor(255, 255, 255, 28) if is_dark else QColor(0, 0, 0, 28)

        track_path = QPainterPath()
        track_path.addRoundedRect(0, 0, self.width(), self.height(), self.height() / 2, self.height() / 2)
        p.fillPath(track_path, bg_col)

        if not self._checked:
            p.setPen(QPen(QColor(255, 255, 255, 35) if is_dark else QColor(0, 0, 0, 25), 1))
            p.drawPath(track_path)

        # Smooth Knob with soft depth
        knob_size = self.height() - 4
        knob_y = 2
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 40 if is_dark else 25))
        p.drawEllipse(int(self._position), knob_y + 1, knob_size, knob_size)

        p.setBrush(QColor("#FFFFFF"))
        p.setPen(QPen(QColor(0, 0, 0, 20), 0.5))
        p.drawEllipse(int(self._position), knob_y, knob_size, knob_size)
        p.end()


class GlowingAccentOrb(QWidget):
    """
    A glowing multi-stop radial gradient orb with specular highlight showing the exact accent color.
    """
    def __init__(self, accent_hex: str = "#007AFF", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(36, 36)
        self.accent_hex = accent_hex

    def set_accent_hex(self, hex_code: str):
        self.accent_hex = hex_code
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        col = QColor(self.accent_hex)
        if not col.isValid():
            col = QColor("#007AFF")

        cx, cy = self.width() / 2.0, self.height() / 2.0
        radius = 13.0

        # Ambient Glow Halo
        glow_grad = QRadialGradient(cx, cy, radius + 4)
        glow_col = QColor(col.red(), col.green(), col.blue(), 65)
        glow_grad.setColorAt(0.0, glow_col)
        glow_grad.setColorAt(0.7, QColor(col.red(), col.green(), col.blue(), 20))
        glow_grad.setColorAt(1.0, QColor(col.red(), col.green(), col.blue(), 0))
        p.setBrush(glow_grad)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), radius + 4, radius + 4)

        # Core Orb with Linear Gradient & Glint
        orb_grad = QLinearGradient(cx, cy - radius, cx, cy + radius)
        top_col = col.lighter(125)
        bot_col = col.darker(110)
        orb_grad.setColorAt(0.0, top_col)
        orb_grad.setColorAt(1.0, bot_col)

        p.setBrush(orb_grad)
        p.setPen(QPen(QColor(255, 255, 255, 140), 1.0))
        p.drawEllipse(QPointF(cx, cy), radius, radius)

        # Top Specular Glint
        glint_grad = QLinearGradient(cx, cy - radius, cx, cy)
        glint_grad.setColorAt(0.0, QColor(255, 255, 255, 175))
        glint_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(glint_grad)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy - 3.5), radius * 0.70, radius * 0.40)

        p.end()


class LiveAccentPreviewCard(QWidget):
    """
    Apple Tahoe Liquid Glass Live Accent Showcase.
    Demonstrates interactive controls, status tags, and system color specs in real time.
    """
    def __init__(self, current_accent: str = "blue", parent=None):
        super().__init__(parent)
        self.raw_accent = current_accent or "blue"
        self.accent_hex = self._resolve_hex(self.raw_accent)
        self.is_multicolor = (self.raw_accent == "multicolor")
        self.setAttribute(Qt.WA_Hover, True)
        self.setFixedHeight(74)

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 8, 14, 8)
        root.setSpacing(12)

        # ── 1. Interactive Button ──
        self.btn_preview = QPushButton(t("appearance.preview_button", "Action"), self)
        self.btn_preview.setCursor(Qt.PointingHandCursor)
        self.btn_preview.setFixedHeight(34)
        self.btn_preview.setMinimumWidth(80)
        self._btn_clicks = 0
        self.btn_preview.clicked.connect(self._on_btn_clicked)
        root.addWidget(self.btn_preview)

        # ── 2. Live Interactive Switch ──
        self.switch_preview = InteractiveAccentSwitch(self.accent_hex, self)
        root.addWidget(self.switch_preview)

        # ── 3. Translucent Live Badge ──
        self.badge_lbl = QLabel(self)
        self.badge_lbl.setAlignment(Qt.AlignCenter)
        self.badge_lbl.setFixedHeight(26)
        root.addWidget(self.badge_lbl)

        root.addStretch(1)

        # ── Vertical Subtle Divider ──
        self.v_divider = QFrame(self)
        self.v_divider.setFrameShape(QFrame.VLine)
        self.v_divider.setFixedHeight(30)
        root.addWidget(self.v_divider)

        # ── 4. Glowing Accent Orb ──
        self.orb_widget = GlowingAccentOrb(self.accent_hex, self)
        root.addWidget(self.orb_widget)

        # ── 5. Color Spec & System Status ──
        self.spec_box = QWidget(self)
        spec_layout = QVBoxLayout(self.spec_box)
        spec_layout.setContentsMargins(0, 2, 0, 2)
        spec_layout.setSpacing(1)

        self.name_label = QLabel(self.spec_box)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        spec_layout.addWidget(self.name_label)

        self.status_label = QLabel(self.spec_box)
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        spec_layout.addWidget(self.status_label)

        root.addWidget(self.spec_box)

        self.update_style()
        ThemeManager.theme_changed.connect(lambda _: self.update_style())

    def _resolve_hex(self, accent_val: str) -> str:
        if not accent_val:
            return "#007AFF"
        val = str(accent_val).strip().lower()
        if val in ACCENT_COLOR_DATA:
            return ACCENT_COLOR_DATA[val]["hex"]
        if val.startswith("#") and len(val) in (4, 7, 9):
            return val
        return "#007AFF"

    def _get_color_name(self) -> str:
        val = str(self.raw_accent).strip().lower()
        if val in ACCENT_COLOR_DATA:
            loc_key = ACCENT_COLOR_DATA[val]["loc_key"]
            return t(loc_key, val.capitalize())
        return val.capitalize()

    def _on_btn_clicked(self):
        self._btn_clicks += 1
        labels = [
            t("appearance.preview_active", "Active ✓"),
            t("appearance.preview_clicked", "Pressed!"),
            t("appearance.preview_button", "Action"),
        ]
        self.btn_preview.setText(labels[self._btn_clicks % len(labels)])

    def set_accent_color(self, accent: str):
        self.set_accent(accent)

    def set_accent(self, accent: str):
        self.raw_accent = str(accent)
        self.is_multicolor = (self.raw_accent == "multicolor")
        self.accent_hex = self._resolve_hex(self.raw_accent)
        self.switch_preview.set_accent_hex(self.accent_hex)
        self.orb_widget.set_accent_hex(self.accent_hex)
        self.update_style()

    def get_computed_hex(self) -> str:
        return self.accent_hex

    def update_style(self):
        is_dark = ThemeManager.is_dark
        col = QColor(self.accent_hex)
        if not col.isValid():
            col = QColor("#007AFF")

        # Dynamic high-contrast calculation
        lum = 0.299 * col.red() + 0.587 * col.green() + 0.114 * col.blue()
        btn_fg = "#18181A" if lum > 175 else "#FFFFFF"
        badge_fg = self.accent_hex if lum <= 175 else ("#FFCC00" if is_dark else "#A07000")

        soft_bg = f"rgba({col.red()}, {col.green()}, {col.blue()}, 0.16)"
        border_rgba = f"rgba({col.red()}, {col.green()}, {col.blue()}, 0.45)"

        # Primary Action Button with subtle shadow & contrast text
        btn_border = "rgba(0, 0, 0, 0.20)" if lum > 175 else "rgba(255, 255, 255, 0.28)"
        self.btn_preview.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent_hex};
                color: {btn_fg};
                border: 1px solid {btn_border};
                border-radius: 8px;
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 12.5px;
                font-weight: 600;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background-color: {self.accent_hex};
                opacity: 0.90;
            }}
            QPushButton:pressed {{
                background-color: {self.accent_hex};
                opacity: 0.75;
            }}
        """)

        # Badge Pill
        badge_text = t("appearance.preview_badge", "● Accent Live")
        self.badge_lbl.setText(badge_text)
        self.badge_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {soft_bg};
                color: {badge_fg};
                border: 1px solid {border_rgba};
                border-radius: 6px;
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 11.5px;
                font-weight: 600;
                padding: 3px 10px;
            }}
        """)

        # Divider
        div_col = "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(0, 0, 0, 0.10)"
        self.v_divider.setStyleSheet(f"QFrame {{ color: {div_col}; background-color: {div_col}; border: none; width: 1px; }}")

        # Spec Name & Hex
        color_title = self._get_color_name()
        hex_display = self.accent_hex
        self.name_label.setText(f"{color_title} <span style='font-family: SF Mono, Fira Code, monospace; font-size: 11px; opacity: 0.65; font-weight: normal;'>{hex_display}</span>")
        self.name_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 12.5px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)

        # System Status Subtitle
        status_text = t("appearance.preview_status_system", "System-wide Active ✓")
        self.status_label.setText(f"<span style='color: #28CD41;'>●</span> {status_text}")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 11px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
        """)

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        is_dark = ThemeManager.is_dark

        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 10.0, 10.0)

        # Apple Liquid Glass frosted substrate
        fill_col = QColor(255, 255, 255, 12 if is_dark else 22)
        p.fillPath(path, fill_col)

        # Delicate glass border with top specular highlight
        border_col = QColor(255, 255, 255, 24 if is_dark else 30)
        p.setPen(QPen(border_col, 1.0))
        p.drawPath(path)
        p.end()
