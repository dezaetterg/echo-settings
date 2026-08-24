from PySide6.QtWidgets import QComboBox, QAbstractItemView, QListView
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QFont, QPen
from theme.colors import Colors
from theme.manager import ThemeManager
from theme.typography import Typography

class PopupButton(QComboBox):
    valueChanged = Signal(object) # Emits the selected ID

    def __init__(self, options: dict, active_id):
        """
        options: { id: label }
        """
        super().__init__()
        self.options = options
        self.active_id = active_id
        
        self.setFixedHeight(32)
        self.setMinimumWidth(160)
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        
        # Wayland fix: Set QListView with parent and limit visible items
        self.setView(QListView(self))
        self.setMaxVisibleItems(8)
        
        from PySide6.QtCore import QSize
        self.setIconSize(QSize(16, 16))
        
        # Add items
        for opt_id, item in self.options.items():
            if isinstance(item, dict):
                label = item.get("label", str(opt_id))
                icon_name = item.get("icon")
                if icon_name:
                    from PySide6.QtGui import QIcon
                    icon = QIcon.fromTheme(icon_name)
                    if icon.isNull():
                        icon = QIcon.fromTheme(icon_name.replace("-symbolic", ""))
                    self.addItem(icon, label, userData=opt_id)
                else:
                    self.addItem(label, userData=opt_id)
            elif isinstance(item, tuple):
                from PySide6.QtGui import QIcon
                self.addItem(QIcon.fromTheme(item[1]), item[0], userData=opt_id)
            else:
                self.addItem(str(item), userData=opt_id)
            
        self.set_active_id(active_id)
        self.currentIndexChanged.connect(self._on_index_changed)
        
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def wheelEvent(self, event):
        # Ignore wheel event to prevent accidental scrolling
        event.ignore()

    def update_style(self, _is_dark=False):
        # Dynamic theme colors
        is_dark = ThemeManager.is_dark
        bg_color = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.04)"
        border_color = "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(0, 0, 0, 0.1)"
        text_color = "#FFFFFF" if is_dark else "#000000"
        
        popup_bg = "#2C2C2E" if is_dark else "#FFFFFF"
        popup_border = "rgba(255, 255, 255, 0.15)" if is_dark else "rgba(0, 0, 0, 0.15)"
        
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 4px 10px;
                min-width: 160px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none; /* Handled by paintEvent or left blank for clean look */
            }}
            QComboBox QAbstractItemView {{
                background-color: {popup_bg};
                color: {text_color};
                border: 1px solid {popup_border};
                border-radius: 8px;
                padding: 4px;
                outline: none;
                selection-background-color: #007AFF;
                selection-color: #FFFFFF;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 28px;
                border-radius: 4px;
                padding-left: 8px;
            }}
            QComboBox QAbstractItemView::item:hover,
            QComboBox QAbstractItemView::item:selected {{
                background-color: #007AFF;
                color: #FFFFFF;
            }}
        """)
        self.update()

    def _on_index_changed(self, index):
        self.active_id = self.itemData(index)
        self.valueChanged.emit(self.active_id)
        self.update()

    def set_active_id(self, new_id):
        idx = self.findData(new_id)
        if idx >= 0:
            self.setCurrentIndex(idx)
            self.active_id = new_id
            self.update()

    def update_options(self, options: dict, active_id=None):
        """Update options list while preserving selection."""
        cur_id = active_id if active_id is not None else self.active_id
        self.blockSignals(True)
        self.clear()
        self.options = options
        for opt_id, item in self.options.items():
            if isinstance(item, dict):
                label = item.get("label", str(opt_id))
                icon_name = item.get("icon")
                if icon_name:
                    from PySide6.QtGui import QIcon
                    icon = QIcon.fromTheme(icon_name)
                    if icon.isNull():
                        icon = QIcon.fromTheme(icon_name.replace("-symbolic", ""))
                    self.addItem(icon, label, userData=opt_id)
                else:
                    self.addItem(label, userData=opt_id)
            elif isinstance(item, tuple):
                from PySide6.QtGui import QIcon
                self.addItem(QIcon.fromTheme(item[1]), item[0], userData=opt_id)
            else:
                self.addItem(str(item), userData=opt_id)
        self.set_active_id(cur_id)
        self.blockSignals(False)
        self.update()

    def set_options(self, options: dict, active_id=None):
        self.update_options(options, active_id)

    def set_value(self, new_id):
        self.set_active_id(new_id)



