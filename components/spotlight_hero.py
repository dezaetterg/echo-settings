from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QPropertyAnimation, Property
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen
from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from theme.glass_shimmer import GlassShimmerHelper
from PySide6.QtCore import QRectF
import subprocess
import os

class SpotlightHero(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.setFixedHeight(110)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self.shimmer = GlassShimmerHelper(self)
        
        # Hover animation setup
        self._hover_progress = 0.0
        self.anim = QPropertyAnimation(self, b"hover_progress")
        self.anim.setDuration(200)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(24, 20, 24, 20)
        self.layout.setSpacing(18)
        
        # Icon
        self.icon_lbl = QLabel("🔍")
        self.icon_lbl.setFixedSize(52, 52)
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.icon_lbl, 0, Qt.AlignVCenter)
        
        # Texts
        from localization import t
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        info_layout.setAlignment(Qt.AlignVCenter)
        
        self.title_lbl = QLabel(t("nav.search", "Echo Search"))
        self.desc_lbl = QLabel(t("search.hero_desc", "Instant search for applications, files, and actions"))
        
        status_layout = QHBoxLayout()
        status_layout.setSpacing(8)
        
        self.status_dot = QWidget()
        self.status_dot.setFixedSize(8, 8)
        self.status_dot.setStyleSheet("background: #34C759; border-radius: 4px;")
        
        self.status_lbl = QLabel()
        status_layout.addWidget(self.status_dot)
        status_layout.addWidget(self.status_lbl)
        status_layout.addStretch()
        
        info_layout.addWidget(self.title_lbl)
        info_layout.addWidget(self.desc_lbl)
        info_layout.addSpacing(2)
        info_layout.addLayout(status_layout)
        
        self.layout.addLayout(info_layout)
        self.layout.addStretch()
        
        # Button
        self.open_btn = QPushButton(t("search.open_btn", "Open Search"))
        self.open_btn.setFixedSize(140, 32)
        self.open_btn.setCursor(Qt.PointingHandCursor)
        self.open_btn.clicked.connect(self._launch)
        self.layout.addWidget(self.open_btn, 0, Qt.AlignVCenter)
        
        ThemeManager.theme_changed.connect(self.update_style)
        self.update_style()
        
    @Property(float)
    def hover_progress(self): return self._hover_progress
    
    @hover_progress.setter
    def hover_progress(self, val):
        self._hover_progress = val
        self.update()
        
    def enterEvent(self, event):
        self.shimmer.handle_enter(event)
        self.anim.stop()
        self.anim.setEndValue(1.0)
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.shimmer.handle_leave(event)
        self.anim.stop()
        self.anim.setEndValue(0.0)
        self.anim.start()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        self.shimmer.handle_mouse_move(event)
        super().mouseMoveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._launch()
        super().mousePressEvent(event)
        
    def _launch(self):
        candidates = [
            os.path.expanduser('~/.local/share/spotlight-glass/main.py'),
            os.path.expanduser('~/echo_search/main.py'),
            os.path.expanduser('~/.local/bin/echo-search'),
            '/usr/local/bin/echo-search',
            '/usr/bin/echo-search'
        ]
        for c in candidates:
            if os.path.exists(c):
                if c.endswith('.py'):
                    subprocess.Popen(['python3', c])
                else:
                    subprocess.Popen([c])
                return
        subprocess.Popen(['python3', os.path.expanduser('~/.local/share/spotlight-glass/main.py')])

        
    def _format_shortcut(self, shortcut):
        if not shortcut: return ""
        s = shortcut
        s = s.replace("<Super>", "⌘ ")
        s = s.replace("<Ctrl>", "⌃ ")
        s = s.replace("<Alt>", "⌥ ")
        s = s.replace("<Shift>", "⇧ ")
        parts = s.split(" ")
        if len(parts) > 1:
            return f"{parts[0]} {parts[-1].capitalize()}"
        return s.capitalize()

    def update(self):
        super().update()
        if hasattr(self, 'status_lbl'):
            from localization import t
            active_sources = len(self.service.get("enabled_modes") or [])
            shortcut = self.service.get("launch_shortcut") or "<Super>space"
            ready_txt = t("search.status_ready", "Ready")
            src_txt = t("search.sources_count", "Sources")
            self.status_lbl.setText(f"{ready_txt}  •  {active_sources} {src_txt}  •  {self._format_shortcut(shortcut)}")

    def update_style(self, _is_dark=False):
        is_dark = ThemeManager.is_dark
        
        # Icon styling (subtle highlight)
        icon_bg = "rgba(10, 132, 255, 0.15)" if is_dark else "rgba(0, 122, 255, 0.1)"
        icon_color = "#0A84FF" if is_dark else "#007AFF"
        self.icon_lbl.setStyleSheet(f"background: {icon_bg}; color: {icon_color}; border-radius: 14px; font-size: 22px;")
        
        # Text styling
        title_color = Colors.TEXT_PRIMARY
        desc_color = Colors.TEXT_SECONDARY
        
        self.title_lbl.setStyleSheet(f"color: {title_color}; font-weight: 600; font-size: 17px; background: transparent;")
        self.desc_lbl.setStyleSheet(f"color: {desc_color}; font-size: 13px; background: transparent;")
        self.status_lbl.setStyleSheet(f"color: {desc_color}; font-weight: 500; font-size: 11px; background: transparent;")
        
        # Button styling
        btn_bg = "rgba(120, 120, 128, 0.16)" if is_dark else "rgba(120, 120, 128, 0.12)"
        btn_hover = "rgba(120, 120, 128, 0.24)" if is_dark else "rgba(120, 120, 128, 0.18)"
        self.open_btn.setStyleSheet(f"""
            QPushButton {{
                background: {btn_bg};
                color: {title_color};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {btn_hover};
            }}
        """)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        is_dark = ThemeManager.is_dark
        rect = self.rect()
        
        bg_color = QColor(Colors.CARD_BG)
        bg_color.setAlpha(160 if is_dark else 240)
            
        path = QPainterPath()
        path.addRoundedRect(rect, 16, 16)
        p.fillPath(path, bg_color)
        
        if self._hover_progress > 0:
            hover_color = QColor(255, 255, 255, int(15 * self._hover_progress)) if is_dark else QColor(0, 0, 0, int(8 * self._hover_progress))
            p.fillPath(path, hover_color)
            
        border_color = QColor(Colors.CARD_BORDER)
        border_color.setAlpha(40 if is_dark else 60)
        p.setPen(QPen(border_color, 1))
        p.drawPath(path)

        # Dynamic specular edge sheen
        self.shimmer.paint_shimmer(p, QRectF(rect), 16, is_dark)
