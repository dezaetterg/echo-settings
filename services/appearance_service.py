import os
import logging
from backends.appearance_backend import AppearanceBackend

# Set up logging to track user clicks
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

class AppearanceService:
    def __init__(self):
        self.backend = AppearanceBackend()
        self.current_collection = "tahoe"

    def get_current_collection(self):
        return self.current_collection
        
    def set_collection(self, collection_name: str):
        self.current_collection = collection_name
        self.set_theme(self.get_theme())

    def get_theme(self) -> str:
        return self.backend.get_theme_mode()

    def get_theme_mode(self) -> str:
        return self.backend.get_theme_mode()

    def get_effective_theme(self, mode: str = None) -> str:
        return self.backend.get_effective_color_scheme(mode)

    def apply_effective_theme(self, scheme: str) -> bool:
        return self.backend.apply_effective_color_scheme(scheme)

    def set_theme(self, theme: str) -> bool:
        logging.info(f"AppearanceService.set_theme called with: {theme}")
        success = self.backend.set_theme_mode(theme)
        logging.info(f"AppearanceService.set_theme result: {success}")
        return success

    def set_wallpaper(self, light_uri: str, dark_uri: str) -> bool:
        logging.info(f"AppearanceService.set_wallpaper called with light={light_uri}, dark={dark_uri}")
        light_encoded = "file://" + light_uri.replace(" ", "%20")
        dark_encoded = "file://" + dark_uri.replace(" ", "%20")
        success_light = self.backend.set_wallpaper(light_encoded, is_dark=False)
        success_dark = self.backend.set_wallpaper(dark_encoded, is_dark=True)
        logging.info(f"Wallpaper result: light={success_light}, dark={success_dark}")
        return success_light and success_dark

    def supports_accent_color(self) -> bool:
        return self.backend.supports_accent_color()

    def get_accent_color(self) -> str:
        return self.backend.get_accent_color()

    def get_accent_intensity(self) -> int:
        return self.backend.get_accent_intensity()

    def set_accent_color(self, color: str, intensity: int = 80, custom_hex: str = None) -> bool:
        return self.backend.set_accent_color(color, intensity=intensity, custom_hex=custom_hex)

    # --- Desktop Support Checks ---
    def is_hot_corners_supported(self) -> bool:
        return self.backend.is_hot_corners_supported()

    def is_multitasking_supported(self) -> bool:
        return self.backend.is_multitasking_supported()

    # --- GNOME Multitasking & Workspaces ---
    def get_hot_corners_enabled(self) -> bool:
        return self.backend.get_hot_corners_enabled()

    def set_hot_corners_enabled(self, enabled: bool) -> bool:
        return self.backend.set_hot_corners_enabled(enabled)

    def get_top_left_corner_action(self) -> str:
        return self.backend.get_top_left_corner_action()

    def set_top_left_corner_action(self, action: str) -> bool:
        return self.backend.set_top_left_corner_action(action)

    def get_top_right_corner_action(self) -> str:
        return self.backend.get_top_right_corner_action()

    def set_top_right_corner_action(self, action: str) -> bool:
        return self.backend.set_top_right_corner_action(action)

    def get_bottom_left_corner_action(self) -> str:
        return self.backend.get_bottom_left_corner_action()

    def set_bottom_left_corner_action(self, action: str) -> bool:
        return self.backend.set_bottom_left_corner_action(action)

    def get_bottom_right_corner_action(self) -> str:
        return self.backend.get_bottom_right_corner_action()

    def set_bottom_right_corner_action(self, action: str) -> bool:
        return self.backend.set_bottom_right_corner_action(action)

    def get_is_dynamic_workspaces(self) -> bool:
        return self.backend.get_is_dynamic_workspaces()

    def set_dynamic_workspaces(self, dynamic: bool) -> bool:
        return self.backend.set_dynamic_workspaces(dynamic)

    def get_num_workspaces(self) -> int:
        return self.backend.get_num_workspaces()

    def set_num_workspaces(self, num: int) -> bool:
        return self.backend.set_num_workspaces(num)

    def get_workspaces_only_on_primary(self) -> bool:
        return self.backend.get_workspaces_only_on_primary()

    def set_workspaces_only_on_primary(self, primary_only: bool) -> bool:
        return self.backend.set_workspaces_only_on_primary(primary_only)

    def get_app_switcher_current_workspace_only(self) -> bool:
        return self.backend.get_app_switcher_current_workspace_only()

    def set_app_switcher_current_workspace_only(self, current_only: bool) -> bool:
        return self.backend.set_app_switcher_current_workspace_only(current_only)
