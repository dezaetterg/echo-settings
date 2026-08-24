import re
from PySide6.QtWidgets import QLabel
from theme.colors import ThemeColors, Colors

def fix_label_styles(widget):
    """
    Recursively finds QLabels and updates their stylesheets 
    by swapping the explicit hex/rgba codes for the current dynamic theme colors.
    This preserves padding, margins, borders, and specific styling.
    """
    labels = widget.findChildren(QLabel)
    
    # We will replace all known Light and Dark hardcoded colors with the current Theme color.
    replacements = [
        # Primary Text
        (ThemeColors.LIGHT_TEXT_PRIMARY, Colors.TEXT_PRIMARY),
        (ThemeColors.DARK_TEXT_PRIMARY, Colors.TEXT_PRIMARY),
        # Secondary Text
        (ThemeColors.LIGHT_TEXT_SECONDARY, Colors.TEXT_SECONDARY),
        (ThemeColors.DARK_TEXT_SECONDARY, Colors.TEXT_SECONDARY),
        (ThemeColors.LIGHT_SECTION_HEADER, Colors.SECTION_HEADER),
        (ThemeColors.DARK_SECTION_HEADER, Colors.SECTION_HEADER),
    ]
    
    for lbl in labels:
        if lbl.parent() and lbl.parent().__class__.__name__ == 'SidebarItem':
            continue
        current_ss = lbl.styleSheet()
        if not current_ss:
            continue
            
        last_applied = lbl.property("last_applied_ss")
        
        # If the current stylesheet differs from what we last applied,
        # it means it was modified externally (e.g. selection state changed).
        # We must update our original_ss cache.
        if last_applied != current_ss:
            lbl.setProperty("original_ss", current_ss)
            original_ss = current_ss
        else:
            original_ss = lbl.property("original_ss")
            
        new_ss = original_ss
        for search_str, replace_str in replacements:
            escaped_search = re.escape(search_str)
            new_ss = re.sub(escaped_search, replace_str, new_ss, flags=re.IGNORECASE)
            
        if new_ss != current_ss:
            lbl.setStyleSheet(new_ss)
            lbl.setProperty("last_applied_ss", new_ss)
        elif last_applied != current_ss:
            # Even if we made no replacements, we must record that we saw this new stylesheet
            lbl.setProperty("last_applied_ss", current_ss)
