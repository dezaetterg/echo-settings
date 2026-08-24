"""
Vector Icons Engine for Echo Settings.
Renders high-precision, anti-aliased Apple SF Symbols style vector icons
using QPainterPath and SVG rendering for maximum visual fidelity and DPI scaling.
"""

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPainterPath, QPen, QBrush, QPixmap, QLinearGradient
)


class VectorIcons:
    """Renders Apple-style vector iconography with pure geometric paths."""

    @staticmethod
    def draw_sunrise(p: QPainter, rect: QRectF, color: QColor):
        """SF Symbol: sun.and.horizon (Sunrise)"""
        p.save()
        p.setRenderHint(QPainter.Antialiasing)

        cx = rect.center().x()
        cy = rect.center().y()
        w = rect.width()
        h = rect.height()

        # Horizon line
        horizon_y = cy + h * 0.18
        p.setPen(QPen(color, max(1.2, w * 0.08), Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(cx - w * 0.42, horizon_y), QPointF(cx + w * 0.42, horizon_y))

        # Rising sun dome
        r = w * 0.24
        dome_rect = QRectF(cx - r, horizon_y - r, r * 2, r * 2)
        dome_path = QPainterPath()
        dome_path.arcMoveTo(dome_rect, 0)
        dome_path.arcTo(dome_rect, 0, 180)
        dome_path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawPath(dome_path)

        # 3 Top Radiating Rays
        p.setPen(QPen(color, max(1.2, w * 0.075), Qt.SolidLine, Qt.RoundCap))
        # Top ray
        p.drawLine(QPointF(cx, horizon_y - r - h * 0.06), QPointF(cx, horizon_y - r - h * 0.22))
        # Top-left 45 deg ray
        p.drawLine(QPointF(cx - r * 0.85, horizon_y - r * 0.85), QPointF(cx - r * 1.3, horizon_y - r * 1.3))
        # Top-right 45 deg ray
        p.drawLine(QPointF(cx + r * 0.85, horizon_y - r * 0.85), QPointF(cx + r * 1.3, horizon_y - r * 1.3))

        p.restore()

    @staticmethod
    def draw_sun(p: QPainter, rect: QRectF, color: QColor):
        """SF Symbol: sun.max (Noon / Full Sun)"""
        p.save()
        p.setRenderHint(QPainter.Antialiasing)

        cx = rect.center().x()
        cy = rect.center().y()
        w = rect.width()

        # Center core disc
        r = w * 0.22
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawEllipse(QPointF(cx, cy), r, r)

        # 8 Radiating Rays
        p.setPen(QPen(color, max(1.2, w * 0.08), Qt.SolidLine, Qt.RoundCap))
        ray_in = r + w * 0.08
        ray_out = r + w * 0.22

        # 0, 90, 180, 270 deg
        p.drawLine(QPointF(cx, cy - ray_in), QPointF(cx, cy - ray_out))
        p.drawLine(QPointF(cx, cy + ray_in), QPointF(cx, cy + ray_out))
        p.drawLine(QPointF(cx - ray_in, cy), QPointF(cx - ray_out, cy))
        p.drawLine(QPointF(cx + ray_in, cy), QPointF(cx + ray_out, cy))

        # Diagonal 45 deg rays (0.707 factor)
        d_in = ray_in * 0.707
        d_out = ray_out * 0.707
        p.drawLine(QPointF(cx - d_in, cy - d_in), QPointF(cx - d_out, cy - d_out))
        p.drawLine(QPointF(cx + d_in, cy - d_in), QPointF(cx + d_out, cy - d_out))
        p.drawLine(QPointF(cx - d_in, cy + d_in), QPointF(cx - d_out, cy + d_out))
        p.drawLine(QPointF(cx + d_in, cy + d_in), QPointF(cx + d_out, cy + d_out))

        p.restore()

    @staticmethod
    def draw_sunset(p: QPainter, rect: QRectF, color: QColor):
        """SF Symbol: sunset (Sunset / Golden Hour)"""
        p.save()
        p.setRenderHint(QPainter.Antialiasing)

        cx = rect.center().x()
        cy = rect.center().y()
        w = rect.width()
        h = rect.height()

        # Horizon line
        horizon_y = cy + h * 0.08
        p.setPen(QPen(color, max(1.2, w * 0.08), Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(cx - w * 0.42, horizon_y), QPointF(cx + w * 0.42, horizon_y))

        # Setting sun disc (clipped by horizon)
        r = w * 0.24
        dome_rect = QRectF(cx - r, horizon_y - r * 0.7, r * 2, r * 2)
        dome_path = QPainterPath()
        dome_path.arcMoveTo(dome_rect, 0)
        dome_path.arcTo(dome_rect, 0, 180)
        dome_path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawPath(dome_path)

        # Downward indicator arrow below horizon
        arrow_y1 = horizon_y + h * 0.16
        arrow_y2 = horizon_y + h * 0.32
        p.setPen(QPen(color, max(1.1, w * 0.07), Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(cx, arrow_y1), QPointF(cx, arrow_y2))
        p.drawLine(QPointF(cx - w * 0.12, arrow_y2 - h * 0.09), QPointF(cx, arrow_y2))
        p.drawLine(QPointF(cx + w * 0.12, arrow_y2 - h * 0.09), QPointF(cx, arrow_y2))

        # Top sunset ray
        p.drawLine(QPointF(cx, horizon_y - r * 0.7 - h * 0.06), QPointF(cx, horizon_y - r * 0.7 - h * 0.18))

        p.restore()

    @staticmethod
    def draw_moon(p: QPainter, rect: QRectF, color: QColor):
        """SF Symbol: moon.stars (Night / Stars)"""
        p.save()
        p.setRenderHint(QPainter.Antialiasing)

        cx = rect.center().x()
        cy = rect.center().y()
        w = rect.width()

        # Crescent Moon
        moon_r = w * 0.34
        outer_circle = QPainterPath()
        outer_circle.addEllipse(QPointF(cx - w * 0.06, cy), moon_r, moon_r)

        inner_cutter = QPainterPath()
        inner_cutter.addEllipse(QPointF(cx + w * 0.08, cy - w * 0.06), moon_r * 0.92, moon_r * 0.92)

        crescent = outer_circle.subtracted(inner_cutter)
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawPath(crescent)

        # Micro Star 1 (Top right)
        s1_x = cx + w * 0.28
        s1_y = cy - w * 0.22
        s1_r = w * 0.075
        star1 = QPainterPath()
        star1.moveTo(s1_x, s1_y - s1_r)
        star1.quadTo(s1_x, s1_y, s1_x + s1_r, s1_y)
        star1.quadTo(s1_x, s1_y, s1_x, s1_y + s1_r)
        star1.quadTo(s1_x, s1_y, s1_x - s1_r, s1_y)
        star1.quadTo(s1_x, s1_y, s1_x, s1_y - s1_r)
        p.drawPath(star1)

        # Micro Star 2 (Bottom right)
        s2_x = cx + w * 0.34
        s2_y = cy + w * 0.16
        s2_r = w * 0.05
        star2 = QPainterPath()
        star2.moveTo(s2_x, s2_y - s2_r)
        star2.quadTo(s2_x, s2_y, s2_x + s2_r, s2_y)
        star2.quadTo(s2_x, s2_y, s2_x, s2_y + s2_r)
        star2.quadTo(s2_x, s2_y, s2_x - s2_r, s2_y)
        star2.quadTo(s2_x, s2_y, s2_x, s2_y - s2_r)
        p.drawPath(star2)

        p.restore()

    @staticmethod
    def draw_cycle_24h(p: QPainter, rect: QRectF, color: QColor):
        """SF Symbol: clock.arrow.2.circlepath (24h Dynamic Cycle)"""
        p.save()
        p.setRenderHint(QPainter.Antialiasing)

        cx = rect.center().x()
        cy = rect.center().y()
        w = rect.width()
        r = w * 0.36

        # Dual sweeping circular arcs
        p.setPen(QPen(color, max(1.4, w * 0.09), Qt.SolidLine, Qt.RoundCap))
        
        # Arc 1: Top Right to Bottom
        arc1_rect = QRectF(cx - r, cy - r, r * 2, r * 2)
        p.drawArc(arc1_rect, int(30 * 16), int(130 * 16))
        
        # Arc 2: Bottom Left to Top
        p.drawArc(arc1_rect, int(210 * 16), int(130 * 16))

        # Arrowhead 1
        p.setBrush(color)
        p.setPen(Qt.NoPen)
        a1_x = cx + r * 0.96
        a1_y = cy - r * 0.28
        a1_path = QPainterPath()
        a1_path.moveTo(a1_x, a1_y)
        a1_path.lineTo(a1_x - w * 0.16, a1_y - w * 0.08)
        a1_path.lineTo(a1_x - w * 0.08, a1_y + w * 0.12)
        a1_path.closeSubpath()
        p.drawPath(a1_path)

        # Arrowhead 2
        a2_x = cx - r * 0.96
        a2_y = cy + r * 0.28
        a2_path = QPainterPath()
        a2_path.moveTo(a2_x, a2_y)
        a2_path.lineTo(a2_x + w * 0.16, a2_y + w * 0.08)
        a2_path.lineTo(a2_x + w * 0.08, a2_y - w * 0.12)
        a2_path.closeSubpath()
        p.drawPath(a2_path)

        p.restore()

    @staticmethod
    def draw_plus(p: QPainter, rect: QRectF, color: QColor):
        """Minimalist crisp plus icon"""
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        cx = rect.center().x()
        cy = rect.center().y()
        w = rect.width()
        arm = w * 0.32
        p.setPen(QPen(color, max(1.5, w * 0.11), Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(cx - arm, cy), QPointF(cx + arm, cy))
        p.drawLine(QPointF(cx, cy - arm), QPointF(cx, cy + arm))
        p.restore()

    @classmethod
    def render_pixmap(cls, icon_type: str, size: int = 24, color: QColor = None) -> QPixmap:
        """Renders any vector icon into a high-DPI transparent QPixmap."""
        if color is None:
            color = QColor("#FFFFFF")
        scale = 2  # 2x Retina rendering
        pix = QPixmap(size * scale, size * scale)
        pix.fill(Qt.transparent)
        pix.setDevicePixelRatio(scale)

        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(0, 0, size, size)

        if icon_type == "sunrise" or icon_type == "morning":
            cls.draw_sunrise(p, rect, color)
        elif icon_type == "sun" or icon_type == "day":
            cls.draw_sun(p, rect, color)
        elif icon_type == "sunset":
            cls.draw_sunset(p, rect, color)
        elif icon_type == "moon" or icon_type == "night":
            cls.draw_moon(p, rect, color)
        elif icon_type == "cycle" or icon_type == "24h":
            cls.draw_cycle_24h(p, rect, color)
        elif icon_type == "plus":
            cls.draw_plus(p, rect, color)
        else:
            cls.draw_sun(p, rect, color)

        p.end()
        return pix
