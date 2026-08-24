from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QSizePolicy, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QRectF, QPoint, QPropertyAnimation, QVariantAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen

from theme.manager import ThemeManager
from .utils import make_label
from .model import StorageCategory

class StoragePopover(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 12, 16, 12)
        self._layout.setSpacing(4)
        
        self.name_lbl = make_label("", True, "TEXT_PRIMARY", 13)
        self._layout.addWidget(self.name_lbl)
        
        self.size_lbl = make_label("", False, "TEXT_SECONDARY", 12)
        self._layout.addWidget(self.size_lbl)
        self.pct_lbl = make_label("", False, "TEXT_SECONDARY", 12)
        self._layout.addWidget(self.pct_lbl)
        
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(160)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.finished.connect(self._on_hide_finished)
        self.setWindowOpacity(0.0)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(r, 12, 12)
        
        is_dark = ThemeManager.is_dark
        bg_color = QColor(30, 30, 30, 230) if is_dark else QColor(255, 255, 255, 240)
        p.fillPath(path, bg_color)
        
        border_color = QColor(255, 255, 255, 45) if is_dark else QColor(0, 0, 0, 40)
        p.setPen(QPen(border_color, 1))
        p.drawPath(path)
        p.end()

    def show_info(self, name, size_gb, pct, pos):
        from localization import t
        translated_name = t(f"storage.{name.lower()}", name)
        self.name_lbl.setText(translated_name)
        self.size_lbl.setText(f"{size_gb:.1f} GB")
        self.pct_lbl.setText(f"{pct:.1f}%")
        self.adjustSize()
        self.move(pos.x() - self.width() // 2, pos.y() - self.height() - 12)
        
        self.show()
        if self.windowOpacity() < 1.0:
            self.anim.stop()
            self.anim.setStartValue(self.windowOpacity())
            self.anim.setEndValue(1.0)
            self.anim.start()
            
    def move_to(self, pos):
        self.move(pos.x() - self.width() // 2, pos.y() - self.height() - 12)

    def hide_info(self):
        if self.windowOpacity() > 0.0:
            self.anim.stop()
            self.anim.setStartValue(self.windowOpacity())
            self.anim.setEndValue(0.0)
            self.anim.start()
            
    def _on_hide_finished(self):
        if self.windowOpacity() <= 0.05:
            self.hide()


class StorageProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMouseTracking(True)
        self._total_gb = 1.0
        self._categories: list[StorageCategory] = []
        self._anim_pct = 1.0
        
        # Per-category hover tracking
        self._hovered_cat_name: str | None = None
        self._hover_scales: dict[str, float] = {}  # category name -> float 0.0..1.0
        
        self.popover = StoragePopover()
        
        # Smooth transition animation
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(500)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.valueChanged.connect(self._on_anim)
        
        # Smooth hover scale transition timer (60 fps)
        self._hover_timer = QTimer(self)
        self._hover_timer.setInterval(16)
        self._hover_timer.timeout.connect(self._step_hover_animations)

    def _on_anim(self, val):
        self._anim_pct = val
        self.update()

    def _step_hover_animations(self):
        """Smoothly interpolates per-category hover scales towards target values."""
        still_animating = False
        step_factor = 0.28
        
        # Collect all active category names
        known_names = {c.name for c in self._categories}
        
        for name in list(self._hover_scales.keys()):
            if name not in known_names:
                del self._hover_scales[name]
                continue
                
            target = 1.0 if name == self._hovered_cat_name else 0.0
            current = self._hover_scales[name]
            diff = target - current
            
            if abs(diff) < 0.008:
                self._hover_scales[name] = target
            else:
                self._hover_scales[name] = current + diff * step_factor
                still_animating = True
                
        # If hovered category is not yet in dict
        if self._hovered_cat_name and self._hovered_cat_name not in self._hover_scales:
            self._hover_scales[self._hovered_cat_name] = 0.0
            still_animating = True
            
        self.update()
        
        if not still_animating:
            self._hover_timer.stop()

    def _trigger_hover_update(self):
        if not self._hover_timer.isActive():
            self._hover_timer.start()

    def hideEvent(self, event):
        self._hovered_cat_name = None
        self._hover_scales.clear()
        self._hover_timer.stop()
        self.popover.hide_info()
        super().hideEvent(event)
        
    def leaveEvent(self, event):
        self._hovered_cat_name = None
        self._trigger_hover_update()
        self.popover.hide_info()
        super().leaveEvent(event)
        
    def mouseMoveEvent(self, event):
        if not self._categories:
            return
            
        x = event.pos().x()
        total_width = self.width()
        x_offset = 0.0
        found_cat = None
        found_center_x = 0
        
        for cat in self._categories:
            cat_pct = (cat.size_gb / self._total_gb) * self._anim_pct
            if cat_pct <= 0:
                continue
            cat_width = total_width * cat_pct
            if x_offset <= x <= x_offset + cat_width:
                found_cat = cat
                found_center_x = x_offset + cat_width / 2
                break
            x_offset += cat_width
            
        new_hovered_name = found_cat.name if found_cat else None
        
        if new_hovered_name != self._hovered_cat_name:
            self._hovered_cat_name = new_hovered_name
            
            # Ensure target scale key exists
            if new_hovered_name and new_hovered_name not in self._hover_scales:
                self._hover_scales[new_hovered_name] = 0.0
                
            self._trigger_hover_update()
            
            if found_cat:
                pct = (found_cat.size_gb / self._total_gb) * 100
                global_pos = self.mapToGlobal(QPoint(int(found_center_x), 0))
                self.popover.show_info(found_cat.name, found_cat.size_gb, pct, global_pos)
            else:
                self.popover.hide_info()
        else:
            if found_cat:
                global_pos = self.mapToGlobal(QPoint(int(found_center_x), 0))
                self.popover.move_to(global_pos)
                
        super().mouseMoveEvent(event)

    def set_data(self, total_gb: float, categories: list[StorageCategory], animate: bool = True):
        self._total_gb = max(0.1, total_gb)
        self._categories = categories
        self._hovered_cat_name = None
        self._hover_scales.clear()
        
        if animate:
            self.anim.stop()
            self.anim.setStartValue(0.0)
            self.anim.setEndValue(1.0)
            self.anim.start()
        else:
            self._anim_pct = 1.0
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect())
        
        base_h = 12.0
        hover_h = 18.0
        cy = r.height() / 2.0
        track_y = cy - base_h / 2.0
        
        # 1. Background Track
        track = QPainterPath()
        track.addRoundedRect(QRectF(0, track_y, r.width(), base_h), base_h / 2.0, base_h / 2.0)
        p.fillPath(track, QColor(120, 120, 128, 50 if ThemeManager.is_dark else 40))
        
        if not self._categories:
            p.end()
            return
            
        x_offset = 0.0
        total_width = r.width()
        
        # Calculate max hover scale across all segments for dimming
        max_hover_scale = max(self._hover_scales.values(), default=0.0)
        is_dark = ThemeManager.is_dark
        
        for i, cat in enumerate(self._categories):
            cat_pct = (cat.size_gb / self._total_gb) * self._anim_pct
            if cat_pct <= 0:
                continue
            cat_width = total_width * cat_pct
            
            # Retrieve animated scale for this specific category
            scale = self._hover_scales.get(cat.name, 0.0)
            h = base_h + (hover_h - base_h) * scale
            y = cy - h / 2.0
            
            seg_rect = QRectF(x_offset, y, cat_width, h)
            
            # Clip each segment smoothly to bar bounds
            clip = QPainterPath()
            clip.addRoundedRect(QRectF(0, y, r.width(), h), h / 2.0, h / 2.0)
            intersect_rect = QPainterPath()
            intersect_rect.addRect(seg_rect)
            final_path = clip.intersected(intersect_rect)
            
            p.fillPath(final_path, QColor(cat.color))
            
            # Subtle dimming on non-hovered segments when a hover is active
            if max_hover_scale > 0.0 and scale < 1.0:
                dim_factor = max_hover_scale * (1.0 - scale)
                overlay = QColor(0, 0, 0, int(60 * dim_factor)) if is_dark else QColor(255, 255, 255, int(110 * dim_factor))
                p.fillPath(final_path, overlay)
            
            # Separator line between segments
            if x_offset > 0:
                sep_color = QColor(0, 0, 0, 80) if is_dark else QColor(255, 255, 255, 120)
                p.setPen(QPen(sep_color, 1))
                p.drawLine(int(x_offset), int(y), int(x_offset), int(y + h))
                
            x_offset += cat_width
            
        p.end()


class StorageLegend(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setHorizontalSpacing(16)
        self.layout.setVerticalSpacing(8)
        
        self.effect = QGraphicsOpacityEffect(self)
        self.effect.setOpacity(1.0)
        self.setGraphicsEffect(self.effect)
        
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0.2)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        
    def set_categories(self, categories: list[StorageCategory]):
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
                item.layout().deleteLater()
                
        cols = 3
        for idx, cat in enumerate(categories):
            row_idx, col_idx = divmod(idx, cols)
            
            item_vl = QVBoxLayout()
            item_vl.setContentsMargins(0, 0, 0, 0)
            item_vl.setSpacing(2)
            
            top_row = QHBoxLayout()
            top_row.setContentsMargins(0, 0, 0, 0)
            top_row.setSpacing(6)
            
            dot = QLabel()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(f"background-color: {cat.color}; border-radius: 5px;")
            
            from localization import t
            translated_cat_name = t(f"storage.{cat.name.lower()}", cat.name)
            name_lbl = make_label(translated_cat_name, False, "TEXT_PRIMARY", 12)
            top_row.addWidget(dot)
            top_row.addWidget(name_lbl)
            top_row.addStretch()
            
            size_lbl = make_label(f"{cat.size_gb:.1f} GB", True, "TEXT_SECONDARY", 11)
            size_lbl.setStyleSheet(size_lbl.styleSheet() + "padding-left: 16px;")
            
            item_vl.addLayout(top_row)
            item_vl.addWidget(size_lbl)
            
            w = QWidget()
            w.setLayout(item_vl)
            self.layout.addWidget(w, row_idx, col_idx)
