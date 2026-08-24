from backends.display_backend import DisplayBackend

class DisplayService:
    def __init__(self):
        self.backend = DisplayBackend()
        self.monitors = self.backend.get_monitors()
        self.active_monitor_id = self.monitors[0].id if self.monitors else None

    def get_monitors(self):
        return self.monitors

    def set_active_monitor(self, monitor_id: str):
        self.active_monitor_id = monitor_id

    def _get_active_monitor(self):
        if not self.monitors: return None
        for m in self.monitors:
            if m.id == self.active_monitor_id:
                return m
        return self.monitors[0]

    # ==========================
    # Display Settings (Resolution & Refresh Rate)
    # ==========================
    def get_display_info(self):
        # Kept for compatibility, returns True if monitors exist
        return bool(self.monitors)

    def get_resolution_options(self):
        mon = self._get_active_monitor()
        if not mon: return {"default": "Default"}
        
        options = {}
        for res in mon.resolutions:
            options[res] = res.replace('x', ' x ')
        return options

    def get_current_resolution(self):
        mon = self._get_active_monitor()
        if not mon: return "default"
        return mon.current_mode

    def set_resolution(self, res: str):
        mon = self._get_active_monitor()
        if not mon: return
        self.backend.apply_display_config(mon.id, {'mode': res})
        self.monitors = self.backend.get_monitors()

    def get_refresh_rate_options(self, resolution=None):
        mon = self._get_active_monitor()
        if not mon: return {"default": "Default"}
        
        res = resolution or mon.current_mode
        rates = mon.rates.get(res, [])
        
        options = {}
        for r in rates:
            try:
                val = float(r)
                label = f"{round(val)} Hz"
            except ValueError:
                label = f"{r} Hz"
            options[str(r)] = label
        return options

    def get_current_refresh_rate(self):
        mon = self._get_active_monitor()
        if not mon: return "default"
        return str(mon.current_rate)

    def set_refresh_rate(self, rate: str):
        mon = self._get_active_monitor()
        if not mon: return
        self.backend.apply_display_config(mon.id, {'mode': mon.current_mode, 'rate': float(rate)})
        self.monitors = self.backend.get_monitors()

    # ==========================
    # Scale
    # ==========================
    def get_scale_options(self):
        return {
            "1.0": "100%",
            "1.25": "125%",
            "1.5": "150%",
            "2.0": "200%"
        }

    def get_current_scale(self):
        val = self.backend.get_scale()
        # Find closest string match
        if val == 1.0: return "1.0"
        if val == 1.25: return "1.25"
        if val == 1.5: return "1.5"
        if val == 2.0: return "2.0"
        return "1.0"

    def set_scale(self, scale_str: str):
        try:
            val = float(scale_str)
            self.backend.set_scale(val)
            self.monitors = self.backend.get_monitors()
        except ValueError:
            pass

    # ==========================
    # Orientation & Layout
    # ==========================
    def get_current_orientation(self) -> str:
        mon = self._get_active_monitor()
        if not mon: return "0"
        return str(mon.orientation)
        
    def set_orientation(self, orientation_str: str):
        mon = self._get_active_monitor()
        if not mon: return
        self.backend.apply_display_config(mon.id, {'orientation': int(orientation_str)})
        self.monitors = self.backend.get_monitors()

    def is_primary(self) -> bool:
        mon = self._get_active_monitor()
        if not mon: return False
        return mon.is_primary
        
    def set_primary(self, is_primary: bool):
        mon = self._get_active_monitor()
        if not mon: return
        self.backend.apply_display_config(mon.id, {'is_primary': is_primary})
        self.monitors = self.backend.get_monitors()
        
    def update_arrangement(self, positions: dict):
        self.backend.apply_arrangement(positions)
        self.monitors = self.backend.get_monitors()

    # ==========================
    # Night Shift (Night Light)
    # ==========================
    def is_night_shift_enabled(self):
        return self.backend.is_night_light_enabled()

    def set_night_shift_enabled(self, enabled: bool):
        self.backend.set_night_light_enabled(enabled)
        
        try:
            from services.appearance_service import AppearanceService
            from PySide6.QtCore import QSettings
            app_service = AppearanceService()
            settings = QSettings("TahoeSettings", "App")
            
            if enabled:
                # Save previous theme if it was light
                current_theme = app_service.get_theme()
                settings.setValue("pre_nightshift_theme", current_theme)
                app_service.set_theme("prefer-dark")
            else:
                prev = settings.value("pre_nightshift_theme", None)
                if prev is not None:
                    app_service.set_theme(prev)
                    settings.remove("pre_nightshift_theme")
        except Exception as e:
            print(f"Failed to auto-set dark mode: {e}")

    def get_night_shift_schedule_options(self):
        return {
            "custom": "Custom",
            "sunset": "Sunset to Sunrise"
        }

    def get_night_shift_schedule(self):
        return self.backend.get_night_light_schedule()

    def set_night_shift_schedule(self, mode: str):
        if mode in ["custom", "sunset"]:
            self.backend.set_night_light_schedule(mode)

    def get_night_shift_warmth(self):
        return self.backend.get_night_light_temperature()
        
    def set_night_shift_warmth(self, value: int):
        # Auto-enable Night Shift if user changes warmth
        if not self.is_night_shift_enabled():
            self.set_night_shift_enabled(True)
        self.backend.set_night_light_temperature(value)

    # ==========================
    # Power
    # ==========================
    def get_idle_delay(self):
        return self.backend.get_idle_delay()
        
    def set_idle_delay(self, mode: str):
        self.backend.set_idle_delay(mode)

    def is_auto_brightness_enabled(self):
        return self.backend.is_auto_brightness_enabled()
        
    def set_auto_brightness_enabled(self, enabled: bool):
        self.backend.set_auto_brightness_enabled(enabled)

    # ==========================
    # Advanced: DDC/CI
    # ==========================
    def has_hardware_ddcci(self):
        return self.backend.has_ddcci()

    def get_brightness(self):
        return self.backend.get_brightness()

    def set_brightness(self, value: int):
        self.backend.set_brightness(value)

    def get_contrast(self):
        val = self.backend.get_ddc_value("12")
        return val if val is not None else 50

    def set_contrast(self, value: int):
        self.backend.set_ddc_value("12", value)

    def get_color_temperature_options(self):
        return {
            "04": "5000K (Warm)",
            "05": "6500K (Standard)",
            "08": "9300K (Cool)"
        }

    def get_color_temperature(self):
        # Read preset
        val = self.backend.get_ddc_value("14")
        if val == 4: return "04"
        if val == 8: return "08"
        return "05"

    def set_color_temperature(self, value: str):
        self.backend.set_ddc_value("14", int(value))

    # ==========================
    # Advanced: VRR & HDR
    # ==========================
    def has_vrr(self):
        return self.backend.has_vrr()

    def get_vrr_mode(self):
        return self.backend.get_vrr_mode()

    def set_vrr_mode(self, mode: str):
        self.backend.set_vrr_mode(mode)
        
    def is_vsync_enabled(self):
        return self.backend.is_vsync_enabled()
        
    def set_vsync_enabled(self, enabled: bool):
        self.backend.set_vsync_enabled(enabled)
        
    def get_response_time(self):
        return self.backend.get_response_time()
        
    def set_response_time(self, mode: str):
        self.backend.set_response_time(mode)

    def has_hdr(self):
        return self.backend.has_hdr()

    def is_hdr_enabled(self):
        return self.backend.is_hdr_enabled()

    def set_hdr_enabled(self, enabled: bool):
        self.backend.set_hdr_enabled(enabled)

    # ==========================
    # Color Profiles & OLED Care
    # ==========================
    def get_color_profile(self):
        return self.backend.get_color_profile()
        
    def set_color_profile(self, profile: str):
        self.backend.set_color_profile(profile)
        
    def get_sdr_brightness(self):
        return self.backend.get_sdr_brightness()
        
    def set_sdr_brightness(self, value: int):
        self.backend.set_sdr_brightness(value)
        
    def is_oled_care_enabled(self):
        return self.backend.is_oled_care_enabled()
        
    def set_oled_care_enabled(self, enabled: bool):
        self.backend.set_oled_care_enabled(enabled)

