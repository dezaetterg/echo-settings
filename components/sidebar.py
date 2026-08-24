from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QLineEdit, QLabel
)
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen

from theme.metrics import SIDEBAR_WIDTH
from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from components.sidebar_item import SidebarItem

class SystemWindowButton(QPushButton):
    def __init__(self, role: str = "close", parent=None):
        super().__init__(parent)
        self.role = role
        self.setFixedSize(14, 14)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.is_hovered = False

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        cx = rect.center().x()
        cy = rect.center().y()
        r = 6.0

        if self.role == "close":
            base_col = QColor("#FF5F56")
            glyph = "×"
            glyph_col = QColor("#4D0000")
        elif self.role == "minimize":
            base_col = QColor("#FFBD2E")
            glyph = "−"
            glyph_col = QColor("#5A4000")
        else: # maximize
            base_col = QColor("#27C93F")
            glyph = "+"
            glyph_col = QColor("#004A00")

        p.setBrush(base_col)
        p.setPen(QPen(QColor(0, 0, 0, 40), 0.5))
        p.drawEllipse(QPoint(int(cx), int(cy)), int(r), int(r))

        if self.is_hovered:
            p.setPen(glyph_col)
            f = p.font()
            f.setPixelSize(10)
            f.setBold(True)
            p.setFont(f)
            p.drawText(rect, Qt.AlignCenter, glyph)
        p.end()

class SidebarSectionHeader(QLabel):

    """Subtle uppercase section header for grouped sidebar items."""
    def __init__(self, text: str, is_first: bool = False, parent=None):
        super().__init__(text, parent)
        self.is_first = is_first
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def update_style(self, _is_dark=False):
        top_pad = 4 if self.is_first else 14
        self.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: 11px;
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                letter-spacing: 0.5px;
                padding-left: 10px;
                padding-top: {top_pad}px;
                padding-bottom: 3px;
                background: transparent;
                border: none;
            }}
        """)

class SearchLineEdit(QLineEdit):
    down_pressed = Signal()
    up_pressed = Signal()
    return_pressed = Signal()
    escape_pressed = Signal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clear()
            self.clearFocus()
            self.escape_pressed.emit()
            return
        elif event.key() == Qt.Key_Down:
            self.down_pressed.emit()
            return
        elif event.key() == Qt.Key_Up:
            self.up_pressed.emit()
            return
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.return_pressed.emit()
            return
        super().keyPressEvent(event)


class Sidebar(QWidget):
    page_changed = Signal(int, str)
    search_result_selected = Signal(object)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(SIDEBAR_WIDTH)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # System Window Controls (directly embedded, no titlebar row)
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(4, 2, 4, 4)
        controls_layout.setSpacing(8)

        self.btn_close = SystemWindowButton("close")
        self.btn_minimize = SystemWindowButton("minimize")
        self.btn_maximize = SystemWindowButton("maximize")

        controls_layout.addWidget(self.btn_close)
        controls_layout.addWidget(self.btn_minimize)
        controls_layout.addWidget(self.btn_maximize)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)
        
        # Search Box
        from localization import t
        self.search_box = SearchLineEdit()
        self.search_box.setPlaceholderText(t("search.placeholder", "Search"))
        self.search_box.textChanged.connect(self._on_search_text_changed)
        self.search_box.down_pressed.connect(self._select_next_result)
        self.search_box.up_pressed.connect(self._select_prev_result)
        self.search_box.return_pressed.connect(self._activate_selected_result)
        main_layout.addWidget(self.search_box)
        
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)
        
        from services.search_service import SearchService, SearchResult
        from components.search_result_item import SearchResultItem, SearchEmptyState
        self.search_service = SearchService()
        self._current_search_results: list[SearchResult] = []
        self._search_result_items: list[SearchResultItem] = []
        self._selected_result_idx = -1
        
        # Scroll Area for menu & search results
        self.scroll = QScrollArea()
        self.scroll.setObjectName("SidebarScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("""
            QScrollArea#SidebarScroll {
                border: none;
                background: transparent;
            }
            QScrollArea#SidebarScroll QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 0px;
                margin: 0px;
            }
            QScrollArea#SidebarScroll QScrollBar::handle:vertical,
            QScrollArea#SidebarScroll QScrollBar::add-line:vertical,
            QScrollArea#SidebarScroll QScrollBar::sub-line:vertical,
            QScrollArea#SidebarScroll QScrollBar::add-page:vertical,
            QScrollArea#SidebarScroll QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
                height: 0px;
            }
        """)
        self.scroll.viewport().setStyleSheet("background: transparent;")
        
        # Stacked container for menu vs search results
        from PySide6.QtWidgets import QStackedWidget
        self.sidebar_stack = QStackedWidget()
        self.sidebar_stack.setStyleSheet("background: transparent;")
        
        # Container for regular menu
        self.menu_container = QWidget()
        self.menu_container.setStyleSheet("background: transparent;")
        self.menu_layout = QVBoxLayout(self.menu_container)
        self.menu_layout.setContentsMargins(0, 0, 0, 10)
        self.menu_layout.setSpacing(2)
        self.menu_layout.setAlignment(Qt.AlignTop)
        
        # Container for search results
        self.results_container = QWidget()
        self.results_container.setStyleSheet("background: transparent;")
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 10)
        self.results_layout.setSpacing(3)
        self.results_layout.setAlignment(Qt.AlignTop)
        
        self.sidebar_stack.addWidget(self.menu_container)    # Index 0
        self.sidebar_stack.addWidget(self.results_container) # Index 1
        
        # Structured groups matching exact specification
        self.group_defs = [
            ("nav.connectivity", [
                ("Wi-Fi", "nav.wifi", "#007AFF"),
                ("Bluetooth", "nav.bluetooth", "#007AFF"),
                ("Network", "nav.network", "#007AFF"),
            ]),
            ("nav.interaction", [
                ("Sound", "nav.sound", "#FF2D55"),
                ("Notifications", "nav.notifications", "#FF3B30"),
                ("Keyboard", "nav.keyboard", "#8E8E93"),
                ("Mouse", "nav.mouse", "#8E8E93"),
            ]),
            ("nav.privacy_section", [
                ("Privacy & Security", "nav.privacy", "#007AFF"),
            ]),
            ("nav.customization", [
                ("General", "nav.general", "#8E8E93"),
                ("Appearance", "nav.appearance", "#AF52DE"),
                ("Display", "nav.display", "#32ADE6"),
            ]),
            ("nav.storage_power", [
                ("Storage", "nav.storage", "#8E8E93"),
                ("Power", "nav.power", "#4CD964"),
            ]),
            ("nav.system", [
                ("Echo Search", "nav.search", "#FF9500"),
            ]),
        ]

        self.items = []
        self.group_map = {}  # SidebarSectionHeader -> list of SidebarItem
        self.headers = []    # list of (SidebarSectionHeader, key)
        self.item_key_map = {} # SidebarItem -> key

        from localization import i18n

        for g_idx, (group_key, item_defs) in enumerate(self.group_defs):
            hdr = SidebarSectionHeader(t(group_key), is_first=(g_idx == 0))
            self.menu_layout.addWidget(hdr)
            self.headers.append((hdr, group_key))
            group_items = []
            
            for key, t_key, color in item_defs:
                item = SidebarItem(t(t_key), color, category_key=key)
                item.clicked.connect(self._on_item_clicked)
                self.menu_layout.addWidget(item)
                self.items.append(item)
                group_items.append(item)
                self.item_key_map[item] = t_key
                
            self.group_map[hdr] = group_items
        
        self.scroll.setWidget(self.sidebar_stack)
        main_layout.addWidget(self.scroll)

        i18n.language_changed.connect(self.retranslate_ui)
        
        # Default selection
        if self.items:
            self._on_item_clicked(self.items[0].category_key)
            
    def _on_search_text_changed(self, text: str):
        query = text.strip()
        from components.search_result_item import SearchResultItem, SearchEmptyState
        
        if not query:
            self.sidebar_stack.setCurrentIndex(0)
            self._current_search_results.clear()
            self._search_result_items.clear()
            self._selected_result_idx = -1
            return
            
        # Switch stack view to results container
        self.sidebar_stack.setCurrentIndex(1)
        
        # Clear previous result widgets
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self._current_search_results = self.search_service.search(query)
        self._search_result_items.clear()
        self._selected_result_idx = -1
        
        if not self._current_search_results:
            empty_state = SearchEmptyState()
            self.results_layout.addWidget(empty_state)
        else:
            for idx, res in enumerate(self._current_search_results[:12]):
                item_widget = SearchResultItem(res)
                item_widget.clicked.connect(self._on_search_result_clicked)
                self.results_layout.addWidget(item_widget)
                self._search_result_items.append(item_widget)
                
            # Default highlight top result
            if self._search_result_items:
                self._selected_result_idx = 0
                self._search_result_items[0].set_selected(True)

    def _select_next_result(self):
        if not self._search_result_items:
            return
        if self._selected_result_idx >= 0:
            self._search_result_items[self._selected_result_idx].set_selected(False)
        self._selected_result_idx = (self._selected_result_idx + 1) % len(self._search_result_items)
        self._search_result_items[self._selected_result_idx].set_selected(True)
        self.scroll.ensureWidgetVisible(self._search_result_items[self._selected_result_idx])

    def _select_prev_result(self):
        if not self._search_result_items:
            return
        if self._selected_result_idx >= 0:
            self._search_result_items[self._selected_result_idx].set_selected(False)
        self._selected_result_idx = (self._selected_result_idx - 1) % len(self._search_result_items)
        self._search_result_items[self._selected_result_idx].set_selected(True)
        self.scroll.ensureWidgetVisible(self._search_result_items[self._selected_result_idx])

    def _activate_selected_result(self):
        if self._search_result_items and 0 <= self._selected_result_idx < len(self._search_result_items):
            res = self._current_search_results[self._selected_result_idx]
            self._on_search_result_clicked(res)

    def _on_search_result_clicked(self, result):
        self.search_result_selected.emit(result)

    def retranslate_ui(self, _lang=None):
        from localization import t
        self.search_box.setPlaceholderText(t("search.placeholder", "Search"))
        for hdr, key in self.headers:
            hdr.setText(t(key))
        for item, key in self.item_key_map.items():
            item.set_text(t(key))
        if self.search_box.text().strip():
            self._on_search_text_changed(self.search_box.text())

    def update_style(self, _is_dark=False):
        self.search_box.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.SEARCH_BG};
                border: 2px solid transparent;
                border-radius: 6px;
                padding: 4px 8px;
                color: {Colors.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border: 2px solid {Colors.SEARCH_BORDER_FOCUS};
                background-color: {Colors.WINDOW_BG};
            }}
        """)
        
    def _on_item_clicked(self, category_key):
        for idx, item in enumerate(self.items):
            if item.category_key == category_key:
                item.set_selected(True)
                self.page_changed.emit(idx, category_key)
            else:
                item.set_selected(False)
