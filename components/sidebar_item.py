from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen
from theme.metrics import MENU_ITEM_HEIGHT, MENU_ITEM_RADIUS
from theme.colors import Colors

class CategoryIconWidget(QWidget):
    def __init__(self, category: str, color_hex: str, parent=None):
        super().__init__(parent)
        self.category = category
        self.color_hex = color_hex
        self.setFixedSize(22, 22) # Slightly larger to match Tahoe

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Draw the colored rounded rect background
        p.setBrush(QColor(self.color_hex))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 6, 6)

        # Draw the specific white icon inside
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(Qt.white, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        cx, cy = self.width() / 2, self.height() / 2
        
        if self.category in ["Wi-Fi"]:
            p.drawArc(cx-6, cy-4, 12, 12, 45*16, 90*16)
            p.drawArc(cx-4, cy-2, 8, 8, 45*16, 90*16)
            p.drawArc(cx-2, cy, 4, 4, 45*16, 90*16)
            p.setBrush(Qt.white)
            p.drawEllipse(cx-1, cy+3, 2, 2)
            
        elif self.category in ["Bluetooth", "USB Devices"]:
            p.drawLine(cx, cy-5, cx, cy+5)
            p.drawLine(cx, cy-5, cx+4, cy-2)
            p.drawLine(cx+4, cy-2, cx-3, cy+3)
            p.drawLine(cx, cy+5, cx+4, cy+2)
            p.drawLine(cx+4, cy+2, cx-3, cy-3)
            
        elif self.category in ["Network"]:
            p.drawEllipse(cx-5, cy-5, 10, 10)
            p.drawEllipse(cx-2, cy-5, 4, 10)
            p.drawLine(cx-5, cy, cx+5, cy)
            
        elif self.category in ["General", "Hardware"]:
            p.setPen(QPen(Qt.white, 2.0))
            p.drawEllipse(cx-3, cy-3, 6, 6)
            p.setPen(QPen(Qt.white, 1.5))
            for i in range(8):
                p.save()
                p.translate(cx, cy)
                p.rotate(45 * i)
                p.drawLine(0, -3, 0, -5)
                p.restore()
                
        elif self.category in ["Appearance"]:
            p.drawArc(cx-4, cy-4, 8, 8, -45*16, 180*16)
            p.setBrush(Qt.white)
            p.drawChord(cx-4, cy-4, 8, 8, 135*16, 180*16)
            
        elif self.category in ["Display", "Graphics"]:
            p.drawRoundedRect(cx-6, cy-5, 12, 8, 1, 1)
            p.drawLine(cx-3, cy+5, cx+3, cy+5)
            p.drawLine(cx, cy+3, cx, cy+5)
            
        elif self.category in ["Storage"]:
            p.drawRoundedRect(cx-5, cy-6, 10, 12, 2, 2)
            p.drawEllipse(cx-3, cy-3, 6, 6)
            
        elif self.category in ["Power"]:
            p.drawRoundedRect(cx-6, cy-4, 10, 8, 1, 1)
            p.drawRect(cx+4, cy-2, 2, 4)
            p.setBrush(Qt.white)
            p.setPen(Qt.NoPen)
            p.drawRect(cx-4, cy-2, 4, 4)
            
        elif self.category in ["Sound"]:
            # Speaker body
            p.setBrush(Qt.white)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(cx-7, cy-3, 4, 6, 1, 1)
            speaker_path = QPainterPath()
            speaker_path.moveTo(cx-4, cy-3)
            speaker_path.lineTo(cx+1, cy-7)
            speaker_path.lineTo(cx+1, cy+7)
            speaker_path.lineTo(cx-4, cy+3)
            speaker_path.closeSubpath()
            p.drawPath(speaker_path)
            
            # Sound waves
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(Qt.white, 1.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawArc(cx-1, cy-3, 6, 6, -45*16, 90*16)
            p.drawArc(cx-3, cy-5, 10, 10, -45*16, 90*16)
            
        elif self.category in ["Keyboard"]:
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(Qt.white, 1.5))
            p.drawRoundedRect(cx-7, cy-4, 14, 9, 2, 2)
            p.setPen(Qt.NoPen)
            p.setBrush(Qt.white)
            p.drawRect(cx-4, cy-2, 2, 2)
            p.drawRect(cx-1, cy-2, 2, 2)
            p.drawRect(cx+2, cy-2, 2, 2)
            p.drawRect(cx-3, cy+1, 6, 2) # Spacebar
            
        elif self.category in ["Mouse"]:
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(Qt.white, 1.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawRoundedRect(cx-4.5, cy-6.5, 9, 13, 4.5, 4.5)
            p.drawLine(cx, cy-6.5, cx, cy-2)
            p.setBrush(Qt.white)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(cx-0.75, cy-4, 1.5, 3, 0.75, 0.75)
            
        elif self.category in ["Notifications"]:
            p.setPen(QPen(Qt.white, 1.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            p.drawArc(cx-3, cy-4, 6, 6, 0, 180*16)
            p.drawLine(cx-3, cy-1, cx-4, cy+2)
            p.drawLine(cx+3, cy-1, cx+4, cy+2)
            p.drawLine(cx-5, cy+2, cx+5, cy+2)
            p.setBrush(Qt.white)
            p.setPen(Qt.NoPen)
            p.drawEllipse(cx-1, cy+3, 2, 2)
            # small dot indicator for macOS notification bell
            p.setBrush(QColor("#FF3B30")) # Red dot
            p.drawEllipse(cx+2, cy-5, 3, 3)
            
        elif self.category in ["Echo Search", "Spotlight"]:
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(Qt.white, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawEllipse(cx-3, cy-3, 6, 6)
            p.drawLine(cx+1, cy+1, cx+4, cy+4)

        elif self.category in ["Privacy", "Privacy & Security"]:
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(Qt.white, 1.3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawArc(cx-3, cy-6, 6, 6, 0, 180*16)
            p.setBrush(Qt.white)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(cx-4.5, cy-2.5, 9, 7.5, 1.5, 1.5)
            p.setBrush(QColor(self.color_hex))
            p.drawEllipse(cx-1, cy-0.5, 2, 2)
            p.drawRect(cx-0.75, cy+1, 1.5, 1.8)


class SidebarItem(QWidget):
    clicked = Signal(str)

    def __init__(self, text, icon_color_hex="#8E8E93", category_key=None):
        super().__init__()
        self.category_key = category_key or text
        self.text = text
        self.icon_color = icon_color_hex
        self.setFixedHeight(MENU_ITEM_HEIGHT + 4) # Slightly taller for breathing room
        self.setCursor(Qt.PointingHandCursor)
        
        self.is_selected = False
        self.is_hovered = False
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(12)
        
        self.icon_widget = CategoryIconWidget(self.category_key, icon_color_hex)
        
        self.text_label = QLabel(self.text)
        
        self.layout.addWidget(self.icon_widget)
        self.layout.addWidget(self.text_label)
        self.layout.addStretch()
        
        from theme.manager import ThemeManager
        self.update_style()
        ThemeManager.theme_changed.connect(self.update_style)

    def set_text(self, text: str):
        self.text = text
        self.text_label.setText(text)
        
    def update_style(self, _is_dark=False):
        from theme.typography import Typography
        
        # Clear the stylesheet first to force Qt to register a change
        self.text_label.setStyleSheet("")
        
        if self.is_selected:
            self.text_label.setStyleSheet(f"background: transparent; color: {Colors.MENU_ITEM_TEXT_SELECTED}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_MEDIUM};")
        else:
            self.text_label.setStyleSheet(f"background: transparent; color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_BODY}px; font-weight: {Typography.WEIGHT_MEDIUM};")
            
        self.text_label.style().unpolish(self.text_label)
        self.text_label.style().polish(self.text_label)
        self.update()

    def set_selected(self, selected):
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
            self.clicked.emit(self.category_key)
            
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
