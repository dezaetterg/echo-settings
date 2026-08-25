from theme.manager import ThemeManager

class ThemeColors:
    # Common Accent
    ACCENT_BLUE = "#007AFF"
    SWITCH_ON = "#34C759"
    MENU_ITEM_SELECTED = "#007AFF"
    MENU_ITEM_TEXT_SELECTED = "#FFFFFF"

    # Light Theme
    LIGHT_TEXT_PRIMARY = "#1D1D1F"
    LIGHT_TEXT_SECONDARY = "#993C3C43"
    LIGHT_TEXT_TERTIARY = "#8E8E93"
    LIGHT_CARD_BORDER = "#D2D2D7"
    LIGHT_WINDOW_BG = "#F5F5F7"
    LIGHT_CARD_BG = "#FFFFFF"

    # Sidebar & Menu specific
    LIGHT_SIDEBAR_BG = "#EBEBEB"
    LIGHT_SIDEBAR_BORDER = "#D2D2D7"
    LIGHT_SEARCH_BG = "#E3E3E8"
    LIGHT_SEARCH_BORDER_FOCUS = "#007AFF"
    LIGHT_MENU_ITEM_HOVER = "#0D000000"
    
    LIGHT_SECTION_HEADER = "#6E6E73"
    
    LIGHT_HOVER_BG = "#0D000000"
    LIGHT_PRESSED_BG = "#1A000000"

    # Dark Theme (macOS Tahoe specs)
    DARK_TEXT_PRIMARY = "#F5F5F7"
    DARK_TEXT_SECONDARY = "#99EBEBF5"
    DARK_TEXT_TERTIARY = "#8E8E93"
    DARK_CARD_BORDER = "#3A3A3C"
    DARK_WINDOW_BG = "#1C1C1E"
    DARK_CARD_BG = "#2C2C2E"

    # Sidebar & Menu specific
    DARK_SIDEBAR_BG = "#1C1C1E"
    DARK_SIDEBAR_BORDER = "#2C2C2E"
    DARK_SEARCH_BG = "#2C2C2E"
    DARK_SEARCH_BORDER_FOCUS = "#0A84FF"
    DARK_MENU_ITEM_HOVER = "#1AFFFFFF"
    
    DARK_SECTION_HEADER = "#98989D"
    
    DARK_HOVER_BG = "#1AFFFFFF"
    DARK_PRESSED_BG = "#33FFFFFF"
    
    DESTRUCTIVE = "#FF3B30"

    # Common aliases for safety and backward compatibility
    BORDER = DARK_CARD_BORDER
    BORDER_LIGHT = DARK_CARD_BORDER
    BORDER_SUBTLE = DARK_CARD_BORDER
    ACCENT_COLOR = ACCENT_BLUE
    TEXT_MUTED = DARK_TEXT_SECONDARY
    TEXT_HINT = DARK_TEXT_TERTIARY
    BG_CARD = DARK_CARD_BG
    BG_WINDOW = DARK_WINDOW_BG

    @classmethod
    def get(cls, name):
        if hasattr(cls, name):
            return getattr(cls, name)
        alias_map = {
            "BORDER": "CARD_BORDER",
            "BORDER_LIGHT": "CARD_BORDER",
            "BORDER_SUBTLE": "CARD_BORDER",
            "ACCENT_COLOR": "ACCENT_BLUE",
            "TEXT_MUTED": "TEXT_SECONDARY",
            "TEXT_HINT": "TEXT_TERTIARY",
            "BG_CARD": "CARD_BG",
            "BG_WINDOW": "WINDOW_BG",
        }
        actual_name = alias_map.get(name, name)
        if hasattr(cls, actual_name):
            return getattr(cls, actual_name)
        prefix = "DARK_" if ThemeManager.is_dark else "LIGHT_"
        if hasattr(cls, prefix + actual_name):
            return getattr(cls, prefix + actual_name)
        return "#007AFF"

class _ColorsProxy:
    def __getattr__(self, name):
        return ThemeColors.get(name)

Colors = _ColorsProxy()
