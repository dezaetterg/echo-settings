import weakref
from PySide6.QtWidgets import QLabel
from theme.colors import Colors
from theme.typography import Typography

_STYLED_LABELS = weakref.WeakSet()

def _style_label(lbl, bold=False, color_attr=None, px=None):
    lbl._ss_args = (bold, color_attr, px)
    _apply_style(lbl)
    _STYLED_LABELS.add(lbl)

def _apply_style(lbl):
    bold, color_attr, px = getattr(lbl, "_ss_args", (False, None, None))
    color = getattr(Colors, color_attr) if color_attr else None
    p = ["background:transparent;border:none;"]
    if color: p.append(f"color:{color};")
    if px:    p.append(f"font-size:{px}px;")
    if bold:  p.append(f"font-weight:{Typography.WEIGHT_SEMIBOLD};")
    lbl.setStyleSheet("".join(p))

def make_label(text, bold=False, color_attr=None, px=None, **kwargs):
    lbl = QLabel(text, **kwargs)
    _style_label(lbl, bold, color_attr, px)
    return lbl
