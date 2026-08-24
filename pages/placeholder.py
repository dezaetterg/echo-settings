from theme.typography import Typography
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class PlaceholderPage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.label = QLabel("Раздел в разработке")
        self.label.setStyleSheet("color: #8E8E93; font-size: {Typography.SIZE_TITLE}px; font-weight: {Typography.WEIGHT_SEMIBOLD};")
        self.label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.label)
