import subprocess

class PowerBackend:
    def _run(self, cmd, default="", timeout=1.5):
        try:
            return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL, timeout=timeout).strip()
        except Exception:
            return default

    # ==========================
    # Power Profiles (DBus)
    # ==========================
    def get_power_profile(self):
        """Returns the current active profile (e.g., 'performance', 'balanced', 'power-saver')."""
        cmd = ["busctl", "--user", "get-property", "net.hadess.PowerProfiles", 
               "/net/hadess/PowerProfiles", "net.hadess.PowerProfiles", "ActiveProfile"]
        out = self._run(cmd)
        if not out and self._run(["busctl", "get-property", "net.hadess.PowerProfiles", 
               "/net/hadess/PowerProfiles", "net.hadess.PowerProfiles", "ActiveProfile"]):
            # Try system bus if user bus fails
            out = self._run(["busctl", "get-property", "net.hadess.PowerProfiles", 
               "/net/hadess/PowerProfiles", "net.hadess.PowerProfiles", "ActiveProfile"])
            
        if out.startswith('s '):
            return out[2:].strip('"\'')
        return ""

    def set_power_profile(self, profile):
        """Sets the power profile."""
        cmd = ["busctl", "set-property", "net.hadess.PowerProfiles", 
               "/net/hadess/PowerProfiles", "net.hadess.PowerProfiles", "ActiveProfile", "s", profile]
        self._run(cmd)

    # ==========================
    # Battery (UPower)
    # ==========================
    def get_battery_info(self):
        """Returns dict with battery stats or None if no battery."""
        devices = self._run(["upower", "-e"]).split('\n')
        bat_dev = None
        for dev in devices:
            if "battery" in dev.lower() and "displaydevice" not in dev.lower():
                bat_dev = dev
                break
        
        # Fallback to DisplayDevice if it reports battery
        if not bat_dev:
            for dev in devices:
                if "displaydevice" in dev.lower():
                    # Check if it actually has a battery
                    info = self._run(["upower", "-i", dev])
                    if "power supply: yes" in info.lower() or ("percentage:" in info and "0%" not in info):
                        bat_dev = dev
                    break
                    
        if not bat_dev:
            return None
            
        info = self._run(["upower", "-i", bat_dev])
        if not info:
            return None
            
        result = {}
        for line in info.split('\n'):
            line = line.strip()
            if line.startswith("state:"):
                result['state'] = line.split(":", 1)[1].strip()
            elif line.startswith("percentage:"):
                result['percentage'] = line.split(":", 1)[1].strip()
            elif line.startswith("time to empty:"):
                result['time_to_empty'] = line.split(":", 1)[1].strip()
            elif line.startswith("time to full:"):
                result['time_to_full'] = line.split(":", 1)[1].strip()
            elif line.startswith("energy-full:"):
                result['energy_full'] = line.split(":", 1)[1].strip()
            elif line.startswith("energy-full-design:"):
                result['energy_full_design'] = line.split(":", 1)[1].strip()
                
        # Calculate health if possible
        try:
            current = float(result.get('energy_full', '0').split()[0])
            design = float(result.get('energy_full_design', '0').split()[0])
            if design > 0:
                result['health'] = f"{int((current / design) * 100)}%"
        except:
            pass
            
        return result if 'percentage' in result else None

    # ==========================
    # GSettings (Timeouts)
    # ==========================
    def get_display_sleep(self):
        """Returns screen blank timeout in seconds (0 = never)."""
        for schema in ("org.gnome.desktop.session", "org.cinnamon.desktop.session"):
            out = self._run(["gsettings", "get", schema, "idle-delay"])
            try:
                if out:
                    return int(out.split()[-1])
            except:
                pass
        return 0

    def set_display_sleep(self, seconds):
        for schema in ("org.gnome.desktop.session", "org.cinnamon.desktop.session"):
            self._run(["gsettings", "set", schema, "idle-delay", str(seconds)])

    def get_computer_sleep(self):
        """Returns automatic suspend timeout in seconds (0 = never)."""
        for schema in ("org.gnome.settings-daemon.plugins.power", "org.cinnamon.settings-daemon.plugins.power"):
            out = self._run(["gsettings", "get", schema, "sleep-inactive-ac-timeout"])
            try:
                if out:
                    return int(out.split()[-1])
            except:
                pass
        return 0

    def set_computer_sleep(self, seconds):
        for schema in ("org.gnome.settings-daemon.plugins.power", "org.cinnamon.settings-daemon.plugins.power"):
            self._run(["gsettings", "set", schema, "sleep-inactive-ac-timeout", str(seconds)])
            self._run(["gsettings", "set", schema, "sleep-inactive-battery-timeout", str(seconds)])
            state = 'suspend' if seconds > 0 else 'nothing'
            self._run(["gsettings", "set", schema, "sleep-inactive-ac-type", f"'{state}'"])
            self._run(["gsettings", "set", schema, "sleep-inactive-battery-type", f"'{state}'"])

    def get_power_button_action(self):
        """Returns power button action ('suspend', 'hibernate', 'interactive', 'nothing', 'poweroff')."""
        out = self._run(["gsettings", "get", "org.gnome.settings-daemon.plugins.power", "power-button-action"])
        return out.strip("'\"") if out else "suspend"

    def set_power_button_action(self, action):
        self._run(["gsettings", "set", "org.gnome.settings-daemon.plugins.power", "power-button-action", f"'{action}'"])

    def get_low_power_mode(self):
        out = self._run(["gsettings", "get", "org.gnome.settings-daemon.plugins.power", "power-saver-profile-on-low-battery"])
        return out.strip() == "true"

    def set_low_power_mode(self, enabled):
        val = "true" if enabled else "false"
        self._run(["gsettings", "set", "org.gnome.settings-daemon.plugins.power", "power-saver-profile-on-low-battery", val])
