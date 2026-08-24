import subprocess
import re
import os
import shutil
import glob

from models.monitor import MonitorModel


def detect_desktop_environment() -> str:
    """Detects current Desktop Environment (gnome, cinnamon, xfce, mate, kde, etc.)."""
    xdg = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    session = os.environ.get("DESKTOP_SESSION", "").lower()
    if "cinnamon" in xdg or "cinnamon" in session or "x-cinnamon" in xdg:
        return "cinnamon"
    if "xfce" in xdg or "xfce" in session:
        return "xfce"
    if "mate" in xdg or "mate" in session:
        return "mate"
    if "kde" in xdg or "plasma" in xdg or "plasma" in session:
        return "kde"
    return "gnome"


class DisplayBackend:
    def __init__(self):
        self.de = detect_desktop_environment()
        self._cached_hdr = None
        self._cached_schemas = None
        self._cached_ddcci = None

    def _run(self, cmd, default="", timeout=1.0):
        try:
            return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL, timeout=timeout).strip()
        except Exception:
            return default

    def _has_schema(self, schema_id: str) -> bool:
        if self._cached_schemas is None:
            try:
                out = subprocess.check_output(["gsettings", "list-schemas"], text=True, stderr=subprocess.DEVNULL, timeout=1.0)
                self._cached_schemas = set(out.splitlines())
            except Exception:
                self._cached_schemas = set()
        return schema_id in self._cached_schemas

    def get_monitors(self):
        # On Wayland + GNOME only, try Mutter DBus
        is_wayland = os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
        if is_wayland and self.de == "gnome":
            dbus_mons = self._get_dbus_monitors()
            if dbus_mons:
                return dbus_mons
        # Fallback to xrandr (X11 / Cinnamon / Linux Mint / XFCE / MATE / etc.)
        return self._get_xrandr_monitors()

    def _get_dbus_monitors(self):
        try:
            import json
            out = subprocess.check_output([
                "busctl", "--user", "--timeout=1", "call", "org.gnome.Mutter.DisplayConfig",
                "/org/gnome/Mutter/DisplayConfig", "org.gnome.Mutter.DisplayConfig",
                "GetCurrentState", "-j"
            ], text=True, stderr=subprocess.DEVNULL, timeout=1.0)
            data = json.loads(out)
            
            physicals = data['data'][1]
            logicals = data['data'][2]
            
            monitors = []
            
            for log_mon in logicals:
                x = log_mon[0]
                y = log_mon[1]
                scale = log_mon[2]
                transform = log_mon[3]
                primary = log_mon[4]
                connectors = log_mon[5]
                
                for phys_mon in physicals:
                    phys_info = phys_mon[0]
                    connector = phys_info[0]
                    # Check if this physical connector is part of this logical monitor
                    if connector in [c[0] for c in connectors]:
                        name = phys_info[2]
                        modes = phys_mon[1]
                        
                        current_res = "1920x1080"
                        current_rate = 60.0
                        width, height = 1920, 1080
                        
                        all_res = []
                        rates_map = {}
                        
                        for mode in modes:
                            w = mode[1]
                            h = mode[2]
                            rate = mode[3]
                            props = mode[6]
                            
                            res_str = f"{w}x{h}"
                            if res_str not in all_res:
                                all_res.append(res_str)
                                rates_map[res_str] = []
                            
                            # Rate formatting
                            rate_val = round(rate, 2)
                            if rate_val not in rates_map[res_str]:
                                rates_map[res_str].append(rate_val)
                                
                            if props.get('is-current', False):
                                current_res = res_str
                                current_rate = rate_val
                                width = w
                                height = h
                        
                        # Sort resolutions descending
                        def res_key(r):
                            parts = r.split('x')
                            return int(parts[0]) * int(parts[1])
                        all_res.sort(key=res_key, reverse=True)
                        
                        # Sort rates descending for each res
                        for r in rates_map:
                            rates_map[r].sort(reverse=True)

                        mon = MonitorModel(
                            id=connector,
                            name=name if name else connector,
                            is_primary=primary,
                            current_mode=current_res,
                            current_rate=current_rate,
                            resolutions=all_res,
                            rates=rates_map,
                            x=x,
                            y=y,
                            width=width,
                            height=height,
                            orientation=transform,
                            scale=scale
                        )
                        monitors.append(mon)
            return monitors
        except Exception:
            return []

    def _get_xrandr_monitors(self):
        out = self._run(["xrandr", "--query"])
        if not out:
            return []

        monitors = []
        current_mon = None
        
        # Regex patterns
        mon_pattern = re.compile(r"^([\w-]+)\s+(connected|disconnected)\s+(primary\s+)?(\d+x\d+\+\d+\+\d+)?\s*(left|right|inverted)?\s*(?:\((?:normal|left|inverted|right)[\w\s]*\))?\s*(?:(\d+)mm\s+x\s+(\d+)mm)?")
        mode_pattern = re.compile(r"^\s+(\d+x\d+)\s+((?:[\d.]+\*?\+?\s*)+)")

        for line in out.splitlines():
            m_match = mon_pattern.match(line)
            if m_match:
                conn = m_match.group(1)
                status = m_match.group(2)
                is_pri = bool(m_match.group(3))
                geom = m_match.group(4)
                orient_str = m_match.group(5)
                
                if status != "connected":
                    current_mon = None
                    continue

                x, y, w, h = 0, 0, 1920, 1080
                curr_res = ""
                if geom:
                    g_match = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", geom)
                    if g_match:
                        w = int(g_match.group(1))
                        h = int(g_match.group(2))
                        x = int(g_match.group(3))
                        y = int(g_match.group(4))
                        curr_res = f"{w}x{h}"

                orient = 0
                if orient_str == "left": orient = 1
                elif orient_str == "inverted": orient = 2
                elif orient_str == "right": orient = 3

                current_mon = MonitorModel(
                    id=conn,
                    name=conn,
                    is_primary=is_pri,
                    current_mode=curr_res,
                    current_rate=60.0,
                    resolutions=[],
                    rates={},
                    x=x,
                    y=y,
                    width=w,
                    height=h,
                    orientation=orient,
                    scale=1.0
                )
                monitors.append(current_mon)
                continue

            if current_mon:
                mode_match = mode_pattern.match(line)
                if mode_match:
                    res = mode_match.group(1)
                    rates_str = mode_match.group(2)
                    
                    if res not in current_mon.resolutions:
                        current_mon.resolutions.append(res)
                        current_mon.rates[res] = []

                    # Parse rates like "60.00*+ 50.00"
                    tokens = rates_str.split()
                    for tok in tokens:
                        is_active = "*" in tok
                        is_pref = "+" in tok
                        clean_rate = tok.replace("*", "").replace("+", "")
                        try:
                            rate_val = float(clean_rate)
                            if rate_val not in current_mon.rates[res]:
                                current_mon.rates[res].append(rate_val)
                            if is_active:
                                current_mon.current_rate = rate_val
                                if not current_mon.current_mode:
                                    current_mon.current_mode = res
                        except ValueError:
                            pass
        return monitors

    def apply_display_config(self, connector, config):
        if os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
            self._apply_wayland_config(connector, config)
            return

        # X11 Fallback using xrandr
        cmd = ["xrandr", "--output", connector]
        
        if "mode" in config:
            cmd.extend(["--mode", str(config["mode"])])
        if "rate" in config:
            cmd.extend(["--rate", str(config["rate"])])
        if "orientation" in config:
            orient_map = {0: "normal", 1: "left", 2: "inverted", 3: "right"}
            cmd.extend(["--rotate", orient_map.get(config["orientation"], "normal")])
        if "primary" in config:
            if config["primary"]:
                cmd.append("--primary")
        if "scale" in config:
            s = float(config["scale"])
            cmd.extend(["--scale", f"{s}x{s}"])

        self._run(cmd)

    def apply_display_arrangement(self, positions):
        if os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
            self._apply_wayland_arrangement(positions)
            return

        cmd = ["xrandr"]
        for connector, pos in positions.items():
            cmd.extend(["--output", connector, "--pos", f"{pos['x']}x{pos['y']}"])
        self._run(cmd)

    def _apply_wayland_config(self, target_connector, config):
        try:
            import json
            config_json = json.dumps(config)
            self._run(["/usr/bin/python3", "backends/wayland_dbus.py", "config", target_connector, config_json])
        except Exception as e:
            print("Wayland config error:", e)

    def _apply_wayland_arrangement(self, positions):
        try:
            import json
            pos_json = json.dumps(positions)
            self._run(["/usr/bin/python3", "backends/wayland_dbus.py", "arrange", pos_json])
        except Exception as e:
            print("Wayland arrangement error:", e)

    # ==========================
    # Scale (Multi-DE Support: Cinnamon, GNOME, XFCE)
    # ==========================
    def get_scale(self) -> float:
        """Returns text/display scaling factor (e.g. 1.0, 1.25, 1.5, 2.0)."""
        if self.de == "cinnamon" or self._has_schema("org.cinnamon.desktop.interface"):
            out = self._run(["gsettings", "get", "org.cinnamon.desktop.interface", "text-scaling-factor"])
            try:
                val = float(out.replace("'", ""))
                if val > 0:
                    return val
            except Exception:
                pass

        if self._has_schema("org.gnome.desktop.interface"):
            out = self._run(["gsettings", "get", "org.gnome.desktop.interface", "text-scaling-factor"])
            try:
                return float(out.replace("'", ""))
            except Exception:
                pass

        return 1.0

    def set_scale(self, scale: float):
        """Sets scale factor across Cinnamon, GNOME, and active compositor."""
        scale_val = max(0.5, min(3.0, float(scale)))
        
        # 1. Cinnamon Desktop Interface
        if self.de == "cinnamon" or self._has_schema("org.cinnamon.desktop.interface"):
            self._run(["gsettings", "set", "org.cinnamon.desktop.interface", "text-scaling-factor", str(scale_val)])
            int_scale = 2 if scale_val >= 1.75 else 1
            try:
                self._run(["gsettings", "set", "org.cinnamon.desktop.interface", "scaling-factor", f"uint32 {int_scale}"])
            except Exception:
                pass

        # 2. GNOME Desktop Interface
        if self._has_schema("org.gnome.desktop.interface"):
            self._run(["gsettings", "set", "org.gnome.desktop.interface", "text-scaling-factor", str(scale_val)])

    # ==========================
    # Night Light / Night Shift (Multi-DE Support: Cinnamon, GNOME, Redshift)
    # ==========================
    def is_night_light_enabled(self) -> bool:
        # Cinnamon Schema
        if self.de == "cinnamon" or self._has_schema("org.cinnamon.settings-daemon.plugins.color"):
            out = self._run(["gsettings", "get", "org.cinnamon.settings-daemon.plugins.color", "night-light-enabled"])
            if out.strip().lower() in ("true", "1"):
                return True

        # GNOME Schema
        if self._has_schema("org.gnome.settings-daemon.plugins.color"):
            out = self._run(["gsettings", "get", "org.gnome.settings-daemon.plugins.color", "night-light-enabled"])
            if out.strip().lower() in ("true", "1"):
                return True

        # Redshift process check fallback
        if shutil.which("pgrep"):
            p_out = self._run(["pgrep", "-x", "redshift"])
            if p_out:
                return True

        # File state fallback
        state_file = os.path.expanduser("~/.config/tahoe_night_light")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    return f.read().strip() == "1"
            except Exception:
                pass
        return False

    def set_night_light_enabled(self, enabled: bool):
        val_str = "true" if enabled else "false"

        # Cinnamon Schema
        if self.de == "cinnamon" or self._has_schema("org.cinnamon.settings-daemon.plugins.color"):
            self._run(["gsettings", "set", "org.cinnamon.settings-daemon.plugins.color", "night-light-enabled", val_str])

        # GNOME Schema
        if self._has_schema("org.gnome.settings-daemon.plugins.color"):
            self._run(["gsettings", "set", "org.gnome.settings-daemon.plugins.color", "night-light-enabled", val_str])

        # Redshift / Gammastep fallback on other DEs
        if not self._has_schema("org.cinnamon.settings-daemon.plugins.color") and not self._has_schema("org.gnome.settings-daemon.plugins.color"):
            if enabled:
                temp = int(6500 - (self.get_night_light_temperature() * 45.0))
                if shutil.which("redshift"):
                    self._run(["redshift", "-x"])
                    subprocess.Popen(["redshift", "-O", str(temp), "-P"])
                elif shutil.which("gammastep"):
                    self._run(["gammastep", "-x"])
                    subprocess.Popen(["gammastep", "-O", str(temp)])
            else:
                if shutil.which("redshift"):
                    self._run(["redshift", "-x"])
                elif shutil.which("gammastep"):
                    self._run(["gammastep", "-x"])

        # Persist state file
        try:
            state_file = os.path.expanduser("~/.config/tahoe_night_light")
            with open(state_file, "w") as f:
                f.write("1" if enabled else "0")
        except Exception:
            pass

    def get_night_light_schedule(self) -> str:
        """Returns 'sunset' or 'custom'."""
        if self.de == "cinnamon" or self._has_schema("org.cinnamon.settings-daemon.plugins.color"):
            out = self._run(["gsettings", "get", "org.cinnamon.settings-daemon.plugins.color", "night-light-schedule-automatic"])
            if out.strip().lower() in ("true", "1"):
                return "sunset"

        if self._has_schema("org.gnome.settings-daemon.plugins.color"):
            out = self._run(["gsettings", "get", "org.gnome.settings-daemon.plugins.color", "night-light-schedule-automatic"])
            if out.strip().lower() in ("true", "1"):
                return "sunset"
        return "custom"

    def set_night_light_schedule(self, mode: str):
        val = "true" if mode == "sunset" else "false"
        if self.de == "cinnamon" or self._has_schema("org.cinnamon.settings-daemon.plugins.color"):
            self._run(["gsettings", "set", "org.cinnamon.settings-daemon.plugins.color", "night-light-schedule-automatic", val])
        if self._has_schema("org.gnome.settings-daemon.plugins.color"):
            self._run(["gsettings", "set", "org.gnome.settings-daemon.plugins.color", "night-light-schedule-automatic", val])

    def get_night_light_temperature(self) -> int:
        """Returns 0-100 (0=6500K Cool, 100=2000K Warm)."""
        temp = None
        if self.de == "cinnamon" or self._has_schema("org.cinnamon.settings-daemon.plugins.color"):
            out = self._run(["gsettings", "get", "org.cinnamon.settings-daemon.plugins.color", "night-light-temperature"])
            try:
                temp = int(out.split()[-1])
            except Exception:
                pass

        if temp is None and self._has_schema("org.gnome.settings-daemon.plugins.color"):
            out = self._run(["gsettings", "get", "org.gnome.settings-daemon.plugins.color", "night-light-temperature"])
            try:
                temp = int(out.split()[-1])
            except Exception:
                pass

        if temp is not None:
            temp = max(2000, min(6500, temp))
            return int((6500 - temp) / 45.0)

        # Fallback to local config
        state_file = os.path.expanduser("~/.config/tahoe_night_light_temp")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    return int(f.read().strip())
            except Exception:
                pass
        return 50

    def set_night_light_temperature(self, value: int):
        """Value is 0-100. 0=6500K, 100=2000K."""
        temp = int(6500 - (value * 45.0))
        temp = max(2000, min(6500, temp))

        if self.de == "cinnamon" or self._has_schema("org.cinnamon.settings-daemon.plugins.color"):
            self._run(["gsettings", "set", "org.cinnamon.settings-daemon.plugins.color", "night-light-temperature", f"uint32 {temp}"])

        if self._has_schema("org.gnome.settings-daemon.plugins.color"):
            self._run(["gsettings", "set", "org.gnome.settings-daemon.plugins.color", "night-light-temperature", f"uint32 {temp}"])

        try:
            state_file = os.path.expanduser("~/.config/tahoe_night_light_temp")
            with open(state_file, "w") as f:
                f.write(str(value))
        except Exception:
            pass

    # ==========================
    # Power & Auto Brightness (Multi-DE GSettings)
    # ==========================
    def get_idle_delay(self):
        if self.de == "cinnamon" or self._has_schema("org.cinnamon.desktop.session"):
            out = self._run(["gsettings", "get", "org.cinnamon.desktop.session", "idle-delay"])
            try:
                val = int(out.split()[-1])
                if val == 0: return "never"
                if val <= 300: return "5m"
                if val <= 600: return "10m"
                if val <= 900: return "15m"
                if val <= 1800: return "30m"
                return "1h"
            except Exception:
                pass

        out = self._run(["gsettings", "get", "org.gnome.desktop.session", "idle-delay"])
        try:
            val = int(out.split()[-1])
            if val == 0: return "never"
            if val <= 300: return "5m"
            if val <= 600: return "10m"
            if val <= 900: return "15m"
            if val <= 1800: return "30m"
            return "1h"
        except Exception:
            return "5m"

    def set_idle_delay(self, mode: str):
        sec_map = {"never": 0, "5m": 300, "10m": 600, "15m": 900, "30m": 1800, "1h": 3600}
        sec = sec_map.get(mode, 300)

        if self.de == "cinnamon" or self._has_schema("org.cinnamon.desktop.session"):
            self._run(["gsettings", "set", "org.cinnamon.desktop.session", "idle-delay", f"uint32 {sec}"])
        if self._has_schema("org.gnome.desktop.session"):
            self._run(["gsettings", "set", "org.gnome.desktop.session", "idle-delay", f"uint32 {sec}"])

    def is_auto_brightness_enabled(self):
        out = self._run(["gsettings", "get", "org.gnome.settings-daemon.plugins.power", "ambient-enabled"])
        return out.strip().lower() == "true"

    def set_auto_brightness_enabled(self, enabled: bool):
        val = "true" if enabled else "false"
        self._run(["gsettings", "set", "org.gnome.settings-daemon.plugins.power", "ambient-enabled", val])

    # ==========================
    # Hardware & Software Brightness (Multi-Level Robust Fallback)
    # ==========================
    def has_ddcci(self):
        if self._cached_ddcci is not None:
            return self._cached_ddcci
        if not shutil.which("ddcutil"):
            self._cached_ddcci = False
            return False
        # Quick non-blocking check with brief mode and timeout
        try:
            out = self._run(["ddcutil", "detect", "--brief", "--sleep-multiplier", ".1"], timeout=0.8)
            self._cached_ddcci = "Display 1" in out
        except Exception:
            self._cached_ddcci = False
        return self._cached_ddcci

    def get_ddc_value(self, vcp_code: str):
        if not self.has_ddcci(): return None
        out = self._run(["ddcutil", "getvcp", vcp_code, "--brief", "--sleep-multiplier", ".1"], timeout=0.8)
        match = re.search(r"current value =\s+(\d+)", out)
        if match:
            return int(match.group(1))
        return None

    def set_ddc_value(self, vcp_code: str, value: int):
        if not self.has_ddcci(): return
        self._run(["ddcutil", "setvcp", vcp_code, str(value), "--sleep-multiplier", ".1"], timeout=0.8)

    def get_brightness(self) -> int:
        """Returns active screen brightness percentage (0-100)."""
        # 1. brightnessctl
        if shutil.which("brightnessctl"):
            out = self._run(["brightnessctl", "g"])
            max_out = self._run(["brightnessctl", "m"])
            try:
                if out and max_out and float(max_out) > 0:
                    return int((float(out) / float(max_out)) * 100)
            except Exception:
                pass

        # 2. Sysfs Backlight Direct Read
        for b_path in glob.glob("/sys/class/backlight/*/brightness"):
            try:
                with open(b_path, "r") as f:
                    cur_b = float(f.read().strip())
                max_path = os.path.join(os.path.dirname(b_path), "max_brightness")
                with open(max_path, "r") as f:
                    max_b = float(f.read().strip())
                if max_b > 0:
                    return int((cur_b / max_b) * 100)
            except Exception:
                pass

        # 3. DDC/CI for external monitors
        ddc_val = self.get_ddc_value("10")
        if ddc_val is not None:
            return ddc_val

        # 4. State file or default
        state_file = os.path.expanduser("~/.config/tahoe_brightness")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    return int(f.read().strip())
            except Exception:
                pass
        return 80

    def set_brightness(self, value: int):
        """Sets hardware screen brightness percentage (0-100)."""
        val = max(1, min(100, int(value)))

        # 1. brightnessctl
        if shutil.which("brightnessctl"):
            try:
                self._run(["brightnessctl", "s", f"{val}%"])
            except Exception:
                pass

        # 2. Sysfs direct write
        for b_path in glob.glob("/sys/class/backlight/*/brightness"):
            try:
                max_path = os.path.join(os.path.dirname(b_path), "max_brightness")
                with open(max_path, "r") as f:
                    max_b = float(f.read().strip())
                target_raw = int((val / 100.0) * max_b)
                with open(b_path, "w") as f:
                    f.write(str(target_raw))
            except Exception:
                pass

        # 3. DDC/CI
        if self.has_ddcci():
            self.set_ddc_value("10", val)

        # 4. Software fallback via xrandr on X11
        if os.environ.get("XDG_SESSION_TYPE", "").lower() != "wayland" and shutil.which("xrandr"):
            try:
                ratio = max(0.1, min(1.0, val / 100.0))
                mons = self._get_xrandr_monitors()
                for m in mons:
                    self._run(["xrandr", "--output", m.id, "--brightness", f"{ratio:.2f}"])
            except Exception:
                pass

        # Save to state
        try:
            state_file = os.path.expanduser("~/.config/tahoe_brightness")
            with open(state_file, "w") as f:
                f.write(str(val))
        except Exception:
            pass

    # ==========================
    # VRR (Adaptive Sync) & High Dynamic Range (HDR)
    # ==========================
    def has_vrr(self):
        drm_vrr = False
        for path in glob.glob("/sys/class/drm/card*-*/vrr_capable"):
            try:
                with open(path, "r") as f:
                    if f.read().strip() == "1":
                        drm_vrr = True
                        break
            except Exception:
                pass
        
        if self._has_schema("org.gnome.mutter"):
            features = self._run(["gsettings", "get", "org.gnome.mutter", "experimental-features"])
            if "variable-refresh-rate" in features or drm_vrr:
                return True
        return drm_vrr

    def get_vrr_mode(self):
        if self._has_schema("org.gnome.mutter"):
            features = self._run(["gsettings", "get", "org.gnome.mutter", "experimental-features"])
            if "variable-refresh-rate" in features:
                return "always"
        return "off"

    def set_vrr_mode(self, mode: str):
        enabled = mode in ["always", "fullscreen"]
        if not self._has_schema("org.gnome.mutter"):
            return
        features_str = self._run(["gsettings", "get", "org.gnome.mutter", "experimental-features"])
        try:
            import ast
            features = ast.literal_eval(features_str)
        except Exception:
            features = []
            
        if enabled and "variable-refresh-rate" not in features:
            features.append("variable-refresh-rate")
        elif not enabled and "variable-refresh-rate" in features:
            features.remove("variable-refresh-rate")
            
        val = str(features).replace('"', "'")
        self._run(["gsettings", "set", "org.gnome.mutter", "experimental-features", val])

    def is_vsync_enabled(self):
        state_file = os.path.expanduser("~/.config/tahoe_vsync")
        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                return f.read().strip() == "1"
        return True

    def set_vsync_enabled(self, enabled: bool):
        state_file = os.path.expanduser("~/.config/tahoe_vsync")
        with open(state_file, "w") as f:
            f.write("1" if enabled else "0")
            
        if os.environ.get("XDG_SESSION_TYPE", "").lower() != "wayland" and shutil.which("xrandr"):
            val = "on" if enabled else "off"
            mons = self._get_xrandr_monitors()
            for m in mons:
                self._run(["xrandr", "--output", m.id, "--set", "TearFree", val])

    def get_response_time(self):
        val = self.get_ddc_value("87")
        if val == 100: return "faster"
        if val == 50: return "fast"
        return "normal"

    def set_response_time(self, mode: str):
        val = 0
        if mode == "fast": val = 50
        elif mode == "faster": val = 100
        self.set_ddc_value("87", val)

    def has_hdr(self) -> bool:
        """Accurate HDR detection: checks EDID CEA HDR static metadata and Wayland compositor."""
        if self._cached_hdr is not None:
            return self._cached_hdr

        # Check EDID dumps in sysfs for HDR metadata tag (tag 0x07 with ext tag 0x06)
        edid_has_hdr = False
        for edid_path in glob.glob("/sys/class/drm/card*-*/edid"):
            try:
                with open(edid_path, "rb") as f:
                    edid_bytes = f.read()
                    if len(edid_bytes) >= 256:  # Has CEA extension block
                        # Search for HDR static metadata descriptor tag
                        for i in range(128, len(edid_bytes) - 4):
                            if edid_bytes[i] == 0x07 and edid_bytes[i+1] == 0x06:
                                edid_has_hdr = True
                                break
            except Exception:
                pass

        # Check Mutter experimental HDR on Wayland
        is_wayland = os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
        mutter_hdr = False
        if is_wayland and self._has_schema("org.gnome.mutter"):
            features = self._run(["gsettings", "get", "org.gnome.mutter", "experimental-features"])
            if "experimental-hdr" in features:
                mutter_hdr = True

        self._cached_hdr = edid_has_hdr or (is_wayland and mutter_hdr)
        return self._cached_hdr

    supports_hdr = has_hdr

    def is_hdr_enabled(self) -> bool:
        if self._has_schema("org.gnome.mutter"):
            features = self._run(["gsettings", "get", "org.gnome.mutter", "experimental-features"])
            if "experimental-hdr" in features:
                return True
        state_file = os.path.expanduser("~/.config/tahoe_hdr_enabled")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    return f.read().strip() == "1"
            except Exception:
                pass
        return False

    def set_hdr_enabled(self, enabled: bool):
        if self._has_schema("org.gnome.mutter"):
            features_str = self._run(["gsettings", "get", "org.gnome.mutter", "experimental-features"])
            try:
                import ast
                features = ast.literal_eval(features_str)
            except Exception:
                features = []
                
            if enabled and "experimental-hdr" not in features:
                features.append("experimental-hdr")
            elif not enabled and "experimental-hdr" in features:
                features.remove("experimental-hdr")
                
            val = str(features).replace('"', "'")
            self._run(["gsettings", "set", "org.gnome.mutter", "experimental-features", val])
        
        # Apply HDR to displays natively if Wayland helper exists
        if os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
            hdr_helper = os.path.join(os.path.dirname(__file__), "wayland_hdr.py")
            if os.path.exists(hdr_helper):
                self._run(["/usr/bin/python3", hdr_helper, "1" if enabled else "0"])

        try:
            state_file = os.path.expanduser("~/.config/tahoe_hdr_enabled")
            with open(state_file, "w") as f:
                f.write("1" if enabled else "0")
        except Exception:
            pass

    # ==========================
    # Color Profiles & SDR Brightness
    # ==========================
    def get_color_profile(self):
        state_file = os.path.expanduser("~/.config/tahoe_color_profile")
        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                return f.read().strip()
        return "p3"
        
    def set_color_profile(self, profile: str):
        state_file = os.path.expanduser("~/.config/tahoe_color_profile")
        try:
            with open(state_file, "w") as f:
                f.write(profile)
        except Exception:
            pass
            
        profile_map = {
            "srgb": "/usr/share/color/icc/colord/sRGB.icc",
            "p3": "/usr/share/color/icc/colord/AdobeRGB1998.icc",
            "dcip3": "/usr/share/color/icc/colord/ProPhotoRGB.icc"
        }
        
        icc_path = profile_map.get(profile)
        if not icc_path or not os.path.exists(icc_path) or not shutil.which("colormgr"):
            return
            
        try:
            out = subprocess.check_output(["colormgr", "import-profile", icc_path], text=True, stderr=subprocess.DEVNULL, timeout=1.0).strip()
            match = re.search(r"Profile ID:\s+(icc-[a-z0-9]+)", out)
            if not match:
                return
            prof_id = match.group(1)
            
            dev_out = subprocess.check_output(["colormgr", "get-devices-by-kind", "display"], text=True, stderr=subprocess.DEVNULL, timeout=1.0).strip()
            dev_ids = re.findall(r"Device ID:\s+(xrandr[^\n]+)", dev_out)
            
            for dev_id in dev_ids:
                subprocess.run(["colormgr", "device-add-profile", dev_id, prof_id], stderr=subprocess.DEVNULL, timeout=1.0)
                subprocess.run(["colormgr", "device-make-profile-default", dev_id, prof_id], stderr=subprocess.DEVNULL, timeout=1.0)
        except Exception as e:
            print("Color profile error:", e)

    def get_sdr_brightness(self) -> int:
        state_file = os.path.expanduser("~/.config/tahoe_sdr_brightness")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    return int(f.read().strip())
            except Exception:
                pass
        return self.get_brightness()

    def set_sdr_brightness(self, value: int):
        val = max(1, min(100, int(value)))
        try:
            state_file = os.path.expanduser("~/.config/tahoe_sdr_brightness")
            with open(state_file, "w") as f:
                f.write(str(val))
        except Exception:
            pass
        self.set_brightness(val)
        
    def is_oled_care_enabled(self):
        state_file = os.path.expanduser("~/.config/tahoe_oled_care")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    return f.read().strip() == "1"
            except Exception:
                pass
        return True
        
    def set_oled_care_enabled(self, enabled: bool):
        try:
            state_file = os.path.expanduser("~/.config/tahoe_oled_care")
            with open(state_file, "w") as f:
                f.write("1" if enabled else "0")
        except Exception:
            pass
