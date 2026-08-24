"""Storage page — skeleton-first, async data loading, no layout rebuild."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QScrollArea,
    QGridLayout, QSizePolicy, QPushButton, QFrame, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QRectF, QProcess, QSize, QThread, Signal, QVariantAnimation, QEasingCurve, QPropertyAnimation, QPoint, QPointF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QPixmap, QLinearGradient, QCursor
from theme.colors import Colors
from theme.typography import Typography
from theme.manager import ThemeManager
from services.storage_service import StorageService
from services.storage_scanner import StorageScannerThread
from services.disk_monitor import DiskActivityMonitor
from collections import deque
import os
import weakref

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP_1COL, BP_2COL = 640, 920

from components.storage.utils import make_label, _STYLED_LABELS, _apply_style
from components.storage.ui import StorageProgressBar, StorageLegend
from components.storage.model import StorageCategory


# ── Background thread: fetch disk info ────────────────────────────
class DiskInfoThread(QThread):
    data_ready = Signal(list)   # emits list of disk dicts

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service

    def run(self):
        try:
            disks = self.service.get_detailed_disks()
        except Exception:
            disks = []
        self.data_ready.emit(disks)


# ── Glass card ────────────────────────────────────────────────────
class GlassCard(QWidget):
    RADIUS = 20

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        is_dark = ThemeManager.is_dark
        r = QRectF(self.rect()).adjusted(1, 1, -1, -3)
        sh = QPainterPath()
        sh.addRoundedRect(r.adjusted(0, 3, 0, 3), self.RADIUS, self.RADIUS)
        p.fillPath(sh, QColor(0, 0, 0, 35 if is_dark else 18))
        bg = QColor(Colors.CARD_BG)
        if is_dark:
            bg.setAlpha(220)
        path = QPainterPath()
        path.addRoundedRect(r, self.RADIUS, self.RADIUS)
        p.fillPath(path, bg)
        bc = QColor(Colors.CARD_BORDER)
        bc.setAlpha(60 if is_dark else 80)
        p.setPen(QPen(bc, 1))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        p.end()





# ── Drive icon (scalable) ─────────────────────────────────────────
class DriveIconWidget(QLabel):
    _PIX = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setMinimumSize(60, 76)
        self.setMaximumSize(120, 152)
        if DriveIconWidget._PIX is None:
            path = os.path.join(BASE_DIR, "assets", "drive.png")
            if os.path.exists(path):
                DriveIconWidget._PIX = QPixmap(path)
        if DriveIconWidget._PIX is None:
            self.setText("💾")
            self.setStyleSheet("font-size:48px;background:transparent;")

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if DriveIconWidget._PIX:
            self.setPixmap(DriveIconWidget._PIX.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def sizeHint(self): return QSize(96, 122)


# ── Hero card (skeleton-ready) ────────────────────────────────────
class HeroCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(0)

        top = QHBoxLayout()
        top.setSpacing(20)
        top.setAlignment(Qt.AlignTop)
        top.addWidget(DriveIconWidget(), 0, Qt.AlignVCenter)

        info = QVBoxLayout()
        info.setSpacing(3)

        self.name_lbl = make_label("Echo HD", True, "TEXT_PRIMARY", 22)
        info.addWidget(self.name_lbl)

        self.sub_lbl = make_label("—", False, "TEXT_SECONDARY", 12)
        info.addWidget(self.sub_lbl)

        info.addSpacing(8) # Reduced spacing to accommodate taller bar
        self.bar = StorageProgressBar()
        info.addWidget(self.bar)
        
        self.legend = StorageLegend()
        info.addWidget(self.legend)
        info.addSpacing(16)
        
        self.bar.anim.finished.connect(self.legend.anim.start)

        from localization import t
        stats = QHBoxLayout()
        # Used
        uc = QVBoxLayout(); uc.setSpacing(1)
        uc.addWidget(make_label(t("storage.used", "Used"), False, "TEXT_SECONDARY", 11))
        self.used_val = make_label("—", True, "TEXT_PRIMARY", 24)
        uc.addWidget(self.used_val)
        stats.addLayout(uc)
        stats.addStretch()
        # Available
        ac = QVBoxLayout(); ac.setSpacing(1)
        al = make_label(t("storage.free", "Available"), False, "TEXT_SECONDARY", 11)
        al.setAlignment(Qt.AlignRight)
        ac.addWidget(al)
        self.avail_val = make_label("—", True, "TEXT_PRIMARY", 24)
        self.avail_val.setAlignment(Qt.AlignRight)
        ac.addWidget(self.avail_val)
        stats.addLayout(ac)
        info.addLayout(stats)

        top.addLayout(info, 1)
        outer.addLayout(top)

    def populate(self, disk, part, category_sizes=None):
        self._disk = disk
        self._part = part
        self._category_sizes = category_sizes or {}
        
        fs = (part.get('fstype') or 'Unknown').upper()
        self.sub_lbl.setText(f"{disk['size_gb']} GB {disk['type']} Drive  •  {fs}")
        
        self._update_categories_ui()
        
        self.used_val.setText(f"{part['used_gb']} GB")
        self.avail_val.setText(f"{part['free_gb']} GB")

    def update_category(self, cat_obj: StorageCategory):
        if not hasattr(self, '_category_sizes'):
            self._category_sizes = {}
        if name := cat_obj.name:
            if self._category_sizes.get(name) and self._category_sizes[name].size_bytes == cat_obj.size_bytes:
                return # No change
            self._category_sizes[name] = cat_obj
        
        # Fast update without re-triggering entry animations if already filled
        was_full = self.bar._anim_pct >= 1.0
        self._update_categories_ui(animate=not was_full)
        
    def _update_categories_ui(self, animate=True):
        if not hasattr(self, '_disk') or not hasattr(self, '_part'): return
        
        total_gb = float(self._part['size_gb'])
        used_gb = float(self._part['used_gb'])
        
        if not self._category_sizes:
            cats = [StorageCategory(name="Used", size_bytes=int(used_gb * (1024**3)))]
        else:
            cats = [c for c in self._category_sizes.values() if c.size_bytes > 0]
            
            # Calculate "Other" dynamically here to guarantee total doesn't exceed 100%
            known_used_bytes = sum(c.size_bytes for c in cats if c.name != "Other")
            used_bytes = int(used_gb * (1024**3))
            other_bytes = max(0, used_bytes - known_used_bytes)
            if other_bytes > 50 * (1024**2): # Only show Other if > 50MB
                cats.append(StorageCategory(name="Other", size_bytes=other_bytes))
            
            cats = [c for c in cats if c.size_gb >= 0.05]
            
        # Re-sort to maintain order: Games, Apps, Downloads, Pictures, Videos, Music, Documents, Trash, Other
        order = ["Games", "Applications", "Downloads", "Pictures", "Videos", "Music", "Documents", "Trash", "Other", "Used"]
        cats.sort(key=lambda c: order.index(c.name) if c.name in order else 99)
            
        if animate:
            self.bar.set_data(total_gb, cats, animate=True)
        else:
            self.bar._total_gb = max(0.1, total_gb)
            self.bar._categories = cats
            self.bar._anim_pct = 1.0
            self.bar.update()
            
        self.legend.set_categories(cats)


# ── Info card ─────────────────────────────────────────────────────
class InfoCard(GlassCard):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(18, 16, 18, 16)
        self._outer.setSpacing(0)
        t = make_label(title, True, "TEXT_PRIMARY", 14)
        self._outer.addWidget(t)
        self._outer.addSpacing(10)
        self._rows_w = QWidget(styleSheet="background:transparent;")
        self._rows_l = QVBoxLayout(self._rows_w)
        self._rows_l.setContentsMargins(0, 0, 0, 0)
        self._rows_l.setSpacing(0)
        self._outer.addWidget(self._rows_w)
        self._n = 0
        self._label_refs: list[tuple[QLabel, QLabel]] = []  # (left, right)

    def _sep(self):
        s = QFrame()
        s.setFrameShape(QFrame.HLine)
        s.setStyleSheet("background-color:rgba(120,120,128,45);border:none;max-height:1px;")
        return s

    def add_row(self, left="", right="", widget=None):
        if self._n > 0:
            self._rows_l.addWidget(self._sep())
        row = QHBoxLayout()
        row.setContentsMargins(0, 7, 0, 7)
        row.setSpacing(6)
        ll = make_label(str(left), False, "TEXT_PRIMARY", 12)
        row.addWidget(ll)
        row.addStretch()
        rl = None
        if widget:
            row.addWidget(widget)
        elif right != "":
            rl = make_label(str(right), False, "TEXT_SECONDARY", 12)
            rl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(rl)
        c = QWidget(styleSheet="background:transparent;")
        c.setLayout(row)
        self._rows_l.addWidget(c)
        self._n += 1
        self._label_refs.append((ll, rl))
        return ll, rl

    def update_row(self, index: int, right: str):
        """Update only the right-side label of a pre-existing row."""
        if 0 <= index < len(self._label_refs):
            _, rl = self._label_refs[index]
            if rl is not None:
                rl.setText(right)

    def clear_rows(self):
        while self._rows_l.count():
            item = self._rows_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._n = 0
        self._label_refs.clear()

    def set_placeholder(self, text):
        self.clear_rows()
        lbl = make_label(text, False, "TEXT_SECONDARY", 12)
        lbl.setWordWrap(True)
        self._rows_l.addWidget(lbl)
        self._n = 1

    def add_stretch(self):
        self._outer.addStretch()

    def add_link(self, text, cb=None):
        lnk = QLabel(f'<a style="color:#007AFF;text-decoration:none;" href="#">{text}</a>',
                     styleSheet="background:transparent;border:none;font-size:12px;")
        lnk.setOpenExternalLinks(False)
        if cb: lnk.linkActivated.connect(lambda _: cb())
        self._outer.addSpacing(6)
        self._outer.addWidget(lnk)

# ── Disk Activity Card ────────────────────────────────────────────
class DiskGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.history = deque(maxlen=30)
        # Seed with 0 values
        for _ in range(30):
            self.history.append((0, 0))

    def update_data(self, read, write):
        self.history.append((read, write))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        if not self.history:
            return
            
        max_val = max(1024, max(max(r, w) for r, w in self.history))
        
        read_points = []
        write_points = []
        dx = width / max(1, len(self.history) - 1)
        
        for i, (r, w) in enumerate(self.history):
            x = i * dx
            y_r = height - (r / max_val * height * 0.9)
            y_w = height - (w / max_val * height * 0.9)
            read_points.append(QPointF(x, y_r))
            write_points.append(QPointF(x, y_w))
            
        is_dark = ThemeManager.is_dark
        read_color = QColor("#0A84FF") if is_dark else QColor("#007AFF")
        write_color = QColor("#30D158") if is_dark else QColor("#34C759")
        
        wp = QPainterPath()
        if write_points:
            wp.moveTo(write_points[0])
            for pt in write_points[1:]:
                wp.lineTo(pt)
        p.setPen(QPen(write_color, 2))
        p.drawPath(wp)
        
        rp = QPainterPath()
        if read_points:
            rp.moveTo(read_points[0])
            for pt in read_points[1:]:
                rp.lineTo(pt)
        p.setPen(QPen(read_color, 2))
        p.drawPath(rp)

        baseline = QColor(Colors.TEXT_SECONDARY)
        baseline.setAlpha(40 if is_dark else 30)
        p.setPen(QPen(baseline, 1))
        p.drawLine(0, height-1, width, height-1)


class DiskActivityCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(18, 16, 18, 16)
        self._outer.setSpacing(12)
        
        header = QHBoxLayout()
        title = make_label("Disk Activity", True, "TEXT_PRIMARY", 14)
        header.addWidget(title)
        header.addStretch()
        
        self.status_lbl = make_label("Idle", False, "TEXT_SECONDARY", 12)
        header.addWidget(self.status_lbl)
        self._outer.addLayout(header)
        
        self.graph = DiskGraphWidget()
        self._outer.addWidget(self.graph)
        
        stats_layout = QHBoxLayout()
        
        rc = QVBoxLayout()
        rc.setSpacing(2)
        rc.addWidget(make_label("Read", False, "TEXT_SECONDARY", 11))
        self.read_val = make_label("0 B/s", True, "TEXT_PRIMARY", 13)
        rc.addWidget(self.read_val)
        stats_layout.addLayout(rc)
        
        wc = QVBoxLayout()
        wc.setSpacing(2)
        wl = make_label("Write", False, "TEXT_SECONDARY", 11)
        wl.setAlignment(Qt.AlignCenter)
        wc.addWidget(wl)
        self.write_val = make_label("0 B/s", True, "TEXT_PRIMARY", 13)
        self.write_val.setAlignment(Qt.AlignCenter)
        wc.addWidget(self.write_val)
        stats_layout.addLayout(wc)
        
        ic = QVBoxLayout()
        ic.setSpacing(2)
        il = make_label("IOPS", False, "TEXT_SECONDARY", 11)
        il.setAlignment(Qt.AlignRight)
        ic.addWidget(il)
        self.iops_val = make_label("0", True, "TEXT_PRIMARY", 13)
        self.iops_val.setAlignment(Qt.AlignRight)
        ic.addWidget(self.iops_val)
        stats_layout.addLayout(ic)
        
        self._outer.addLayout(stats_layout)
        self.update_colors()
        
    def _fmt(self, val):
        if val < 1024: return f"{val:.0f} B/s"
        if val < 1024*1024: return f"{val/1024:.1f} KB/s"
        return f"{val/(1024*1024):.1f} MB/s"
        
    def update_data(self, read_bps, write_bps, iops, active):
        self.read_val.setText(self._fmt(read_bps))
        self.write_val.setText(self._fmt(write_bps))
        self.iops_val.setText(str(iops))
        self.status_lbl.setText("Active" if active else "Idle")
        self.graph.update_data(read_bps, write_bps)
        self.update_colors()
        
    def update_colors(self):
        is_dark = ThemeManager.is_dark
        rc = "#0A84FF" if is_dark else "#007AFF"
        wc = "#30D158" if is_dark else "#34C759"
        self.read_val.setStyleSheet(f"color: {rc}; font-weight: 600; font-size: 13px; background: transparent;")
        self.write_val.setStyleSheet(f"color: {wc}; font-weight: 600; font-size: 13px; background: transparent;")


# ── Responsive grid ───────────────────────────────────────────────
class ResponsiveCardGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        self._cards: list[QWidget] = []
        self._grid = QGridLayout(self)
        self._grid.setSpacing(14)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._cols = -1

    def add_card(self, card):
        self._cards.append(card)
        self._cols = -1  # force relayout
        self._relayout(self._ncols(self.width()))

    def _ncols(self, w):
        if w < BP_1COL: return 1
        if w < BP_2COL: return 2
        return 3

    def _relayout(self, n):
        if n == self._cols: return
        self._cols = n
        for i in reversed(range(self._grid.count())):
            item = self._grid.itemAt(i)
            if item and item.widget():
                self._grid.removeWidget(item.widget())
        for c in range(4): self._grid.setColumnStretch(c, 0)
        for idx, card in enumerate(self._cards):
            r, c = divmod(idx, n)
            self._grid.addWidget(card, r, c)
            card.show()
        for c in range(n): self._grid.setColumnStretch(c, 1)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._relayout(self._ncols(e.size().width()))


# ── Volume row widget (reusable) ──────────────────────────────────
def _make_vol_row(label, fs, free_gb, total_gb, pct):
    w = QWidget(styleSheet="background:transparent;")
    vl = QVBoxLayout(w)
    vl.setContentsMargins(0, 0, 0, 0)
    vl.setSpacing(4)
    tr = QHBoxLayout()
    tr.addWidget(make_label(label, True, "TEXT_PRIMARY", 12))
    tr.addSpacing(5)
    tr.addWidget(make_label(fs, False, "TEXT_SECONDARY", 11))
    tr.addStretch()
    sz = make_label(f"{free_gb} GB free of {total_gb} GB", False, "TEXT_SECONDARY", 11)
    sz.setAlignment(Qt.AlignRight)
    tr.addWidget(sz)
    vl.addLayout(tr)
    
    bar = StorageProgressBar()
    used_gb = float(total_gb) - float(free_gb)
    bar.set_data(float(total_gb), [StorageCategory(name="Used", size_bytes=int(used_gb * (1024**3)))])
    vl.addWidget(bar)
    return w


# ── Storage page ──────────────────────────────────────────────────
class StoragePage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = StorageService()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border:none;background:transparent;")
        scroll.viewport().setStyleSheet("background:transparent;")

        content = QWidget(styleSheet="background:transparent;")
        self._main = QVBoxLayout(content)
        self._main.setContentsMargins(28, 20, 28, 28)
        self._main.setSpacing(16)
        self._main.setAlignment(Qt.AlignTop)

        # ── Build skeleton immediately ────────────────────────────
        from localization import t
        title = QLabel(t("storage.title", "Storage"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.SIZE_HEADER}px; font-weight: {Typography.WEIGHT_BOLD};")
        self._main.addWidget(title)

        self._hero = HeroCard()
        self._main.addWidget(self._hero)

        self._grid_w = ResponsiveCardGrid()
        self._main.addWidget(self._grid_w)

        # Recommendations
        self.rec_card = InfoCard(t("storage.recommendations", "Recommendations"))
        self.rec_card.set_placeholder("Scanning…")
        self.rec_card.add_stretch()
        self._grid_w.add_card(self.rec_card)

        # Disk Information — pre-create 8 rows with "—"
        self._di_card = InfoCard(t("storage.disk_info", "Disk Information"))
        self._di_keys = ["Model", "Interface", "Capacity",
                         "Filesystem", "Mount Point", "TRIM",
                         "Temperature", "Serial"]
        for k in self._di_keys:
            key_name = k.lower().replace(" ", "")
            trans_k = t(f"storage.{key_name}", k)
            self._di_card.add_row(trans_k, "—")
        self._di_card.add_stretch()
        self._grid_w.add_card(self._di_card)

        # Volumes — placeholder until data
        self._vol_card = InfoCard(t("storage.volumes", "Volumes"))
        self._vol_card.set_placeholder("Loading…")
        self._vol_card.add_stretch()
        self._grid_w.add_card(self._vol_card)

        # Largest Files
        self.lf_card = InfoCard(t("storage.largest_files", "Largest Files"))
        self.lf_card.set_placeholder("Scanning…")
        self.lf_card.add_stretch()
        self._grid_w.add_card(self.lf_card)

        # Storage Health — static structure
        self._health_card = InfoCard(t("storage.storage_health", "Storage Health"))
        hw = QWidget(styleSheet="background:transparent;")
        hl = QHBoxLayout(hw)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(8)
        badge = QLabel("✓", alignment=Qt.AlignCenter,
                        styleSheet="background:#34C759;color:white;border-radius:12px;"
                                   "font-weight:700;font-size:12px;")
        badge.setFixedSize(24, 24)
        hlbl = make_label(t("storage.healthy", "Healthy"), True, "TEXT_PRIMARY", 13)
        hl.addWidget(badge)
        hl.addWidget(hlbl)
        self._health_card.add_row("", widget=hw)
        self._health_card.add_row("SMART",          "Unavailable")
        self._health_temp_idx = 2       # row index for temperature
        self._health_card.add_row(t("storage.temperature", "Temperature"), "—")
        self._health_card.add_row("Power On Hours", "Unavailable")
        self._health_card.add_stretch()
        self._grid_w.add_card(self._health_card)

        # Disk Activity
        self._activity_card = DiskActivityCard()
        self._grid_w.add_card(self._activity_card)
        self._activity_monitor = DiskActivityMonitor(self)
        self._activity_monitor.activity_updated.connect(self._activity_card.update_data)

        scroll.setWidget(content)
        ml = QVBoxLayout(self)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.addWidget(scroll)

        ThemeManager.theme_changed.connect(self.update_theme)

        # ── Fetch disk info immediately (instant 10ms) ───────────
        try:
            disks = self.service.get_detailed_disks()
            self._on_disk_data(disks)
        except Exception:
            pass

    def update_theme(self):
        for lbl in _STYLED_LABELS:
            try:
                _apply_style(lbl)
            except RuntimeError:
                pass
        if hasattr(self, '_activity_card'):
            self._activity_card.update_colors()
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, '_boot_disk') and hasattr(self, '_activity_monitor'):
            self._activity_monitor.start(self._boot_disk['name'])

    def hideEvent(self, event):
        if hasattr(self, '_scanner') and self._scanner.isRunning():
            self._scanner.requestInterruption()
        if hasattr(self, '_activity_monitor'):
            self._activity_monitor.stop()
        super().hideEvent(event)

    # ── disk data arrived ─────────────────────────────────────────
    def _on_disk_data(self, disks: list):
        boot_part, boot_disk = self._find_boot(disks)
        if not boot_part or not boot_disk:
            self._di_card.update_row(0, "No disk found")
            return

        self._boot_disk = boot_disk
        self._boot_part = boot_part

        # Hero — populate immediately with cached/instant categories (zero delay)
        from services.storage_scanner import StorageAnalyzer
        initial_cats = StorageAnalyzer().get_cached_or_instant_categories()
        self._hero.populate(boot_disk, boot_part, initial_cats)

        # Disk Information rows — update in-place
        vals = [
            boot_disk['model'],
            boot_disk['tran'],
            f"{boot_disk['size_gb']} GB",
            (boot_part.get('fstype') or 'Unknown').upper(),
            boot_part.get('mountpoint', '—'),
            self.service.get_trim_status(),
            boot_disk['temperature'],
            boot_disk['serial'],
        ]
        for i, v in enumerate(vals):
            self._di_card.update_row(i, v)

        # Health — temperature
        self._health_card.update_row(self._health_temp_idx, boot_disk['temperature'])

        # Volumes — clear placeholder, add real rows (once)
        self._vol_card.clear_rows()
        self._vol_card._n = 0
        all_parts = [p for d in disks for p in d['partitions']]
        for p in all_parts:
            mnt   = p.get('mountpoint') or p.get('name', '?')
            fs    = (p.get('fstype') or '?').upper()
            label = "Echo HD" if mnt == "/" else mnt
            w = _make_vol_row(label, fs,
                              p['free_gb'], p['size_gb'],
                              p.get('percent', 0))
            self._vol_card.add_row("", widget=w)

        # Now start scanner (needs disk data to be meaningful)
        if hasattr(self, '_scanner'):
            self._scanner.requestInterruption()
            self._scanner.wait()
            
        self._activity_monitor.start(boot_disk['name'])
            
        self._scanner = StorageScannerThread(parent=self)
        self._scanner.scan_finished.connect(self._on_scan)
        self._scanner.category_updated.connect(self._on_category_updated)
        self._scanner.start()
        
    def _on_category_updated(self, cat_obj: StorageCategory):
        self._hero.update_category(cat_obj)

    # ── scanner data arrived ──────────────────────────────────────
    def _on_scan(self, data: dict):
        if hasattr(self, '_boot_disk') and hasattr(self, '_boot_part'):
            # The hero is updated dynamically via _on_category_updated, but we can do a final pass
            self._hero.populate(self._boot_disk, self._boot_part, data.get("category_sizes"))

        recs = data.get("recommendations", {})
        self.rec_card.clear_rows()
        self.rec_card._n = 0
        self.rec_card._label_refs.clear()
        any_rec = False
        for key, icon in [("Empty Trash", "🗑"), ("Downloads", "⬇"), ("Cache", "📦")]:
            val = recs.get(key)
            if val and val not in ("", "0 KB", "Clean"):
                self.rec_card.add_row(f"{icon}  {key}", val)
                any_rec = True
        if not any_rec:
            self.rec_card.set_placeholder("No recommendations at this time.")

        largest = data.get("largest_files", [])
        self.lf_card.clear_rows()
        self.lf_card._n = 0
        self.lf_card._label_refs.clear()
        if not largest:
            self.lf_card.set_placeholder("No large files found (>50 MB).")
            return
        for f in largest:
            iw = QWidget(styleSheet="background:transparent;")
            il = QVBoxLayout(iw)
            il.setContentsMargins(0, 0, 0, 0)
            il.setSpacing(1)
            il.addWidget(make_label(f['name'], True, "TEXT_PRIMARY", 12, wordWrap=False))
            il.addWidget(make_label(f['path'], False, "TEXT_SECONDARY", 10))
            sz = make_label(f['size'], False, "TEXT_SECONDARY", 12)
            sz.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            sz.setMinimumWidth(48)
            btn = QPushButton("Reveal")
            btn.setFixedSize(52, 22)
            btn.setStyleSheet("""
                QPushButton{background:rgba(120,120,128,.18);color:#007AFF;
                    border:none;border-radius:5px;font-size:11px;font-weight:500;}
                QPushButton:hover{background:rgba(0,122,255,.15);}""")
            fp = os.path.join(
                os.path.expanduser(f['path'].replace("~", "")), f['name'])
            btn.clicked.connect(
                lambda _, p=fp: QProcess.startDetached("xdg-open", [os.path.dirname(p)]))
            rw = QWidget(styleSheet="background:transparent;")
            rl = QHBoxLayout(rw)
            rl.setContentsMargins(0, 5, 0, 5)
            rl.setSpacing(6)
            rl.addWidget(iw, 1)
            rl.addWidget(sz)
            rl.addWidget(btn)
            if self.lf_card._n > 0:
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet(
                    "background-color:rgba(120,120,128,45);border:none;max-height:1px;")
                self.lf_card._rows_l.addWidget(sep)
            self.lf_card._rows_l.addWidget(rw)
            self.lf_card._n += 1

    def _find_boot(self, disks):
        for d in disks:
            for p in d['partitions']:
                if p.get('mountpoint') == '/':
                    return p, d
        if disks and disks[0]['partitions']:
            return disks[0]['partitions'][0], disks[0]
        return None, None

    def cleanup(self):
        if hasattr(self, '_disk_thread') and self._disk_thread and self._disk_thread.isRunning():
            self._disk_thread.quit()
            self._disk_thread.wait(500)
        if hasattr(self, '_scanner') and self._scanner and self._scanner.isRunning():
            self._scanner.requestInterruption()
            self._scanner.quit()
            self._scanner.wait(500)
        if hasattr(self, '_activity_monitor') and self._activity_monitor:
            try:
                self._activity_monitor.stop()
            except Exception:
                pass


    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)

    def get_search_target(self, target_id: str) -> QWidget | None:
        targets = {
            "storage.overview": getattr(self, "_hero", None),
            "storage.recommendations": getattr(self, "rec_card", None),
            "storage.large_files": getattr(self, "lf_card", None),
            "storage.applications": getattr(self, "apps_card", None) or getattr(self, "_hero", None),
        }
        return targets.get(target_id)

