import os
import urllib.parse
import shutil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QGridLayout,
    QSizePolicy, QPushButton, QGraphicsDropShadowEffect, QFrame
)
from PySide6.QtCore import (
    Qt, Property, QPropertyAnimation, QEasingCurve, QRectF, Signal,
    QPointF, QTimer, QFileSystemWatcher, QSize
)
from PySide6.QtGui import (
    QPainter, QColor, QPainterPath, QPixmap, QPen, QImageReader, QFont,
    QRadialGradient, QLinearGradient
)

from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from theme.glass_shimmer import GlassShimmerHelper
from theme.vector_icons import VectorIcons
from localization import tr


def _load_pixmap_thumbnail(image_path: str, target_size: QSize = QSize(300, 200)) -> QPixmap:
    """Load reduced thumbnail using QImageReader to avoid decoding full 4K/5K in RAM."""
    if not image_path or not os.path.exists(image_path):
        return None
    folder = os.path.dirname(image_path)
    preview_candidates = [
        os.path.join(folder, "preview.jpg"),
        os.path.join(folder, "preview.png"),
        os.path.join(folder, "preview.jpeg")
    ]
    read_path = image_path
    for cand in preview_candidates:
        if os.path.exists(cand):
            read_path = cand
            break

    try:
        reader = QImageReader(read_path)
        reader.setAutoTransform(True)
        reader.setScaledSize(target_size)
        img = reader.read()
        if not img.isNull():
            return QPixmap.fromImage(img)
    except Exception:
        pass
    return QPixmap(image_path)


class WallpaperCard(QWidget):
    clicked = Signal()
    delete_clicked = Signal()

    def __init__(
        self,
        title: str,
        light_path: str,
        dark_path: str,
        is_selected: bool = False,
        is_dark: bool = False,
        is_custom: bool = False
    ):
        super().__init__()
        self.setFixedHeight(122)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)

        self.title = title
        self.is_selected = is_selected
        self._scale = 1.0
        self._hover_alpha = 0.0
        self._active_alpha = 1.0 if is_selected else 0.0
        self.is_custom = is_custom

        self.light_path = light_path
        self.dark_path = dark_path
        self.is_dark = is_dark
        self.is_dummy = False
        self.original_pixmap = None
        self.scaled_pixmap = None

        # Liquid glass specular shimmer
        self.shimmer = GlassShimmerHelper(self)

        image_path = dark_path if is_dark else light_path
        if not (image_path and os.path.exists(image_path)):
            self.is_dummy = True

        self.hover_anim = QPropertyAnimation(self, b"scale_factor")
        self.hover_anim.setDuration(180)
        self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.alpha_anim = QPropertyAnimation(self, b"hover_alpha")
        self.alpha_anim.setDuration(180)

        self.active_anim = QPropertyAnimation(self, b"active_alpha")
        self.active_anim.setDuration(180)
        self.active_anim.setEasingCurve(QEasingCurve.OutCubic)

        if self.is_custom:
            self.del_btn = QPushButton("✕", self)
            self.del_btn.setFixedSize(22, 22)
            self.del_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 160);
                    color: white;
                    border-radius: 11px;
                    font-weight: bold;
                    font-size: 10px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                QPushButton:hover {
                    background-color: rgba(255, 59, 48, 220);
                }
            """)
            self.del_btn.setCursor(Qt.PointingHandCursor)
            self.del_btn.clicked.connect(self.delete_clicked.emit)
            self.del_btn.hide()
        else:
            self.del_btn = None

    def _ensure_pixmap(self):
        if self.original_pixmap is None and not self.is_dummy:
            image_path = self.dark_path if self.is_dark else self.light_path
            if image_path and os.path.exists(image_path):
                self.original_pixmap = _load_pixmap_thumbnail(image_path, QSize(300, 200))
            else:
                self.is_dummy = True

    def set_selected(self, selected: bool):
        if self.is_selected == selected:
            return
        self.is_selected = selected

        self.active_anim.stop()
        self.active_anim.setDirection(QPropertyAnimation.Forward)
        self.active_anim.setStartValue(self._active_alpha)
        self.active_anim.setEndValue(1.0 if selected else 0.0)
        self.active_anim.start()
        self.update()

    def update_theme(self, is_dark: bool):
        if not self.light_path and not self.dark_path:
            return
        self.is_dark = is_dark
        self.original_pixmap = None
        self.scaled_pixmap = None
        self._update_scaled_pixmap()
        self.update()

    @Property(float)
    def scale_factor(self): return self._scale
    @scale_factor.setter
    def scale_factor(self, s):
        self._scale = s
        self.update()

    @Property(float)
    def hover_alpha(self): return self._hover_alpha
    @hover_alpha.setter
    def hover_alpha(self, a):
        self._hover_alpha = a
        self.update()

    @Property(float)
    def active_alpha(self): return self._active_alpha
    @active_alpha.setter
    def active_alpha(self, a):
        self._active_alpha = a
        self.update()

    def enterEvent(self, event):
        self.shimmer.handle_enter(event)
        if not self.is_selected:
            self.hover_anim.setDirection(QPropertyAnimation.Forward)
            self.hover_anim.setStartValue(self._scale)
            self.hover_anim.setEndValue(1.04)
            self.hover_anim.start()

            self.alpha_anim.setDirection(QPropertyAnimation.Forward)
            self.alpha_anim.setStartValue(self._hover_alpha)
            self.alpha_anim.setEndValue(25.0)
            self.alpha_anim.start()

        if self.del_btn:
            self.del_btn.show()
            self.del_btn.raise_()

        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shimmer.handle_leave(event)
        self.hover_anim.stop()
        self.hover_anim.setDirection(QPropertyAnimation.Forward)
        self.hover_anim.setStartValue(self._scale)
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()

        self.alpha_anim.setDirection(QPropertyAnimation.Backward)
        self.alpha_anim.setStartValue(self._hover_alpha)
        self.alpha_anim.setEndValue(0.0)
        self.alpha_anim.start()

        if self.del_btn:
            self.del_btn.hide()

        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        self.shimmer.handle_mouse_move(event)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scaled_pixmap()
        if self.del_btn:
            self.del_btn.move(self.width() - 28, 10)

    def _update_scaled_pixmap(self):
        self._ensure_pixmap()
        if self.original_pixmap and not self.original_pixmap.isNull():
            rect = self.rect()
            w = rect.width() - 16
            h = rect.height() - 28
            if w > 0 and h > 0:
                self.scaled_pixmap = self.original_pixmap.scaled(
                    int(w), int(h),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

    def paintEvent(self, event):
        if self.scaled_pixmap is None and not self.is_dummy:
            self._update_scaled_pixmap()

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.setRenderHint(QPainter.TextAntialiasing)
        rect = self.rect()

        card_rect = QRectF(8, 6, rect.width() - 16, rect.height() - 28)
        center = card_rect.center()
        p.translate(center)
        p.scale(self._scale, self._scale)
        p.translate(-center)

        # 1. Glow shadow
        if self._active_alpha > 0:
            glow_path = QPainterPath()
            glow_path.addRoundedRect(card_rect.adjusted(-2, -2, 2, 2), 14, 14)
            glow_color = QColor(Colors.ACCENT_BLUE)
            glow_color.setAlphaF(0.25 * self._active_alpha)
            p.fillPath(glow_path, glow_color)
        elif self._hover_alpha > 0:
            shadow_path = QPainterPath()
            shadow_path.addRoundedRect(card_rect.adjusted(-1, -1, 1, 1), 12, 12)
            p.fillPath(shadow_path, QColor(0, 0, 0, int(self._hover_alpha * 2)))

        path = QPainterPath()
        path.addRoundedRect(card_rect, 10, 10)
        p.setClipPath(path)

        if self.scaled_pixmap and not self.is_dummy:
            pix_w = self.scaled_pixmap.width()
            pix_h = self.scaled_pixmap.height()
            x_offset = card_rect.x() + (card_rect.width() - pix_w) / 2
            y_offset = card_rect.y() + (card_rect.height() - pix_h) / 2
            p.drawPixmap(QPointF(x_offset, y_offset), self.scaled_pixmap)

            if self._hover_alpha > 0:
                p.fillPath(path, QColor(255, 255, 255, int(self._hover_alpha)))
        else:
            # Action Card: Add Photo
            is_dark = self.is_dark
            p.fillPath(path, QColor(255, 255, 255, 10 if is_dark else 18))
            p.setPen(QPen(QColor(255, 255, 255, 50 if is_dark else 70), 1.2, Qt.DashLine))
            p.drawRoundedRect(card_rect.adjusted(2, 2, -2, -2), 8, 8)

            # Central stylized circular badge
            c_center = card_rect.center()
            circle_r = 16.0
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 22 if is_dark else 35))
            p.drawEllipse(c_center, circle_r, circle_r)

            icon_col = QColor(Colors.TEXT_PRIMARY)
            VectorIcons.draw_plus(p, QRectF(c_center.x() - 8, c_center.y() - 8, 16, 16), icon_col)

        p.setClipping(False)

        # Delicate border
        p.setPen(QPen(QColor(255, 255, 255, 30) if self.is_dark else QColor(0, 0, 0, 30), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(card_rect, 10, 10)

        # 2. Active Checkmark Selection Ring
        if self._active_alpha > 0:
            active_color = QColor(Colors.ACCENT_BLUE)
            active_color.setAlphaF(self._active_alpha)
            p.setPen(QPen(active_color, 2.5))
            p.drawRoundedRect(card_rect.adjusted(-1.5, -1.5, 1.5, 1.5), 12, 12)

            badge_r = 10
            badge_rect = QRectF(card_rect.right() - badge_r - 4, card_rect.bottom() - badge_r - 4, badge_r*2, badge_r*2)

            p.translate(badge_rect.center())
            p.scale(self._active_alpha, self._active_alpha)
            p.translate(-badge_rect.center())

            p.setPen(Qt.NoPen)
            p.setBrush(active_color)
            p.drawEllipse(badge_rect)

            icon_color = QColor(255, 255, 255)
            icon_color.setAlphaF(self._active_alpha)
            p.setPen(QPen(icon_color, 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawLine(badge_rect.x() + 6, badge_rect.y() + 10, badge_rect.x() + 9, badge_rect.y() + 13)
            p.drawLine(badge_rect.x() + 9, badge_rect.y() + 13, badge_rect.x() + 14, badge_rect.y() + 7)

            p.translate(badge_rect.center())
            p.scale(1.0/self._active_alpha if self._active_alpha > 0 else 1.0, 1.0/self._active_alpha if self._active_alpha > 0 else 1.0)
            p.translate(-badge_rect.center())

        # 3. Liquid Glass Specular Shimmer tracking cursor
        self.shimmer.paint_shimmer(p, card_rect, radius=10, is_dark=self.is_dark)

        p.resetTransform()
        p.setPen(QColor(Colors.TEXT_PRIMARY))
        font = p.font()
        font.setPixelSize(Typography.SIZE_SMALL)
        font.setWeight(QFont.Weight(Typography.WEIGHT_NORMAL))
        p.setFont(font)

        text_rect = QRectF(0, card_rect.bottom() + 6, rect.width(), 20)
        p.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, self.title)
        p.end()


class CurrentWallpaperCard(QWidget):
    def __init__(self, image_path: str):
        super().__init__()
        self.setFixedHeight(240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMouseTracking(True)
        self.original_pixmap = _load_pixmap_thumbnail(image_path, QSize(1200, 520)) if image_path and os.path.exists(image_path) else None
        self.scaled_pixmap = None

        self.new_original_pixmap = None
        self.new_scaled_pixmap = None
        self._fade_alpha = 0.0

        self.shimmer = GlassShimmerHelper(self)

        self.fade_anim = QPropertyAnimation(self, b"fade_alpha")
        self.fade_anim.setDuration(180)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_anim.finished.connect(self._on_fade_finished)

    @Property(float)
    def fade_alpha(self): return self._fade_alpha
    @fade_alpha.setter
    def fade_alpha(self, a):
        self._fade_alpha = a
        self.update()

    def set_image(self, image_path):
        if image_path and os.path.exists(image_path):
            self.new_original_pixmap = _load_pixmap_thumbnail(image_path, QSize(1200, 520))
        else:
            self.new_original_pixmap = None

        rect = self.rect()
        if self.new_original_pixmap and not self.new_original_pixmap.isNull():
            self.new_scaled_pixmap = self.new_original_pixmap.scaled(
                rect.width(), rect.height(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
        else:
            self.new_scaled_pixmap = None

        self.fade_anim.stop()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

    def _on_fade_finished(self):
        self.original_pixmap = self.new_original_pixmap
        self.scaled_pixmap = self.new_scaled_pixmap
        self._fade_alpha = 0.0
        self.update()

    def enterEvent(self, event):
        self.shimmer.handle_enter(event)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shimmer.handle_leave(event)
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        self.shimmer.handle_mouse_move(event)
        super().mouseMoveEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        if self.original_pixmap and not self.original_pixmap.isNull():
            self.scaled_pixmap = self.original_pixmap.scaled(
                rect.width(), rect.height(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
        else:
            self.scaled_pixmap = None

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        rect = self.rect()
        card_rect = QRectF(rect).adjusted(0, 0, 0, 0)

        # Base background placeholder
        path = QPainterPath()
        path.addRoundedRect(card_rect, 16, 16)
        p.fillPath(path, QColor(30, 30, 30) if ThemeManager.is_dark else QColor(220, 220, 220))

        p.save()
        p.setClipPath(path)

        # Draw base pixmap
        if self.scaled_pixmap and not self.scaled_pixmap.isNull():
            pix_w = self.scaled_pixmap.width()
            pix_h = self.scaled_pixmap.height()
            x_offset = card_rect.x() + (card_rect.width() - pix_w) / 2
            y_offset = card_rect.y() + (card_rect.height() - pix_h) / 2
            p.drawPixmap(QPointF(x_offset, y_offset), self.scaled_pixmap)

        # Draw fading-in new pixmap
        if self._fade_alpha > 0 and self.new_scaled_pixmap and not self.new_scaled_pixmap.isNull():
            p.setOpacity(self._fade_alpha)
            pix_w = self.new_scaled_pixmap.width()
            pix_h = self.new_scaled_pixmap.height()
            x_offset = card_rect.x() + (card_rect.width() - pix_w) / 2
            y_offset = card_rect.y() + (card_rect.height() - pix_h) / 2
            p.drawPixmap(QPointF(x_offset, y_offset), self.new_scaled_pixmap)
            p.setOpacity(1.0)

        p.restore()

        # Border
        p.setPen(QPen(QColor(255, 255, 255, 30) if ThemeManager.is_dark else QColor(0, 0, 0, 30), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(card_rect, 16, 16)

        # Liquid Glass Specular Shimmer
        self.shimmer.paint_shimmer(p, card_rect, radius=16, is_dark=ThemeManager.is_dark)


class AdaptiveGridWidget(QWidget):
    def __init__(self, spacing=15, parent=None):
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(spacing)
        self.items = []
        self._current_cols = 0
        self.separator_index = -1
        self.separator = None

    def add_widget(self, widget):
        self.items.append(widget)
        self.relayout()

    def set_separator_before(self, index, text):
        self.separator_index = index
        self.separator = QLabel(text)
        self.separator.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: bold; "
            f"margin-top: 15px; margin-bottom: 5px;"
        )
        self.relayout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.relayout()

    def relayout(self):
        w = self.width()
        if w < 550:
            cols = 2
        elif w < 750:
            cols = 3
        elif w < 960:
            cols = 4
        else:
            cols = 5

        if cols == self._current_cols and len(self.items) == self.grid.count():
            return

        self._current_cols = cols

        while self.grid.count() > 0:
            item = self.grid.takeAt(0)
            if item.widget() and item.widget() != self.separator:
                item.widget().setParent(self)

        current_row = 0
        current_col = 0

        for i, widget in enumerate(self.items):
            if self.separator_index != -1 and i == self.separator_index:
                if current_col > 0:
                    current_row += 1
                    current_col = 0
                self.grid.addWidget(self.separator, current_row, 0, 1, cols)
                self.separator.show()
                current_row += 1

            self.grid.addWidget(widget, current_row, current_col)
            current_col += 1
            if current_col >= cols:
                current_col = 0
                current_row += 1


class WallpaperGallery(QWidget):
    def __init__(self, appearance_service, parent=None):
        super().__init__(parent)
        self.service = appearance_service
        self.cards = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # 1. Current Wallpaper Hero Preview Block
        current_path = self._fetch_current_path()
        self.current_card = CurrentWallpaperCard(current_path)
        main_layout.addWidget(self.current_card)

        self.current_light_path = current_path
        self.current_dark_path = current_path
        self._last_polled_path = current_path

        # 2. Collections Gallery Grid
        self.gallery_container = AdaptiveGridWidget(spacing=15)
        self._load_gallery()
        main_layout.addWidget(self.gallery_container)

        ThemeManager.theme_changed.connect(self.on_theme_changed)

        # Auto-refresh: poll gsettings every 3s
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_wallpaper)
        self._poll_timer.start(3000)

        # Auto-refresh: watch Custom wallpaper folder
        self._custom_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'assets', 'wallpapers', 'Custom')
        )
        os.makedirs(self._custom_dir, exist_ok=True)
        self._fs_watcher = QFileSystemWatcher(self)
        self._fs_watcher.addPath(self._custom_dir)
        self._fs_watcher.directoryChanged.connect(self._on_custom_dir_changed)

    def _fetch_current_path(self) -> str:
        uri = self.service.backend.get_current_wallpaper()
        path = uri.replace("file://", "") if uri else ""
        if path:
            path = urllib.parse.unquote(path)
        return path

    def _poll_wallpaper(self):
        current_path = self._fetch_current_path()
        if current_path and current_path != self._last_polled_path:
            self._last_polled_path = current_path
            self.current_light_path = current_path
            self.current_dark_path = current_path
            if os.path.exists(current_path):
                self.current_card.set_image(current_path)
            for card in self.cards:
                is_sel = (card.light_path == current_path or card.dark_path == current_path)
                if card.is_selected != is_sel:
                    card.set_selected(is_sel)

    def _on_custom_dir_changed(self, path: str):
        QTimer.singleShot(400, self._load_gallery)

    def _load_gallery(self):
        self.cards.clear()
        for i in reversed(range(self.gallery_container.grid.count())):
            item = self.gallery_container.grid.itemAt(i)
            if item and item.widget():
                w = item.widget()
                self.gallery_container.grid.removeWidget(w)
                w.deleteLater()
        self.gallery_container.items.clear()

        if hasattr(self, '_fs_watcher') and self._custom_dir not in self._fs_watcher.directories():
            self._fs_watcher.addPath(self._custom_dir)

        is_dark_theme = self.service.get_theme() == "prefer-dark"
        current_path = self.current_light_path if self.current_light_path else ""

        # ── 1. Action Card: Add Photo... ──
        add_photo_card = WallpaperCard("Add Photo...", "", "", is_selected=False, is_dark=is_dark_theme)
        add_photo_card.clicked.connect(self.prompt_add_photo)
        self.gallery_container.add_widget(add_photo_card)

        # ── 2. Wallpaper Folders ──
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'wallpapers'))
        if os.path.exists(base_dir):
            collections = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

            def process_folder(col, force_custom=False):
                col_path = os.path.join(base_dir, col)
                images = [f for f in os.listdir(col_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                images = [f for f in images if 'preview' not in f.lower()]
                if not images:
                    return 0

                is_custom = force_custom or (col in ["Custom", "Recent"])
                has_dark = any('dark' in f.lower() or 'black' in f.lower() for f in images)
                has_light = any('light' in f.lower() or 'white' in f.lower() for f in images)

                count_added = 0
                if has_dark and has_light and not is_custom:
                    light_img = next((f for f in images if 'light' in f.lower() or 'white' in f.lower()), images[0])
                    dark_img = next((f for f in images if 'dark' in f.lower() or 'black' in f.lower()), light_img)
                    l_path = os.path.join(col_path, light_img)
                    d_path = os.path.join(col_path, dark_img)
                    is_sel = (l_path == current_path or d_path == current_path)
                    card = WallpaperCard(col.capitalize(), l_path, d_path, is_selected=is_sel, is_dark=is_dark_theme, is_custom=is_custom)
                    card.clicked.connect(lambda l=l_path, d=d_path, card_widget=card: self.select_wallpaper(l, d, card_widget))
                    self.gallery_container.add_widget(card)
                    self.cards.append(card)
                    count_added += 1
                else:
                    for i, img in enumerate(sorted(images)):
                        img_path = os.path.join(col_path, img)
                        name = "Custom" if is_custom else (col.capitalize() if len(images) == 1 else f"{col.capitalize()} {i+1}")
                        is_sel = (img_path == current_path)
                        card = WallpaperCard(name, img_path, img_path, is_selected=is_sel, is_dark=is_dark_theme, is_custom=is_custom)
                        card.clicked.connect(lambda l=img_path, d=img_path, card_widget=card: self.select_wallpaper(l, d, card_widget))
                        if is_custom:
                            card.delete_clicked.connect(lambda p=img_path: self._delete_custom_wallpaper(p))
                        self.gallery_container.add_widget(card)
                        self.cards.append(card)
                        count_added += 1
                return count_added

            # First load user custom/recent photos
            for col in sorted(collections):
                if col in ["Custom", "Recent"]:
                    process_folder(col, force_custom=True)

            # Then load standard collections
            for col in sorted(collections):
                if col not in ["Custom", "Recent"]:
                    process_folder(col, force_custom=False)

    def _delete_custom_wallpaper(self, path):
        try:
            if os.path.exists(path):
                os.remove(path)
            self._load_gallery()
        except Exception as e:
            print(f"Failed to delete wallpaper: {e}")

    def on_theme_changed(self, is_dark):
        current_img = self.current_dark_path if is_dark else self.current_light_path
        if current_img and os.path.exists(current_img):
            self.current_card.set_image(current_img)

        for card in self.cards:
            card.update_theme(is_dark)

    def select_wallpaper(self, light_path, dark_path, clicked_card):
        self.current_light_path = light_path
        self.current_dark_path = dark_path
        self._last_polled_path = light_path

        if light_path and os.path.exists(light_path):
            self.service.set_wallpaper(light_path, dark_path)

            for card in self.cards:
                card.set_selected(card == clicked_card)

            theme = self.service.get_theme()
            current_img = dark_path if theme == "prefer-dark" else light_path
            self.current_card.set_image(current_img)

    def prompt_add_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Wallpaper", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            custom_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'wallpapers', 'Custom'))
            os.makedirs(custom_dir, exist_ok=True)

            filename = os.path.basename(file_path)
            dest_path = os.path.join(custom_dir, filename)

            counter = 1
            while os.path.exists(dest_path):
                base, ext = os.path.splitext(filename)
                dest_path = os.path.join(custom_dir, f"{base}_{counter}{ext}")
                counter += 1

            try:
                shutil.copy2(file_path, dest_path)
                self.select_wallpaper(dest_path, dest_path, None)
                self._load_gallery()
            except Exception as e:
                print(f"Failed to add photo: {e}")
