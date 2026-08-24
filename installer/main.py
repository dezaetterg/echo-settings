#!/usr/bin/env python3
"""
Echo Settings Installer - macOS 26 Edition.
Standalone graphical installation and setup assistant suite for Echo Settings.
Delivers a high-fidelity Apple-grade setup experience with 3D liquid glass cursive greeting,
interactive language selector, system validation, and background deployment with native window framing.
"""

import sys
import os
import subprocess
import traceback

# Ensure current and parent dirs are in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
TAHOE_DIR = os.path.join(PARENT_DIR, "Tahoe Settings")

for path in (SCRIPT_DIR, PARENT_DIR, TAHOE_DIR):
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QProgressBar, QScrollArea, QFrame, QCheckBox, QMessageBox,
    QLineEdit
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QPoint, QPointF, QRectF, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QTimer, QUrl
)
from PySide6.QtGui import (
    QIcon, QPixmap, QImage, QPainter, QColor, QFont, QPen, QPainterPath,
    QLinearGradient, QRadialGradient, QCursor, QDesktopServices
)

from version import VERSION, APP_NAME, APP_ID, APP_DESCRIPTION
from localization import i18n, t, SUPPORTED_LANGUAGES
from installer.system_checker import SystemChecker, CheckResult
from installer.installer_engine import InstallationEngine
from installer.ui_components import (
    MacGlassCard, LiquidGlassScriptTypography, LiquidGlassGlobeIcon, LiquidGlassDriveIcon,
    LiquidGlassShieldIcon, LiquidGlassSuccessIcon, LiquidGlassSearchHeroIcon, SystemCheckStatusBadge, CupertinoSystemCheckRow,
    CupertinoThemeToggle, CupertinoCheckbox, LiquidGlassPulsingLogo, InstallingMilestoneBar,
    SystemWindowControls, CupertinoSearchField, CupertinoLanguageRow, CupertinoScopeCard,
    CupertinoPrimaryButton, CupertinoSecondaryButton, MacPalette, LiquidGlassCompleteLogo, GlassTerminalDrawer
)







LANGUAGE_FLAGS = {
    "ru": "🇷🇺",
    "en": "🇺🇸",
    "es": "🇪🇸",
    "de": "🇩🇪",
    "fr": "🇫🇷",
    "zh_CN": "🇨🇳",
    "ja": "🇯🇵",
    "it": "🇮🇹",
    "pt_BR": "🇧🇷",
    "tr": "🇹🇷",
    "uk": "🇺🇦",
    "kk": "🇰🇿",
    "ar": "🇸🇦"
}


def is_dark_mode():
    try:
        res = subprocess.run(
            ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
            capture_output=True, text=True
        )
        return "prefer-dark" in res.stdout
    except Exception:
        return True


# --- Worker Threads ---
class InstallWorker(QThread):
    progress = Signal(int, str, int)
    finished = Signal(bool, str)

    def __init__(self, scope: str = "user", autostart: bool = False, desktop_shortcut: bool = False, install_echo_search: bool = True):
        super().__init__()
        self.scope = scope
        self.autostart = autostart
        self.desktop_shortcut = desktop_shortcut
        self.install_echo_search = install_echo_search

    def run(self):
        try:
            if self.scope == "system" and os.geteuid() != 0:
                installer_script = os.path.abspath(__file__)
                cmd = ["pkexec", sys.executable, installer_script, "--internal-install-system"]
                if self.autostart:
                    cmd.append("--autostart")
                if self.install_echo_search:
                    cmd.append("--echo-search")
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = proc.communicate()
                if proc.returncode != 0:
                    self.finished.emit(False, stderr or stdout or "Authentication cancelled or failed.")
                    return
                self.finished.emit(True, "")
            else:
                def cb(step, total, msg):
                    pct = int(min(100, max(0, (step / total) * 100))) if total > 0 else step
                    stage = 1
                    if pct >= 85:
                        stage = 5
                    elif pct >= 70:
                        stage = 4
                    elif pct >= 45:
                        stage = 3
                    elif pct >= 15:
                        stage = 2
                    else:
                        stage = 1
                    self.progress.emit(pct, msg, stage)

                success = InstallationEngine.install(
                    self.scope,
                    autostart=self.autostart,
                    desktop_shortcut=self.desktop_shortcut,
                    install_echo_search=self.install_echo_search,
                    progress_callback=cb
                )
                self.finished.emit(success, "")
        except Exception as e:
            self.finished.emit(False, f"{str(e)}\n\n{traceback.format_exc()}")




class UninstallWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, scope: str = "user", remove_data: bool = False):
        super().__init__()
        self.scope = scope
        self.remove_data = remove_data

    def run(self):
        try:
            if self.scope == "system" and os.geteuid() != 0:
                cmd = ["pkexec", sys.executable, os.path.abspath(__file__), "--internal-uninstall-system"]
                if self.remove_data:
                    cmd.append("--remove-data")
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = proc.communicate()
                if proc.returncode != 0:
                    self.finished.emit(False, stderr or stdout or "Authentication failed.")
                    return
                self.finished.emit(True, "")
            else:
                success = InstallationEngine.uninstall(self.scope, self.remove_data)
                self.finished.emit(success, "")
        except Exception as e:
            self.finished.emit(False, str(e))


# =============================================================================
# View 1: Welcome / Hello Hero (Apple Initial Setup Screen)
# =============================================================================
class WelcomeHeroView(QWidget):
    start_requested = Signal()

    def __init__(self, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self._init_ui()

    def _init_ui(self):
        self.setFocusPolicy(Qt.StrongFocus)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 24, 40, 36)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        # 1. Echo Settings Logo Squircle
        self.logo_lbl = QLabel()
        logo_path = os.path.join(InstallationEngine.get_source_dir(), "icon.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(PARENT_DIR, "Tahoe Settings", "icon.png")

        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(88, 88, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_lbl.setPixmap(pix)
        self.logo_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_lbl)

        # 2. Bold Header: Echo Settings (SF Pro Display)
        self.title_lbl = QLabel("Echo Settings")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        self.title_lbl.setStyleSheet(f"""
            color: {t_col};
            font-family: 'SF Pro Display', 'Inter', -apple-system, sans-serif;
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.title_lbl)

        # 3. Release Version Badge
        self.badge_lbl = QLabel(t("installer.edition_badge", "Echo Settings • Version {version}").format(version=VERSION))
        self.badge_lbl.setAlignment(Qt.AlignCenter)
        self.badge_lbl.setStyleSheet(f"""
            color: {MacPalette.ACCENT_BLUE};
            font-family: 'SF Pro Text', 'Inter', -apple-system, sans-serif;
            font-size: 13px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.badge_lbl)

        layout.addSpacing(10)

        # 4. Floating 3D Liquid Glass Cursive Greeting Typography (Frameless, exact style as photo)
        self.greeting_widget = LiquidGlassScriptTypography(is_dark=self.is_dark)
        layout.addWidget(self.greeting_widget)

        layout.addSpacing(6)

        # 5. Explanatory Subtitle
        self.hint_lbl = QLabel(t("installer.welcome_hint"))
        self.hint_lbl.setAlignment(Qt.AlignCenter)
        self.hint_lbl.setWordWrap(True)
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.hint_lbl.setStyleSheet(f"""
            color: {s_col};
            font-family: 'SF Pro Text', 'Inter', -apple-system, sans-serif;
            font-size: 13px;
            line-height: 1.45;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.hint_lbl)

        layout.addStretch()

        # 6. Action Button: Get Started
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)

        self.btn_start = CupertinoPrimaryButton(t("installer.get_started"))
        self.btn_start.setMinimumWidth(220)
        self.btn_start.clicked.connect(self.start_requested.emit)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.start_requested.emit()
            return
        super().keyPressEvent(event)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.greeting_widget.set_dark(is_dark)
        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.title_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 30px; font-weight: 800; background: transparent; border: none;")
        self.hint_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; background: transparent; border: none;")

    def retranslate_ui(self):
        self.badge_lbl.setText(t("installer.edition_badge", "Echo Settings • Version {version}").format(version=VERSION))
        self.hint_lbl.setText(t("installer.welcome_hint"))
        self.btn_start.setText(t("installer.get_started"))



# =============================================================================
# View 2: Dedicated Language Selector View (macOS Setup Assistant 2-Column Hero)
# =============================================================================
class LanguageSelectView(QWidget):
    continue_requested = Signal()
    back_requested = Signal()

    def __init__(self, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.row_widgets = {}
        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(36, 12, 36, 24)
        root_layout.setSpacing(16)

        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"

        # ── Two-Column macOS Setup Assistant Composition ──
        body_layout = QHBoxLayout()
        body_layout.setSpacing(32)

        # ── LEFT COLUMN: Hero Panel (Globe Icon, Title, Subtitle, Tip Card) ──
        left_widget = QWidget()
        left_widget.setFixedWidth(230)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 4, 0, 0)
        left_layout.setSpacing(12)

        # 1. 3D Translucent Liquid Glass Globe Icon
        self.globe_icon = LiquidGlassGlobeIcon(size=68, is_dark=self.is_dark)
        left_layout.addWidget(self.globe_icon)
        left_layout.addSpacing(4)

        # 2. SF Pro Display Bold Title
        self.title_lbl = QLabel(t("installer.select_lang_title"))
        self.title_lbl.setStyleSheet(f"""
            color: {t_col};
            font-family: 'SF Pro Display', 'Inter', -apple-system, sans-serif;
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.4px;
            background: transparent;
            border: none;
        """)
        self.title_lbl.setWordWrap(True)
        left_layout.addWidget(self.title_lbl)

        # 3. SF Pro Text Subtitle
        self.sub_lbl = QLabel(t("installer.select_lang_sub"))
        self.sub_lbl.setStyleSheet(f"""
            color: {s_col};
            font-family: 'SF Pro Text', 'Inter', -apple-system, sans-serif;
            font-size: 13px;
            line-height: 1.45;
            background: transparent;
            border: none;
        """)
        self.sub_lbl.setWordWrap(True)
        left_layout.addWidget(self.sub_lbl)

        left_layout.addSpacing(6)

        # 4. Cupertino Helpful Tip Card
        self.tip_card = MacGlassCard(is_dark=self.is_dark, corner_radius=12)
        tip_layout = QVBoxLayout(self.tip_card)
        tip_layout.setContentsMargins(12, 10, 12, 10)
        tip_layout.setSpacing(4)

        self.tip_title = QLabel("💡 " + t("installer.tip_title", "Language Tip"))
        self.tip_title.setStyleSheet(f"color: {MacPalette.ACCENT_BLUE}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11.5px; font-weight: 600; border: none; background: transparent;")
        tip_layout.addWidget(self.tip_title)

        self.tip_desc = QLabel(t("installer.tip_desc", "You can change interface language anytime in Echo Settings."))
        self.tip_desc.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; line-height: 1.35; border: none; background: transparent;")
        self.tip_desc.setWordWrap(True)
        tip_layout.addWidget(self.tip_desc)

        left_layout.addWidget(self.tip_card)
        left_layout.addStretch()

        # 5. Back Button (Bottom Left)
        self.btn_back = CupertinoSecondaryButton(t("installer.back"), is_dark=self.is_dark)
        self.btn_back.clicked.connect(self.back_requested.emit)
        left_layout.addWidget(self.btn_back)

        body_layout.addWidget(left_widget)

        # ── RIGHT COLUMN: Search + Grouped Inset Glass Card List ──
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # 1. Cupertino Search Bar with Vector SVG Magnifier Icon
        self.search_box = CupertinoSearchField(placeholder=t("installer.search_lang", "Search language..."), is_dark=self.is_dark)
        self.search_box.textChanged.connect(self._filter_languages)
        self.search_box.down_pressed.connect(lambda: self._cycle_language(1))
        self.search_box.up_pressed.connect(lambda: self._cycle_language(-1))
        self.search_box.return_pressed.connect(self.continue_requested.emit)
        self.search_box.escape_pressed.connect(self.search_box.clear)
        right_layout.addWidget(self.search_box)

        # 2. Unified Inset-Grouped Glass Card Container
        self.list_card = MacGlassCard(is_dark=self.is_dark, corner_radius=16)
        list_card_layout = QVBoxLayout(self.list_card)
        list_card_layout.setContentsMargins(6, 6, 6, 6)
        list_card_layout.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 0px; }")

        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.c_layout = QVBoxLayout(self.list_container)
        self.c_layout.setContentsMargins(0, 0, 0, 0)
        self.c_layout.setSpacing(0)
        self.c_layout.setAlignment(Qt.AlignTop)

        current_lang = i18n.current_language

        for code, meta in SUPPORTED_LANGUAGES.items():
            row = CupertinoLanguageRow(
                code=code,
                flag="",
                native_name=meta["native"],
                english_name=meta["name"],
                is_selected=(code == current_lang),
                is_dark=self.is_dark
            )
            row.clicked.connect(self._on_language_selected)
            self.row_widgets[code] = row
            self.c_layout.addWidget(row)

        self.scroll.setWidget(self.list_container)
        list_card_layout.addWidget(self.scroll)
        right_layout.addWidget(self.list_card, 1)

        # 3. Continue Button (Bottom Right)
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.btn_continue = CupertinoPrimaryButton(t("installer.continue"))
        self.btn_continue.clicked.connect(self.continue_requested.emit)
        btn_box.addWidget(self.btn_continue)
        right_layout.addLayout(btn_box)

        body_layout.addWidget(right_widget, 1)
        root_layout.addLayout(body_layout)
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            self._cycle_language(1)
            return
        elif event.key() == Qt.Key_Up:
            self._cycle_language(-1)
            return
        elif event.key() == Qt.Key_Escape:
            self.search_box.clear()
            return
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.continue_requested.emit()
            return
        super().keyPressEvent(event)

    def _cycle_language(self, delta: int):
        visible_codes = [code for code, row in self.row_widgets.items() if row.isVisible()]
        if not visible_codes:
            return
        current = i18n.current_language
        if current in visible_codes:
            idx = visible_codes.index(current)
            new_idx = (idx + delta) % len(visible_codes)
        else:
            new_idx = 0
        target = visible_codes[new_idx]
        self._on_language_selected(target)

    def _filter_languages(self, query: str):
        q = query.strip().lower()
        for code, row in self.row_widgets.items():
            meta = SUPPORTED_LANGUAGES.get(code, {})
            native = meta.get("native", "").lower()
            name = meta.get("name", "").lower()
            match = not q or (q in native) or (q in name) or (q in code.lower())
            row.setVisible(match)

    def _on_language_selected(self, code: str):
        if code != i18n.current_language:
            i18n.set_language(code)
            self.retranslate_ui()
            for c, row in self.row_widgets.items():
                row.set_selected(c == code)
        if code in self.row_widgets and hasattr(self, 'scroll'):
            self.scroll.ensureWidgetVisible(self.row_widgets[code])

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.globe_icon.set_dark(is_dark)
        self.tip_card.set_dark(is_dark)
        self.list_card.set_dark(is_dark)
        self.btn_back.set_dark(is_dark)
        self.search_box.set_dark(is_dark)
        for row in self.row_widgets.values():
            row.set_dark(is_dark)
        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.title_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 26px; font-weight: 700; letter-spacing: -0.4px; background: transparent; border: none;")
        self.sub_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; line-height: 1.45; background: transparent; border: none;")
        self.tip_desc.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; line-height: 1.35; border: none; background: transparent;")

    def retranslate_ui(self):
        self.title_lbl.setText(t("installer.select_lang_title"))
        self.sub_lbl.setText(t("installer.select_lang_sub"))
        self.btn_back.setText(t("installer.back"))
        self.btn_continue.setText(t("installer.continue"))
        self.search_box.setPlaceholderText(t("installer.search_lang", "Search language..."))
        self.tip_title.setText("💡 " + t("installer.tip_title", "Language Tip"))
        self.tip_desc.setText(t("installer.tip_desc", "You can change interface language anytime in Echo Settings."))
        cur = i18n.current_language
        for c, row in self.row_widgets.items():
            row.set_selected(c == cur)



# =============================================================================
# View 3: System Compatibility Check View (macOS Setup Assistant 2-Column Hero)
# =============================================================================
class SystemCheckView(QWidget):
    continue_requested = Signal()
    back_requested = Signal()

    def __init__(self, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.check_rows = []
        self.has_critical_fail = False
        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(36, 12, 36, 24)
        root_layout.setSpacing(16)

        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"

        # ── Two-Column macOS Composition ──
        body_layout = QHBoxLayout()
        body_layout.setSpacing(32)

        # ── LEFT COLUMN: Hero Panel (Shield Icon, Title, Subtitle, Tip Card, Back Button) ──
        left_widget = QWidget()
        left_widget.setFixedWidth(230)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 4, 0, 0)
        left_layout.setSpacing(12)

        # 1. 3D Translucent Liquid Glass Shield Icon
        self.shield_icon = LiquidGlassShieldIcon(size=68, is_dark=self.is_dark)
        left_layout.addWidget(self.shield_icon)
        left_layout.addSpacing(4)

        # 2. SF Pro Display Bold Title
        self.title_lbl = QLabel(t("installer.system_check_title"))
        self.title_lbl.setStyleSheet(f"""
            color: {t_col};
            font-family: 'SF Pro Display', 'Inter', -apple-system, sans-serif;
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.4px;
            background: transparent;
            border: none;
        """)
        self.title_lbl.setWordWrap(True)
        left_layout.addWidget(self.title_lbl)

        # 3. SF Pro Text Subtitle
        self.sub_lbl = QLabel(t("installer.system_check_sub"))
        self.sub_lbl.setStyleSheet(f"""
            color: {s_col};
            font-family: 'SF Pro Text', 'Inter', -apple-system, sans-serif;
            font-size: 13px;
            line-height: 1.45;
            background: transparent;
            border: none;
        """)
        self.sub_lbl.setWordWrap(True)
        left_layout.addWidget(self.sub_lbl)

        left_layout.addSpacing(6)

        # 4. Cupertino Helpful Tip Card
        self.tip_card = MacGlassCard(is_dark=self.is_dark, corner_radius=12)
        tip_layout = QVBoxLayout(self.tip_card)
        tip_layout.setContentsMargins(12, 10, 12, 10)
        tip_layout.setSpacing(4)

        self.tip_title = QLabel("🛡️ " + t("installer.check_tip_title", "Hardware & OS"))
        self.tip_title.setStyleSheet(f"color: {MacPalette.ACCENT_BLUE}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11.5px; font-weight: 600; border: none; background: transparent;")
        tip_layout.addWidget(self.tip_title)

        self.tip_desc = QLabel(t("installer.check_tip_desc", "All core GNOME, Python, and system services are validated."))
        self.tip_desc.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; line-height: 1.35; border: none; background: transparent;")
        self.tip_desc.setWordWrap(True)
        tip_layout.addWidget(self.tip_desc)

        left_layout.addWidget(self.tip_card)
        left_layout.addStretch()

        # 5. Back Button (Bottom Left)
        self.btn_back = CupertinoSecondaryButton(t("installer.back"), is_dark=self.is_dark)
        self.btn_back.clicked.connect(self.back_requested.emit)
        left_layout.addWidget(self.btn_back)

        body_layout.addWidget(left_widget)

        # ── RIGHT COLUMN: Main System Check Glass Card + Continue Button ──
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # Inset-Grouped Glass Container
        self.main_card = MacGlassCard(is_dark=self.is_dark, corner_radius=14)
        c_main_layout = QVBoxLayout(self.main_card)
        c_main_layout.setContentsMargins(14, 12, 14, 12)
        c_main_layout.setSpacing(8)

        # Card Header with Recheck Button
        card_hdr = QHBoxLayout()
        self.card_hdr_title = QLabel(t("installer.system_check_title"))
        self.card_hdr_title.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        card_hdr.addWidget(self.card_hdr_title)
        card_hdr.addStretch()

        self.btn_recheck = QPushButton("↻ " + t("installer.recheck", "Recheck"))
        self.btn_recheck.setCursor(Qt.PointingHandCursor)
        self._update_recheck_btn_style()
        self.btn_recheck.clicked.connect(self.on_recheck_clicked)
        card_hdr.addWidget(self.btn_recheck)
        c_main_layout.addLayout(card_hdr)

        # Scroll Area for Check Rows (Clean glass container, scrollbar completely hidden)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 0px; height: 0px; background: transparent; }
            QScrollBar:horizontal { width: 0px; height: 0px; background: transparent; }
        """)

        self.rows_content = QWidget()
        self.rows_content.setStyleSheet("background: transparent;")
        self.rows_layout = QVBoxLayout(self.rows_content)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(6)

        self.scroll.setWidget(self.rows_content)
        c_main_layout.addWidget(self.scroll, 1)



        # Bottom Notice Banner
        self.notice_box = QWidget()
        n_layout = QHBoxLayout(self.notice_box)
        n_layout.setContentsMargins(4, 4, 4, 4)
        n_layout.setSpacing(8)

        self.notice_icon = QLabel("✓")
        self.notice_icon.setStyleSheet("color: #34C759; font-size: 13px; font-weight: bold; background: transparent; border: none;")
        n_layout.addWidget(self.notice_icon)

        self.notice_lbl = QLabel(t("installer.check_all_passed"))
        self.notice_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; border: none; background: transparent;")
        self.notice_lbl.setWordWrap(True)
        n_layout.addWidget(self.notice_lbl, 1)

        c_main_layout.addWidget(self.notice_box)
        right_layout.addWidget(self.main_card, 1)

        # Continue Button (Bottom Right)
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.btn_continue = CupertinoPrimaryButton(t("installer.continue"))
        self.btn_continue.clicked.connect(self.continue_requested.emit)
        btn_box.addWidget(self.btn_continue)
        right_layout.addLayout(btn_box)

        body_layout.addWidget(right_widget, 1)
        root_layout.addLayout(body_layout)

        # Run checks on init
        self.run_checks()

    def _update_recheck_btn_style(self):
        bg = "rgba(255, 255, 255, 0.12)" if self.is_dark else "rgba(0, 0, 0, 0.08)"
        fg = "#FFFFFF" if self.is_dark else "#1D1D1F"
        self.btn_recheck.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: none;
                border-radius: 6px;
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 11px;
                font-weight: 500;
                padding: 4px 10px;
            }}
            QPushButton:hover {{
                background-color: {"rgba(255, 255, 255, 0.22)" if self.is_dark else "rgba(0, 0, 0, 0.14)"};
            }}
        """)

    def on_recheck_clicked(self):
        self.btn_recheck.setEnabled(False)
        self.btn_recheck.setText("↻ " + t("installer.checking", "Checking..."))
        QTimer.singleShot(260, self._finish_recheck)

    def _finish_recheck(self):
        self.run_checks()
        self.btn_recheck.setText("↻ " + t("installer.recheck", "Recheck"))
        self.btn_recheck.setEnabled(True)

    def run_checks(self):
        # Clear existing rows

        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.check_rows.clear()

        checks = SystemChecker.run_all_checks()
        self.has_critical_fail = False
        has_warnings = False

        for chk in checks:
            if chk.critical and chk.status == "fail":
                self.has_critical_fail = True
            if chk.status == "warning":
                has_warnings = True

            row = CupertinoSystemCheckRow(
                title=chk.title,
                details=chk.details,
                value=chk.value,
                status=chk.status,
                is_dark=self.is_dark
            )
            self.rows_layout.addWidget(row)
            self.check_rows.append(row)

        self.rows_layout.addStretch()

        # Update notice banner & continue button
        if self.has_critical_fail:
            self.notice_icon.setText("✕")
            self.notice_icon.setStyleSheet("color: #FF3B30; font-size: 13px; font-weight: bold; background: transparent; border: none;")
            self.notice_lbl.setText(t("installer.check_fail_notice"))
            self.btn_continue.setEnabled(False)
        elif has_warnings:
            self.notice_icon.setText("▲")
            self.notice_icon.setStyleSheet("color: #FF9500; font-size: 13px; font-weight: bold; background: transparent; border: none;")
            self.notice_lbl.setText(t("installer.check_warn_notice"))
            self.btn_continue.setEnabled(True)
        else:
            self.notice_icon.setText("✓")
            self.notice_icon.setStyleSheet("color: #34C759; font-size: 13px; font-weight: bold; background: transparent; border: none;")
            self.notice_lbl.setText(t("installer.check_all_passed"))
            self.btn_continue.setEnabled(True)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.shield_icon.set_dark(is_dark)
        self.tip_card.set_dark(is_dark)
        self.main_card.set_dark(is_dark)
        self.btn_back.set_dark(is_dark)
        self._update_recheck_btn_style()
        for r in self.check_rows:
            r.set_dark(is_dark)

        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.title_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 26px; font-weight: 700; letter-spacing: -0.4px; background: transparent; border: none;")
        self.sub_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; line-height: 1.45; background: transparent; border: none;")
        self.tip_desc.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; line-height: 1.35; border: none; background: transparent;")
        self.card_hdr_title.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        self.notice_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; border: none; background: transparent;")

    def retranslate_ui(self):
        self.title_lbl.setText(t("installer.system_check_title"))
        self.sub_lbl.setText(t("installer.system_check_sub"))
        self.tip_title.setText("🛡️ " + t("installer.check_tip_title", "Hardware & OS"))
        self.tip_desc.setText(t("installer.check_tip_desc", "All core GNOME, Python, and system services are validated."))
        self.card_hdr_title.setText(t("installer.system_check_title"))
        self.btn_recheck.setText("↻ " + t("installer.recheck", "Recheck"))
        self.btn_back.setText(t("installer.back"))
        self.btn_continue.setText(t("installer.continue"))
        self.run_checks()


# =============================================================================
# View 4: Scope & Options View (macOS Setup Assistant 2-Column Hero Composition)
# =============================================================================
class ScopeView(QWidget):
    continue_requested = Signal(str, bool, bool)  # scope, autostart, desktop_shortcut
    back_requested = Signal()

    def __init__(self, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.selected_scope = "user"
        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(36, 12, 36, 24)
        root_layout.setSpacing(16)

        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"

        # ── Two-Column macOS Composition ──
        body_layout = QHBoxLayout()
        body_layout.setSpacing(32)

        # ── LEFT COLUMN: Hero Panel (Drive Icon, Title, Subtitle, Tip Card) ──
        left_widget = QWidget()
        left_widget.setFixedWidth(230)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 4, 0, 0)
        left_layout.setSpacing(12)

        # 1. 3D Translucent Liquid Glass Drive Icon
        self.drive_icon = LiquidGlassDriveIcon(size=68, is_dark=self.is_dark)
        left_layout.addWidget(self.drive_icon)
        left_layout.addSpacing(4)

        # 2. SF Pro Display Bold Title
        self.title_lbl = QLabel(t("installer.scope_title"))
        self.title_lbl.setStyleSheet(f"""
            color: {t_col};
            font-family: 'SF Pro Display', 'Inter', -apple-system, sans-serif;
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.4px;
            background: transparent;
            border: none;
        """)
        self.title_lbl.setWordWrap(True)
        left_layout.addWidget(self.title_lbl)

        # 3. SF Pro Text Subtitle
        self.sub_lbl = QLabel(t("installer.scope_sub"))
        self.sub_lbl.setStyleSheet(f"""
            color: {s_col};
            font-family: 'SF Pro Text', 'Inter', -apple-system, sans-serif;
            font-size: 13px;
            line-height: 1.45;
            background: transparent;
            border: none;
        """)
        self.sub_lbl.setWordWrap(True)
        left_layout.addWidget(self.sub_lbl)

        left_layout.addSpacing(6)

        # 4. Cupertino Helpful Tip Card
        self.tip_card = MacGlassCard(is_dark=self.is_dark, corner_radius=12)
        tip_layout = QVBoxLayout(self.tip_card)
        tip_layout.setContentsMargins(12, 10, 12, 10)
        tip_layout.setSpacing(4)

        self.tip_title = QLabel("🔒 " + t("installer.scope_tip_title", "Access Permissions"))
        self.tip_title.setStyleSheet(f"color: {MacPalette.ACCENT_BLUE}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11.5px; font-weight: 600; border: none; background: transparent;")
        tip_layout.addWidget(self.tip_title)

        self.tip_desc = QLabel(t("installer.scope_tip_desc", "User installation is recommended and does not require root privileges."))
        self.tip_desc.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; line-height: 1.35; border: none; background: transparent;")
        self.tip_desc.setWordWrap(True)
        tip_layout.addWidget(self.tip_desc)

        left_layout.addWidget(self.tip_card)
        left_layout.addStretch()

        # 5. Back Button (Bottom Left)
        self.btn_back = CupertinoSecondaryButton(t("installer.back"), is_dark=self.is_dark)
        self.btn_back.clicked.connect(self.back_requested.emit)
        left_layout.addWidget(self.btn_back)

        body_layout.addWidget(left_widget)

        # ── RIGHT COLUMN: Destination Scope Cards + Options + Storage Bar + Continue Button ──
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # 1. User Scope Card (~/.local)
        self.card_user = CupertinoScopeCard(
            scope_id="user",
            title=t("installer.scope_user"),
            description=t("installer.scope_user_desc"),
            path_badge="~/.local/bin",
            is_selected=True,
            is_dark=self.is_dark
        )
        self.card_user.clicked.connect(self._select_scope)
        right_layout.addWidget(self.card_user)

        # 2. System Scope Card (/usr/share)
        self.card_system = CupertinoScopeCard(
            scope_id="system",
            title=t("installer.scope_system"),
            description=t("installer.scope_system_desc"),
            path_badge="/usr/bin",
            is_selected=False,
            is_dark=self.is_dark
        )
        self.card_system.clicked.connect(self._select_scope)
        right_layout.addWidget(self.card_system)

        # 3. Installation Options Card (Autostart & Desktop Shortcut)
        self.options_card = MacGlassCard(is_dark=self.is_dark, corner_radius=12)
        opt_layout = QVBoxLayout(self.options_card)
        opt_layout.setContentsMargins(14, 8, 14, 8)
        opt_layout.setSpacing(4)

        self.chk_autostart = CupertinoCheckbox(t("installer.opt_autostart"), is_checked=False, is_dark=self.is_dark)
        opt_layout.addWidget(self.chk_autostart)

        self.chk_desktop = CupertinoCheckbox(t("installer.opt_desktop_icon"), is_checked=False, is_dark=self.is_dark)
        opt_layout.addWidget(self.chk_desktop)
        right_layout.addWidget(self.options_card)

        # 4. Storage Space Card
        src_dir = InstallationEngine.get_source_dir()
        self.req_mb = InstallationEngine.get_required_size_mb(src_dir)
        self.avail_mb = InstallationEngine.get_available_size_mb(os.path.expanduser("~/.local"))

        self.space_card = MacGlassCard(is_dark=self.is_dark, corner_radius=12)
        sp_layout = QHBoxLayout(self.space_card)
        sp_layout.setContentsMargins(14, 8, 14, 8)
        sp_layout.setSpacing(10)

        self.sp_icon = LiquidGlassDriveIcon(size=22, is_dark=self.is_dark)
        sp_layout.addWidget(self.sp_icon)

        self.sp_lbl = QLabel(f"{t('installer.space_req', 'Required')}: {self.req_mb:.1f} MB   •   {t('installer.space_avail', 'Available')}: {self.avail_mb/1024:.1f} GB")
        self.sp_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11.5px; font-weight: 500; border: none; background: transparent;")
        sp_layout.addWidget(self.sp_lbl)
        sp_layout.addStretch()

        right_layout.addWidget(self.space_card)
        right_layout.addStretch()

        # 5. Continue Button (Bottom Right)
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.btn_continue = CupertinoPrimaryButton(t("installer.continue"))
        self.btn_continue.clicked.connect(self._on_continue_clicked)
        btn_box.addWidget(self.btn_continue)
        right_layout.addLayout(btn_box)

        body_layout.addWidget(right_widget, 1)
        root_layout.addLayout(body_layout)

    def _select_scope(self, scope: str):
        self.selected_scope = scope
        self.card_user.set_selected(scope == "user")
        self.card_system.set_selected(scope == "system")
        if scope == "system":
            self.avail_mb = InstallationEngine.get_available_size_mb("/usr")
        else:
            self.avail_mb = InstallationEngine.get_available_size_mb(os.path.expanduser("~/.local"))
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.sp_lbl.setText(f"{t('installer.space_req', 'Required')}: {self.req_mb:.1f} MB   •   {t('installer.space_avail', 'Available')}: {self.avail_mb/1024:.1f} GB")

    def _on_continue_clicked(self):
        self.continue_requested.emit(
            self.selected_scope,
            self.chk_autostart.isChecked(),
            self.chk_desktop.isChecked()
        )

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.drive_icon.set_dark(is_dark)
        self.tip_card.set_dark(is_dark)
        self.card_user.set_dark(is_dark)
        self.card_system.set_dark(is_dark)
        self.options_card.set_dark(is_dark)
        self.chk_autostart.set_dark(is_dark)
        self.chk_desktop.set_dark(is_dark)
        self.space_card.set_dark(is_dark)
        self.sp_icon.set_dark(is_dark)
        self.btn_back.set_dark(is_dark)
        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.title_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 26px; font-weight: 700; letter-spacing: -0.4px; background: transparent; border: none;")
        self.sub_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; line-height: 1.45; background: transparent; border: none;")
        self.tip_desc.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; line-height: 1.35; border: none; background: transparent;")
        self.sp_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11.5px; font-weight: 500; border: none; background: transparent;")

    def retranslate_ui(self):
        self.title_lbl.setText(t("installer.scope_title"))
        self.sub_lbl.setText(t("installer.scope_sub"))
        self.card_user.set_texts(t("installer.scope_user"), t("installer.scope_user_desc"), "~/.local/bin")
        self.card_system.set_texts(t("installer.scope_system"), t("installer.scope_system_desc"), "/usr/bin")
        self.chk_autostart.setText(t("installer.opt_autostart"))
        self.chk_desktop.setText(t("installer.opt_desktop_icon"))
        self.tip_title.setText("🔒 " + t("installer.scope_tip_title", "Access Permissions"))
        self.tip_desc.setText(t("installer.scope_tip_desc", "User installation is recommended and does not require root privileges."))
        self.sp_lbl.setText(f"{t('installer.space_req', 'Required')}: {self.req_mb:.1f} MB   •   {t('installer.space_avail', 'Available')}: {self.avail_mb/1024:.1f} GB")
        self.btn_back.setText(t("installer.back"))
        self.btn_continue.setText(t("installer.continue"))


# =============================================================================
# View 4: Echo Search Companion Showcase View (Apple Spotlight Masterpiece)
# =============================================================================
class EchoSearchCompanionView(QWidget):
    install_requested = Signal(bool)
    back_requested = Signal()

    def __init__(self, is_dark: bool = True, is_welcome_mode: bool = False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.is_welcome_mode = is_welcome_mode
        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(36, 12, 36, 24)
        root_layout.setSpacing(16)

        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"

        # ── Two-Column macOS Setup Assistant Composition ──
        body_layout = QHBoxLayout()
        body_layout.setSpacing(28)

        # ── LEFT COLUMN: Hero Panel (Search Icon, Title, Subtitle, Feature Highlights, Back Button) ──
        left_widget = QWidget()
        left_widget.setFixedWidth(225)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 2, 0, 0)
        left_layout.setSpacing(10)

        # 1. 3D Translucent Liquid Glass Search Icon
        self.search_icon = LiquidGlassSearchHeroIcon(size=64, is_dark=self.is_dark)
        left_layout.addWidget(self.search_icon)

        # 2. SF Pro Display Bold Title
        self.title_lbl = QLabel(t("installer.search_companion_title"))
        self.title_lbl.setStyleSheet(f"""
            color: {t_col};
            font-family: 'SF Pro Display', 'Inter', -apple-system, sans-serif;
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.4px;
            background: transparent;
            border: none;
        """)
        self.title_lbl.setWordWrap(True)
        left_layout.addWidget(self.title_lbl)

        # 3. SF Pro Text Subtitle
        self.sub_lbl = QLabel(t("installer.search_companion_sub"))
        self.sub_lbl.setStyleSheet(f"""
            color: {s_col};
            font-family: 'SF Pro Text', 'Inter', -apple-system, sans-serif;
            font-size: 12px;
            line-height: 1.4;
            background: transparent;
            border: none;
        """)
        self.sub_lbl.setWordWrap(True)
        left_layout.addWidget(self.sub_lbl)

        left_layout.addSpacing(2)

        # 4. Cupertino Feature Highlights Glass Card
        self.tip_card = MacGlassCard(is_dark=self.is_dark, corner_radius=12)
        tip_layout = QVBoxLayout(self.tip_card)
        tip_layout.setContentsMargins(12, 10, 12, 10)
        tip_layout.setSpacing(6)

        self.tip_item1 = QLabel("⚡ " + t("installer.search_feature_shortcut"))
        self.tip_item2 = QLabel("📂 " + t("installer.search_feature_files"))
        self.tip_item3 = QLabel("🧮 " + t("installer.search_feature_calc"))

        for lbl in (self.tip_item1, self.tip_item2, self.tip_item3):
            lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 10.5px; line-height: 1.35; border: none; background: transparent;")
            lbl.setWordWrap(True)
            tip_layout.addWidget(lbl)

        left_layout.addWidget(self.tip_card)
        left_layout.addStretch()

        # 5. Back Button (Bottom Left)
        self.btn_back = CupertinoSecondaryButton(t("installer.back"), is_dark=self.is_dark)
        self.btn_back.clicked.connect(self.back_requested.emit)
        left_layout.addWidget(self.btn_back)

        body_layout.addWidget(left_widget, 0)

        # ── RIGHT COLUMN: Live Apple Spotlight Mockup + Activation Card + Action Button ──
        right_widget = QWidget()
        right_widget.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # 1. Floating Liquid Glass Spotlight Window Mockup
        self.preview_card = MacGlassCard(is_dark=self.is_dark, corner_radius=14)
        prev_layout = QVBoxLayout(self.preview_card)
        prev_layout.setContentsMargins(12, 10, 12, 10)
        prev_layout.setSpacing(8)

        # 1.1 Top Spotlight Search Bar
        self.spotlight_bar = QFrame()
        sp_bar_bg = "rgba(255, 255, 255, 0.14)" if self.is_dark else "rgba(0, 0, 0, 0.06)"
        sp_bar_border = "rgba(255, 255, 255, 0.24)" if self.is_dark else "rgba(0, 0, 0, 0.12)"
        self.spotlight_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {sp_bar_bg};
                border: 1px solid {sp_bar_border};
                border-radius: 9px;
            }}
        """)
        sp_bar_layout = QHBoxLayout(self.spotlight_bar)
        sp_bar_layout.setContentsMargins(10, 6, 10, 6)
        sp_bar_layout.setSpacing(8)

        sp_icon = QLabel("🔍")
        sp_icon.setStyleSheet("font-size: 13px; border: none; background: transparent;")
        sp_bar_layout.addWidget(sp_icon)

        self.sp_query = QLabel("Echo Settings")
        self.sp_query.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 13px; font-weight: 700; border: none; background: transparent;")
        sp_bar_layout.addWidget(self.sp_query, 1)

        self.sp_badge = QLabel("⌘ Space")
        badge_bg = "rgba(255, 255, 255, 0.18)" if self.is_dark else "rgba(0, 0, 0, 0.10)"
        self.sp_badge.setStyleSheet(f"""
            color: {t_col};
            background-color: {badge_bg};
            border-radius: 5px;
            padding: 2px 7px;
            font-family: monospace;
            font-size: 10px;
            font-weight: 600;
            border: none;
        """)
        sp_bar_layout.addWidget(self.sp_badge)
        prev_layout.addWidget(self.spotlight_bar)

        # 1.2 Spotlight Results Pane
        self.results_frame = QFrame()
        self.results_frame.setStyleSheet("background: transparent; border: none;")
        res_layout = QVBoxLayout(self.results_frame)
        res_layout.setContentsMargins(2, 0, 2, 0)
        res_layout.setSpacing(4)

        # Section Header: Applications
        self.cat_apps_lbl = QLabel(t("installer.spotlight_cat_apps"))
        self.cat_apps_lbl.setStyleSheet(f"color: {MacPalette.ACCENT_BLUE}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 9.5px; font-weight: 700; letter-spacing: 0.5px; border: none; background: transparent;")
        res_layout.addWidget(self.cat_apps_lbl)

        # Active / Selected Spotlight Item: Echo Settings (Glowing Accent Pill)
        self.active_item = QFrame()
        self.active_item.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 122, 255, 0.85), stop:1 rgba(10, 132, 255, 0.90));
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 7px;
            }}
        """)
        ai_layout = QHBoxLayout(self.active_item)
        ai_layout.setContentsMargins(8, 4, 8, 4)
        ai_layout.setSpacing(8)

        ai_icon = QLabel("⚙️")
        ai_icon.setStyleSheet("font-size: 14px; border: none; background: transparent;")
        ai_layout.addWidget(ai_icon)

        ai_text_layout = QVBoxLayout()
        ai_text_layout.setSpacing(1)
        self.ai_title = QLabel("Echo Settings")
        self.ai_title.setStyleSheet("color: #FFFFFF; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11.5px; font-weight: 700; border: none; background: transparent;")
        ai_text_layout.addWidget(self.ai_title)
        self.ai_sub = QLabel(t("installer.spotlight_app_desc"))
        self.ai_sub.setStyleSheet("color: rgba(255, 255, 255, 0.85); font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 9.5px; border: none; background: transparent;")
        ai_text_layout.addWidget(self.ai_sub)
        ai_layout.addLayout(ai_text_layout, 1)

        ai_badge = QLabel("Enter ↵")
        ai_badge.setStyleSheet("color: #FFFFFF; background: rgba(0, 0, 0, 0.25); border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: 600; font-family: monospace; border: none;")
        ai_layout.addWidget(ai_badge)
        res_layout.addWidget(self.active_item)

        # Secondary Spotlight Item: Terminal
        self.item2 = QFrame()
        item2_bg = "rgba(255, 255, 255, 0.06)" if self.is_dark else "rgba(0, 0, 0, 0.03)"
        self.item2.setStyleSheet(f"QFrame {{ background: {item2_bg}; border-radius: 6px; border: none; }}")
        i2_layout = QHBoxLayout(self.item2)
        i2_layout.setContentsMargins(8, 3, 8, 3)
        i2_layout.setSpacing(8)

        i2_icon = QLabel("💻")
        i2_icon.setStyleSheet("font-size: 13px; border: none; background: transparent;")
        i2_layout.addWidget(i2_icon)

        i2_text_layout = QVBoxLayout()
        i2_text_layout.setSpacing(1)
        self.i2_title = QLabel(t("installer.spotlight_term_name"))
        self.i2_title.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; font-weight: 600; border: none; background: transparent;")
        i2_text_layout.addWidget(self.i2_title)
        self.i2_sub = QLabel(t("installer.spotlight_term_desc"))
        self.i2_sub.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 9px; border: none; background: transparent;")
        i2_text_layout.addWidget(self.i2_sub)
        i2_layout.addLayout(i2_text_layout, 1)
        res_layout.addWidget(self.item2)

        # Section Header: Quick Calculations
        self.cat_calc_lbl = QLabel(t("installer.spotlight_cat_calc"))
        self.cat_calc_lbl.setStyleSheet(f"color: {MacPalette.ACCENT_BLUE}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 9.5px; font-weight: 700; letter-spacing: 0.5px; margin-top: 2px; border: none; background: transparent;")
        res_layout.addWidget(self.cat_calc_lbl)

        # Calculator Item: 256 * 4 = 1024
        self.calc_item = QFrame()
        self.calc_item.setStyleSheet(f"QFrame {{ background: {item2_bg}; border-radius: 6px; border: none; }}")
        calc_layout = QHBoxLayout(self.calc_item)
        calc_layout.setContentsMargins(8, 3, 8, 3)
        calc_layout.setSpacing(8)

        calc_icon = QLabel("🧮")
        calc_icon.setStyleSheet("font-size: 13px; border: none; background: transparent;")
        calc_layout.addWidget(calc_icon)

        calc_text_layout = QVBoxLayout()
        calc_text_layout.setSpacing(1)
        self.calc_title = QLabel("256 × 4 = 1024")
        self.calc_title.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; font-weight: 700; border: none; background: transparent;")
        calc_text_layout.addWidget(self.calc_title)
        self.calc_sub = QLabel(t("installer.spotlight_calc_desc"))
        self.calc_sub.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 9px; border: none; background: transparent;")
        calc_text_layout.addWidget(self.calc_sub)
        calc_layout.addLayout(calc_text_layout, 1)
        res_layout.addWidget(self.calc_item)

        prev_layout.addWidget(self.results_frame)
        prev_layout.addStretch()
        right_layout.addWidget(self.preview_card, 1)

        # 2. Checkbox Option Card
        self.opt_card = MacGlassCard(is_dark=self.is_dark, corner_radius=11)
        self.opt_card.setFixedHeight(60)
        opt_layout = QVBoxLayout(self.opt_card)
        opt_layout.setContentsMargins(12, 6, 12, 6)
        opt_layout.setSpacing(1)

        chk_text = t("installer.search_opt_enable") if self.is_welcome_mode else t("installer.search_opt_install")
        self.chk_install_search = CupertinoCheckbox(chk_text, is_checked=True, is_dark=self.is_dark)
        opt_layout.addWidget(self.chk_install_search)

        self.opt_desc = QLabel(t("installer.search_opt_desc"))
        self.opt_desc.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 10px; margin-left: 24px; border: none; background: transparent;")
        self.opt_desc.setWordWrap(True)
        opt_layout.addWidget(self.opt_desc)
        right_layout.addWidget(self.opt_card, 0)

        # 3. Bottom Control Row: GitHub Link (Left) + Continue Button (Right)
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 2, 0, 0)
        bottom_row.setSpacing(12)

        self.btn_github = QPushButton(t("installer.search_github_btn") + "  Echo Search")
        self.btn_github.setCursor(Qt.PointingHandCursor)
        self._update_github_btn_style()
        self.btn_github.clicked.connect(self._open_github_repo)
        bottom_row.addWidget(self.btn_github)

        bottom_row.addStretch()

        btn_lbl = t("installer.continue") if self.is_welcome_mode else t("installer.install_btn")
        self.btn_install = CupertinoPrimaryButton(btn_lbl)
        self.btn_install.clicked.connect(self._on_install_clicked)
        bottom_row.addWidget(self.btn_install)

        right_layout.addLayout(bottom_row)

        body_layout.addWidget(right_widget, 1)
        root_layout.addLayout(body_layout)

    def _update_github_btn_style(self):
        bg = "rgba(0, 122, 255, 0.16)" if self.is_dark else "rgba(0, 122, 255, 0.10)"
        fg = MacPalette.ACCENT_BLUE
        self.btn_github.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: 1px solid rgba(0, 122, 255, 0.30);
                border-radius: 8px;
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 11px;
                font-weight: 600;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 122, 255, 0.28);
                border-color: rgba(0, 122, 255, 0.55);
            }}
        """)

    def _open_github_repo(self):
        QDesktopServices.openUrl(QUrl("https://github.com/echo-desktop/echo-search"))

    def _on_install_clicked(self):
        self.install_requested.emit(self.chk_install_search.isChecked())

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.search_icon.set_dark(is_dark)
        self.tip_card.set_dark(is_dark)
        self.preview_card.set_dark(is_dark)
        self.opt_card.set_dark(is_dark)
        self.chk_install_search.set_dark(is_dark)
        self.btn_back.set_dark(is_dark)
        self._update_github_btn_style()
        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.title_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 24px; font-weight: 800; letter-spacing: -0.4px; background: transparent; border: none;")
        self.sub_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 12px; line-height: 1.4; background: transparent; border: none;")
        for lbl in (self.tip_item1, self.tip_item2, self.tip_item3):
            lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 10.5px; line-height: 1.35; border: none; background: transparent;")
        self.sp_query.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 13px; font-weight: 700; background: transparent; border: none;")
        self.opt_desc.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 10px; margin-left: 24px; border: none; background: transparent;")

        item2_bg = "rgba(255, 255, 255, 0.06)" if self.is_dark else "rgba(0, 0, 0, 0.03)"
        self.item2.setStyleSheet(f"QFrame {{ background: {item2_bg}; border-radius: 6px; border: none; }}")
        self.calc_item.setStyleSheet(f"QFrame {{ background: {item2_bg}; border-radius: 6px; border: none; }}")
        self.i2_title.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; font-weight: 600; border: none; background: transparent;")
        self.i2_sub.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 9px; border: none; background: transparent;")
        self.calc_title.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 11px; font-weight: 700; border: none; background: transparent;")
        self.calc_sub.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 9px; border: none; background: transparent;")

        sp_bar_bg = "rgba(255, 255, 255, 0.14)" if self.is_dark else "rgba(0, 0, 0, 0.06)"
        sp_bar_border = "rgba(255, 255, 255, 0.24)" if self.is_dark else "rgba(0, 0, 0, 0.12)"
        self.spotlight_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {sp_bar_bg};
                border: 1px solid {sp_bar_border};
                border-radius: 9px;
            }}
        """)
        badge_bg = "rgba(255, 255, 255, 0.18)" if self.is_dark else "rgba(0, 0, 0, 0.10)"
        self.sp_badge.setStyleSheet(f"""
            color: {t_col};
            background-color: {badge_bg};
            border-radius: 5px;
            padding: 2px 7px;
            font-family: monospace;
            font-size: 10px;
            font-weight: 600;
            border: none;
        """)

    def retranslate_ui(self):
        self.title_lbl.setText(t("installer.search_companion_title"))
        self.sub_lbl.setText(t("installer.search_companion_sub"))
        self.tip_item1.setText("⚡ " + t("installer.search_feature_shortcut"))
        self.tip_item2.setText("📂 " + t("installer.search_feature_files"))
        self.tip_item3.setText("🧮 " + t("installer.search_feature_calc"))
        self.cat_apps_lbl.setText(t("installer.spotlight_cat_apps"))
        self.ai_sub.setText(t("installer.spotlight_app_desc"))
        self.i2_title.setText(t("installer.spotlight_term_name"))
        self.i2_sub.setText(t("installer.spotlight_term_desc"))
        self.cat_calc_lbl.setText(t("installer.spotlight_cat_calc"))
        self.calc_sub.setText(t("installer.spotlight_calc_desc"))
        chk_text = t("installer.search_opt_enable") if self.is_welcome_mode else t("installer.search_opt_install")
        self.chk_install_search.setText(chk_text)
        self.opt_desc.setText(t("installer.search_opt_desc"))
        self.btn_github.setText(t("installer.search_github_btn") + "  Echo Search")
        self.btn_back.setText(t("installer.back"))
        btn_lbl = t("installer.continue") if self.is_welcome_mode else t("installer.install_btn")
        self.btn_install.setText(btn_lbl)



# =============================================================================
# View 5: Installing Progress View (Echo Liquid Glass Onboarding State)
# =============================================================================
class InstallingView(QWidget):
    def __init__(self, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 24, 40, 32)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"

        # 1. Pulsing 3D Liquid Chrome Emblem in Center
        self.logo_pulse = LiquidGlassPulsingLogo(size=96, is_dark=self.is_dark)
        layout.addWidget(self.logo_pulse, 0, Qt.AlignCenter)
        layout.addSpacing(2)

        # 2. Bold Title
        self.title_lbl = QLabel(t("installer.installing_title"))
        self.title_lbl.setAlignment(Qt.AlignCenter)
        self.title_lbl.setStyleSheet(f"""
            color: {t_col};
            font-family: 'SF Pro Display', 'Inter', -apple-system, sans-serif;
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.4px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.title_lbl)

        # 3. Subtitle / General status
        self.sub_lbl = QLabel(t("installer.installing_sub"))
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        self.sub_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; border: none; background: transparent;")
        layout.addWidget(self.sub_lbl)

        layout.addSpacing(8)

        # 4. Main Glass Progress Container
        self.progress_card = MacGlassCard(is_dark=self.is_dark, corner_radius=14)
        p_card_layout = QVBoxLayout(self.progress_card)
        p_card_layout.setContentsMargins(20, 16, 20, 16)
        p_card_layout.setSpacing(10)

        # Header with step text and percentage
        step_header = QHBoxLayout()
        self.status_lbl = QLabel("Preparing installation pipeline...")
        self.status_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 12.5px; font-weight: 600; border: none; background: transparent;")
        step_header.addWidget(self.status_lbl, 1)

        self.pct_lbl = QLabel("0%")
        self.pct_lbl.setStyleSheet(f"color: {MacPalette.ACCENT_BLUE}; font-family: monospace; font-size: 13px; font-weight: 700; border: none; background: transparent;")
        step_header.addWidget(self.pct_lbl, 0, Qt.AlignRight)
        p_card_layout.addLayout(step_header)

        # Progress Bar (Liquid Glass Gradient)
        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(8)
        self.pbar.setTextVisible(False)
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)
        self.pbar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {"rgba(255, 255, 255, 0.12)" if self.is_dark else "rgba(0, 0, 0, 0.08)"};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007AFF, stop:1 #00D2FF);
                border-radius: 4px;
            }}
        """)
        p_card_layout.addWidget(self.pbar)

        p_card_layout.addSpacing(4)

        # 5-Stage Milestone Sequence Bar
        self.milestone_bar = InstallingMilestoneBar(current_stage=1, is_dark=self.is_dark)
        self._update_milestone_names()
        p_card_layout.addWidget(self.milestone_bar)

        layout.addWidget(self.progress_card)

        # Collapsible Live Terminal Log Drawer (Hidden by default)
        self.log_drawer = GlassTerminalDrawer(is_dark=self.is_dark)
        layout.addWidget(self.log_drawer)

        layout.addStretch()

    def _update_milestone_names(self):
        names = [
            t("installer.stage_prep", "Validation"),
            t("installer.stage_app", "Deployment"),
            t("installer.stage_icon", "Icons & Assets"),
            t("installer.stage_desktop", "Desktop Entry"),
            t("installer.stage_env", "Runtime Sync")
        ]
        self.milestone_bar.set_stage_names(names)

    def update_progress(self, pct: int, status_text: str, stage_idx: int):
        self.pbar.setValue(pct)
        self.pct_lbl.setText(f"{pct}%")
        self.status_lbl.setText(status_text)
        self.milestone_bar.set_stage(stage_idx)
        self.log_drawer.append_log(f"[{pct:>2}%] {status_text}")

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.logo_pulse.set_dark(is_dark)
        self.progress_card.set_dark(is_dark)
        self.milestone_bar.set_dark(is_dark)
        self.log_drawer.set_dark(is_dark)
        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.title_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 24px; font-weight: 800; background: transparent; border: none;")
        self.sub_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; border: none; background: transparent;")
        self.status_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 12.5px; font-weight: 600; border: none; background: transparent;")
        self.pbar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {"rgba(255, 255, 255, 0.12)" if self.is_dark else "rgba(0, 0, 0, 0.08)"};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007AFF, stop:1 #00D2FF);
                border-radius: 4px;
            }}
        """)

    def retranslate_ui(self):
        self.title_lbl.setText(t("installer.installing_title"))
        self.sub_lbl.setText(t("installer.installing_sub"))
        self._update_milestone_names()


# =============================================================================
# View 6: Complete Triumph View (Premium Final Onboarding State)
# =============================================================================
class CompleteView(QWidget):
    back_requested = Signal()
    launch_requested = Signal()
    close_requested = Signal()

    def __init__(self, is_dark: bool = True, is_welcome_mode: bool = False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.is_welcome_mode = is_welcome_mode
        self.autostart_enabled = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 24, 40, 32)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"

        # 1. Authentic Echo Logo Hero with Radiant Aura & Subtle Confetti
        self.complete_logo = LiquidGlassCompleteLogo(size=96, is_dark=self.is_dark)
        layout.addWidget(self.complete_logo, 0, Qt.AlignCenter)
        layout.addSpacing(2)

        # 2. Bold Title: Echo Settings is Ready
        title_str = t("installer.welcome_complete_title") if self.is_welcome_mode else t("installer.complete_title")
        self.title_lbl = QLabel(title_str)
        self.title_lbl.setAlignment(Qt.AlignCenter)
        self.title_lbl.setStyleSheet(f"""
            color: {t_col};
            font-family: 'SF Pro Display', 'Inter', -apple-system, sans-serif;
            font-size: 26px;
            font-weight: 800;
            letter-spacing: -0.4px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.title_lbl)

        # 3. Subtitle
        sub_str = t("installer.welcome_complete_sub") if self.is_welcome_mode else t("installer.complete_sub")
        self.sub_lbl = QLabel(sub_str)
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        self.sub_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; border: none; background: transparent;")
        layout.addWidget(self.sub_lbl)

        layout.addSpacing(8)

        # 4. Summary Glass Card of Actions
        self.summary_card = MacGlassCard(is_dark=self.is_dark, corner_radius=14)
        c_layout = QVBoxLayout(self.summary_card)
        c_layout.setContentsMargins(20, 14, 20, 14)
        c_layout.setSpacing(8)

        if self.is_welcome_mode:
            self.item1_lbl = QLabel("✨  " + t("installer.welcome_item1"))
            self.item2_lbl = QLabel("⚡  " + t("installer.welcome_item2"))
            self.item3_lbl = QLabel("💎  " + t("installer.welcome_item3"))
        else:
            self.item1_lbl = QLabel("✨  " + t("installer.complete_item1"))
            self.item2_lbl = QLabel("⚡  " + t("installer.complete_item2"))
            self.item3_lbl = QLabel("💎  " + t("installer.complete_item3"))
        self.item_search_lbl = QLabel("🔍  " + t("installer.complete_item_search"))
        self.item_search_lbl.setVisible(False)

        for lbl in (self.item1_lbl, self.item2_lbl, self.item3_lbl, self.item_search_lbl):
            lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 12px; line-height: 1.45; border: none; background: transparent;")
            lbl.setWordWrap(True)
            c_layout.addWidget(lbl)

        layout.addWidget(self.summary_card)
        layout.addStretch()

        # 5. Buttons (Bottom Row)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_back = CupertinoSecondaryButton(t("installer.back"), is_dark=self.is_dark)
        self.btn_back.clicked.connect(self.back_requested.emit)
        btn_layout.addWidget(self.btn_back)

        btn_layout.addStretch()

        self.btn_close = CupertinoSecondaryButton(t("installer.close_btn"), is_dark=self.is_dark)
        self.btn_close.clicked.connect(self.close_requested.emit)
        btn_layout.addWidget(self.btn_close)

        self.btn_launch = CupertinoPrimaryButton(t("installer.launch_btn"))
        self.btn_launch.clicked.connect(self.launch_requested.emit)
        btn_layout.addWidget(self.btn_launch)

        layout.addLayout(btn_layout)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(150, self.complete_logo.trigger_confetti)

    def set_autostart_enabled(self, enabled: bool):
        self.autostart_enabled = enabled

    def set_echo_search_enabled(self, enabled: bool):
        self.item_search_lbl.setVisible(enabled)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.complete_logo.set_dark(is_dark)
        self.summary_card.set_dark(is_dark)
        self.btn_back.set_dark(is_dark)
        self.btn_close.set_dark(is_dark)
        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.title_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 26px; font-weight: 800; letter-spacing: -0.4px; background: transparent; border: none;")
        self.sub_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; border: none; background: transparent;")
        for lbl in (self.item1_lbl, self.item2_lbl, self.item3_lbl, self.item_search_lbl):
            lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 12px; line-height: 1.45; border: none; background: transparent;")

    def retranslate_ui(self):
        title_str = t("installer.welcome_complete_title") if self.is_welcome_mode else t("installer.complete_title")
        sub_str = t("installer.welcome_complete_sub") if self.is_welcome_mode else t("installer.complete_sub")
        self.title_lbl.setText(title_str)
        self.sub_lbl.setText(sub_str)
        self.btn_back.setText(t("installer.back"))
        self.btn_close.setText(t("installer.close_btn"))
        self.btn_launch.setText(t("installer.launch_btn"))
        if self.is_welcome_mode:
            self.item1_lbl.setText("✨  " + t("installer.welcome_item1"))
            self.item2_lbl.setText("⚡  " + t("installer.welcome_item2"))
            self.item3_lbl.setText("💎  " + t("installer.welcome_item3"))
        else:
            self.item1_lbl.setText("✨  " + t("installer.complete_item1"))
            self.item2_lbl.setText("⚡  " + t("installer.complete_item2"))
            self.item3_lbl.setText("💎  " + t("installer.complete_item3"))
        self.item_search_lbl.setText("🔍  " + t("installer.complete_item_search"))
        self.btn_close.setText(t("installer.close_btn"))
        self.btn_launch.setText(t("installer.launch_btn"))



# =============================================================================
# View 7: Error View (Fully Localized & Styled)
# =============================================================================
class ErrorView(QWidget):
    retry_requested = Signal()
    cancel_requested = Signal()

    def __init__(self, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.error_msg = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 28, 40, 32)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"

        # Alert Badge
        self.alert_icon = QLabel("✕")
        self.alert_icon.setAlignment(Qt.AlignCenter)
        self.alert_icon.setStyleSheet("color: #FF3B30; font-size: 48px; font-weight: bold; border: none; background: transparent;")
        layout.addWidget(self.alert_icon)

        self.title_lbl = QLabel(t("installer.error_title"))
        self.title_lbl.setAlignment(Qt.AlignCenter)
        self.title_lbl.setStyleSheet(f"""
            color: {t_col};
            font-family: 'SF Pro Display', 'Inter', -apple-system, sans-serif;
            font-size: 24px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.title_lbl)

        self.sub_lbl = QLabel(t("installer.error_sub"))
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        self.sub_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; border: none; background: transparent;")
        layout.addWidget(self.sub_lbl)

        layout.addSpacing(6)

        self.card = MacGlassCard(is_dark=self.is_dark, corner_radius=12)
        c_layout = QVBoxLayout(self.card)
        c_layout.setContentsMargins(16, 12, 16, 12)
        c_layout.setSpacing(4)

        self.detail_lbl = QLabel("")
        self.detail_lbl.setWordWrap(True)
        self.detail_lbl.setStyleSheet("color: #FF3B30; font-size: 11px; font-family: monospace; border: none; background: transparent;")
        c_layout.addWidget(self.detail_lbl)
        layout.addWidget(self.card)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_copy = CupertinoSecondaryButton(t("installer.copy_diag", "Copy Diagnostics"), is_dark=self.is_dark)
        self.btn_copy.clicked.connect(self._copy_diagnostic)
        btn_layout.addWidget(self.btn_copy)

        btn_layout.addStretch()

        self.btn_cancel = CupertinoSecondaryButton(t("installer.cancel", "Cancel"), is_dark=self.is_dark)
        self.btn_cancel.clicked.connect(self.cancel_requested.emit)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_retry = CupertinoPrimaryButton(t("installer.retry", "Retry"))
        self.btn_retry.clicked.connect(self.retry_requested.emit)
        btn_layout.addWidget(self.btn_retry)

        layout.addLayout(btn_layout)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.card.set_dark(is_dark)
        self.btn_copy.set_dark(is_dark)
        self.btn_cancel.set_dark(is_dark)
        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.title_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 24px; font-weight: 800; background: transparent; border: none;")
        self.sub_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; border: none; background: transparent;")

    def set_error(self, message: str):
        self.error_msg = message
        self.detail_lbl.setText(message[:400] + ("..." if len(message) > 400 else ""))

    def _copy_diagnostic(self):
        cb = QApplication.clipboard()
        cb.setText(f"Echo Settings {VERSION} Installation Error:\n\n{self.error_msg}")
        QMessageBox.information(self, "Copied", "Diagnostic information copied to clipboard.")

    def retranslate_ui(self):
        self.title_lbl.setText(t("installer.error_title"))
        self.sub_lbl.setText(t("installer.error_sub"))
        self.btn_copy.setText(t("installer.copy_diag", "Copy Diagnostics"))
        self.btn_cancel.setText(t("installer.cancel", "Cancel"))
        self.btn_retry.setText(t("installer.retry", "Retry"))


# =============================================================================
# Main Window with Embedded System Window Controls & Theme Switcher
# =============================================================================
class EchoInstallerWindow(QWidget):
    def __init__(self, on_complete: callable = None, is_welcome_mode: bool = False):
        super().__init__()
        self.on_complete = on_complete
        self.is_welcome_mode = is_welcome_mode
        self.is_dark = is_dark_mode()
        self.selected_scope = "user"
        self.selected_autostart = False
        self.selected_desktop_shortcut = False
        self.selected_echo_search = True
        self.worker = None

        title_str = f"Welcome to Echo Settings (v{VERSION})" if self.is_welcome_mode else f"Echo Settings Installer (v{VERSION})"
        self.setWindowTitle(title_str)
        self.setFixedSize(880, 580)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        # Root Layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Top embedded window header: Window Controls (left) + Theme Switcher (right)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(18, 14, 18, 0)

        self.win_controls = SystemWindowControls(is_dark=self.is_dark)
        self.win_controls.close_clicked.connect(self.close)
        self.win_controls.minimize_clicked.connect(self.showMinimized)
        self.win_controls.maximize_clicked.connect(self._toggle_maximize)
        header_layout.addWidget(self.win_controls)

        header_layout.addStretch()

        # Minimal Liquid Glass Dark/Light Capsule Toggle
        self.theme_toggle = CupertinoThemeToggle(is_dark=self.is_dark)
        self.theme_toggle.toggled.connect(self.set_dark)
        header_layout.addWidget(self.theme_toggle)

        root_layout.addLayout(header_layout)

        # Stacked Views
        self.stack = QStackedWidget(self)
        self.stack.setStyleSheet("background: transparent;")

        # 1. Welcome Hero View (Apple Setup Hello Screen)
        self.welcome_hero_view = WelcomeHeroView(is_dark=self.is_dark)
        self.welcome_hero_view.start_requested.connect(self._goto_language_select)
        self.stack.addWidget(self.welcome_hero_view)

        # 2. Dedicated Language Selection View
        self.lang_select_view = LanguageSelectView(is_dark=self.is_dark)
        self.lang_select_view.back_requested.connect(lambda: self.stack.setCurrentWidget(self.welcome_hero_view))
        self.lang_select_view.continue_requested.connect(self._goto_system_check)
        self.stack.addWidget(self.lang_select_view)

        # 3. System Check View (2-Column macOS Layout)
        self.system_check_view = SystemCheckView(is_dark=self.is_dark)
        self.system_check_view.back_requested.connect(lambda: self.stack.setCurrentWidget(self.lang_select_view))
        self.system_check_view.continue_requested.connect(self._on_system_check_continue)
        self.stack.addWidget(self.system_check_view)

        # 4. Scope View (2-Column macOS Layout + Options) - Used in Installer Mode
        self.scope_view = ScopeView(is_dark=self.is_dark)
        self.scope_view.back_requested.connect(lambda: self.stack.setCurrentWidget(self.system_check_view))
        self.scope_view.continue_requested.connect(self._goto_search_companion)
        self.stack.addWidget(self.scope_view)

        # 5. Echo Search Companion View
        self.echo_search_view = EchoSearchCompanionView(is_dark=self.is_dark, is_welcome_mode=self.is_welcome_mode)
        self.echo_search_view.back_requested.connect(self._on_echo_search_back)
        self.echo_search_view.install_requested.connect(self._on_echo_search_continue)
        self.stack.addWidget(self.echo_search_view)

        # 6. Installing View
        self.installing_view = InstallingView(is_dark=self.is_dark)
        self.stack.addWidget(self.installing_view)

        # 7. Complete View
        self.complete_view = CompleteView(is_dark=self.is_dark, is_welcome_mode=self.is_welcome_mode)
        self.complete_view.back_requested.connect(self._on_complete_back)
        self.complete_view.launch_requested.connect(self._launch_app)
        self.complete_view.close_requested.connect(self._launch_app)
        self.stack.addWidget(self.complete_view)

        # 8. Error View
        self.error_view = ErrorView(is_dark=self.is_dark)
        self.error_view.retry_requested.connect(lambda: self._start_installation(
            self.selected_scope, self.selected_autostart, self.selected_desktop_shortcut, getattr(self, "selected_echo_search", True)
        ))
        self.error_view.cancel_requested.connect(self.close)
        self.stack.addWidget(self.error_view)

        root_layout.addWidget(self.stack, 1)

        # Global Retranslation Listener
        i18n.language_changed.connect(self._retranslate_all)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.win_controls.set_dark(is_dark)
        self.theme_toggle.set_dark(is_dark)
        self.welcome_hero_view.set_dark(is_dark)
        self.lang_select_view.set_dark(is_dark)
        self.system_check_view.set_dark(is_dark)
        self.scope_view.set_dark(is_dark)
        self.echo_search_view.set_dark(is_dark)
        self.installing_view.set_dark(is_dark)
        self.complete_view.set_dark(is_dark)
        self.error_view.set_dark(is_dark)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            wh = self.windowHandle()
            if wh:
                wh.startSystemMove()
                return
        super().mousePressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), 24.0, 24.0)

        # ── Liquid Glass Substrate Gradient ──
        if self.is_dark:
            grad = QRadialGradient(QPointF(rect.width() * 0.5, 0), rect.width() * 0.90)
            grad.setColorAt(0.0, QColor(36, 38, 44, 252))
            grad.setColorAt(0.5, QColor(26, 28, 32, 253))
            grad.setColorAt(1.0, QColor(18, 20, 24, 255))
            p.fillPath(path, grad)
        else:
            grad = QRadialGradient(QPointF(rect.width() * 0.5, 0), rect.width() * 0.90)
            grad.setColorAt(0.0, QColor(255, 255, 255, 253))
            grad.setColorAt(0.6, QColor(246, 247, 250, 253))
            grad.setColorAt(1.0, QColor(238, 240, 244, 255))
            p.fillPath(path, grad)

        # Top specular highlight line (Liquid Glass reflection)
        spec_pen = QPen(QColor(255, 255, 255, 55 if self.is_dark else 130), 1.0)
        p.setPen(spec_pen)
        p.drawLine(QPointF(24, 1.0), QPointF(rect.width() - 24, 1.0))

        # Outer Glass Border
        border_col = QColor(255, 255, 255, 38) if self.is_dark else QColor(0, 0, 0, 28)
        p.setPen(QPen(border_col, 1.0))
        p.drawPath(path)
        p.end()

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _goto_language_select(self):
        self.stack.setCurrentWidget(self.lang_select_view)

    def _goto_system_check(self):
        self.system_check_view.run_checks()
        self.stack.setCurrentWidget(self.system_check_view)

    def _on_system_check_continue(self):
        if self.is_welcome_mode:
            self.stack.setCurrentWidget(self.echo_search_view)
        else:
            self._goto_scope()

    def _goto_scope(self):
        self.stack.setCurrentWidget(self.scope_view)

    def _on_echo_search_back(self):
        if self.is_welcome_mode:
            self.stack.setCurrentWidget(self.system_check_view)
        else:
            self.stack.setCurrentWidget(self.scope_view)

    def _goto_search_companion(self, scope: str, autostart: bool, desktop_shortcut: bool):
        self.selected_scope = scope
        self.selected_autostart = autostart
        self.selected_desktop_shortcut = desktop_shortcut
        self.stack.setCurrentWidget(self.echo_search_view)

    def _on_echo_search_continue(self, install_echo_search: bool):
        self.selected_echo_search = install_echo_search
        if self.is_welcome_mode:
            if install_echo_search:
                self._start_installation_with_search(True)
            else:
                self.complete_view.set_autostart_enabled(self.selected_autostart)
                self.complete_view.set_echo_search_enabled(False)
                self.stack.setCurrentWidget(self.complete_view)
        else:
            self._start_installation_with_search(install_echo_search)

    def _on_complete_back(self):
        self.stack.setCurrentWidget(self.echo_search_view)

    def _start_installation_with_search(self, install_echo_search: bool):
        self.selected_echo_search = install_echo_search
        self._start_installation(
            getattr(self, "selected_scope", "user"),
            getattr(self, "selected_autostart", False),
            getattr(self, "selected_desktop_shortcut", False),
            install_echo_search
        )

    def _start_installation(self, scope: str = "user", autostart: bool = False, desktop_shortcut: bool = False, install_echo_search: bool = True):
        self.selected_scope = scope
        self.selected_autostart = autostart
        self.selected_desktop_shortcut = desktop_shortcut
        self.selected_echo_search = install_echo_search
        self.stack.setCurrentWidget(self.installing_view)

        self.worker = InstallWorker(
            scope=scope,
            autostart=autostart,
            desktop_shortcut=desktop_shortcut,
            install_echo_search=install_echo_search
        )
        self.worker.progress.connect(self.installing_view.update_progress)
        self.worker.finished.connect(self._on_install_finished)
        self.worker.start()

    def _on_install_finished(self, success: bool, error_msg: str):
        if success:
            self.complete_view.set_autostart_enabled(self.selected_autostart)
            self.complete_view.set_echo_search_enabled(getattr(self, "selected_echo_search", True))
            self.stack.setCurrentWidget(self.complete_view)
        else:
            self.error_view.set_error(error_msg)
            self.stack.setCurrentWidget(self.error_view)

    def _launch_app(self):
        if self.on_complete:
            self.on_complete()
            self.close()
            return
        paths = InstallationEngine.get_paths(self.selected_scope)
        if getattr(self, "selected_echo_search", False):
            candidates = [
                os.path.expanduser("~/.local/bin/echo-search"),
                "/usr/local/bin/echo-search",
                "/usr/bin/echo-search",
                os.path.expanduser("~/echo_search/main.py")
            ]
            for c in candidates:
                if os.path.exists(c):
                    if c.endswith(".py"):
                        subprocess.Popen(["python3", c])
                    else:
                        subprocess.Popen([c])
                    break
        if os.path.exists(paths["bin_file"]):
            subprocess.Popen([paths["bin_file"]])
        elif os.path.exists("/usr/bin/echo-settings"):
            subprocess.Popen(["/usr/bin/echo-settings"])
        self.close()

    def _retranslate_all(self):
        self.welcome_hero_view.retranslate_ui()
        self.lang_select_view.retranslate_ui()
        self.system_check_view.retranslate_ui()
        self.scope_view.retranslate_ui()
        self.echo_search_view.retranslate_ui()
        self.installing_view.retranslate_ui()
        self.complete_view.retranslate_ui()
        self.error_view.retranslate_ui()



# =============================================================================
# Uninstaller Window with Embedded System Window Controls & Theme Switcher
# =============================================================================
class EchoUninstallerWindow(QWidget):
    def __init__(self, scope: str = "user"):
        super().__init__()
        self.is_dark = is_dark_mode()
        self.scope = scope
        self.worker = None

        self.setWindowTitle(f"{t('installer.uninstaller_title', 'Uninstall Echo Settings')} (v{VERSION})")
        self.setFixedSize(620, 390)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header: Window Controls (left) + Theme Toggle (right)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(18, 14, 18, 0)
        self.win_controls = SystemWindowControls(is_dark=self.is_dark)
        self.win_controls.close_clicked.connect(self.close)
        self.win_controls.minimize_clicked.connect(self.showMinimized)
        self.win_controls.maximize_clicked.connect(self.close)
        header_layout.addWidget(self.win_controls)

        header_layout.addStretch()

        self.theme_toggle = CupertinoThemeToggle(is_dark=self.is_dark)
        self.theme_toggle.toggled.connect(self.set_dark)
        header_layout.addWidget(self.theme_toggle)

        root_layout.addLayout(header_layout)

        content_w = QWidget()
        layout = QVBoxLayout(content_w)
        layout.setContentsMargins(36, 16, 36, 26)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignCenter)

        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"

        self.title_lbl = QLabel(t("installer.uninstaller_title", "Uninstall Echo Settings"))
        self.title_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 24px; font-weight: 800; border: none; background: transparent;")
        layout.addWidget(self.title_lbl)

        self.desc_lbl = QLabel(t("installer.uninstaller_desc", "This will remove Echo Settings desktop components, background services, and icons from your system."))
        self.desc_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; line-height: 1.45; border: none; background: transparent;")
        self.desc_lbl.setWordWrap(True)
        layout.addWidget(self.desc_lbl)

        # Options Card
        self.card = MacGlassCard(is_dark=self.is_dark, corner_radius=12)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(6)

        self.chk_data = CupertinoCheckbox(t("installer.uninstaller_chk_data", "Also remove user settings and cached theme data"), is_checked=False, is_dark=self.is_dark)
        card_layout.addWidget(self.chk_data)
        layout.addWidget(self.card)

        layout.addStretch()

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(f"color: {s_col}; font-size: 12px; border: none; background: transparent;")
        layout.addWidget(self.status_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        self.btn_cancel = CupertinoSecondaryButton(t("installer.cancel", "Cancel"), is_dark=self.is_dark)
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_remove = QPushButton(t("installer.uninstaller_btn_confirm", "Remove Echo Settings"))
        self.btn_remove.setFixedHeight(40)
        self.btn_remove.setCursor(Qt.PointingHandCursor)
        self.btn_remove.setStyleSheet(f"""
            QPushButton {{
                background-color: #FF3B30;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 13px;
                font-weight: 600;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: #D70015;
            }}
        """)
        self.btn_remove.clicked.connect(self._start_uninstall)
        btn_layout.addWidget(self.btn_remove)

        layout.addLayout(btn_layout)
        root_layout.addWidget(content_w, 1)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.win_controls.set_dark(is_dark)
        self.theme_toggle.set_dark(is_dark)
        self.chk_data.set_dark(is_dark)
        self.card.set_dark(is_dark)
        self.btn_cancel.set_dark(is_dark)
        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.title_lbl.setStyleSheet(f"color: {t_col}; font-family: 'SF Pro Display', 'Inter', sans-serif; font-size: 24px; font-weight: 800; border: none; background: transparent;")
        self.desc_lbl.setStyleSheet(f"color: {s_col}; font-family: 'SF Pro Text', 'Inter', sans-serif; font-size: 13px; line-height: 1.45; border: none; background: transparent;")
        self.status_lbl.setStyleSheet(f"color: {s_col}; font-size: 12px; border: none; background: transparent;")
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            wh = self.windowHandle()
            if wh:
                wh.startSystemMove()
                return
        super().mousePressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), 24.0, 24.0)

        # ── Liquid Glass Substrate Gradient ──
        if self.is_dark:
            grad = QRadialGradient(QPointF(rect.width() * 0.5, 0), rect.width() * 0.90)
            grad.setColorAt(0.0, QColor(36, 38, 44, 252))
            grad.setColorAt(0.5, QColor(26, 28, 32, 253))
            grad.setColorAt(1.0, QColor(18, 20, 24, 255))
            p.fillPath(path, grad)
        else:
            grad = QRadialGradient(QPointF(rect.width() * 0.5, 0), rect.width() * 0.90)
            grad.setColorAt(0.0, QColor(255, 255, 255, 253))
            grad.setColorAt(0.6, QColor(246, 247, 250, 253))
            grad.setColorAt(1.0, QColor(238, 240, 244, 255))
            p.fillPath(path, grad)

        # Top specular highlight line (Liquid Glass reflection)
        spec_pen = QPen(QColor(255, 255, 255, 55 if self.is_dark else 130), 1.0)
        p.setPen(spec_pen)
        p.drawLine(QPointF(24, 1.0), QPointF(rect.width() - 24, 1.0))

        # Outer Glass Border
        border_col = QColor(255, 255, 255, 38) if self.is_dark else QColor(0, 0, 0, 28)
        p.setPen(QPen(border_col, 1.0))
        p.drawPath(path)
        p.end()

    def _start_uninstall(self):
        self.btn_remove.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.status_lbl.setText(t("installer.uninstaller_removing", "Uninstalling Echo Settings components..."))
        self.worker = UninstallWorker(self.scope, self.chk_data.isChecked())
        self.worker.finished.connect(self._on_uninstall_finished)
        self.worker.start()

    def _on_uninstall_finished(self, success: bool, error_msg: str):
        if success:
            QMessageBox.information(self, t("installer.uninstaller_title", "Uninstall"), t("installer.uninstaller_done", "Echo Settings has been successfully removed."))
            self.close()
        else:
            QMessageBox.critical(self, "Error", f"{t('installer.error_title', 'Error')}:\n{error_msg}")
            self.btn_remove.setEnabled(True)
            self.btn_cancel.setEnabled(True)


# =============================================================================
# Entry Point
# =============================================================================
def main():
    if "--internal-install-system" in sys.argv:
        success = InstallationEngine.install("system")
        sys.exit(0 if success else 1)

    if "--internal-uninstall-system" in sys.argv:
        remove_data = "--remove-data" in sys.argv
        success = InstallationEngine.uninstall("system", remove_data)
        sys.exit(0 if success else 1)

    app = QApplication(sys.argv)
    app.setApplicationName("Echo Installer")
    app.setApplicationDisplayName("Echo Settings Installer")

    if "--uninstall" in sys.argv:
        scope = "system" if os.path.exists("/usr/share/echo-settings") else "user"
        win = EchoUninstallerWindow(scope)
    elif "--welcome" in sys.argv or "--onboarding" in sys.argv:
        win = EchoInstallerWindow(is_welcome_mode=True)
    else:
        win = EchoInstallerWindow(is_welcome_mode=False)

    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
