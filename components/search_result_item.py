from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen
from theme.colors import Colors
from theme.typography import Typography
from theme.metrics import MENU_ITEM_RADIUS
from theme.manager import ThemeManager
from components.sidebar_item import CategoryIconWidget
from services.search_service import SearchResult
from localization import t

class SearchResultItem(QWidget):
    """A sleek search result row item in the sidebar matching macOS Tahoe aesthetics."""
    clicked = Signal(object)

    def __init__(self, result: SearchResult, parent=None):
        super().__init__(parent)
        self.result = result
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.is_hovered = False
        self.is_selected = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Icon badge
        self.icon_widget = CategoryIconWidget(result.page, result.icon_color)
        layout.addWidget(self.icon_widget)

        # Text information (Title + Breadcrumb)
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)
        text_layout.setAlignment(Qt.AlignVCenter)

        self.title_lbl = QLabel(result.display_title)
        self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: {Typography.WEIGHT_MEDIUM}; background: transparent; border: none;")

        # Smart breadcrumb: avoid redundant repeating (e.g. "Wi-Fi › Wi-Fi" -> "Wi-Fi")
        sec = result.display_section.strip()
        pg = result.display_page.strip()
        tit = result.display_title.strip()
        if sec.lower() in (tit.lower(), pg.lower()):
            breadcrumb_text = pg
        else:
            breadcrumb_text = f"{pg} › {sec}"

        self.breadcrumb_lbl = QLabel(breadcrumb_text)
        self.breadcrumb_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; background: transparent; border: none;")

        text_layout.addWidget(self.title_lbl)
        text_layout.addWidget(self.breadcrumb_lbl)
        layout.addLayout(text_layout, 1)

        ThemeManager.theme_changed.connect(self.update_style)

    def update_style(self, _is_dark=False):
        if self.is_selected:
            self.title_lbl.setStyleSheet(f"color: {Colors.MENU_ITEM_TEXT_SELECTED}; font-size: 13px; font-weight: {Typography.WEIGHT_MEDIUM}; background: transparent; border: none;")
            self.breadcrumb_lbl.setStyleSheet(f"color: rgba(255, 255, 255, 0.8); font-size: 11px; background: transparent; border: none;")
        else:
            self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: {Typography.WEIGHT_MEDIUM}; background: transparent; border: none;")
            self.breadcrumb_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; background: transparent; border: none;")
        self.update()

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.update_style()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.result)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.is_selected:
            painter.setBrush(QColor(Colors.MENU_ITEM_SELECTED))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect(), MENU_ITEM_RADIUS, MENU_ITEM_RADIUS)
        elif self.is_hovered:
            c_str = Colors.MENU_ITEM_HOVER
            if c_str.startswith("rgba"):
                parts = c_str.replace("rgba(", "").replace(")", "").split(",")
                painter.setBrush(QColor(int(parts[0]), int(parts[1]), int(parts[2]), int(float(parts[3]) * 255)))
            else:
                painter.setBrush(QColor(c_str))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect(), MENU_ITEM_RADIUS, MENU_ITEM_RADIUS)


class SearchEmptyState(QWidget):
    """A clean empty state when no search results match."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 40, 15, 20)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignCenter)

        # Subtle search icon badge
        self.icon_badge = QLabel()
        self.icon_badge.setFixedSize(44, 44)
        self.icon_badge.setAlignment(Qt.AlignCenter)
        
        self.title_lbl = QLabel(t("search.no_results", "No Results Found"))
        self.title_lbl.setAlignment(Qt.AlignCenter)
        self.title_lbl.setWordWrap(True)

        self.sub_lbl = QLabel(t("search.no_results_sub", "Check spelling or try a different keyword"))
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        self.sub_lbl.setWordWrap(True)

        self.layout.addWidget(self.icon_badge, 0, Qt.AlignCenter)
        self.layout.addWidget(self.title_lbl)
        self.layout.addWidget(self.sub_lbl)

        ThemeManager.theme_changed.connect(self.update_style)
        self.update_style()

    def update_style(self, _is_dark=False):
        is_dark = ThemeManager.is_dark
        badge_bg = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.05)"
        icon_color = "rgba(255, 255, 255, 0.4)" if is_dark else "rgba(0, 0, 0, 0.35)"
        
        self.icon_badge.setStyleSheet(f"background: {badge_bg}; border-radius: 22px; color: {icon_color}; font-size: 20px; font-weight: bold;")
        self.icon_badge.setText("⌕")
        
        self.title_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; font-weight: {Typography.WEIGHT_SEMIBOLD}; background: transparent;")
        self.sub_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; background: transparent; line-height: 1.3;")
        self.title_lbl.setText(t("search.no_results", "No Results Found"))
        self.sub_lbl.setText(t("search.no_results_sub", "Check spelling or try a different keyword"))
