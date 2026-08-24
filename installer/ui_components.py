"""
macOS 26 Liquid Glass UI Component Suite for Echo Settings Installer.
Delivers ultra-premium 3D liquid glass cursive typography (like macOS hello screen),
Cupertino interactive language selector cards with pixel-perfect contrast,
and native macOS styling.
"""

import sys
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGraphicsOpacityEffect, QScrollArea, QLineEdit, QTextEdit, QApplication
)
from PySide6.QtCore import (
    Qt, Signal, Property, QPoint, QPointF, QRectF, QTimer, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup
)
from PySide6.QtGui import (
    QPainter, QColor, QPainterPath, QLinearGradient, QRadialGradient, QFont, QPen,
    QPixmap, QImage, QCursor, QFontMetrics, QFontDatabase, QPolygonF
)




from theme.colors import Colors

_FONTS_LOADED = False

def ensure_installer_fonts():
    global _FONTS_LOADED
    if _FONTS_LOADED:
        return
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")
    if os.path.exists(fonts_dir):
        for fname in os.listdir(fonts_dir):
            if fname.endswith((".ttf", ".otf")):
                try:
                    QFontDatabase.addApplicationFont(os.path.join(fonts_dir, fname))
                except Exception:
                    pass
    _FONTS_LOADED = True




# --- Theme & Palette Constants ---
class MacPalette:
    ACCENT_BLUE = "#007AFF"
    ACCENT_BLUE_HOVER = "#0062CC"
    ACCENT_BLUE_GLOW = "rgba(0, 122, 255, 0.35)"

    GLASS_DARK_BG = "#1E1E1E"
    GLASS_DARK_CARD = QColor(255, 255, 255, 16)
    GLASS_DARK_CARD_HOVER = QColor(255, 255, 255, 26)
    GLASS_DARK_CARD_SELECTED = QColor(0, 122, 255, 45)
    GLASS_DARK_BORDER = QColor(255, 255, 255, 28)
    GLASS_DARK_BORDER_HIGHLIGHT = QColor(255, 255, 255, 55)

    GLASS_LIGHT_BG = "#F5F5F7"
    GLASS_LIGHT_CARD = QColor(255, 255, 255, 220)
    GLASS_LIGHT_CARD_HOVER = QColor(255, 255, 255, 250)
    GLASS_LIGHT_CARD_SELECTED = QColor(0, 122, 255, 28)
    GLASS_LIGHT_BORDER = QColor(0, 0, 0, 20)
    GLASS_LIGHT_BORDER_HIGHLIGHT = QColor(255, 255, 255, 200)

    # Solid colors for crisp text rendering
    TEXT_DARK_PRIMARY = QColor(255, 255, 255)
    TEXT_DARK_SECONDARY = QColor(255, 255, 255, 175)
    TEXT_DARK_TERTIARY = QColor(255, 255, 255, 110)

    TEXT_LIGHT_PRIMARY = QColor(29, 29, 31)
    TEXT_LIGHT_SECONDARY = QColor(0, 0, 0, 150)
    TEXT_LIGHT_TERTIARY = QColor(0, 0, 0, 100)


# --- System Window Control Buttons (Directly embedded, without separate titlebar) ---
class SystemWindowButton(QPushButton):
    def __init__(self, role: str = "close", is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.role = role
        self.is_dark = is_dark
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

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

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


class SystemWindowControls(QWidget):
    close_clicked = Signal()
    minimize_clicked = Signal()
    maximize_clicked = Signal()

    def __init__(self, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setFixedHeight(24)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.btn_close = SystemWindowButton("close", is_dark=self.is_dark)
        self.btn_close.clicked.connect(self.close_clicked.emit)

        self.btn_minimize = SystemWindowButton("minimize", is_dark=self.is_dark)
        self.btn_minimize.clicked.connect(self.minimize_clicked.emit)

        self.btn_maximize = SystemWindowButton("maximize", is_dark=self.is_dark)
        self.btn_maximize.clicked.connect(self.maximize_clicked.emit)

        layout.addWidget(self.btn_close)
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_maximize)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.btn_close.set_dark(is_dark)
        self.btn_minimize.set_dark(is_dark)
        self.btn_maximize.set_dark(is_dark)


# --- 3D Liquid Glass Cursive Typography (Frameless, exactly matching Apple's Hello screen) ---
class LiquidGlassScriptTypography(QWidget):

    """
    Renders floating 3D Liquid Glass cursive lettering (like Apple's macOS Hello screen)
    with multi-pass glass tube shaders, specular curve reflections, inner fluid refraction,
    and soft ambient glow. Cycles smoothly through supported languages.
    """
    def __init__(self, is_dark: bool = True, parent=None):
        super().__init__(parent)
        ensure_installer_fonts()
        self.is_dark = is_dark
        self.setFixedHeight(110)

        self.setMinimumWidth(400)

        # Cursive greeting words across 13 supported languages
        self.greetings = [
            ("en", "hello"),
            ("ru", "привет"),
            ("es", "hola"),
            ("fr", "bonjour"),
            ("de", "hallo"),
            ("it", "ciao"),
            ("pt_BR", "olá"),
            ("tr", "merhaba"),
            ("uk", "привіт"),
            ("kk", "сәлем"),
            ("ar", "مرحباً"),
            ("zh_CN", "你好"),
            ("ja", "ようこそ")
        ]
        self.current_idx = 0
        self._opacity = 1.0
        self._offset_y = 0.0

        # Cycle Timer
        self.cycle_timer = QTimer(self)
        self.cycle_timer.setInterval(2400)
        self.cycle_timer.timeout.connect(self._start_transition)
        self.cycle_timer.start()

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    @Property(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, val):
        self._opacity = val
        self.update()

    @Property(float)
    def offset_y(self):
        return self._offset_y

    @offset_y.setter
    def offset_y(self, val):
        self._offset_y = val
        self.update()

    def _start_transition(self):
        self.anim_out_o = QPropertyAnimation(self, b"opacity")
        self.anim_out_o.setDuration(260)
        self.anim_out_o.setStartValue(1.0)
        self.anim_out_o.setEndValue(0.0)
        self.anim_out_o.setEasingCurve(QEasingCurve.InCubic)

        self.anim_out_y = QPropertyAnimation(self, b"offset_y")
        self.anim_out_y.setDuration(260)
        self.anim_out_y.setStartValue(0.0)
        self.anim_out_y.setEndValue(-8.0)
        self.anim_out_y.setEasingCurve(QEasingCurve.InCubic)

        self.group_out = QParallelAnimationGroup(self)
        self.group_out.addAnimation(self.anim_out_o)
        self.group_out.addAnimation(self.anim_out_y)
        self.group_out.finished.connect(self._swap_and_fade_in)
        self.group_out.start()

    def _swap_and_fade_in(self):
        self.current_idx = (self.current_idx + 1) % len(self.greetings)
        self._offset_y = 10.0

        self.anim_in_o = QPropertyAnimation(self, b"opacity")
        self.anim_in_o.setDuration(340)
        self.anim_in_o.setStartValue(0.0)
        self.anim_in_o.setEndValue(1.0)
        self.anim_in_o.setEasingCurve(QEasingCurve.OutCubic)

        self.anim_in_y = QPropertyAnimation(self, b"offset_y")
        self.anim_in_y.setDuration(340)
        self.anim_in_y.setStartValue(10.0)
        self.anim_in_y.setEndValue(0.0)
        self.anim_in_y.setEasingCurve(QEasingCurve.OutCubic)

        self.group_in = QParallelAnimationGroup(self)
        self.group_in.addAnimation(self.anim_in_o)
        self.group_in.addAnimation(self.anim_in_y)
        self.group_in.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)

        p.setOpacity(self._opacity)

        text = self.greetings[self.current_idx][1]
        
        # Font selection: Pacifico for cursive script, fallback for CJK/Arabic
        font = QFont("Pacifico", 66)
        if not font.exactMatch():
            font = QFont("Dancing Script", 66)
            if not font.exactMatch():
                font = QFont("SF Pro Display", 60)
                font.setBold(True)

        fm = QFontMetrics(font)
        tw = fm.horizontalAdvance(text)
        th = fm.ascent()

        cx = self.width() / 2.0
        cy = self.height() / 2.0 + self._offset_y
        x = cx - tw / 2.0
        y = cy + th / 2.0 - 8

        path = QPainterPath()
        path.addText(x, y, font, text)

        # ── 1. Soft Ambient Cyan Glow ──
        p.setPen(QPen(QColor(0, 160, 255, 45), 14, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(path)

        p.setPen(QPen(QColor(0, 195, 255, 75), 8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(path)

        # ── 2. 3D Glass Tube Body (Vibrant Liquid Gradient Stroke) ──
        grad_tube = QLinearGradient(x, y - th, x, y)
        grad_tube.setColorAt(0.0, QColor(120, 220, 255, 245))  # Top azure light
        grad_tube.setColorAt(0.25, QColor(0, 165, 255, 235))  # Mid brilliant cyan
        grad_tube.setColorAt(0.70, QColor(0, 115, 240, 245))  # Deep saturated blue
        grad_tube.setColorAt(1.0, QColor(0, 65, 195, 255))    # Bottom curvature shadow
        p.setPen(QPen(grad_tube, 6.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(path)

        # ── 3. Translucent Inner Fluid Refractive Core Fill ──
        fill_grad = QLinearGradient(x, y - th, x, y)
        fill_grad.setColorAt(0.0, QColor(150, 230, 255, 170))
        fill_grad.setColorAt(0.5, QColor(0, 145, 255, 120))
        fill_grad.setColorAt(1.0, QColor(0, 85, 215, 185))
        p.fillPath(path, fill_grad)

        # ── 4. Top White/Cyan Specular Arc (Glass tube curvature highlight) ──
        spec_path = QPainterPath()
        spec_path.addText(x - 0.8, y - 1.2, font, text)
        spec_grad = QLinearGradient(x, y - th, x, y)
        spec_grad.setColorAt(0.0, QColor(255, 255, 255, 250))
        spec_grad.setColorAt(0.25, QColor(220, 250, 255, 180))
        spec_grad.setColorAt(0.55, QColor(140, 225, 255, 45))
        spec_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setPen(QPen(spec_grad, 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(spec_path)

        # ── 5. Fine Inner Core Light Shimmer ──
        inner_spec = QPainterPath()
        inner_spec.addText(x + 0.3, y + 0.4, font, text)
        inner_grad = QLinearGradient(x, y - th, x, y)
        inner_grad.setColorAt(0.0, QColor(255, 255, 255, 130))
        inner_grad.setColorAt(0.5, QColor(190, 240, 255, 70))
        inner_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setPen(QPen(inner_grad, 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(inner_spec)

        p.end()


# --- macOS Glass Card ---
class MacGlassCard(QFrame):
    def __init__(self, is_dark: bool = True, corner_radius: int = 14, enable_hover: bool = False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.corner_radius = corner_radius
        self.enable_hover = enable_hover
        self.setAttribute(Qt.WA_Hover, enable_hover)
        self.is_hovered = False

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def enterEvent(self, event):
        if self.enable_hover:
            self.is_hovered = True
            self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.enable_hover:
            self.is_hovered = False
            self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), self.corner_radius, self.corner_radius)

        if self.is_dark:
            fill_color = MacPalette.GLASS_DARK_CARD_HOVER if (self.enable_hover and self.is_hovered) else MacPalette.GLASS_DARK_CARD
            border_color = MacPalette.GLASS_DARK_BORDER_HIGHLIGHT if (self.enable_hover and self.is_hovered) else MacPalette.GLASS_DARK_BORDER
        else:
            fill_color = MacPalette.GLASS_LIGHT_CARD_HOVER if (self.enable_hover and self.is_hovered) else MacPalette.GLASS_LIGHT_CARD
            border_color = MacPalette.GLASS_LIGHT_BORDER_HIGHLIGHT if (self.enable_hover and self.is_hovered) else MacPalette.GLASS_LIGHT_BORDER

        p.fillPath(path, fill_color)

        # Specular gradient stroke
        grad = QLinearGradient(0, 0, 0, rect.height())
        if self.is_dark:
            grad.setColorAt(0.0, QColor(255, 255, 255, 60))
            grad.setColorAt(0.4, border_color)
            grad.setColorAt(1.0, QColor(255, 255, 255, 15))
        else:
            grad.setColorAt(0.0, QColor(255, 255, 255, 240))
            grad.setColorAt(0.4, border_color)
            grad.setColorAt(1.0, QColor(0, 0, 0, 15))

        p.setPen(QPen(grad, 1.0))
        p.drawPath(path)
        p.end()


# --- 3D Liquid Glass Globe Icon (macOS Setup Assistant Hero Emblem) ---
class LiquidGlassGlobeIcon(QWidget):
    """
    Renders an Apple-inspired 3D translucent liquid glass globe emblem
    with spherical refraction, cyan-blue iridescent core, specular arc, and glowing grid lines.
    """
    def __init__(self, size: int = 76, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.is_dark = is_dark

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0
        r = min(w, h) / 2.0 - 6.0

        # 1. Outer Cyan Ambient Glow
        glow_grad = QRadialGradient(cx, cy, r + 6)
        glow_grad.setColorAt(0.6, QColor(0, 160, 255, 55))
        glow_grad.setColorAt(1.0, QColor(0, 160, 255, 0))
        p.setBrush(glow_grad)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(int(cx), int(cy)), int(r + 6), int(r + 6))

        # 2. Spherical Fluid Core (Vibrant Blue/Cyan Glass Gradient)
        core_grad = QLinearGradient(cx - r, cy - r, cx + r, cy + r)
        core_grad.setColorAt(0.0, QColor(110, 225, 255, 245))
        core_grad.setColorAt(0.35, QColor(0, 155, 255, 235))
        core_grad.setColorAt(0.75, QColor(0, 105, 240, 240))
        core_grad.setColorAt(1.0, QColor(0, 55, 185, 250))
        p.setBrush(core_grad)
        p.setPen(QPen(QColor(255, 255, 255, 130), 1.2))
        p.drawEllipse(QPoint(int(cx), int(cy)), int(r), int(r))

        # 3. Delicate Liquid Glass Latitude/Longitude Grid Lines
        p.setBrush(Qt.NoBrush)
        grid_pen = QPen(QColor(255, 255, 255, 80), 1.2)
        p.setPen(grid_pen)
        # Equator line
        p.drawLine(int(cx - r + 3), int(cy), int(cx + r - 3), int(cy))
        # Longitude ellipse
        p.drawEllipse(QRectF(cx - r * 0.45, cy - r + 2, r * 0.9, (r - 2) * 2))
        # Latitude arcs
        p.drawArc(QRectF(cx - r * 0.85, cy - r * 0.6, r * 1.7, r * 1.2), 0, 180 * 16)
        p.drawArc(QRectF(cx - r * 0.85, cy - r * 0.6, r * 1.7, r * 1.2), 180 * 16, 180 * 16)

        # 4. Top-Left White Glass Specular Highlight Arc
        spec_grad = QLinearGradient(cx - r, cy - r, cx, cy)
        spec_grad.setColorAt(0.0, QColor(255, 255, 255, 240))
        spec_grad.setColorAt(0.4, QColor(255, 255, 255, 110))
        spec_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(spec_grad)
        p.setPen(Qt.NoPen)
        spec_path = QPainterPath()
        spec_path.addEllipse(QRectF(cx - r * 0.75, cy - r * 0.8, r * 1.2, r * 0.7))
        p.drawPath(spec_path)

        p.end()


# --- Vector Flags Renderer (Authentic High-Definition Apple Flag Squircles) ---
def draw_vector_flag(p: QPainter, rect: QRectF, code: str):
    p.save()
    p.setRenderHint(QPainter.Antialiasing)
    
    path = QPainterPath()
    path.addRoundedRect(rect, 4.5, 4.5)
    p.setClipPath(path)
    
    w = rect.width()
    h = rect.height()
    x = rect.left()
    y = rect.top()
    
    if code == "ru":
        # Russia: White, Blue, Red
        p.fillRect(QRectF(x, y, w, h/3.0), QColor("#FFFFFF"))
        p.fillRect(QRectF(x, y + h/3.0, w, h/3.0), QColor("#0039A6"))
        p.fillRect(QRectF(x, y + 2*h/3.0, w, h/3.0), QColor("#D52B1E"))
    elif code == "en":
        # USA: Red/White stripes & Navy Canton with stars
        stripe_h = h / 7.0
        for i in range(7):
            col = QColor("#B22234") if i % 2 == 0 else QColor("#FFFFFF")
            p.fillRect(QRectF(x, y + i * stripe_h, w, stripe_h), col)
        canton_w = w * 0.45
        canton_h = h * (4.0 / 7.0)
        p.fillRect(QRectF(x, y, canton_w, canton_h), QColor("#3C3B6E"))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#FFFFFF"))
        for r_i in range(3):
            for c_i in range(3):
                p.drawEllipse(QPointF(x + 3.5 + c_i * (canton_w - 7)/2.0, y + 2.5 + r_i * (canton_h - 5)/2.0), 0.9, 0.9)
    elif code == "es":
        # Spain: Red, Gold (2x), Red
        p.fillRect(QRectF(x, y, w, h*0.25), QColor("#AA151B"))
        p.fillRect(QRectF(x, y + h*0.25, w, h*0.5), QColor("#F1BF00"))
        p.fillRect(QRectF(x, y + h*0.75, w, h*0.25), QColor("#AA151B"))
    elif code == "de":
        # Germany: Black, Red, Gold
        p.fillRect(QRectF(x, y, w, h/3.0), QColor("#1D1D1F"))
        p.fillRect(QRectF(x, y + h/3.0, w, h/3.0), QColor("#DD0000"))
        p.fillRect(QRectF(x, y + 2*h/3.0, w, h/3.0), QColor("#FFCE00"))
    elif code == "fr":
        # France: Blue, White, Red
        p.fillRect(QRectF(x, y, w/3.0, h), QColor("#002395"))
        p.fillRect(QRectF(x + w/3.0, y, w/3.0, h), QColor("#FFFFFF"))
        p.fillRect(QRectF(x + 2*w/3.0, y, w/3.0, h), QColor("#ED2939"))
    elif code == "zh_CN":
        # China: Red with golden 5-point star
        p.fillRect(rect, QColor("#DE2910"))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#FFDE00"))
        star_poly = QPolygonF([
            QPointF(x + w*0.28, y + h*0.22),
            QPointF(x + w*0.32, y + h*0.33),
            QPointF(x + w*0.42, y + h*0.33),
            QPointF(x + w*0.34, y + h*0.40),
            QPointF(x + w*0.37, y + h*0.52),
            QPointF(x + w*0.28, y + h*0.44),
            QPointF(x + w*0.19, y + h*0.52),
            QPointF(x + w*0.22, y + h*0.40),
            QPointF(x + w*0.14, y + h*0.33),
            QPointF(x + w*0.24, y + h*0.33)
        ])
        p.drawPolygon(star_poly)
    elif code == "ja":
        # Japan: Pure White with Crimson Sun Disc
        p.fillRect(rect, QColor("#FFFFFF"))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#BC002D"))
        p.drawEllipse(QPointF(x + w/2.0, y + h/2.0), h*0.30, h*0.30)
    elif code == "it":
        # Italy: Green, White, Red
        p.fillRect(QRectF(x, y, w/3.0, h), QColor("#008C45"))
        p.fillRect(QRectF(x + w/3.0, y, w/3.0, h), QColor("#FFFFFF"))
        p.fillRect(QRectF(x + 2*w/3.0, y, w/3.0, h), QColor("#CD212A"))
    elif code == "pt_BR":
        # Brazil: Green, Yellow Rhombus, Blue Circle
        p.fillRect(rect, QColor("#009739"))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#FEDD00"))
        poly = QPolygonF([
            QPointF(x + w/2.0, y + 2.5),
            QPointF(x + w - 3.5, y + h/2.0),
            QPointF(x + w/2.0, y + h - 2.5),
            QPointF(x + 3.5, y + h/2.0)
        ])
        p.drawPolygon(poly)
        p.setBrush(QColor("#002776"))
        p.drawEllipse(QPointF(x + w/2.0, y + h/2.0), 4.0, 4.0)
    elif code == "tr":
        # Turkey: Red with White Crescent & Star
        p.fillRect(rect, QColor("#E30A17"))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(QPointF(x + w*0.40, y + h/2.0), 4.6, 4.6)
        p.setBrush(QColor("#E30A17"))
        p.drawEllipse(QPointF(x + w*0.44, y + h/2.0), 3.7, 3.7)
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(QPointF(x + w*0.62, y + h/2.0), 1.8, 1.8)
    elif code == "uk":
        # Ukraine: Sky Blue & Golden Yellow
        p.fillRect(QRectF(x, y, w, h/2.0), QColor("#005BBB"))
        p.fillRect(QRectF(x, y + h/2.0, w, h/2.0), QColor("#FFD700"))
    elif code == "kk":
        # Kazakhstan: Sky Blue with Gold Sun Motif
        p.fillRect(rect, QColor("#00AFCA"))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#FEC50C"))
        p.drawEllipse(QPointF(x + w/2.0, y + h/2.0), 4.0, 4.0)
    elif code == "ar":
        # Arabic: Pan-Arab horizontal tricolor with Red Chevron
        p.fillRect(QRectF(x, y, w, h/3.0), QColor("#1D1D1F"))
        p.fillRect(QRectF(x, y + h/3.0, w, h/3.0), QColor("#FFFFFF"))
        p.fillRect(QRectF(x, y + 2*h/3.0, w, h/3.0), QColor("#007A3D"))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#D52B1E"))
        chev = QPolygonF([
            QPointF(x, y),
            QPointF(x + w*0.35, y + h/2.0),
            QPointF(x, y + h)
        ])
        p.drawPolygon(chev)
    else:
        p.fillRect(rect, QColor("#007AFF"))

    # Top-to-bottom glassy specular sheen overlay
    sheen = QLinearGradient(x, y, x, y + h)
    sheen.setColorAt(0.0, QColor(255, 255, 255, 120))
    sheen.setColorAt(0.4, QColor(255, 255, 255, 30))
    sheen.setColorAt(1.0, QColor(255, 255, 255, 0))
    p.setBrush(sheen)
    p.setPen(Qt.NoPen)
    p.drawRect(QRectF(x, y, w, h * 0.55))

    # Crisp 1px glass border
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(QColor(255, 255, 255, 75), 0.8))
    p.drawPath(path)
    
    p.restore()


# --- Cupertino Search Field with SVG Magnifier Icon and Frosted Capsule ---
class CupertinoSearchField(QWidget):
    """
    Genuine Apple macOS Cupertino Search Field with vector SVG magnifier icon,
    frosted glass capsule, clear button, and smooth focus glow ring.
    """
    textChanged = Signal(str)
    down_pressed = Signal()
    up_pressed = Signal()
    return_pressed = Signal()
    escape_pressed = Signal()

    def __init__(self, placeholder: str = "Search language...", is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setFixedHeight(34)
        self.is_focused = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 0, 8, 0)
        layout.setSpacing(6)

        self.edit = QLineEdit(self)
        self.edit.setPlaceholderText(placeholder)
        self.edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.edit)

        # Clear Button
        self.clear_btn = QPushButton("✕", self)
        self.clear_btn.setFixedSize(16, 16)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.hide()
        self.clear_btn.clicked.connect(self.clear)
        layout.addWidget(self.clear_btn)

        self.edit.installEventFilter(self)
        self.set_dark(self.is_dark)

    def eventFilter(self, obj, event):
        if obj == self.edit:
            if event.type() == event.Type.FocusIn:
                self.is_focused = True
                self.update()
            elif event.type() == event.Type.FocusOut:
                self.is_focused = False
                self.update()
            elif event.type() == event.Type.KeyPress:
                if event.key() == Qt.Key_Escape:
                    self.clear()
                    self.escape_pressed.emit()
                    return True
                elif event.key() == Qt.Key_Down:
                    self.down_pressed.emit()
                    return True
                elif event.key() == Qt.Key_Up:
                    self.up_pressed.emit()
                    return True
                elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    self.return_pressed.emit()
                    return True
        return super().eventFilter(obj, event)

    def _on_text_changed(self, text: str):
        self.clear_btn.setVisible(bool(text))
        self.textChanged.emit(text)

    def clear(self):
        self.edit.clear()

    def text(self):
        return self.edit.text()

    def setText(self, t: str):
        self.edit.setText(t)

    def setPlaceholderText(self, p: str):
        self.edit.setPlaceholderText(p)

    def _update_clear_style(self):
        bg = "rgba(255, 255, 255, 0.25)" if self.is_dark else "rgba(0, 0, 0, 0.15)"
        fg = "#FFFFFF" if self.is_dark else "#1D1D1F"
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: none;
                border-radius: 8px;
                font-size: 9px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {"rgba(255, 255, 255, 0.40)" if self.is_dark else "rgba(0, 0, 0, 0.25)"};
            }}
        """)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        t_col = "#FFFFFF" if is_dark else "#1D1D1F"
        p_col = "rgba(255, 255, 255, 0.45)" if is_dark else "rgba(0, 0, 0, 0.40)"
        self.edit.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {t_col};
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 12.5px;
            }}
            QLineEdit::placeholder {{
                color: {p_col};
            }}
        """)
        self._update_clear_style()
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 9.0, 9.0)

        # Background fill
        if self.is_dark:
            fill_col = QColor(255, 255, 255, 28) if self.is_focused else QColor(255, 255, 255, 18)
            border_col = QColor("#007AFF") if self.is_focused else QColor(255, 255, 255, 32)
        else:
            fill_col = QColor(0, 0, 0, 18) if self.is_focused else QColor(0, 0, 0, 12)
            border_col = QColor("#007AFF") if self.is_focused else QColor(0, 0, 0, 24)

        p.fillPath(path, fill_col)
        p.setPen(QPen(border_col, 1.4 if self.is_focused else 0.8))
        p.drawPath(path)

        # ── Vector SVG Magnifier Icon (Left) ──
        mag_col = QColor("#007AFF") if self.is_focused else (QColor(255, 255, 255, 130) if self.is_dark else QColor(0, 0, 0, 110))
        p.setPen(QPen(mag_col, 1.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)

        # Lens ring (radius 4.0px)
        lx = 14.0
        ly = 16.0
        lr = 4.0
        p.drawEllipse(QPointF(lx, ly), lr, lr)

        # Handle (angled line)
        p.drawLine(QPointF(lx + 2.8, ly + 2.8), QPointF(lx + 6.2, ly + 6.2))

        p.end()


# --- macOS Inset-Grouped Language Row Item with SF Pro Typography ---
class CupertinoLanguageRow(QWidget):
    clicked = Signal(str)

    def __init__(self, code: str, flag: str, native_name: str, english_name: str, is_selected: bool = False, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.code = code
        self.flag = flag
        self.native_name = native_name
        self.english_name = english_name
        self.is_selected = is_selected
        self.is_dark = is_dark

        self.setFixedHeight(42)
        self.setCursor(Qt.PointingHandCursor)

        self.setAttribute(Qt.WA_Hover, True)
        self.is_hovered = False

    def set_selected(self, selected: bool):
        if self.is_selected != selected:
            self.is_selected = selected
            self.update()

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

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
            self.clicked.emit(self.code)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)

        rect = self.rect().adjusted(4, 2, -4, -2)

        if self.is_selected:
            # Apple Accent Blue Selection Pill with Smooth Gradient
            path = QPainterPath()
            path.addRoundedRect(QRectF(rect), 10.0, 10.0)

            pill_grad = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
            pill_grad.setColorAt(0.0, QColor("#0084FF"))
            pill_grad.setColorAt(1.0, QColor("#006BE0"))
            p.fillPath(path, pill_grad)

            # Subtle top light border
            p.setPen(QPen(QColor(255, 255, 255, 60), 0.8))
            p.drawPath(path)

        elif self.is_hovered:
            path = QPainterPath()
            path.addRoundedRect(QRectF(rect), 10.0, 10.0)
            fill_hover = QColor(255, 255, 255, 22) if self.is_dark else QColor(0, 0, 0, 16)
            p.fillPath(path, fill_hover)

        else:
            # Subtle 1px bottom divider line
            div_col = QColor(255, 255, 255, 14) if self.is_dark else QColor(0, 0, 0, 12)
            p.setPen(QPen(div_col, 1.0))
            p.drawLine(rect.left() + 48, rect.bottom(), rect.right() - 8, rect.bottom())

        # ── Vector Flag Badge (Crisp 30x20 squircle) ──
        flag_rect = QRectF(rect.left() + 8, rect.top() + (rect.height() - 20) / 2.0, 30, 20)
        draw_vector_flag(p, flag_rect, self.code)

        # Primary Title: SF Pro Rounded 14px Medium (Vertically Centered, Single Line)
        t_font = QFont("SF Pro Rounded", 14)
        if not t_font.exactMatch():
            t_font = QFont("SF Pro Display", 14)
            if not t_font.exactMatch():
                t_font = QFont("Inter", 14)
        t_font.setWeight(QFont.DemiBold if self.is_selected else QFont.Medium)
        t_font.setLetterSpacing(QFont.AbsoluteSpacing, -0.2)
        p.setFont(t_font)

        if self.is_selected:
            t_col = QColor("#FFFFFF")
        else:
            t_col = MacPalette.TEXT_DARK_PRIMARY if self.is_dark else MacPalette.TEXT_LIGHT_PRIMARY
        p.setPen(t_col)
        p.drawText(QRectF(rect.left() + 48, rect.top(), rect.width() - 85, rect.height()), Qt.AlignVCenter | Qt.AlignLeft, self.native_name)

        # Indicator Checkmark on Right
        if self.is_selected:
            cx = rect.right() - 20
            cy = rect.center().y()
            r = 8.5

            # Circular White Badge
            p.setBrush(QColor("#FFFFFF"))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(int(cx), int(cy)), int(r), int(r))

            # Blue Checkmark Glyph
            chk_pen = QPen(QColor("#007AFF"), 2.0)
            chk_pen.setCapStyle(Qt.RoundCap)
            chk_pen.setJoinStyle(Qt.RoundJoin)
            p.setPen(chk_pen)
            p.drawLine(int(cx - 3.2), int(cy), int(cx - 0.8), int(cy + 2.4))
            p.drawLine(int(cx - 0.8), int(cy + 2.4), int(cx + 3.6), int(cy - 2.4))

        p.end()





# --- Liquid Glass 3D Drive Icon for Destination / Scope Screen ---
class LiquidGlassDriveIcon(QWidget):
    def __init__(self, size: int = 68, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.size = size
        self.is_dark = is_dark
        self.setFixedSize(size, size)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        cx = rect.center().x()
        cy = rect.center().y()
        w = float(self.size)
        h = float(self.size)

        # 1. Ambient Glow
        glow = QRadialGradient(cx, cy, w * 0.48)
        glow.setColorAt(0.0, QColor(0, 122, 255, 120))
        glow.setColorAt(0.7, QColor(0, 210, 255, 35))
        glow.setColorAt(1.0, QColor(0, 122, 255, 0))
        p.fillRect(rect, glow)

        # 2. Outer Glass Squircle Chassis
        drive_rect = QRectF(cx - w * 0.38, cy - h * 0.38, w * 0.76, h * 0.76)
        d_path = QPainterPath()
        d_path.addRoundedRect(drive_rect, 13.0, 13.0)

        body_grad = QLinearGradient(drive_rect.left(), drive_rect.top(), drive_rect.right(), drive_rect.bottom())
        body_grad.setColorAt(0.0, QColor(0, 122, 255, 235) if self.is_dark else QColor(0, 100, 230, 235))
        body_grad.setColorAt(0.5, QColor(0, 80, 200, 220))
        body_grad.setColorAt(1.0, QColor(5, 35, 130, 240))
        p.fillPath(d_path, body_grad)

        # 3. Inner Drive Slot
        slot_rect = QRectF(cx - w * 0.26, cy - h * 0.24, w * 0.52, h * 0.34)
        s_path = QPainterPath()
        s_path.addRoundedRect(slot_rect, 6.0, 6.0)
        p.fillPath(s_path, QColor(0, 0, 0, 75))

        # Downward Arrow or Glowing Installation Platter
        p.setPen(QPen(QColor(0, 230, 255, 230), 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawLine(QPointF(cx, cy - h * 0.16), QPointF(cx, cy + h * 0.04))
        p.drawLine(QPointF(cx - w * 0.10, cy - h * 0.04), QPointF(cx, cy + h * 0.04))
        p.drawLine(QPointF(cx + w * 0.10, cy - h * 0.04), QPointF(cx, cy + h * 0.04))

        # LED status dot
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#00FF66"))
        p.drawEllipse(QPointF(cx + w * 0.24, cy + h * 0.22), 3.2, 3.2)

        # 4. Top-Left White Glass Specular Highlight Arc
        spec = QLinearGradient(drive_rect.left(), drive_rect.top(), cx, cy)
        spec.setColorAt(0.0, QColor(255, 255, 255, 220))
        spec.setColorAt(0.45, QColor(255, 255, 255, 70))
        spec.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(spec)
        p.setPen(Qt.NoPen)
        spec_path = QPainterPath()
        spec_path.addEllipse(QRectF(drive_rect.left() + 2, drive_rect.top() + 2, drive_rect.width() * 0.8, drive_rect.height() * 0.45))
        p.drawPath(spec_path)

        # 5. Crisp Glass Border
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(255, 255, 255, 110), 1.0))
        p.drawPath(d_path)

        p.end()


# --- macOS Inset-Grouped Destination Scope Card (No Text Clipping) ---
class CupertinoScopeCard(QWidget):
    clicked = Signal(str)

    def __init__(self, scope_id: str, title: str, description: str, path_badge: str = "", is_selected: bool = False, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.scope_id = scope_id
        self.title_text = title
        self.desc_text = description
        self.path_badge = path_badge
        self.is_selected = is_selected
        self.is_dark = is_dark
        self.is_hovered = False

        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMinimumHeight(78)
        self._init_ui()


    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        # Left Radio Indicator Widget
        self.radio_widget = QWidget()
        self.radio_widget.setFixedSize(22, 22)
        self.radio_widget.paintEvent = self._paint_radio
        layout.addWidget(self.radio_widget, 0, Qt.AlignVCenter)

        # Middle Info Layout (Title + Subtitle + Path Badge)
        mid_layout = QVBoxLayout()
        mid_layout.setSpacing(3)
        mid_layout.setContentsMargins(0, 0, 0, 0)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.title_lbl = QLabel(self.title_text)
        top_row.addWidget(self.title_lbl)

        self.badge_lbl = QLabel(self.path_badge)
        self.badge_lbl.setVisible(bool(self.path_badge))
        top_row.addWidget(self.badge_lbl)
        top_row.addStretch()
        mid_layout.addLayout(top_row)

        self.desc_lbl = QLabel(self.desc_text)
        self.desc_lbl.setWordWrap(True)
        mid_layout.addWidget(self.desc_lbl)
        layout.addLayout(mid_layout, 1)

        self._update_styles()

    def _paint_radio(self, event):
        p = QPainter(self.radio_widget)
        p.setRenderHint(QPainter.Antialiasing)
        cx = 11
        cy = 11
        r = 8.5
        if self.is_selected:
            p.setBrush(QColor(MacPalette.ACCENT_BLUE))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(cx, cy), int(r), int(r))

            p.setBrush(QColor("#FFFFFF"))
            p.drawEllipse(QPoint(cx, cy), 3, 3)
        else:
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255, 70) if self.is_dark else QColor(0, 0, 0, 50), 1.5))
            p.drawEllipse(QPoint(cx, cy), int(r), int(r))
        p.end()

    def set_selected(self, selected: bool):
        if self.is_selected != selected:
            self.is_selected = selected
            self.radio_widget.update()
            self._update_styles()
            self.update()

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self._update_styles()
        self.radio_widget.update()
        self.update()

    def set_texts(self, title: str, description: str, path_badge: str = ""):
        self.title_text = title
        self.desc_text = description
        self.title_lbl.setText(title)
        self.desc_lbl.setText(description)
        if path_badge:
            self.path_badge = path_badge
            self.badge_lbl.setText(path_badge)
            self.badge_lbl.setVisible(True)
        self.update()

    def _update_styles(self):
        t_col = "#007AFF" if self.is_selected else ("#FFFFFF" if self.is_dark else "#1D1D1F")
        s_col = "rgba(255, 255, 255, 0.70)" if self.is_dark else "rgba(0, 0, 0, 0.60)"
        self.title_lbl.setStyleSheet(f"""
            QLabel {{
                color: {t_col};
                font-family: 'SF Pro Rounded', 'SF Pro Display', 'Inter', sans-serif;
                font-size: 14px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        self.desc_lbl.setStyleSheet(f"""
            QLabel {{
                color: {s_col};
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 11.5px;
                line-height: 1.35;
                background: transparent;
                border: none;
            }}
        """)
        self.badge_lbl.setStyleSheet(f"""
            QLabel {{
                color: {"rgba(255, 255, 255, 0.85)" if self.is_dark else "rgba(0, 0, 0, 0.70)"};
                background-color: {"rgba(255, 255, 255, 0.10)" if self.is_dark else "rgba(0, 0, 0, 0.06)"};
                border: 1px solid {"rgba(255, 255, 255, 0.15)" if self.is_dark else "rgba(0, 0, 0, 0.10)"};
                border-radius: 5px;
                font-family: monospace;
                font-size: 10px;
                font-weight: 600;
                padding: 1px 5px;
            }}
        """)

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
            self.clicked.emit(self.scope_id)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 13.0, 13.0)

        if self.is_selected:
            fill_col = MacPalette.GLASS_DARK_CARD_SELECTED if self.is_dark else MacPalette.GLASS_LIGHT_CARD_SELECTED
            border_col = QColor(MacPalette.ACCENT_BLUE)
        elif self.is_hovered:
            fill_col = MacPalette.GLASS_DARK_CARD_HOVER if self.is_dark else MacPalette.GLASS_LIGHT_CARD_HOVER
            border_col = MacPalette.GLASS_DARK_BORDER_HIGHLIGHT if self.is_dark else MacPalette.GLASS_LIGHT_BORDER_HIGHLIGHT
        else:
            fill_col = MacPalette.GLASS_DARK_CARD if self.is_dark else MacPalette.GLASS_LIGHT_CARD
            border_col = MacPalette.GLASS_DARK_BORDER if self.is_dark else MacPalette.GLASS_LIGHT_BORDER

        p.fillPath(path, fill_col)
        p.setPen(QPen(border_col, 1.4 if self.is_selected else 0.8))
        p.drawPath(path)
        p.end()



# --- Cupertino Primary Pill Button ---
class CupertinoPrimaryButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(42)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacPalette.ACCENT_BLUE};
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 10px;
                font-family: 'SF Pro Text', 'Inter', -apple-system, sans-serif;
                font-size: 14px;
                font-weight: 600;
                padding: 0 26px;
            }}
            QPushButton:hover {{
                background-color: {MacPalette.ACCENT_BLUE_HOVER};
                border: 1px solid rgba(255, 255, 255, 0.40);
            }}
            QPushButton:pressed {{
                background-color: #004DB3;
            }}
            QPushButton:disabled {{
                background-color: rgba(0, 122, 255, 0.35);
                color: rgba(255, 255, 255, 0.5);
                border: none;
            }}
        """)


# --- Cupertino Secondary Button ---
class CupertinoSecondaryButton(QPushButton):
    def __init__(self, text: str, is_dark: bool = True, parent=None):
        super().__init__(text, parent)
        self.is_dark = is_dark
        self.setFixedHeight(42)
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update_style()

    def update_style(self):
        bg = "rgba(255, 255, 255, 0.10)" if self.is_dark else "rgba(0, 0, 0, 0.06)"
        bg_hover = "rgba(255, 255, 255, 0.18)" if self.is_dark else "rgba(0, 0, 0, 0.12)"
        text_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        border = "rgba(255, 255, 255, 0.16)" if self.is_dark else "rgba(0, 0, 0, 0.12)"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_col};
                border: 1px solid {border};
                border-radius: 10px;
                font-family: 'SF Pro Text', 'Inter', -apple-system, sans-serif;
                font-size: 14px;
                font-weight: 500;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
                border: 1px solid rgba(255, 255, 255, 0.30);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.05);
            }}
        """)


# =============================================================================
# Liquid Glass 3D Shield Icon for System Check Screen
# =============================================================================
class LiquidGlassShieldIcon(QWidget):
    def __init__(self, size: int = 68, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.size = size
        self.is_dark = is_dark
        self.setFixedSize(size, size)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        cx = rect.center().x()
        cy = rect.center().y()
        w = float(self.size)
        h = float(self.size)

        # 1. Ambient Emerald/Cyan Glow
        glow = QRadialGradient(cx, cy, w * 0.48)
        glow.setColorAt(0.0, QColor(52, 199, 89, 130))
        glow.setColorAt(0.65, QColor(0, 210, 255, 40))
        glow.setColorAt(1.0, QColor(0, 122, 255, 0))
        p.fillRect(rect, glow)

        # 2. Outer Shield Geometry
        sw = w * 0.72
        sh = h * 0.76
        sx = cx - sw / 2.0
        sy = cy - sh / 2.0 - 2.0

        shield_path = QPainterPath()
        shield_path.moveTo(cx, sy)
        shield_path.quadTo(sx + sw, sy, sx + sw, sy + sh * 0.45)
        shield_path.quadTo(sx + sw, sy + sh * 0.85, cx, sy + sh)
        shield_path.quadTo(sx, sy + sh * 0.85, sx, sy + sh * 0.45)
        shield_path.quadTo(sx, sy, cx, sy)
        shield_path.closeSubpath()

        # Body Gradient
        body_grad = QLinearGradient(sx, sy, sx + sw, sy + sh)
        body_grad.setColorAt(0.0, QColor(48, 209, 88, 235) if self.is_dark else QColor(40, 190, 80, 235))
        body_grad.setColorAt(0.5, QColor(0, 160, 120, 220))
        body_grad.setColorAt(1.0, QColor(0, 85, 140, 240))
        p.fillPath(shield_path, body_grad)

        # 3. Inner Luminous Lock / Check Crest
        crest_pen = QPen(QColor("#FFFFFF"), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(crest_pen)
        # Checkmark
        p.drawLine(QPointF(cx - w * 0.12, cy + h * 0.02), QPointF(cx - w * 0.02, cy + h * 0.12))
        p.drawLine(QPointF(cx - w * 0.02, cy + h * 0.12), QPointF(cx + w * 0.14, cy - h * 0.06))

        # 4. Top Specular Sheen Arc
        p.setPen(Qt.NoPen)
        spec = QLinearGradient(sx, sy, cx, cy)
        spec.setColorAt(0.0, QColor(255, 255, 255, 220))
        spec.setColorAt(0.45, QColor(255, 255, 255, 70))
        spec.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(spec)
        p.drawEllipse(QRectF(sx + 2, sy + 2, sw * 0.8, sh * 0.42))

        # 5. Crisp Glass Shield Border
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(255, 255, 255, 120), 1.0))
        p.drawPath(shield_path)
        p.end()


# =============================================================================
# Liquid Glass 3D Success Emblem for Complete Screen
# =============================================================================
class LiquidGlassSuccessIcon(QWidget):
    def __init__(self, size: int = 76, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.size = size
        self.is_dark = is_dark
        self.setFixedSize(size, size)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        cx = rect.center().x()
        cy = rect.center().y()
        w = float(self.size)
        h = float(self.size)

        # 1. Radial Radiant Halo
        halo = QRadialGradient(cx, cy, w * 0.48)
        halo.setColorAt(0.0, QColor(52, 199, 89, 160))
        halo.setColorAt(0.6, QColor(48, 209, 88, 45))
        halo.setColorAt(1.0, QColor(0, 122, 255, 0))
        p.fillRect(rect, halo)

        # 2. 3D Glass Disc Squircle
        r = w * 0.36
        disc_path = QPainterPath()
        disc_path.addEllipse(QPointF(cx, cy), r, r)

        body_grad = QLinearGradient(cx - r, cy - r, cx + r, cy + r)
        body_grad.setColorAt(0.0, QColor(52, 199, 89, 245))
        body_grad.setColorAt(0.5, QColor(40, 175, 75, 235))
        body_grad.setColorAt(1.0, QColor(25, 125, 60, 245))
        p.fillPath(disc_path, body_grad)

        # 3. 3D Luminous White Checkmark
        chk_pen = QPen(QColor("#FFFFFF"), 3.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(chk_pen)
        p.drawLine(QPointF(cx - w * 0.14, cy + h * 0.01), QPointF(cx - w * 0.03, cy + h * 0.13))
        p.drawLine(QPointF(cx - w * 0.03, cy + h * 0.13), QPointF(cx + w * 0.16, cy - h * 0.10))

        # 4. Specular Reflection Arc
        p.setPen(Qt.NoPen)
        spec = QLinearGradient(cx - r, cy - r, cx, cy)
        spec.setColorAt(0.0, QColor(255, 255, 255, 230))
        spec.setColorAt(0.5, QColor(255, 255, 255, 80))
        spec.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(spec)
        p.drawEllipse(QRectF(cx - r + 3, cy - r + 2, r * 1.5, r * 0.9))

        # 5. Crisp Glass Rim
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(255, 255, 255, 130), 1.0))
        p.drawPath(disc_path)
        p.end()


# =============================================================================
# 3D Liquid Glass Spotlight / Search Hero Icon
# =============================================================================
class LiquidGlassSearchHeroIcon(QWidget):
    def __init__(self, size: int = 68, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.size = size
        self.is_dark = is_dark
        self.setFixedSize(size, size)

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        cx = rect.center().x()
        cy = rect.center().y()
        w = float(self.size)
        h = float(self.size)

        # 1. Radial Neon Cyan & Indigo Halo Glow
        halo = QRadialGradient(cx, cy, w * 0.48)
        halo.setColorAt(0.0, QColor(0, 122, 255, 130))
        halo.setColorAt(0.5, QColor(0, 210, 255, 55))
        halo.setColorAt(1.0, QColor(88, 86, 214, 0))
        p.fillRect(rect, halo)

        # 2. 3D Glass Squircle Chassis
        drive_rect = QRectF(cx - w * 0.38, cy - h * 0.38, w * 0.76, h * 0.76)
        d_path = QPainterPath()
        d_path.addRoundedRect(drive_rect, 14.0, 14.0)

        body_grad = QLinearGradient(drive_rect.left(), drive_rect.top(), drive_rect.right(), drive_rect.bottom())
        body_grad.setColorAt(0.0, QColor(0, 122, 255, 240) if self.is_dark else QColor(0, 110, 245, 240))
        body_grad.setColorAt(0.5, QColor(88, 86, 214, 230))
        body_grad.setColorAt(1.0, QColor(25, 20, 95, 245))
        p.fillPath(d_path, body_grad)

        # 3. 3D Spotlight Magnifying Glass Lens
        # Lens outer ring center offset
        lx = cx - w * 0.04
        ly = cy - h * 0.04
        lr = w * 0.19

        # Handle angled bottom-right
        h_pen = QPen(QColor("#FFFFFF"), 3.4, Qt.SolidLine, Qt.RoundCap)
        p.setPen(h_pen)
        import math
        hx1 = lx + lr * math.cos(math.pi / 4.0)
        hy1 = ly + lr * math.sin(math.pi / 4.0)
        hx2 = hx1 + w * 0.15
        hy2 = hy1 + h * 0.15
        p.drawLine(QPointF(hx1, hy1), QPointF(hx2, hy2))

        # Lens Glass Fill
        p.setPen(QPen(QColor(255, 255, 255, 240), 2.8))
        lens_grad = QRadialGradient(lx, ly, lr)
        lens_grad.setColorAt(0.0, QColor(255, 255, 255, 120))
        lens_grad.setColorAt(0.7, QColor(0, 210, 255, 90))
        lens_grad.setColorAt(1.0, QColor(0, 122, 255, 160))
        p.setBrush(lens_grad)
        p.drawEllipse(QPointF(lx, ly), lr, lr)

        # 4. Sparkling Star in Focus Center
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(QPointF(lx - 2.0, ly - 2.0), 1.5, 1.5)

        # 5. Specular Reflection Arc
        spec = QLinearGradient(drive_rect.left(), drive_rect.top(), cx, cy)
        spec.setColorAt(0.0, QColor(255, 255, 255, 200))
        spec.setColorAt(0.5, QColor(255, 255, 255, 60))
        spec.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(spec)
        p.drawEllipse(QRectF(drive_rect.left() + 2, drive_rect.top() + 2, drive_rect.width() * 0.7, drive_rect.height() * 0.45))

        # 6. Outer Glass Border
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(255, 255, 255, 110), 1.0))
        p.drawPath(d_path)

        p.end()


# =============================================================================
# Vector Status Badge Indicator (Success / Warning / Failure / Checking)
# =============================================================================

class SystemCheckStatusBadge(QWidget):
    def __init__(self, status: str = "pass", size: int = 20, parent=None):
        super().__init__(parent)
        self.status = status  # 'pass', 'warning', 'fail', 'checking'
        self.size = size
        self.setFixedSize(size, size)

    def set_status(self, status: str):
        self.status = status
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        cx = self.width() / 2.0
        cy = self.height() / 2.0
        r = (self.width() / 2.0) - 1.5

        if self.status == "pass":
            # Emerald Green Circle
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#34C759"))
            p.drawEllipse(QPointF(cx, cy), r, r)

            # Crisp White Checkmark
            chk = QPen(QColor("#FFFFFF"), 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            p.setPen(chk)
            p.drawLine(QPointF(cx - 3.8, cy + 0.2), QPointF(cx - 1.0, cy + 3.2))
            p.drawLine(QPointF(cx - 1.0, cy + 3.2), QPointF(cx + 4.2, cy - 3.2))

        elif self.status == "warning":
            # Amber Rounded Squircle/Triangle
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#FF9500"))
            path = QPainterPath()
            path.addRoundedRect(QRectF(cx - r, cy - r, r * 2, r * 2), 5.0, 5.0)
            p.fillPath(path, QColor("#FF9500"))

            # White Exclamation Mark
            p.setPen(QPen(QColor("#FFFFFF"), 1.8, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(QPointF(cx, cy - 3.5), QPointF(cx, cy + 0.5))
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#FFFFFF"))
            p.drawEllipse(QPointF(cx, cy + 3.5), 1.0, 1.0)

        elif self.status == "fail":
            # Coral Red Circle
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#FF3B30"))
            p.drawEllipse(QPointF(cx, cy), r, r)

            # White X
            x_pen = QPen(QColor("#FFFFFF"), 1.8, Qt.SolidLine, Qt.RoundCap)
            p.setPen(x_pen)
            p.drawLine(QPointF(cx - 3.2, cy - 3.2), QPointF(cx + 3.2, cy + 3.2))
            p.drawLine(QPointF(cx + 3.2, cy - 3.2), QPointF(cx - 3.2, cy + 3.2))

        else:  # 'checking'
            p.setPen(QPen(QColor("#007AFF"), 2.0, Qt.SolidLine, Qt.RoundCap))
            p.setBrush(Qt.NoBrush)
            p.drawArc(QRectF(cx - r, cy - r, r * 2, r * 2), 0, 270 * 16)

        p.end()


# =============================================================================
# Cupertino System Check Row Widget (Inset-Grouped List Item)
# =============================================================================
class CupertinoSystemCheckRow(QWidget):
    def __init__(self, title: str, details: str, value: str, status: str = "pass", is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.status = status
        self.title_text = title
        self.details_text = details
        self.value_text = value
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        # 1. Vector Status Indicator Badge
        self.badge = SystemCheckStatusBadge(status=self.status, size=18)
        layout.addWidget(self.badge, 0, Qt.AlignVCenter)

        # 2. Text Labels (Title + Subtitle)
        v_layout = QVBoxLayout()
        v_layout.setSpacing(1)
        v_layout.setContentsMargins(0, 0, 0, 0)

        self.title_lbl = QLabel(self.title_text)
        v_layout.addWidget(self.title_lbl)

        self.details_lbl = QLabel(self.details_text)
        self.details_lbl.setWordWrap(True)
        v_layout.addWidget(self.details_lbl)
        layout.addLayout(v_layout, 1)

        # 3. Value Badge on the Right (Monospace pill)
        self.val_badge = QLabel(self.value_text)
        self.val_badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.val_badge, 0, Qt.AlignVCenter)

        self._update_styles()


    def set_data(self, title: str, details: str, value: str, status: str):
        self.title_text = title
        self.details_text = details
        self.value_text = value
        self.status = status
        self.title_lbl.setText(title)
        self.details_lbl.setText(details)
        self.val_badge.setText(value)
        self.badge.set_status(status)
        self._update_styles()

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self._update_styles()

    def _update_styles(self):
        t_col = "#FFFFFF" if self.is_dark else "#1D1D1F"
        s_col = "rgba(255, 255, 255, 0.65)" if self.is_dark else "rgba(0, 0, 0, 0.55)"

        self.title_lbl.setStyleSheet(f"""
            QLabel {{
                color: {t_col};
                font-family: 'SF Pro Rounded', 'SF Pro Display', 'Inter', sans-serif;
                font-size: 13.5px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        self.details_lbl.setStyleSheet(f"""
            QLabel {{
                color: {s_col};
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 11px;
                line-height: 1.35;
                background: transparent;
                border: none;
            }}
        """)
        self.val_badge.setStyleSheet(f"""
            QLabel {{
                color: {"rgba(255, 255, 255, 0.85)" if self.is_dark else "rgba(0, 0, 0, 0.70)"};
                background-color: {"rgba(255, 255, 255, 0.10)" if self.is_dark else "rgba(0, 0, 0, 0.06)"};
                border: 1px solid {"rgba(255, 255, 255, 0.15)" if self.is_dark else "rgba(0, 0, 0, 0.10)"};
                border-radius: 6px;
                font-family: monospace;
                font-size: 11px;
                font-weight: 600;
                padding: 3px 7px;
            }}
        """)


# =============================================================================
# Cupertino Theme Toggle Button (Exact Liquid Glass Sun/Moon Capsule from Reference)
# =============================================================================
class CupertinoThemeToggle(QWidget):
    toggled = Signal(bool)  # emits is_dark

    def __init__(self, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self._is_dark = is_dark
        self._pos = 1.0 if is_dark else 0.0
        self.setFixedSize(56, 30)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.is_hovered = False

        self._anim = QPropertyAnimation(self, b"pos_val", self)
        self._anim.setDuration(230)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def get_pos_val(self) -> float:
        return self._pos

    def set_pos_val(self, val: float):
        self._pos = val
        self.update()

    pos_val = Property(float, get_pos_val, set_pos_val)

    def set_dark(self, is_dark: bool):
        if self._is_dark != is_dark:
            self._is_dark = is_dark
            self._anim.stop()
            self._anim.setStartValue(self._pos)
            self._anim.setEndValue(1.0 if is_dark else 0.0)
            self._anim.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dark = not self._is_dark
            self._anim.stop()
            self._anim.setStartValue(self._pos)
            self._anim.setEndValue(1.0 if self._is_dark else 0.0)
            self._anim.start()
            self.toggled.emit(self._is_dark)
        super().mousePressEvent(event)

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

        w = float(self.width())
        h = float(self.height())

        # ── 1. Capsule Track Background ──
        track_rect = QRectF(0.5, 0.5, w - 1.0, h - 1.0)
        t_path = QPainterPath()
        t_path.addRoundedRect(track_rect, 14.5, 14.5)

        # Track background color based on theme
        if self._is_dark:
            bg_col = QColor(44, 44, 46, 240) if not self.is_hovered else QColor(58, 58, 60, 240)
            border_col = QColor(255, 255, 255, 38)
        else:
            bg_col = QColor(234, 234, 238, 240) if not self.is_hovered else QColor(225, 225, 230, 240)
            border_col = QColor(0, 0, 0, 25)

        p.fillPath(t_path, bg_col)
        p.setPen(QPen(border_col, 1.0))
        p.drawPath(t_path)

        # ── 2. Inactive Background Glyphs inside Track ──
        # Inactive Moon Glyph on Right (Visible when Sun is active / pos < 0.8)
        if self._pos < 0.85:
            moon_opacity = int(255 * (1.0 - self._pos / 0.85))
            mcx = w - 15.0
            mcy = h / 2.0
            m_path = QPainterPath()
            m_path.addEllipse(QPointF(mcx, mcy), 4.5, 4.5)
            cut_path = QPainterPath()
            cut_path.addEllipse(QPointF(mcx + 2.0, mcy - 1.2), 3.8, 3.8)
            moon_shape = m_path.subtracted(cut_path)
            p.fillPath(moon_shape, QColor(142, 142, 147, int(moon_opacity * 0.55)))

        # Inactive Sun Glyph on Left (Visible when Moon is active / pos > 0.15)
        if self._pos > 0.15:
            sun_opacity = int(255 * ((self._pos - 0.15) / 0.85))
            scx = 15.0
            scy = h / 2.0
            p.setBrush(QColor(142, 142, 147, int(sun_opacity * 0.55)))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(scx, scy), 2.8, 2.8)

            s_pen = QPen(QColor(142, 142, 147, int(sun_opacity * 0.55)), 1.2, Qt.SolidLine, Qt.RoundCap)
            p.setPen(s_pen)
            import math
            for i in range(8):
                angle = i * (math.pi / 4.0)
                r1, r2 = 4.2, 5.8
                p.drawLine(
                    QPointF(scx + r1 * math.cos(angle), scy + r1 * math.sin(angle)),
                    QPointF(scx + r2 * math.cos(angle), scy + r2 * math.sin(angle))
                )

        # ── 3. Sliding Raised Knob (Thumb) ──
        knob_d = 25.0
        knob_x = 2.5 + self._pos * (w - knob_d - 5.0)
        knob_y = 2.5
        k_center_x = knob_x + knob_d / 2.0
        k_center_y = knob_y + knob_d / 2.0

        # Drop shadow below white knob
        p.setPen(Qt.NoPen)
        shadow_path = QPainterPath()
        shadow_path.addEllipse(QRectF(knob_x, knob_y + 1.2, knob_d, knob_d))
        p.fillPath(shadow_path, QColor(0, 0, 0, 42))

        # Outer Raised White Bezel
        bezel_path = QPainterPath()
        bezel_path.addEllipse(QRectF(knob_x, knob_y, knob_d, knob_d))
        p.fillPath(bezel_path, QColor("#FFFFFF"))
        p.setPen(QPen(QColor(0, 0, 0, 20), 0.8))
        p.drawPath(bezel_path)

        # Inner Dark Core (Dark brown/black circle)
        core_d = 19.0
        core_rect = QRectF(k_center_x - core_d / 2.0, k_center_y - core_d / 2.0, core_d, core_d)
        core_path = QPainterPath()
        core_path.addEllipse(core_rect)

        # Interpolate core color from Sun brown (#1F1711) to Moon navy (#0C1A30)
        if self._pos < 0.5:
            core_col = QColor("#1F1711")
        else:
            core_col = QColor("#0C1A30")
        p.fillPath(core_path, core_col)

        # ── 4. Active Glyph inside Knob ──
        if self._pos < 0.5:
            # ☀️ Golden Sun Disc with 8 Radiating Ray Ticks (Exact match to reference)
            sun_col = QColor("#FFD60A")

            # Center golden circle
            p.setBrush(sun_col)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(k_center_x, k_center_y), 3.6, 3.6)

            # 8 radiating rays
            ray_pen = QPen(sun_col, 1.35, Qt.SolidLine, Qt.RoundCap)
            p.setPen(ray_pen)
            import math
            for i in range(8):
                angle = i * (math.pi / 4.0)
                r_in = 5.0
                r_out = 7.0
                p.drawLine(
                    QPointF(k_center_x + r_in * math.cos(angle), k_center_y + r_in * math.sin(angle)),
                    QPointF(k_center_x + r_out * math.cos(angle), k_center_y + r_out * math.sin(angle))
                )
        else:
            # 🌙 Glowing Cyan / White Crescent Moon
            moon_col = QColor("#00D2FF")
            m_path = QPainterPath()
            m_path.addEllipse(QPointF(k_center_x, k_center_y), 4.6, 4.6)
            cut_path = QPainterPath()
            cut_path.addEllipse(QPointF(k_center_x + 2.0, k_center_y - 1.2), 3.8, 3.8)
            active_moon = m_path.subtracted(cut_path)
            p.fillPath(active_moon, moon_col)

            # Tiny star sparkle
            p.setBrush(QColor("#FFFFFF"))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(k_center_x - 3.2, k_center_y - 2.8), 0.9, 0.9)

        p.end()



# =============================================================================
# Cupertino Interactive Checkbox for Scope / Installation Options
# =============================================================================
class CupertinoCheckbox(QWidget):
    toggled = Signal(bool)

    def __init__(self, text: str, is_checked: bool = False, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_checked = is_checked
        self.is_dark = is_dark
        self.setFixedHeight(30)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.is_hovered = False

    def setChecked(self, checked: bool):
        if self.is_checked != checked:
            self.is_checked = checked
            self.update()
            self.toggled.emit(checked)

    def isChecked(self) -> bool:
        return self.is_checked

    def setText(self, text: str):
        self.text = text
        self.update()

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setChecked(not self.is_checked)
        super().mousePressEvent(event)

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

        # 1. Checkbox Box
        bx = 2.0
        by = (self.height() - 18.0) / 2.0
        bw = 18.0
        bh = 18.0

        box_path = QPainterPath()
        box_path.addRoundedRect(QRectF(bx, by, bw, bh), 5.0, 5.0)

        if self.is_checked:
            # Active Apple Accent Blue fill
            pill_grad = QLinearGradient(bx, by, bx, by + bh)
            pill_grad.setColorAt(0.0, QColor("#0084FF"))
            pill_grad.setColorAt(1.0, QColor("#006BE0"))
            p.fillPath(box_path, pill_grad)

            # Checkmark
            chk = QPen(QColor("#FFFFFF"), 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            p.setPen(chk)
            cx = bx + bw / 2.0
            cy = by + bh / 2.0
            p.drawLine(QPointF(cx - 3.8, cy + 0.2), QPointF(cx - 1.0, cy + 3.2))
            p.drawLine(QPointF(cx - 1.0, cy + 3.2), QPointF(cx + 4.2, cy - 3.2))
        else:
            bg_col = QColor(255, 255, 255, 24 if self.is_hovered else 14) if self.is_dark else QColor(0, 0, 0, 16 if self.is_hovered else 8)
            border_col = QColor(255, 255, 255, 50 if self.is_hovered else 30) if self.is_dark else QColor(0, 0, 0, 35 if self.is_hovered else 20)
            p.fillPath(box_path, bg_col)
            p.setPen(QPen(border_col, 1.0))
            p.drawPath(box_path)

        # 2. Text Label
        t_col = QColor("#FFFFFF" if self.is_dark else "#1D1D1F")
        p.setPen(t_col)
        t_font = QFont("SF Pro Text", 10.5 if len(self.text) > 28 else 11.5)
        if not t_font.exactMatch():
            t_font = QFont("Inter", 10.5 if len(self.text) > 28 else 11.5)
        t_font.setWeight(QFont.Medium)
        p.setFont(t_font)
        p.drawText(QRectF(bx + bw + 8, 0, self.width() - bx - bw - 8, self.height()), Qt.AlignVCenter | Qt.AlignLeft, self.text)

        p.end()




# =============================================================================
# Liquid Glass Pulsing Logo for Installing Screen
# =============================================================================
class LiquidGlassPulsingLogo(QWidget):
    def __init__(self, size: int = 96, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.size = size
        self.is_dark = is_dark
        self.setFixedSize(size, size)
        self._glow_phase = 0.0

        # Load transparent app icon
        icon_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Tahoe Settings", "icon.png")
        if not os.path.exists(icon_p):
            icon_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png")
        self.icon_img = QImage(icon_p)

        # Soft breathing timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._step_pulse)
        self.timer.start(35)
        self._delta = 0.035

    def _step_pulse(self):
        self._glow_phase += self._delta
        if self._glow_phase >= 1.0:
            self._glow_phase = 1.0
            self._delta = -0.035
        elif self._glow_phase <= 0.0:
            self._glow_phase = 0.0
            self._delta = 0.035
        self.update()

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        rect = self.rect()
        cx = rect.center().x()
        cy = rect.center().y()
        w = float(self.size)

        # 1. Pulsing Radial Cyan/Blue Glow
        glow_r = w * (0.42 + 0.08 * self._glow_phase)
        glow_alpha = int(90 + 60 * self._glow_phase)
        glow = QRadialGradient(cx, cy, glow_r)
        glow.setColorAt(0.0, QColor(0, 122, 255, glow_alpha))
        glow.setColorAt(0.65, QColor(0, 210, 255, int(glow_alpha * 0.4)))
        glow.setColorAt(1.0, QColor(0, 122, 255, 0))
        p.fillRect(rect, glow)

        # 2. Center Icon Image (with slight scale breathing)
        if not self.icon_img.isNull():
            draw_sz = int(w * (0.76 + 0.04 * self._glow_phase))
            scaled = self.icon_img.scaled(draw_sz, draw_sz, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            ox = (w - draw_sz) / 2.0
            oy = (w - draw_sz) / 2.0
            p.drawImage(int(ox), int(oy), scaled)

        p.end()


# =============================================================================
# Installing Milestone Progress Sequence Bar (5 Stages)
# =============================================================================
class InstallingMilestoneBar(QWidget):
    def __init__(self, current_stage: int = 1, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.current_stage = current_stage  # 1 to 5
        self.is_dark = is_dark
        self.setFixedHeight(36)
        self.stages = ["Preparing", "Core Assets", "Qt6 Runtime", "System Links", "Integration"]

    def set_stage(self, stage: int):
        self.current_stage = stage
        self.update()

    def set_stage_names(self, names: list):
        if len(names) == 5:
            self.stages = names
            self.update()

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        n = len(self.stages)
        step_w = w / float(n)

        font = QFont("SF Pro Text", 10)
        if not font.exactMatch():
            font = QFont("Inter", 10)
        p.setFont(font)

        for i, name in enumerate(self.stages, 1):
            cx = step_w * (i - 0.5)
            cy = 10.0

            # 1. Connecting line to next stage
            if i < n:
                p.setPen(QPen(QColor(255, 255, 255, 30) if self.is_dark else QColor(0, 0, 0, 20), 1.5))
                p.drawLine(QPointF(cx + 8.0, cy), QPointF(cx + step_w - 8.0, cy))

            # 2. Stage Dot Indicator
            if i < self.current_stage:
                # Completed: Emerald Green with mini check
                p.setPen(Qt.NoPen)
                p.setBrush(QColor("#34C759"))
                p.drawEllipse(QPointF(cx, cy), 6.5, 6.5)

                chk = QPen(QColor("#FFFFFF"), 1.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                p.setPen(chk)
                p.drawLine(QPointF(cx - 2.5, cy + 0.2), QPointF(cx - 0.7, cy + 2.0))
                p.drawLine(QPointF(cx - 0.7, cy + 2.0), QPointF(cx + 2.8, cy - 2.0))

            elif i == self.current_stage:
                # Active: Glowing Apple Blue Circle with center dot
                glow = QRadialGradient(cx, cy, 12.0)
                glow.setColorAt(0.0, QColor(0, 122, 255, 160))
                glow.setColorAt(1.0, QColor(0, 122, 255, 0))
                p.setPen(Qt.NoPen)
                p.setBrush(glow)
                p.drawEllipse(QPointF(cx, cy), 12.0, 12.0)

                p.setBrush(QColor("#007AFF"))
                p.drawEllipse(QPointF(cx, cy), 6.5, 6.5)
                p.setBrush(QColor("#FFFFFF"))
                p.drawEllipse(QPointF(cx, cy), 2.2, 2.2)

            else:
                # Pending: Faint Circle
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(255, 255, 255, 35) if self.is_dark else QColor(0, 0, 0, 25))
                p.drawEllipse(QPointF(cx, cy), 5.0, 5.0)

            # 3. Stage Text
            if i == self.current_stage:
                p.setPen(QColor("#007AFF"))
            elif i < self.current_stage:
                p.setPen(QColor("#FFFFFF" if self.is_dark else "#1D1D1F"))
            else:
                p.setPen(QColor(255, 255, 255, 100) if self.is_dark else QColor(0, 0, 0, 90))

            p.drawText(QRectF(cx - step_w / 2.0, 20.0, step_w, 16.0), Qt.AlignCenter, name)

        p.end()


# =============================================================================
# Liquid Glass Complete Hero Logo with Subtle Particle Burst
# =============================================================================
class LiquidGlassParticle:
    def __init__(self, x: float, y: float, vx: float, vy: float, color: QColor, size: float, shape: str = "shard"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.alpha = 255.0
        self.rot = 0.0
        self.vrot = ((int(abs(vx * 100)) % 24) - 12) * 0.35
        self.shape = shape


class LiquidGlassCompleteLogo(QWidget):
    """
    Renders the authentic Echo logo as the central completion hero element,
    with a soft radiant completion aura and a multi-wave celebratory burst of
    translucent Liquid Glass confetti particles (cyan, blue, violet, green, pink, orange, yellow)
    with specular highlights, glowing sheen, and graceful air-resistance deceleration.
    """
    def __init__(self, size: int = 96, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.size = size
        self.is_dark = is_dark
        self.setFixedSize(320, 180)  # Generous room for wide particle dispersal without clipping
        self.particles: list = []

        # Load transparent app icon
        icon_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Tahoe Settings", "icon.png")
        if not os.path.exists(icon_p):
            icon_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png")
        self.icon_img = QImage(icon_p)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._step_particles)

    def trigger_confetti(self):
        """Triggers a 3-wave celebratory Liquid Glass confetti sequence."""
        self.particles.clear()
        self._spawn_burst(count=26, min_speed=2.6, max_speed=5.0)
        # Staggered subsequent waves for celebratory layered effect
        QTimer.singleShot(320, lambda: self._spawn_burst(count=20, min_speed=2.2, max_speed=4.2))
        QTimer.singleShot(650, lambda: self._spawn_burst(count=16, min_speed=1.8, max_speed=3.6))

        if not self.anim_timer.isActive():
            self.anim_timer.start(16)  # ~60 fps
        self.update()

    def _spawn_burst(self, count: int = 24, min_speed: float = 2.4, max_speed: float = 4.8):
        import math, random
        cx = self.width() / 2.0
        cy = self.height() / 2.0

        # Curated Liquid Glass jewel palette
        palette = [
            QColor("#00F5D4"),  # Radiant Cyan
            QColor("#00C7BE"),  # Teal
            QColor("#0A84FF"),  # Apple Blue
            QColor("#2997FF"),  # Sky Blue
            QColor("#BF5AF2"),  # Violet
            QColor("#AF52DE"),  # Deep Purple
            QColor("#30D158"),  # Emerald Green
            QColor("#34C759"),  # Apple Green
            QColor("#FF375F"),  # Pink / Magenta
            QColor("#FF2D55"),  # Vivid Coral Pink
            QColor("#FF9F0A"),  # Warm Orange
            QColor("#FFD60A"),  # Luminous Yellow
        ]

        shapes = ["shard", "pill", "orb", "diamond", "square"]

        for i in range(count):
            angle = (i / float(count)) * 2.0 * math.pi + (random.random() - 0.5) * 0.4
            speed = min_speed + random.random() * (max_speed - min_speed)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 0.2
            col = random.choice(palette)
            sz = 2.8 + random.random() * 3.2
            shp = random.choice(shapes)
            # Offset spawn from logo periphery
            dist = (self.size / 2.0) * 0.72 + random.random() * 8.0
            px = cx + math.cos(angle) * dist
            py = cy + math.sin(angle) * dist
            self.particles.append(LiquidGlassParticle(px, py, vx, vy, col, sz, shp))

    def _step_particles(self):
        alive = False
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vx *= 0.955
            p.vy = (p.vy + 0.012) * 0.955
            p.alpha -= 2.2
            p.rot += p.vrot
            if p.alpha > 0:
                alive = True

        if not alive:
            self.particles.clear()
            self.anim_timer.stop()
        self.update()

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        cx = self.width() / 2.0
        cy = self.height() / 2.0
        r_logo = self.size / 2.0

        # 1. Soft Emerald/Cyan Radiant Completion Aura
        aura = QRadialGradient(cx, cy, r_logo * 1.55)
        aura.setColorAt(0.0, QColor(52, 199, 89, 110) if self.is_dark else QColor(52, 199, 89, 70))
        aura.setColorAt(0.55, QColor(0, 199, 190, 45) if self.is_dark else QColor(0, 199, 190, 25))
        aura.setColorAt(1.0, QColor(0, 122, 255, 0))
        p.fillRect(self.rect(), aura)

        # 2. Confetti / Liquid Glass Particles
        for part in self.particles:
            if part.alpha <= 0:
                continue
            alpha_f = max(0.0, min(255.0, part.alpha)) / 255.0
            
            p.save()
            p.translate(part.x, part.y)
            p.rotate(part.rot)

            # A. Soft Glow Bloom underneath
            glow_intensity = 0.40 if self.is_dark else 0.22
            glow_col = QColor(part.color)
            glow_col.setAlpha(int(255 * alpha_f * glow_intensity))
            p.setBrush(glow_col)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(0, 0), part.size * 1.6, part.size * 1.6)

            # B. Translucent Glass Shard / Body
            fill_col = QColor(part.color)
            fill_col.setAlpha(int(255 * alpha_f * (0.85 if self.is_dark else 0.70)))
            p.setBrush(fill_col)

            border_alpha = int(255 * alpha_f * (0.80 if self.is_dark else 0.50))
            p.setPen(QPen(QColor(255, 255, 255, border_alpha), 0.75))

            sz = part.size
            if part.shape == "shard" or part.shape == "diamond":
                diamond_path = QPainterPath()
                diamond_path.moveTo(0, -sz * 1.2)
                diamond_path.lineTo(sz * 0.75, 0)
                diamond_path.lineTo(0, sz * 1.2)
                diamond_path.lineTo(-sz * 0.75, 0)
                diamond_path.closeSubpath()
                p.drawPath(diamond_path)
            elif part.shape == "pill":
                p.drawRoundedRect(QRectF(-sz * 1.4, -sz * 0.7, sz * 2.8, sz * 1.4), sz * 0.6, sz * 0.6)
            elif part.shape == "square":
                p.drawRoundedRect(QRectF(-sz * 0.9, -sz * 0.9, sz * 1.8, sz * 1.8), sz * 0.35, sz * 0.35)
            else:  # orb
                p.drawEllipse(QPointF(0, 0), sz, sz)

            # C. Specular Glass Highlight Glint (Top reflection)
            spec_alpha = int(255 * alpha_f * (0.90 if self.is_dark else 0.60))
            p.setBrush(QColor(255, 255, 255, spec_alpha))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(-sz * 0.3, -sz * 0.3), sz * 0.35, sz * 0.35)

            p.restore()

        # 3. Authentic Central Echo Logo
        if not self.icon_img.isNull():
            draw_sz = int(self.size * 0.88)
            scaled = self.icon_img.scaled(draw_sz, draw_sz, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            ox = cx - draw_sz / 2.0
            oy = cy - draw_sz / 2.0
            p.drawImage(int(ox), int(oy), scaled)

        p.end()


# =============================================================================
# Collapsible Glass Terminal Drawer (Installation Output Log)
# =============================================================================
class GlassTerminalDrawer(QWidget):
    """
    Collapsible glass terminal drawer for viewing live/completed installation logs.
    Collapsed by default, expands cleanly with a single click.
    """
    def __init__(self, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.is_expanded = False
        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(4)

        # Header Toggle Row
        hdr_layout = QHBoxLayout()
        hdr_layout.setContentsMargins(4, 0, 4, 0)
        hdr_layout.setSpacing(8)

        from localization import t
        show_txt = t("installer.log_show") or "Показать подробный журнал"
        self.btn_toggle = QPushButton(show_txt + "  ▼")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self._update_btn_style()
        self.btn_toggle.clicked.connect(self.toggle_expansion)
        hdr_layout.addWidget(self.btn_toggle)

        hdr_layout.addStretch()

        copy_txt = t("installer.log_copy") or "Скопировать"
        self.btn_copy = QPushButton(copy_txt)
        self.btn_copy.setCursor(Qt.PointingHandCursor)
        self.btn_copy.setVisible(False)
        self._update_copy_btn_style()
        self.btn_copy.clicked.connect(self._copy_log)
        hdr_layout.addWidget(self.btn_copy)

        root_layout.addLayout(hdr_layout)

        # Expandable Log Box Container
        self.log_container = MacGlassCard(is_dark=self.is_dark, corner_radius=10)
        self.log_container.setFixedHeight(120)
        self.log_container.setVisible(False)

        c_layout = QVBoxLayout(self.log_container)
        c_layout.setContentsMargins(10, 8, 10, 8)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFrameShape(QFrame.NoFrame)
        self._update_log_style()
        c_layout.addWidget(self.log_edit)

        root_layout.addWidget(self.log_container)

    def append_log(self, text: str):
        self.log_edit.append(text)
        sb = self.log_edit.verticalScrollBar()
        if sb:
            sb.setValue(sb.maximum())

    def clear_log(self):
        self.log_edit.clear()

    def toggle_expansion(self):
        self.is_expanded = not self.is_expanded
        self.log_container.setVisible(self.is_expanded)
        self.btn_copy.setVisible(self.is_expanded)
        from localization import t
        if self.is_expanded:
            lbl = (t("installer.log_hide") or "Скрыть подробный журнал") + "  ▲"
        else:
            lbl = (t("installer.log_show") or "Показать подробный журнал") + "  ▼"
        self.btn_toggle.setText(lbl)

    def _copy_log(self):
        QApplication.clipboard().setText(self.log_edit.toPlainText())
        from localization import t
        copied_txt = t("installer.log_copied") or "Скопировано!"
        orig_txt = t("installer.log_copy") or "Скопировать"
        self.btn_copy.setText(copied_txt)
        QTimer.singleShot(1800, lambda: self.btn_copy.setText(orig_txt))

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.log_container.set_dark(is_dark)
        self._update_btn_style()
        self._update_copy_btn_style()
        self._update_log_style()

    def _update_btn_style(self):
        color = MacPalette.ACCENT_BLUE
        self.btn_toggle.setStyleSheet(f"""
            QPushButton {{
                color: {color};
                background: transparent;
                border: none;
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 11.5px;
                font-weight: 600;
                padding: 3px 6px;
            }}
            QPushButton:hover {{
                text-decoration: underline;
            }}
        """)

    def _update_copy_btn_style(self):
        bg = "rgba(255, 255, 255, 0.10)" if self.is_dark else "rgba(0, 0, 0, 0.06)"
        fg = "#FFFFFF" if self.is_dark else "#1D1D1F"
        border = "rgba(255, 255, 255, 0.15)" if self.is_dark else "rgba(0, 0, 0, 0.10)"
        self.btn_copy.setStyleSheet(f"""
            QPushButton {{
                color: {fg};
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 6px;
                font-family: 'SF Pro Text', 'Inter', sans-serif;
                font-size: 11px;
                font-weight: 600;
                padding: 3px 8px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.18);
            }}
        """)

    def _update_log_style(self):
        fg = "rgba(255, 255, 255, 0.88)" if self.is_dark else "rgba(0, 0, 0, 0.88)"
        bg = "rgba(0, 0, 0, 0.25)" if self.is_dark else "rgba(0, 0, 0, 0.04)"
        self.log_edit.setStyleSheet(f"""
            QTextEdit {{
                color: {fg};
                background-color: {bg};
                font-family: 'SF Mono', 'Fira Code', 'Ubuntu Mono', monospace;
                font-size: 10.5px;
                line-height: 1.4;
                border: none;
                border-radius: 6px;
            }}
        """)


