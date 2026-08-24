import os
import math
from urllib.parse import unquote
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from PySide6.QtCore import (
    Qt, Signal, QRectF, QPointF, QPropertyAnimation, QEasingCurve,
    Property, QSize, QTimer
)
from PySide6.QtGui import (
    QPainter, QColor, QPainterPath, QLinearGradient, QRadialGradient,
    QPen, QFont, QPixmap, QImage, QImageReader, QTransform, QPolygonF
)
from models.monitor import MonitorModel
from theme.colors import Colors, ThemeColors
from theme.typography import Typography
from theme.manager import ThemeManager
from backends.appearance_backend import AppearanceBackend


class WallpaperCache:
    """Cached scaled wallpaper pixmap to ensure zero lag on display renders."""
    _cached_uri = None
    _cached_pixmap = None
    _cached_size = None

    @classmethod
    def get_pixmap(cls, target_w: int, target_h: int) -> QPixmap | None:
        try:
            current_uri = AppearanceBackend().get_current_wallpaper()
            if not current_uri:
                return None

            path = current_uri
            if path.startswith("file://"):
                path = path[7:]
            path = unquote(path)

            if not os.path.exists(path):
                return None

            if (cls._cached_uri == path and cls._cached_pixmap is not None
                    and cls._cached_size == (target_w, target_h)):
                return cls._cached_pixmap

            reader = QImageReader(path)
            reader.setAutoTransform(True)
            orig_size = reader.size()
            if orig_size.isValid() and orig_size.width() > 0 and orig_size.height() > 0:
                scaled_size = orig_size.scaled(target_w, target_h, Qt.KeepAspectRatioByExpanding)
                reader.setScaledSize(scaled_size)
                img = reader.read()
                if not img.isNull():
                    pix = QPixmap.fromImage(img)
                    cls._cached_uri = path
                    cls._cached_pixmap = pix
                    cls._cached_size = (target_w, target_h)
                    return pix
        except Exception:
            pass
        return None


class EchoLogoCache:
    """Loads and caches the cropped official Echo liquid glass emblem."""
    _cropped_img: QImage | None = None

    @classmethod
    def get_image(cls) -> QImage | None:
        if cls._cropped_img is not None:
            return cls._cropped_img

        search_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "echo_icon.png"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "echo_icon.png"),
            "/usr/share/echo-settings/assets/echo_icon.png",
            "/usr/share/echo-settings/assets/icons/app_icon.png",
            "/usr/share/echo-settings/icon.png",
        ]
        for path in search_paths:
            if os.path.exists(path):
                img = QImage(path)
                if not img.isNull():
                    w, h = img.width(), img.height()
                    if w == 1024 and h == 1024:
                        cls._cropped_img = img.copy(194, 200, 632, 600)
                    else:
                        cls._cropped_img = img
                    return cls._cropped_img
        return None


def project_3d(x: float, y: float, z: float, yaw: float, pitch: float, cx: float, cy: float, focal: float = 850.0) -> QPointF:
    """
    Projects 3D point (x, y, z) in monitor-local coordinates onto the 2D plane at (cx, cy).
    Yaw = Y-axis rotation (radians), Pitch = X-axis rotation (radians).
    """
    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)
    cos_x = math.cos(pitch)
    sin_x = math.sin(pitch)

    # 1. Yaw rotation
    x1 = x * cos_y + z * sin_y
    y1 = y
    z1 = -x * sin_y + z * cos_y

    # 2. Pitch rotation
    x2 = x1
    y2 = y1 * cos_x - z1 * sin_x
    z2 = y1 * sin_x + z1 * cos_x

    # 3. Perspective projection
    scale = focal / (focal + z2)
    return QPointF(cx + x2 * scale, cy + y2 * scale)


class DisplayMonitorView(QWidget):
    """
    Realistic 3D Hardware Desktop Monitor Visualization (Grand Scale).
    Matches the exact proportions and stand architecture of the reference:
    - Grand physical size and presence
    - 3D perspective orientation (Yaw / Pitch)
    - Extruded dark chassis with rounded corners, side bevels, and specular chamfers
    - Recessed dark glossy glass screen with wallpaper, Fresnel highlights, and curved softbox sheen
    - Wide curved satin-brushed aluminum stand arm with oval cable pass-through hole
    - Broad, thin, beveled rectangular aluminum base plate with realistic floor drop shadows
    - Real official Echo liquid glass emblem logo centered on the bottom chin
    - Interactive micro-parallax tilt on mouse hover
    """
    clicked = Signal(str)  # monitor.id

    def __init__(self, monitor: MonitorModel, is_selected: bool = False,
                 base_yaw: float = 0.0, base_pitch: float = 0.040,
                 scale_factor: float = 1.0, is_primary_visual: bool = False, parent=None):
        super().__init__(parent)
        self.monitor = monitor
        self.is_selected = is_selected
        self.base_yaw = base_yaw
        self.base_pitch = base_pitch
        self.scale_factor = scale_factor
        self.is_primary_visual = is_primary_visual or monitor.is_primary

        # Interactive dynamic parallax
        self._target_yaw_offset = 0.0
        self._target_pitch_offset = 0.0
        self._current_yaw_offset = 0.0
        self._current_pitch_offset = 0.0

        # Animation states
        self._select_prog = 1.0 if is_selected else 0.0
        self._hover_prog = 0.0

        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setMinimumSize(320, 310)
        self.setMaximumHeight(380)

        # Smooth animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(16)
        self.anim_timer.timeout.connect(self._on_anim_tick)

        self.select_anim = QPropertyAnimation(self, b"select_prog")
        self.select_anim.setDuration(220)
        self.select_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.hover_anim = QPropertyAnimation(self, b"hover_prog")
        self.hover_anim.setDuration(180)
        self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)

    @Property(float)
    def select_prog(self):
        return self._select_prog

    @select_prog.setter
    def select_prog(self, val):
        self._select_prog = val
        self.update()

    @Property(float)
    def hover_prog(self):
        return self._hover_prog

    @hover_prog.setter
    def hover_prog(self, val):
        self._hover_prog = val
        self.update()

    def set_selected(self, selected: bool):
        if self.is_selected == selected:
            return
        self.is_selected = selected
        self.select_anim.stop()
        self.select_anim.setStartValue(self._select_prog)
        self.select_anim.setEndValue(1.0 if selected else 0.0)
        self.select_anim.start()

    def set_yaw(self, yaw: float):
        if self.base_yaw != yaw:
            self.base_yaw = yaw
            self.update()

    def set_scale_factor(self, scale: float):
        if self.scale_factor != scale:
            self.scale_factor = scale
            self.update()

    def enterEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self._hover_prog)
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()
        if not self.anim_timer.isActive():
            self.anim_timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self._hover_prog)
        self.hover_anim.setEndValue(0.0)
        self.hover_anim.start()
        self._target_yaw_offset = 0.0
        self._target_pitch_offset = 0.0
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position()
        w = self.width()
        h = self.height()
        norm_x = (pos.x() - w / 2.0) / (w / 2.0)
        norm_y = (pos.y() - h / 2.0) / (h / 2.0)
        self._target_yaw_offset = max(-1.0, min(1.0, norm_x)) * 0.022
        self._target_pitch_offset = -max(-1.0, min(1.0, norm_y)) * 0.012
        if not self.anim_timer.isActive():
            self.anim_timer.start()
        super().mouseMoveEvent(event)

    def _on_anim_tick(self):
        dy = (self._target_yaw_offset - self._current_yaw_offset) * 0.20
        dp = (self._target_pitch_offset - self._current_pitch_offset) * 0.20
        self._current_yaw_offset += dy
        self._current_pitch_offset += dp

        if abs(dy) < 0.0001 and abs(dp) < 0.0001 and self._hover_prog == 0.0:
            self._current_yaw_offset = self._target_yaw_offset
            self._current_pitch_offset = self._target_pitch_offset
            self.anim_timer.stop()

        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.monitor.id)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def sizeHint(self) -> QSize:
        return QSize(440, 345)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        w = float(self.width())
        h = float(self.height())
        is_dark = ThemeManager.is_dark

        # ── 1. Scale & Dimensions ──
        aspect = 16.0 / 9.0
        if self.monitor.width > 0 and self.monitor.height > 0:
            aspect = max(1.3, min(2.4, self.monitor.width / self.monitor.height))

        eff_scale = self.scale_factor * (1.0 + 0.016 * self._hover_prog + 0.012 * self._select_prog)

        panel_w = min(w - 44.0, 355.0) * eff_scale
        panel_h = (panel_w / aspect)
        panel_h = min(panel_h, 190.0 * eff_scale)
        panel_w = panel_h * aspect

        cx = w / 2.0
        cy = 22.0 + panel_h / 2.0

        yaw = self.base_yaw + self._current_yaw_offset
        pitch = self.base_pitch + self._current_pitch_offset
        focal = 850.0

        half_w = panel_w / 2.0
        half_h = panel_h / 2.0
        chassis_depth = 11.5

        # ── 2. Calculate 3D Panel Corners ──
        z_front = -chassis_depth / 2.0
        z_back = chassis_depth / 2.0

        f_tl = project_3d(-half_w, -half_h, z_front, yaw, pitch, cx, cy, focal)
        f_tr = project_3d(half_w, -half_h, z_front, yaw, pitch, cx, cy, focal)
        f_br = project_3d(half_w, half_h, z_front, yaw, pitch, cx, cy, focal)
        f_bl = project_3d(-half_w, half_h, z_front, yaw, pitch, cx, cy, focal)
        front_poly = QPolygonF([f_tl, f_tr, f_br, f_bl])

        b_tl = project_3d(-half_w, -half_h, z_back, yaw, pitch, cx, cy, focal)
        b_tr = project_3d(half_w, -half_h, z_back, yaw, pitch, cx, cy, focal)
        b_br = project_3d(half_w, half_h, z_back, yaw, pitch, cx, cy, focal)
        b_bl = project_3d(-half_w, half_h, z_back, yaw, pitch, cx, cy, focal)

        # ── 3. Desk Ground & Realistic Contact Shadows ──
        desk_y = cy + half_h + 48.0 * eff_scale
        base_cx = cx + math.sin(yaw) * 6.0
        base_center_y = desk_y + 10.0 * eff_scale
        base_w_front = 150.0 * eff_scale
        base_w_back = 130.0 * eff_scale
        base_depth = 40.0 * eff_scale
        base_thick = 4.0 * eff_scale

        # 3a. Ambient Soft Floor Shadow
        amb_w = 280.0 * eff_scale
        amb_h = 58.0 * eff_scale
        amb_rect = QRectF(base_cx - amb_w / 2.0, base_center_y + base_depth / 2.0 - 16.0, amb_w, amb_h)
        amb_grad = QRadialGradient(amb_rect.center(), amb_w / 2.0)
        amb_alpha = 50 if is_dark else 36
        amb_grad.setColorAt(0.0, QColor(0, 0, 0, amb_alpha))
        amb_grad.setColorAt(0.5, QColor(0, 0, 0, int(amb_alpha * 0.42)))
        amb_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(amb_grad)
        p.drawEllipse(amb_rect)

        # 3b. Tight Occluded Contact Shadow
        cont_w = base_w_front * 1.06
        cont_h = 16.0 * eff_scale
        cont_rect = QRectF(base_cx - cont_w / 2.0, base_center_y + base_depth / 2.0 - 8.0, cont_w, cont_h)
        cont_grad = QRadialGradient(cont_rect.center(), cont_w / 2.0)
        cont_alpha = 120 if is_dark else 85
        cont_grad.setColorAt(0.0, QColor(0, 0, 0, cont_alpha))
        cont_grad.setColorAt(0.65, QColor(0, 0, 0, int(cont_alpha * 0.35)))
        cont_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(cont_grad)
        p.drawEllipse(cont_rect)

        # ── 5. Stand Arm (Angled Cantilever Satin Aluminum Console with 3D Depth) ──
        neck_top_w = 33.0 * eff_scale
        neck_bot_w = 46.0 * eff_scale
        neck_top_pt = project_3d(0.0, half_h * 0.16, z_back + 1.0, yaw, pitch, cx, cy, focal)
        neck_bot_pt = QPointF(base_cx, desk_y - 1.0)

        neck_tl = QPointF(neck_top_pt.x() - neck_top_w / 2.0, neck_top_pt.y())
        neck_tr = QPointF(neck_top_pt.x() + neck_top_w / 2.0, neck_top_pt.y())
        neck_br = QPointF(neck_bot_pt.x() + neck_bot_w / 2.0, neck_bot_pt.y())
        neck_bl = QPointF(neck_bot_pt.x() - neck_bot_w / 2.0, neck_bot_pt.y())
        neck_poly = QPolygonF([neck_tl, neck_tr, neck_br, neck_bl])

        # 5a. 3D Side Depth of Stand Arm (visible when angled)
        arm_depth_x = -yaw * 5.5 * eff_scale
        if yaw < -0.015:
            # Left monitor turned right -> Left facet of arm is visible
            arm_side_tl = QPointF(neck_tl.x() + arm_depth_x, neck_tl.y())
            arm_side_bl = QPointF(neck_bl.x() + arm_depth_x, neck_bl.y())
            arm_side_poly = QPolygonF([arm_side_tl, neck_tl, neck_bl, arm_side_bl])
            p.setBrush(QColor("#7A7A84") if not is_dark else QColor("#222228"))
            p.setPen(Qt.NoPen)
            p.drawPolygon(arm_side_poly)
        elif yaw > 0.015:
            # Right monitor turned left -> Right facet of arm is visible
            arm_side_tr = QPointF(neck_tr.x() + arm_depth_x, neck_tr.y())
            arm_side_br = QPointF(neck_br.x() + arm_depth_x, neck_br.y())
            arm_side_poly = QPolygonF([neck_tr, arm_side_tr, arm_side_br, neck_br])
            p.setBrush(QColor("#8E8E98") if not is_dark else QColor("#282830"))
            p.setPen(Qt.NoPen)
            p.drawPolygon(arm_side_poly)

        # 5b. Front Satin Face of Stand Arm
        neck_grad = QLinearGradient(neck_tl, neck_tr)
        if is_dark:
            neck_grad.setColorAt(0.0, QColor("#34343A"))
            neck_grad.setColorAt(0.28, QColor("#666672"))
            neck_grad.setColorAt(0.70, QColor("#8E8E9C"))
            neck_grad.setColorAt(1.0, QColor("#28282E"))
        else:
            neck_grad.setColorAt(0.0, QColor("#B4B4BA"))
            neck_grad.setColorAt(0.35, QColor("#ECECF2"))
            neck_grad.setColorAt(0.70, QColor("#F8F8FC"))
            neck_grad.setColorAt(1.0, QColor("#9A9AA0"))

        p.setPen(Qt.NoPen)
        p.setBrush(neck_grad)
        p.drawPolygon(neck_poly)

        # Specular Highlight Lines on Outer Arm Edges
        p.setPen(QPen(QColor(255, 255, 255, 80 if not is_dark else 35), 0.8))
        p.drawLine(neck_tl, neck_bl)
        p.setPen(QPen(QColor(255, 255, 255, 45 if not is_dark else 20), 0.8))
        p.drawLine(neck_tr, neck_br)

        # 5c. 3D Cable Pass-Through Hole (Precisely centered in visible arm portion)
        chin_bot_y = (f_bl.y() + f_br.y()) / 2.0
        hole_cx = (neck_top_pt.x() + neck_bot_pt.x()) / 2.0
        hole_cy = (chin_bot_y + desk_y) / 2.0 - 2.0
        hole_w = 11.5 * eff_scale
        hole_h = 16.0 * eff_scale
        hole_rect = QRectF(hole_cx - hole_w / 2.0, hole_cy - hole_h / 2.0, hole_w, hole_h)
        hole_path = QPainterPath()
        hole_path.addRoundedRect(hole_rect, hole_w / 2.0, hole_w / 2.0)

        hole_bg = QColor("#121316") if is_dark else QColor("#5A5B62")
        p.setBrush(hole_bg)
        p.setPen(QPen(QColor(255, 255, 255, 65 if not is_dark else 28), 0.8))
        p.drawPath(hole_path)

        # ── 6. 3D Broad Thin Beveled Aluminum Base Plate ──
        # Top 4 Corners
        bt_tl = QPointF(base_cx - base_w_back / 2.0 - yaw * 8.0, base_center_y - base_depth / 2.0)
        bt_tr = QPointF(base_cx + base_w_back / 2.0 - yaw * 8.0, base_center_y - base_depth / 2.0)
        bt_br = QPointF(base_cx + base_w_front / 2.0 + yaw * 8.0, base_center_y + base_depth / 2.0)
        bt_bl = QPointF(base_cx - base_w_front / 2.0 + yaw * 8.0, base_center_y + base_depth / 2.0)

        # Bottom 4 Corners (+ base_thick)
        bb_bl = QPointF(bt_bl.x(), bt_bl.y() + base_thick)
        bb_br = QPointF(bt_br.x(), bt_br.y() + base_thick)
        bb_tl = QPointF(bt_tl.x(), bt_tl.y() + base_thick)
        bb_tr = QPointF(bt_tr.x(), bt_tr.y() + base_thick)

        # 6a. Side Thickness Facet
        if yaw > 0.015:
            b_side_poly = QPolygonF([bt_tl, bt_bl, bb_bl, bb_tl])
            side_color = QColor("#2A2A30") if is_dark else QColor("#9898A0")
            p.setBrush(side_color)
            p.setPen(Qt.NoPen)
            p.drawPolygon(b_side_poly)
        elif yaw < -0.015:
            b_side_poly = QPolygonF([bt_tr, bt_br, bb_br, bb_tr])
            side_color = QColor("#2A2A30") if is_dark else QColor("#9898A0")
            p.setBrush(side_color)
            p.setPen(Qt.NoPen)
            p.drawPolygon(b_side_poly)

        # 6b. Front Thickness Facet
        b_front_poly = QPolygonF([bt_bl, bt_br, bb_br, bb_bl])
        front_grad = QLinearGradient(bt_bl, bt_br)
        if is_dark:
            front_grad.setColorAt(0.0, QColor("#38383E"))
            front_grad.setColorAt(0.5, QColor("#505058"))
            front_grad.setColorAt(1.0, QColor("#303036"))
        else:
            front_grad.setColorAt(0.0, QColor("#B0B0B6"))
            front_grad.setColorAt(0.5, QColor("#D8D8E0"))
            front_grad.setColorAt(1.0, QColor("#A8A8B0"))
        p.setBrush(front_grad)
        p.setPen(Qt.NoPen)
        p.drawPolygon(b_front_poly)

        # 6c. Top Surface Satin Aluminum
        b_top_poly = QPolygonF([bt_tl, bt_tr, bt_br, bt_bl])
        top_grad = QLinearGradient(bt_tl, bt_br)
        if is_dark:
            top_grad.setColorAt(0.0, QColor("#2D2D33"))
            top_grad.setColorAt(0.40, QColor("#464650"))
            top_grad.setColorAt(0.70, QColor("#5A5A66"))
            top_grad.setColorAt(1.0, QColor("#36363E"))
        else:
            top_grad.setColorAt(0.0, QColor("#E4E4EB"))
            top_grad.setColorAt(0.40, QColor("#FFFFFF"))
            top_grad.setColorAt(0.75, QColor("#F4F4F8"))
            top_grad.setColorAt(1.0, QColor("#D2D2DA"))
        p.setBrush(top_grad)
        p.setPen(Qt.NoPen)
        p.drawPolygon(b_top_poly)

        # Front Top Rim Specular Chamfer Line
        p.setPen(QPen(QColor(255, 255, 255, 160 if not is_dark else 60), 0.9))
        p.drawLine(bt_bl, bt_br)

        # ── 7. Extruded Chassis Side & Top Depth Facets ──
        top_facet = QPolygonF([f_tl, f_tr, b_tr, b_tl])
        top_facet_grad = QLinearGradient(b_tl, f_tl)
        top_facet_grad.setColorAt(0.0, QColor("#141518") if is_dark else QColor("#222327"))
        top_facet_grad.setColorAt(0.85, QColor("#2A2C32") if is_dark else QColor("#40434C"))
        top_facet_grad.setColorAt(1.0, QColor("#3A3D46") if is_dark else QColor("#565A66"))
        p.setPen(Qt.NoPen)
        p.setBrush(top_facet_grad)
        p.drawPolygon(top_facet)

        if yaw > 0.01:
            side_facet = QPolygonF([f_tl, f_bl, b_bl, b_tl])
            side_facet_grad = QLinearGradient(b_tl, f_tl)
            side_facet_grad.setColorAt(0.0, QColor("#101113"))
            side_facet_grad.setColorAt(0.7, QColor("#1E1F24"))
            side_facet_grad.setColorAt(1.0, QColor("#303239"))
            p.setBrush(side_facet_grad)
            p.drawPolygon(side_facet)
        elif yaw < -0.01:
            side_facet = QPolygonF([f_tr, f_br, b_br, b_tr])
            side_facet_grad = QLinearGradient(f_tr, b_tr)
            side_facet_grad.setColorAt(0.0, QColor("#303239"))
            side_facet_grad.setColorAt(0.3, QColor("#1E1F24"))
            side_facet_grad.setColorAt(1.0, QColor("#101113"))
            p.setBrush(side_facet_grad)
            p.drawPolygon(side_facet)

        # ── 8. Front Bezel Frame ──
        front_grad = QLinearGradient(f_tl, f_bl)
        front_grad.setColorAt(0.0, QColor("#222327"))
        front_grad.setColorAt(0.80, QColor("#16171A"))
        front_grad.setColorAt(1.0, QColor("#101013"))
        p.setPen(Qt.NoPen)
        p.setBrush(front_grad)
        p.drawPolygon(front_poly)

        # ── 9. Recessed Screen & Wallpaper ──
        bz_top = 2.8 * eff_scale
        bz_side = 2.8 * eff_scale
        bz_chin = 14.5 * eff_scale

        s_tl_3d = (-half_w + bz_side, -half_h + bz_top, z_front + 0.5)
        s_tr_3d = (half_w - bz_side, -half_h + bz_top, z_front + 0.5)
        s_br_3d = (half_w - bz_side, half_h - bz_chin, z_front + 0.5)
        s_bl_3d = (-half_w + bz_side, half_h - bz_chin, z_front + 0.5)

        s_tl = project_3d(*s_tl_3d, yaw, pitch, cx, cy, focal)
        s_tr = project_3d(*s_tr_3d, yaw, pitch, cx, cy, focal)
        s_br = project_3d(*s_br_3d, yaw, pitch, cx, cy, focal)
        s_bl = project_3d(*s_bl_3d, yaw, pitch, cx, cy, focal)
        screen_poly = QPolygonF([s_tl, s_tr, s_br, s_bl])

        # Recessed Screen Pocket Shadow (Ambient Occlusion inside bezel)
        p.setBrush(QColor(0, 0, 0, 190))
        p.setPen(Qt.NoPen)
        p.drawPolygon(screen_poly)

        p.save()
        clip_path = QPainterPath()
        clip_path.addPolygon(screen_poly)
        p.setClipPath(clip_path)

        # 9a. Real System Wallpaper (Perspective Mapped)
        tex_w = max(100, int(panel_w - bz_side * 2))
        tex_h = max(60, int(panel_h - bz_top - bz_chin))
        pix = WallpaperCache.get_pixmap(tex_w, tex_h)

        if pix and not pix.isNull():
            src_poly = QPolygonF([
                QPointF(0, 0),
                QPointF(pix.width(), 0),
                QPointF(pix.width(), pix.height()),
                QPointF(0, pix.height())
            ])
            trans = QTransform()
            ok = QTransform.quadToQuad(src_poly, screen_poly, trans)
            if ok:
                p.save()
                p.setTransform(trans, True)
                p.drawPixmap(0, 0, pix)
                p.restore()
            else:
                p.drawPixmap(QRectF(s_tl.x(), s_tl.y(), panel_w, panel_h), pix)
        else:
            # Clean dark fallback if no system wallpaper is found
            bg_grad = QLinearGradient(s_tl, s_br)
            bg_grad.setColorAt(0.0, QColor("#080D1A"))
            bg_grad.setColorAt(0.5, QColor("#111A2E"))
            bg_grad.setColorAt(1.0, QColor("#050810"))
            p.setBrush(bg_grad)
            p.setPen(Qt.NoPen)
            p.drawPolygon(screen_poly)

        # 9b. Soft Inner Bezel Drop Shadow
        inner_sh_grad = QLinearGradient(s_tl, QPointF(s_tl.x(), s_tl.y() + 6.0))
        inner_sh_grad.setColorAt(0.0, QColor(0, 0, 0, 140))
        inner_sh_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(inner_sh_grad)
        p.drawPolygon(screen_poly)

        # 9c. Studio Ambient Diagonal Curved Glass Sheen Reflection
        glass_grad = QLinearGradient(s_tl, s_br)
        glass_grad.setColorAt(0.0, QColor(255, 255, 255, 40))
        glass_grad.setColorAt(0.34, QColor(255, 255, 255, 12))
        glass_grad.setColorAt(0.35, QColor(255, 255, 255, 0))
        glass_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(glass_grad)
        p.drawPolygon(screen_poly)

        # 9d. Fresnel Edge Ambient Highlight
        fresnel_grad = QLinearGradient(s_tl, s_tr)
        fresnel_grad.setColorAt(0.0, QColor(255, 255, 255, 30))
        fresnel_grad.setColorAt(0.12, QColor(255, 255, 255, 0))
        fresnel_grad.setColorAt(0.88, QColor(255, 255, 255, 0))
        fresnel_grad.setColorAt(1.0, QColor(255, 255, 255, 20))
        p.setBrush(fresnel_grad)
        p.drawPolygon(screen_poly)

        p.restore()

        # ── 10. Bottom Chin Separator & Official Real Echo Logo ──
        p.setPen(QPen(QColor(255, 255, 255, 25), 0.7))
        p.drawLine(s_bl, s_br)

        chin_pt_3d = (0.0, half_h - bz_chin / 2.0 + 0.5, z_front)
        chin_pt = project_3d(*chin_pt_3d, yaw, pitch, cx, cy, focal)

        p.save()
        p.translate(chin_pt.x(), chin_pt.y())
        p.rotate(yaw * (180.0 / math.pi) * 0.35)

        logo_img = EchoLogoCache.get_image()
        logo_alpha = 235 if is_dark else 190

        font = QFont(Typography.FONT_FAMILY, 7, QFont.Medium)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 0.4)
        p.setFont(font)
        fm = p.fontMetrics()
        text_str = "Echo"
        text_w = fm.horizontalAdvance(text_str)

        icon_h = 8.5 * eff_scale
        icon_w = icon_h * (632.0 / 600.0) if (logo_img and not logo_img.isNull()) else icon_h
        spacing = 3.5 * eff_scale
        total_w = icon_w + spacing + text_w

        start_x = -total_w / 2.0
        icon_rect = QRectF(start_x, -icon_h / 2.0, icon_w, icon_h)

        if logo_img and not logo_img.isNull():
            p.setOpacity(logo_alpha / 255.0)
            p.drawImage(icon_rect, logo_img)
            p.setOpacity(1.0)
        else:
            p.setPen(QPen(QColor(255, 255, 255, logo_alpha), 1.2))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(icon_rect)

        p.setPen(QColor(255, 255, 255, logo_alpha))
        text_rect = QRectF(start_x + icon_w + spacing, -6.0, text_w + 4.0, 12.0)
        p.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text_str)
        p.restore()

        # ── 11. Top Outer Chamfer Light Catch Line ──
        p.setPen(QPen(QColor(255, 255, 255, 115 if is_dark else 70), 0.8))
        p.drawLine(f_tl, f_tr)

        # ── 12. Active Selection Accent / Blue Frame Outline ──
        if self._select_prog > 0.01 or self.is_primary_visual:
            accent_prog = max(self._select_prog, 1.0 if self.is_primary_visual else 0.0)
            blue = QColor(Colors.ACCENT_BLUE)
            accent_color = QColor(blue.red(), blue.green(), blue.blue(), int(220 * accent_prog))
            p.setPen(QPen(accent_color, 1.5))
            p.setBrush(Qt.NoBrush)
            p.drawPolygon(front_poly)


class DisplayStageWidget(QWidget):
    """
    Studio Stage container managing multi-monitor 3D perspective layout.
    Arranges displays in studio space exactly matching the hardware reference:
    - Primary display: Foreground, grand scale (1.06x), slight right yaw (-0.13 rad), volumetric blue halo
    - Secondary display: Background, matching perspective (+0.15 rad), silver monochrome theme
    - Full synchronization with Mutter backend and Display Summary Cards
    """
    monitor_selected = Signal(str)  # monitor.id

    def __init__(self, monitors: list[MonitorModel], active_id: str = None, parent=None):
        super().__init__(parent)
        self.monitors = monitors or []
        self.active_id = active_id or (self.monitors[0].id if self.monitors else "")
        self.monitor_views: list[DisplayMonitorView] = []

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(330)
        self.setMaximumHeight(380)

        self._build_stage()

    def _build_stage(self):
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(6, 2, 6, 2)
            layout.setSpacing(20)
            layout.setAlignment(Qt.AlignCenter)
            self.setLayout(layout)

        self.monitor_views.clear()

        if not self.monitors:
            return

        sorted_monitors = sorted(self.monitors, key=lambda m: m.x)
        num_monitors = len(sorted_monitors)

        for i, mon in enumerate(sorted_monitors):
            is_sel = (mon.id == self.active_id)
            is_prim = mon.is_primary

            if num_monitors == 1:
                yaw = 0.0
                scale = 1.0
                is_prim_vis = True
            elif num_monitors == 2:
                yaw = -0.11 if i == 0 else 0.13
                scale = 1.04 if is_prim or (i == 0) else 0.90
                is_prim_vis = is_prim or (i == 0)
            else:
                t_pos = (i / (num_monitors - 1.0)) * 2.0 - 1.0
                yaw = t_pos * 0.14
                scale = 1.04 if is_prim else 0.88
                is_prim_vis = is_prim

            view = DisplayMonitorView(
                mon,
                is_selected=is_sel,
                base_yaw=yaw,
                base_pitch=0.038,
                scale_factor=scale,
                is_primary_visual=is_prim_vis
            )
            view.clicked.connect(self._on_view_clicked)
            self.layout().addWidget(view)
            self.monitor_views.append(view)

    def set_active_monitor(self, monitor_id: str):
        self.active_id = monitor_id
        for v in self.monitor_views:
            v.set_selected(v.monitor.id == monitor_id)

    def update_monitors(self, monitors: list[MonitorModel], active_id: str = None):
        self.monitors = monitors
        if active_id:
            self.active_id = active_id
        elif not any(m.id == self.active_id for m in self.monitors) and self.monitors:
            self.active_id = self.monitors[0].id
        self._build_stage()

    def _on_view_clicked(self, monitor_id: str):
        self.set_active_monitor(monitor_id)
        self.monitor_selected.emit(monitor_id)
