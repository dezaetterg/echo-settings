import sys
import os

os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.services=false;qt.qpa.portal=false")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
for p in (SCRIPT_DIR, PARENT_DIR, os.path.join(SCRIPT_DIR, "installer"), os.path.join(PARENT_DIR, "installer")):
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPoint, QTimer, QObject, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
from services.system_info_watcher import SystemInfoWatcher
from theme.manager import ThemeManager

from theme.metrics import WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT
from theme.constants import APP_TITLE
from components.sidebar import Sidebar

from components.theme_transition import ThemeTransitionOverlay

class ScrollBarAnimator(QObject):
    def __init__(self, scrollbar):
        super().__init__(scrollbar)
        self.scrollbar = scrollbar
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(400)
        self.timer.timeout.connect(self.stop_scroll)
        self.scrollbar.valueChanged.connect(self.on_scroll)
        
    def on_scroll(self):
        if self.scrollbar.property("scrolling") != "true":
            self.scrollbar.setProperty("scrolling", "true")
            self.scrollbar.style().unpolish(self.scrollbar)
            self.scrollbar.style().polish(self.scrollbar)
        self.timer.start()
        
    def stop_scroll(self):
        self.scrollbar.setProperty("scrolling", "false")
        self.scrollbar.style().unpolish(self.scrollbar)
        self.scrollbar.style().polish(self.scrollbar)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.central_widget.setAttribute(Qt.WA_StyledBackground, True)
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.sidebar = Sidebar()
        self.sidebar.setAttribute(Qt.WA_StyledBackground, True)
        self.main_layout.addWidget(self.sidebar)
        
        self.right_widget = QWidget()
        self.right_widget.setObjectName("RightArea")
        self.right_widget.setAttribute(Qt.WA_StyledBackground, True)
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        
        self.content_stack = QStackedWidget()
        self.right_layout.addWidget(self.content_stack)
        
        self.main_layout.addWidget(self.right_widget)
        
        # Lazy pages storage and scroll animators
        self._pages = {}
        self.scroll_animators = []
        
        self.sidebar.page_changed.connect(self.change_page)
        self.sidebar.btn_close.clicked.connect(self.close)
        self.sidebar.btn_minimize.clicked.connect(self.showMinimized)
        self.sidebar.btn_maximize.clicked.connect(self.toggle_maximize)

        
        # Load startup settings
        from PySide6.QtCore import QSettings
        settings = QSettings("TahoeSettings", "App")
        if settings.value("remember_size", False, type=bool):
            w = settings.value("window_width", WINDOW_DEFAULT_WIDTH, type=int)
            h = settings.value("window_height", WINDOW_DEFAULT_HEIGHT, type=int)
            self.resize(w, h)

        # Theme initial setup
        self.last_theme = None
        self.check_theme()

        # Theme sync timer
        self.theme_timer = QTimer(self)
        self.theme_timer.timeout.connect(self.check_theme)
        self.theme_timer.start(3000) # Check every 3s

        initial_page = "General"
        if settings.value("restore_page", False, type=bool):
            initial_page = settings.value("last_page", "General", type=str)
            
        self.change_page(0, initial_page)
        self.sidebar._on_item_clicked(initial_page)
        
        # System info watcher — poll every 5 seconds
        self.info_watcher = SystemInfoWatcher(interval_ms=5000, parent=self)
        self.info_watcher.info_changed.connect(self._on_system_info_changed)

        # Connect live dynamic language switching
        from localization import i18n
        i18n.language_changed.connect(self._on_language_changed)

        # Connect search navigation
        self.sidebar.search_result_selected.connect(self._on_search_result_selected)


    def _create_page(self, title: str) -> QWidget:
        """Factory for on-demand page creation."""
        from PySide6.QtWidgets import QScrollArea
        page = None
        if title == "General":
            from pages.general import GeneralPage
            page = GeneralPage()
            page.request_page.connect(self._navigate_from_shortcut)
        elif title == "Appearance":
            from pages.appearance import AppearancePage
            page = AppearancePage()
            page.theme_switched.connect(self.check_theme)
        elif title == "Storage":
            from pages.storage import StoragePage
            page = StoragePage()
        elif title == "Power":
            from pages.power import PowerPage
            page = PowerPage()
        elif title == "Display":
            from pages.display import DisplayPage
            page = DisplayPage()
        elif title == "Wi-Fi":
            from pages.wifi import WiFiPage
            page = WiFiPage()
        elif title == "Bluetooth":
            from pages.bluetooth import BluetoothPage
            page = BluetoothPage()
        elif title == "Network":
            from pages.network import NetworkPage
            page = NetworkPage()
        elif title == "Sound":
            from pages.sound import SoundPage
            page = SoundPage()
        elif title == "Notifications":
            from pages.notifications import NotificationsPage
            page = NotificationsPage()
        elif title == "Keyboard":
            from pages.keyboard import KeyboardPage
            page = KeyboardPage()
        elif title == "Mouse":
            from pages.mouse import MousePage
            page = MousePage()
        elif title in ["Privacy", "Privacy & Security"]:
            from pages.privacy import PrivacyPage
            page = PrivacyPage()
        elif title == "Echo Search":
            from pages.spotlight import SpotlightPage
            page = SpotlightPage()
        else:
            from pages.placeholder import PlaceholderPage
            page = PlaceholderPage()
            page.label.setText(f"Раздел '{title}' в разработке")

        # Attach scrollbar animators to any scroll areas inside newly created page
        for scroll_area in page.findChildren(QScrollArea):
            vsb = scroll_area.verticalScrollBar()
            if vsb:
                animator = ScrollBarAnimator(vsb)
                self.scroll_animators.append(animator)

        return page

    # Property accessors for backward compatibility and audits
    @property
    def general_page(self): return self._get_or_create_page("General")
    @property
    def appearance_page(self): return self._get_or_create_page("Appearance")
    @property
    def storage_page(self): return self._get_or_create_page("Storage")
    @property
    def power_page(self): return self._get_or_create_page("Power")
    @property
    def display_page(self): return self._get_or_create_page("Display")
    @property
    def wifi_page(self): return self._get_or_create_page("Wi-Fi")
    @property
    def bluetooth_page(self): return self._get_or_create_page("Bluetooth")
    @property
    def network_page(self): return self._get_or_create_page("Network")
    @property
    def sound_page(self): return self._get_or_create_page("Sound")
    @property
    def notifications_page(self): return self._get_or_create_page("Notifications")
    @property
    def keyboard_page(self): return self._get_or_create_page("Keyboard")
    @property
    def mouse_page(self): return self._get_or_create_page("Mouse")
    @property
    def privacy_page(self): return self._get_or_create_page("Privacy & Security")
    @property
    def spotlight_page(self): return self._get_or_create_page("Echo Search")

    def _get_or_create_page(self, title: str) -> QWidget:
        # Normalize title alias
        norm_title = "Privacy & Security" if title == "Privacy" else title
        if norm_title not in self._pages:
            page = self._create_page(norm_title)
            self._pages[norm_title] = page
            self.content_stack.addWidget(page)
        return self._pages[norm_title]

    def check_theme(self, force_theme=None):
        if "Appearance" in self._pages:
            service = self._pages["Appearance"].service
        else:
            from services.appearance_service import AppearanceService
            service = AppearanceService()

        if force_theme and isinstance(force_theme, str):
            mode = force_theme
        else:
            mode = service.get_theme_mode()

        effective = service.get_effective_theme(mode)

        if effective != self.last_theme or force_theme is not None:
            # Only apply to system gsettings when the theme actually changes,
            # avoiding flooding GNOME/Mutter with settings-change events that cause
            # black screen flicker in PipeWire/GNOME screen recordings.
            service.apply_effective_theme(effective)
            # Create crossfade transition if this is not the initial load
            if self.last_theme is not None:
                self.start_theme_transition()
                
            self.last_theme = effective
            is_dark = (effective == "prefer-dark")
            ThemeManager.set_dark_mode(is_dark)
            
            style_name = "style_dark.qss" if is_dark else "style.qss"
            style_path = os.path.join(os.path.dirname(__file__), "styles", style_name)
            if os.path.exists(style_path):
                with open(style_path, "r", encoding="utf-8") as f:
                    QApplication.instance().setStyleSheet(f.read())
            
            # Request update for all widgets
            from theme.styler import fix_label_styles
            fix_label_styles(self)
            
            for w in self.findChildren(QWidget):
                w.update()

    def _on_system_info_changed(self, info: dict):
        """Called whenever system info changes (name, avatar, GPU, etc.)."""
        if "General" in self._pages:
            self._pages["General"].refresh_system_info(info)

    def start_theme_transition(self):
        # 1. Grab a snapshot of the current window before stylesheet changes
        pixmap = self.grab()
        
        # 2. Create the custom overlay which manages its own crossfade
        self.theme_overlay = ThemeTransitionOverlay(self.central_widget, pixmap)
        self.theme_overlay.show()
        self.theme_overlay.raise_()
        
        # 3. We don't start the animation yet, we must apply styles FIRST, 
        # but the animation will start immediately after check_theme finishes.
        QTimer.singleShot(10, self.theme_overlay.anim.start)

    def _navigate_from_shortcut(self, target_name):
        self.sidebar._on_item_clicked(target_name)

    def _on_language_changed(self, lang_code: str):
        """Dynamically retranslate the whole application when language is changed."""
        self.sidebar.retranslate_ui()
        current_page_title = getattr(self, "current_page_title", "General")
        for key, widget in list(self._pages.items()):
            self.content_stack.removeWidget(widget)
            widget.deleteLater()
        self._pages.clear()
        
        page = self._get_or_create_page(current_page_title)
        self.content_stack.setCurrentWidget(page)
        for item in self.sidebar.items:
            item.set_selected(item.category_key == current_page_title)

    def change_page(self, index, title):
        self.current_page_title = title
        page = self._get_or_create_page(title)
        
        # Reset nested subpages to root view when navigating from sidebar
        if hasattr(page, "reset_to_root"):
            try:
                page.reset_to_root()
            except Exception:
                pass
        elif isinstance(page, QStackedWidget):
            page.setCurrentIndex(0)
        elif hasattr(page, "stack") and isinstance(page.stack, QStackedWidget):
            page.stack.setCurrentIndex(0)
            
        self.content_stack.setCurrentWidget(page)
        for item in self.sidebar.items:
            item.set_selected(item.category_key == title)
            
        from PySide6.QtCore import QSettings
        settings = QSettings("TahoeSettings", "App")
        if settings.value("restore_page", False, type=bool):
            settings.setValue("last_page", title)

    def _on_search_result_selected(self, result):
        from services.search_service import SearchResult
        if not isinstance(result, SearchResult):
            return
            
        page_name = "Privacy & Security" if result.page in ("Privacy", "Privacy & Security") else result.page
        self.change_page(0, page_name)
        
        page = self._get_or_create_page(page_name)
        if not page:
            return
            
        # Locate concrete target widget
        target_widget = None
        if hasattr(page, "get_search_target"):
            try:
                target_widget = page.get_search_target(result.id)
            except Exception:
                target_widget = None
                
        if not target_widget:
            for child in page.findChildren(QWidget):
                if getattr(child, "_search_target_id", None) == result.id:
                    target_widget = child
                    break

        if not target_widget:
            for group in page.findChildren(QWidget):
                if hasattr(group, "title_lbl") and result.section.lower() in group.title_lbl.text().lower():
                    target_widget = group
                    break

        if target_widget:
            scroll_area = getattr(page, "scroll", None)
            if not scroll_area:
                from PySide6.QtWidgets import QScrollArea
                scroll_areas = page.findChildren(QScrollArea)
                if scroll_areas:
                    scroll_area = scroll_areas[0]

            if scroll_area:
                QTimer.singleShot(50, lambda sa=scroll_area, tw=target_widget: self._smooth_scroll_to_widget(sa, tw))

            from components.control_highlighter import ControlHighlighter
            QTimer.singleShot(220, lambda tw=target_widget: ControlHighlighter.pulse(tw))

    def _smooth_scroll_to_widget(self, scroll_area, target_widget):
        content_w = scroll_area.widget()
        if not content_w or not target_widget or not target_widget.isVisible():
            return
        try:
            top_left = target_widget.mapTo(content_w, QPoint(0, 0))
            target_y = max(0, top_left.y() - 35)
            
            vsb = scroll_area.verticalScrollBar()
            if vsb:
                from PySide6.QtCore import QPropertyAnimation, QEasingCurve
                anim = QPropertyAnimation(vsb, b"value", self)
                anim.setDuration(380)
                anim.setStartValue(vsb.value())
                anim.setEndValue(target_y)
                anim.setEasingCurve(QEasingCurve.OutCubic)
                anim.start()
                self._current_search_scroll_anim = anim
        except Exception:
            pass

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            wh = self.windowHandle()
            if wh:
                wh.startSystemMove()
                return
        super().mousePressEvent(event)



    def closeEvent(self, event):
        if hasattr(self, 'theme_timer'):
            self.theme_timer.stop()
        if hasattr(self, 'info_watcher'):
            self.info_watcher.stop()
        for page in self._pages.values():
            if hasattr(page, 'cleanup'):
                try:
                    page.cleanup()
                except Exception:
                    pass
        super().closeEvent(event)


def main():
    from PySide6.QtCore import QCoreApplication, QSettings
    from PySide6.QtGui import QFont, QGuiApplication
    
    # Set application metadata BEFORE QApplication
    QCoreApplication.setApplicationName("Echo_Settings")
    QCoreApplication.setOrganizationName("EchoOS")
    QCoreApplication.setOrganizationDomain("echo-os.org")
    QGuiApplication.setDesktopFileName("com.echo.settings")

    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Echo Settings")
    app.setQuitOnLastWindowClosed(True)
    
    icon_p = os.path.join(os.path.dirname(__file__), "icon.png")
    if not os.path.exists(icon_p):
        icon_p = os.path.join(os.path.dirname(__file__), "assets", "echo_icon.jpg")
    app.setWindowIcon(QIcon(icon_p))
    
    # Ensure installer module is available in sys.path
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(cur_dir)
    for p in (cur_dir, parent_dir, os.path.join(cur_dir, "installer"), os.path.join(parent_dir, "installer")):
        if os.path.exists(p) and p not in sys.path:
            sys.path.insert(0, p)
    
    from theme.typography import Typography
    
    f = QFont()
    f.setFamilies([family.strip().strip("'") for family in Typography.FONT_FAMILY.split(',')])
    f.setPixelSize(Typography.SIZE_BODY)
    app.setFont(f)
    
    settings = QSettings("EchoOS", "EchoSettings")
    raw_onboarding = settings.value("onboarding_completed", None)
    if raw_onboarding is None:
        onboarding_completed = False
    elif isinstance(raw_onboarding, bool):
        onboarding_completed = raw_onboarding
    elif isinstance(raw_onboarding, str):
        onboarding_completed = raw_onboarding.strip().lower() in ("true", "1", "yes")
    else:
        onboarding_completed = bool(raw_onboarding)

    force_onboarding = "--welcome" in sys.argv or "--onboarding" in sys.argv
    skip_onboarding = "--no-welcome" in sys.argv or "--skip-onboarding" in sys.argv
    
    if (not onboarding_completed or force_onboarding) and not skip_onboarding:
        try:
            from installer.main import EchoInstallerWindow
            
            holder = {}
            def on_onboarding_complete():
                settings.setValue("onboarding_completed", True)
                settings.sync()
                win = MainWindow()
                win.show()
                holder["main"] = win
            
            wizard = EchoInstallerWindow(on_complete=on_onboarding_complete, is_welcome_mode=True)
            wizard.show()
            holder["wizard"] = wizard
            sys.exit(app.exec())
        except Exception as e:
            print(f"Notice: Direct MainWindow fallback ({e})")
            
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

