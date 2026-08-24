from PySide6.QtWidgets import QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QWheelEvent

class HorizontalWheelScrollArea(QScrollArea):
    """
    A QScrollArea that translates vertical mouse wheel scrolling into horizontal scrolling.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setStyleSheet("border: none; background: transparent;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def wheelEvent(self, event: QWheelEvent):
        # Translate vertical scroll to horizontal scroll
        delta = event.angleDelta().y()
        # Also check x just in case it's a horizontal scrolling mouse/trackpad
        delta_x = event.angleDelta().x()
        
        scroll_bar = self.horizontalScrollBar()
        
        if delta != 0:
            # y delta usually scrolls vertically, let's map to horizontal
            new_value = scroll_bar.value() - delta
            scroll_bar.setValue(new_value)
            event.accept()
        elif delta_x != 0:
            new_value = scroll_bar.value() - delta_x
            scroll_bar.setValue(new_value)
            event.accept()
        else:
            super().wheelEvent(event)
