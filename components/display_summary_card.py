from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import (
    QPainter, QColor, QPainterPath, QPen, QFont, QLinearGradient
)
from models.monitor import MonitorModel
from theme.colors import Colors
from theme.typography import Typography
from theme.metrics import CARD_RADIUS
from theme.manager import ThemeManager
from theme.glass_shimmer import GlassShimmerHelper
from localization import Localization


class DisplaySummaryCard(QWidget):
    """
    Summary glass card representing a connected monitor.
    Displays name, primary badge, status dot, chevron, resolution, refresh rate, and HDR status.
    """
    clicked = Signal(str)  # monitor.id

    def __init__(self, monitor: MonitorModel, is_selected: bool = False, hdr_supported: bool = False, parent=None):
        super().__init__(parent)
        self.monitor = monitor
        self.is_selected = is_selected
        self.hdr_supported = hdr_supported

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(84)

        self.shimmer = GlassShimmerHelper(self)
        self._hover_alpha = 0.0

        self.hover_anim = QPropertyAnimation(self, b"hover_alpha")
        self.hover_anim.setDuration(150)
        self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._build_ui()
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def update_style(self, _is_dark=False):
        if hasattr(self, 'name_lbl'):
            self.name_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_BODY + 1}px; "
                f"font-weight: {Typography.WEIGHT_SEMIBOLD}; background: transparent;"
            )
        if hasattr(self, 'res_lbl'):
            self.res_lbl.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_CAPTION}px; "
                f"font-weight: {Typography.WEIGHT_NORMAL}; background: transparent;"
            )
        if hasattr(self, 'rate_lbl'):
            self.rate_lbl.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_CAPTION}px; "
                f"font-weight: {Typography.WEIGHT_NORMAL}; background: transparent;"
            )
        if hasattr(self, 'hdr_lbl'):
            self.hdr_lbl.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_CAPTION}px; "
                f"font-weight: {Typography.WEIGHT_NORMAL}; background: transparent;"
            )
        if hasattr(self, 'dot_lbl'):
            dot_color = Colors.ACCENT_BLUE if self.is_selected else ("#8E8E93" if _is_dark else "#AEAEB2")
            self.dot_lbl.setStyleSheet(f"color: {dot_color}; font-size: 11px; background: transparent;")
        if hasattr(self, 'chevron_lbl'):
            chev_color = Colors.ACCENT_BLUE if self.is_selected else Colors.TEXT_TERTIARY
            self.chevron_lbl.setStyleSheet(
                f"color: {chev_color}; font-size: 18px; font-weight: {Typography.WEIGHT_MEDIUM}; background: transparent;"
            )
        self.update()

    def set_selected(self, selected: bool):
        if self.is_selected != selected:
            self.is_selected = selected
            self.update_style(ThemeManager.is_dark)

    @Property(float)
    def hover_alpha(self):
        return self._hover_alpha

    @hover_alpha.setter
    def hover_alpha(self, val):
        self._hover_alpha = val
        self.update()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(8)

        # ── Top Row: Status Dot, Name, Primary Badge, Spacer, Chevron ──
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        top_row.setAlignment(Qt.AlignVCenter)

        # Status Dot
        self.dot_lbl = QLabel("●")
        self.dot_lbl.setStyleSheet(f"color: {Colors.ACCENT_BLUE}; font-size: 11px; background: transparent;")
        top_row.addWidget(self.dot_lbl)

        # Monitor Name
        display_name = self.monitor.name or f"Display {self.monitor.id}"
        self.name_lbl = QLabel(display_name)
        self.name_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_BODY + 1}px; "
            f"font-weight: {Typography.WEIGHT_SEMIBOLD}; background: transparent;"
        )
        top_row.addWidget(self.name_lbl)

        # Primary Badge Pill
        if self.monitor.is_primary:
            primary_text = Localization.get("display.primary_badge", "Primary")
            self.primary_badge = QLabel(f" {primary_text} ")
            self.primary_badge.setStyleSheet(
                f"color: #007AFF; font-size: {Typography.SIZE_CAPTION}px; font-weight: {Typography.WEIGHT_SEMIBOLD}; "
                f"background: rgba(0, 122, 255, 0.12); border: 1px solid rgba(0, 122, 255, 0.25); "
                f"border-radius: 9px; padding: 2px 6px;"
            )
            top_row.addWidget(self.primary_badge)

        top_row.addStretch()

        # Chevron Indicator
        self.chevron_lbl = QLabel("›")
        self.chevron_lbl.setStyleSheet(
            f"color: {Colors.TEXT_TERTIARY}; font-size: 18px; font-weight: {Typography.WEIGHT_MEDIUM}; background: transparent;"
        )
        top_row.addWidget(self.chevron_lbl)
        main_layout.addLayout(top_row)

        # ── Bottom Row: Resolution, Refresh Rate, HDR Chips ──
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)
        bottom_row.setAlignment(Qt.AlignVCenter)

        # Resolution
        w = self.monitor.width if self.monitor.width > 0 else 1920
        h = self.monitor.height if self.monitor.height > 0 else 1080
        res_text = f"🖥️ {w} × {h}"
        self.res_lbl = QLabel(res_text)
        self.res_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_CAPTION}px; "
            f"font-weight: {Typography.WEIGHT_NORMAL}; background: transparent;"
        )
        bottom_row.addWidget(self.res_lbl)

        # Rate
        rate_val = int(round(self.monitor.current_rate)) if self.monitor.current_rate > 0 else 60
        rate_text = f"〰️ {rate_val} Hz"
        self.rate_lbl = QLabel(rate_text)
        self.rate_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_CAPTION}px; "
            f"font-weight: {Typography.WEIGHT_NORMAL}; background: transparent;"
        )
        bottom_row.addWidget(self.rate_lbl)

        # HDR / SDR
        hdr_key = "display.hdr_status" if self.hdr_supported else "display.sdr_status"
        hdr_fallback = "HDR" if self.hdr_supported else "SDR"
        hdr_text = f"☀️ {Localization.get(hdr_key, hdr_fallback)}"
        self.hdr_lbl = QLabel(hdr_text)
        self.hdr_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_CAPTION}px; "
            f"font-weight: {Typography.WEIGHT_NORMAL}; background: transparent;"
        )
        bottom_row.addWidget(self.hdr_lbl)

        bottom_row.addStretch()
        main_layout.addLayout(bottom_row)

    def set_selected(self, selected: bool):
        if self.is_selected != selected:
            self.is_selected = selected
            self.update_style(ThemeManager.is_dark)

    def update_monitor(self, monitor: MonitorModel, hdr_supported: bool = False):
        self.monitor = monitor
        self.hdr_supported = hdr_supported
        display_name = self.monitor.name or f"Display {self.monitor.id}"
        self.name_lbl.setText(display_name)
        w = self.monitor.width if self.monitor.width > 0 else 1920
        h = self.monitor.height if self.monitor.height > 0 else 1080
        self.res_lbl.setText(f"🖥️ {w} × {h}")
        rate_val = int(round(self.monitor.current_rate)) if self.monitor.current_rate > 0 else 60
        self.rate_lbl.setText(f"〰️ {rate_val} Hz")
        hdr_key = "display.hdr_status" if self.hdr_supported else "display.sdr_status"
        hdr_fallback = "HDR" if self.hdr_supported else "SDR"
        self.hdr_lbl.setText(f"☀️ {Localization.get(hdr_key, hdr_fallback)}")
        self.update()

    def enterEvent(self, event):
        self.shimmer.handle_enter(event)
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self._hover_alpha)
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shimmer.handle_leave(event)
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self._hover_alpha)
        self.hover_anim.setEndValue(0.0)
        self.hover_anim.start()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        self.shimmer.handle_mouse_move(event)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.monitor.id)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        is_dark = ThemeManager.is_dark

        rect = self.rect()

        # Shadow
        shadow_alpha = 35 if is_dark else 15
        shadow_color = QColor(0, 0, 0, shadow_alpha)
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(rect.adjusted(2, 3, -2, -2), CARD_RADIUS, CARD_RADIUS)
        p.fillPath(shadow_path, shadow_color)

        # Card Background
        bg_color = QColor(Colors.CARD_BG)
        if self.is_selected:
            if is_dark:
                bg_color = QColor(36, 42, 54, 230)
            else:
                bg_color = QColor(240, 246, 255, 230)

        # Apply subtle hover highlight
        if self._hover_alpha > 0.01 and not self.is_selected:
            hover_overlay = QColor(255, 255, 255, int(15 * self._hover_alpha)) if is_dark else QColor(0, 0, 0, int(8 * self._hover_alpha))
            bg_path = QPainterPath()
            bg_path.addRoundedRect(rect, CARD_RADIUS, CARD_RADIUS)
            p.fillPath(bg_path, bg_color)
            p.fillPath(bg_path, hover_overlay)
        else:
            bg_path = QPainterPath()
            bg_path.addRoundedRect(rect, CARD_RADIUS, CARD_RADIUS)
            p.fillPath(bg_path, bg_color)

        # Border
        if self.is_selected:
            border_pen = QPen(QColor(Colors.ACCENT_BLUE), 1.5)
        else:
            border_color = QColor(Colors.CARD_BORDER)
            border_color.setAlpha(35 if is_dark else 55)
            border_pen = QPen(border_color, 1)

        p.setPen(border_pen)
        p.drawPath(bg_path)

        # Dynamic specular edge sheen
        self.shimmer.paint_shimmer(p, QRectF(rect), CARD_RADIUS, is_dark)
