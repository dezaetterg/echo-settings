from backends.power_backend import PowerBackend

class PowerService:
    def __init__(self):
        self.backend = PowerBackend()

    def get_power_profile(self):
        """Returns the current power profile: 'performance', 'balanced', or 'power-saver'. Returns empty string if not available."""
        return self.backend.get_power_profile()

    def set_power_profile(self, profile: str):
        if profile in ['performance', 'balanced', 'power-saver']:
            self.backend.set_power_profile(profile)

    def get_battery_info(self):
        """
        Returns a formatted dict of battery info, e.g.:
        {
            'state': 'charging',
            'percentage': '100%',
            'time_remaining': '2h 15m' (or None),
            'health': '95%' (or None)
        }
        Returns None if no battery is detected.
        """
        info = self.backend.get_battery_info()
        if not info:
            return None

        formatted = {
            'state': info.get('state', 'unknown'),
            'percentage': info.get('percentage', '0%'),
            'health': info.get('health', None),
            'time_remaining': None
        }

        # Determine time remaining
        if formatted['state'] == 'charging' and 'time_to_full' in info:
            formatted['time_remaining'] = self._format_upower_time(info['time_to_full'])
        elif formatted['state'] == 'discharging' and 'time_to_empty' in info:
            formatted['time_remaining'] = self._format_upower_time(info['time_to_empty'])

        return formatted

    def _format_upower_time(self, time_str):
        # upower outputs like "2.5 hours" or "45.0 minutes"
        try:
            val, unit = time_str.strip().split()
            val = float(val)
            if 'hour' in unit:
                h = int(val)
                m = int((val - h) * 60)
                if h > 0 and m > 0:
                    return f"{h}h {m}m"
                elif h > 0:
                    return f"{h}h"
                else:
                    return f"{m}m"
            elif 'minute' in unit:
                return f"{int(val)}m"
        except:
            pass
        return time_str

    # Timeouts in seconds for the popup menus
    TIMEOUT_OPTIONS = {
        0: "Never",
        60: "1 minute",
        120: "2 minutes",
        300: "5 minutes",
        600: "10 minutes",
        900: "15 minutes",
        1800: "30 minutes",
        3600: "1 hour"
    }

    def get_display_sleep_options(self):
        from localization import t
        return {
            0: t("power.never", "Never"),
            60: t("power.1m", "1 minute"),
            120: t("power.2m", "2 minutes"),
            300: t("power.5m", "5 minutes"),
            600: t("power.10m", "10 minutes"),
            900: t("power.15m", "15 minutes"),
            1800: t("power.30m", "30 minutes"),
            3600: t("power.1h", "1 hour")
        }

    def get_display_sleep(self):
        return self.backend.get_display_sleep()

    def set_display_sleep(self, seconds: int):
        self.backend.set_display_sleep(seconds)

    def get_computer_sleep(self):
        return self.backend.get_computer_sleep()

    def set_computer_sleep(self, seconds: int):
        self.backend.set_computer_sleep(seconds)

    def get_power_button_options(self):
        from localization import t
        return {
            'suspend': t("power.btn_sleep", "Sleep"),
            'poweroff': t("power.btn_poweroff", "Power Off"),
            'interactive': t("power.btn_ask", "Ask"),
            'nothing': t("power.btn_nothing", "Nothing")
        }

    def get_power_button_action(self):
        return self.backend.get_power_button_action()

    def set_power_button_action(self, action: str):
        if action in self.POWER_BUTTON_OPTIONS:
            self.backend.set_power_button_action(action)

    def get_low_power_mode(self):
        return self.backend.get_low_power_mode()

    def set_low_power_mode(self, enabled: bool):
        self.backend.set_low_power_mode(enabled)
