from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QIcon, QPixmap
from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from theme.metrics import CARD_RADIUS
from theme.glass_shimmer import GlassShimmerHelper
from PySide6.QtCore import QRectF
import os

class HeroCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self.shimmer = GlassShimmerHelper(self)
        self.setMinimumHeight(240)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(40)
        
        # Left side - System Info
        left_layout = QHBoxLayout()
        left_layout.setSpacing(24)
        
        # User Info
        import pwd
        import os
        
        user_info = pwd.getpwuid(os.getuid())
        full_name = user_info.pw_gecos.split(',')[0]
        if not full_name:
            full_name = user_info.pw_name
            
        username = user_info.pw_name
        
        # Priority: AccountsService icon → ~/.face
        accounts_icon = f"/var/lib/AccountsService/icons/{username}"
        if os.path.exists(accounts_icon):
            avatar_path = accounts_icon
        else:
            avatar_path = os.path.expanduser("~/.face")
            if not os.path.exists(avatar_path):
                avatar_path = ""
        self._avatar_hash = ""  # track content via MD5 for refresh
        
        self.logo_lbl = QLabel()
        self.logo_lbl.setFixedSize(120, 120)
        
        pix = self._make_avatar_pixmap(avatar_path) if avatar_path else None
        if pix:
            self.logo_lbl.setPixmap(pix)
        else:
            self.logo_lbl.setText(full_name[0].upper())
            self.logo_lbl.setAlignment(Qt.AlignCenter)
            self.logo_lbl.setStyleSheet(f"background-color: {Colors.ACCENT_BLUE}; color: white; font-size: 40px; font-weight: bold; border-radius: 60px;")
            
        left_layout.addWidget(self.logo_lbl, 0, Qt.AlignVCenter)
        
        # Text Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        info_layout.setAlignment(Qt.AlignVCenter)
        
        self.title = QLabel(full_name)
        self.title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;")
        info_layout.addWidget(self.title)
        
        # OS version — will be updated by refresh()
        os_name = self._get_os_name()
        self.ver = QLabel(os_name)
        self.ver.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_MEDIUM};")
        info_layout.addWidget(self.ver)
        
        session = os.environ.get("XDG_SESSION_TYPE", "wayland").capitalize()
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "GNOME").split(":")[0]
        self.env = QLabel(f"{desktop} \u2022 {session}")
        self.env.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_NORMAL};")
        info_layout.addWidget(self.env)
        
        left_layout.addLayout(info_layout)
        layout.addLayout(left_layout)
        
        layout.addStretch()
        
        # Right side - Buttons
        from localization import t
        right_layout = QVBoxLayout()
        right_layout.setSpacing(12)
        right_layout.setAlignment(Qt.AlignVCenter)
        
        self.btn_update = QPushButton(t("general.software_update", "Software Update..."))
        self.btn_update.setFixedSize(160, 36)
        self.btn_update.setCursor(Qt.PointingHandCursor)
        
        self.btn_report = QPushButton(t("general.system_report", "System Report..."))
        self.btn_report.setFixedSize(160, 36)
        self.btn_report.setCursor(Qt.PointingHandCursor)
        
        self.btn_update.clicked.connect(self._on_update_clicked)
        self.btn_report.clicked.connect(self._on_report_clicked)
        
        right_layout.addWidget(self.btn_update)
        right_layout.addWidget(self.btn_report)
        
        layout.addLayout(right_layout)
        
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    @staticmethod
    def _get_os_name() -> str:
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        except Exception:
            pass
        return "Linux"

    @staticmethod
    def _make_avatar_pixmap(avatar_path: str, size: int = 120) -> "QPixmap | None":
        """Load and circularly-clip an avatar image. Returns None if path is invalid."""
        if not avatar_path or not os.path.exists(avatar_path):
            return None
        pix = QPixmap(avatar_path).scaled(size, size,
                                          Qt.KeepAspectRatioByExpanding,
                                          Qt.SmoothTransformation)
        out = QPixmap(size, size)
        out.fill(Qt.transparent)
        painter = QPainter(out)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap((size - pix.width()) // 2, (size - pix.height()) // 2, pix)
        painter.end()
        return out

    def refresh(self, info: dict):
        """Live-update hero card when system info changes."""
        # --- Name ---
        new_name = info.get("full_name") or info.get("username", "")
        if new_name and new_name != self.title.text():
            self.title.setText(new_name)

        # --- OS version ---
        os_name = info.get("os_name", "")
        if os_name and os_name != self.ver.text():
            self.ver.setText(os_name)

        # --- Session / desktop ---
        session = info.get("session_type", "").capitalize()
        desktop = info.get("desktop", "").split(":")[0]
        if session or desktop:
            env_text = f"{desktop} \u2022 {session}" if desktop and session else (desktop or session)
            if env_text != self.env.text():
                self.env.setText(env_text)

        # --- Avatar ---
        new_avatar_path = info.get("avatar_path", "")
        new_avatar_hash = info.get("avatar_hash", "")
        # Reload if hash changed (file content changed) OR path changed
        if new_avatar_hash != self._avatar_hash:
            self._avatar_hash = new_avatar_hash
            pix = self._make_avatar_pixmap(new_avatar_path)
            if pix:
                self.logo_lbl.setPixmap(pix)
                self.logo_lbl.setStyleSheet("")
                self.logo_lbl.setText("")
            else:
                initials = (new_name or "?")[0].upper()
                self.logo_lbl.setPixmap(QPixmap())
                self.logo_lbl.setText(initials)
                self.logo_lbl.setAlignment(Qt.AlignCenter)
                self.logo_lbl.setStyleSheet(
                    f"background-color: {Colors.ACCENT_BLUE}; color: white; "
                    f"font-size: 40px; font-weight: bold; border-radius: 60px;"
                )

    def update_style(self, _is_dark=False):
        self.title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;")
        self.ver.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_MEDIUM};")
        self.env.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_NORMAL};")
        
        btn_bg = "rgba(255, 255, 255, 0.1)" if ThemeManager.is_dark else "rgba(0, 0, 0, 0.05)"
        
        btn_style = f"""
            QPushButton {{
                background-color: {btn_bg};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.CARD_BORDER};
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {Colors.HOVER_BG};
            }}
            QPushButton:pressed {{
                background-color: {Colors.PRESSED_BG};
            }}
        """
        self.btn_update.setStyleSheet(btn_style)
        self.btn_report.setStyleSheet(btn_style)
        self.update()

    def _on_update_clicked(self):
        import shutil
        import subprocess
        from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel
        
        managers = ['pika-update', 'gnome-software', 'update-manager', 'plasma-discover']
        found = False
        for mgr in managers:
            if shutil.which(mgr):
                subprocess.Popen([mgr])
                found = True
                break
                
        if not found:
            from components.custom_widgets import BlurBackground
            msg = QDialog(self.window())
            msg.setFixedSize(320, 160)
            msg.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
            msg.setAttribute(Qt.WA_TranslucentBackground)
            
            l = QVBoxLayout(msg)
            l.setContentsMargins(0, 0, 0, 0)
            
            bg = QWidget()
            bg.setStyleSheet(f"background-color: {Colors.CARD_BG}; border: 1px solid {Colors.CARD_BORDER}; border-radius: 12px;")
            l.addWidget(bg)
            
            bl = QVBoxLayout(bg)
            bl.setContentsMargins(24, 24, 24, 24)
            bl.setSpacing(12)
            bl.setAlignment(Qt.AlignCenter)
            
            t = QLabel("Software Update Unavailable")
            t.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
            t.setAlignment(Qt.AlignCenter)
            
            d = QLabel("На данной системе не найден поддерживаемый менеджер обновлений.")
            d.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
            d.setWordWrap(True)
            d.setAlignment(Qt.AlignCenter)
            
            btn = QPushButton("OK")
            btn.setFixedSize(80, 28)
            btn.setStyleSheet(f"QPushButton {{ background-color: {Colors.ACCENT_BLUE}; color: white; border-radius: 6px; }}")
            btn.clicked.connect(msg.accept)
            
            bl.addWidget(t)
            bl.addWidget(d)
            bl.addWidget(btn, 0, Qt.AlignCenter)
            
            msg.exec()

    def _on_report_clicked(self):
        from components.system_report_dialog import SystemReportDialog
        dlg = SystemReportDialog(self.window())
        dlg.exec()

    def enterEvent(self, event):
        self.shimmer.handle_enter(event)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shimmer.handle_leave(event)
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        self.shimmer.handle_mouse_move(event)
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        is_dark = ThemeManager.is_dark
        shadow_color = QColor(0, 0, 0, 40 if is_dark else 15)
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(2, 4, -2, -2), CARD_RADIUS, CARD_RADIUS)
        painter.fillPath(path, shadow_color)
        
        bg_color = QColor(Colors.CARD_BG)
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect().adjusted(0, 0, 0, -4), CARD_RADIUS, CARD_RADIUS)
        painter.fillPath(bg_path, bg_color)
        
        border_color = QColor(Colors.CARD_BORDER)
        border_color.setAlpha(30 if is_dark else 50)
        painter.setPen(QPen(border_color, 1))
        painter.drawPath(bg_path)

        # Dynamic specular edge sheen
        self.shimmer.paint_shimmer(painter, QRectF(self.rect().adjusted(0, 0, 0, -4)), CARD_RADIUS, is_dark)
