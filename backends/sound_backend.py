import subprocess
import json

class SoundBackend:
    def __init__(self):
        pass
        
    def get_output_devices(self):
        """Returns a dict of {name: description} for output devices."""
        devices = {}
        try:
            # First line of pactl might have some locale warnings, so we parse carefully.
            # Using LC_ALL=C helps ensure pactl outputs ascii json or standard formats.
            env = dict(subprocess.os.environ, LC_ALL="C")
            result = subprocess.run(["pactl", "-f", "json", "list", "sinks"], capture_output=True, text=True, env=env)
            if result.returncode == 0:
                # Filter out any non-JSON prefix lines (like "Invalid non-ASCII character...")
                out = result.stdout
                json_start = out.find('[')
                if json_start != -1:
                    out = out[json_start:]
                data = json.loads(out)
                for sink in data:
                    name = sink.get("name")
                    desc = sink.get("description")
                    if desc == "(null)":
                        desc = sink.get("properties", {}).get("alsa.card_name", name)
                    if name and desc:
                        icon_name = "audio-card-symbolic"
                        props = sink.get("properties", {})
                        bus = props.get("device.bus", "")
                        active_port = sink.get("active_port", "")
                        port_type = ""
                        for p in sink.get("ports", []):
                            if p.get("name") == active_port:
                                port_type = p.get("type", "")
                                break
                        
                        if "bluetooth" in bus.lower():
                            icon_name = "audio-headphones-symbolic"
                        elif "hdmi" in port_type.lower() or "hdmi" in active_port.lower():
                            icon_name = "video-display-symbolic"
                        elif "headphones" in port_type.lower() or "headphones" in active_port.lower():
                            icon_name = "audio-headphones-symbolic"
                        elif "usb" in bus.lower():
                            icon_name = "audio-speakers-symbolic"
                        else:
                            icon_name = "audio-speakers-symbolic"
                        state = sink.get("state", "UNKNOWN")
                        muted = sink.get("mute", False)
                        devices[name] = {"label": desc, "icon": icon_name, "state": state, "muted": muted}
        except Exception as e:
            print(f"Error getting output devices: {e}")
            
        if not devices:
            devices["dummy"] = {"label": "Dummy Output", "icon": "audio-speakers-symbolic"}
        return devices
        
    def get_active_output_device(self):
        try:
            result = subprocess.run(["pactl", "get-default-sink"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "dummy"
        
    def set_active_output_device(self, name):
        try:
            subprocess.run(["pactl", "set-default-sink", name])
        except Exception as e:
            print(f"Error setting output device: {e}")

    def get_active_device_info(self):
        """Returns a dict with detailed info about the active output device."""
        try:
            env = dict(subprocess.os.environ, LC_ALL="C")
            result = subprocess.run(["pactl", "-f", "json", "list", "sinks"], capture_output=True, text=True, env=env)
            if result.returncode == 0:
                out = result.stdout
                json_start = out.find('[')
                if json_start != -1:
                    out = out[json_start:]
                data = json.loads(out)
                
                res2 = subprocess.run(["pactl", "get-default-sink"], capture_output=True, text=True)
                default_name = res2.stdout.strip()
                
                for sink in data:
                    if sink.get("name") == default_name:
                        info = {}
                        desc = sink.get("description")
                        if desc == "(null)":
                            desc = sink.get("properties", {}).get("alsa.card_name", default_name)
                        info["Name"] = desc
                        
                        props = sink.get("properties", {})
                        bus = props.get("device.bus", "Unknown")
                        active_port_name = sink.get("active_port", "")
                        ports = sink.get("ports", [])
                        port_type = ""
                        for p in ports:
                            if p.get("name") == active_port_name:
                                port_type = p.get("type", "")
                                break
                                
                        if "bluetooth" in bus.lower():
                            conn_type = "Bluetooth"
                        elif "usb" in bus.lower():
                            conn_type = "USB"
                        elif "hdmi" in port_type.lower() or "hdmi" in active_port_name.lower():
                            conn_type = "HDMI / DisplayPort"
                        elif "analog" in active_port_name.lower() or "analog" in port_type.lower() or "line" in port_type.lower() or "headphones" in port_type.lower():
                            conn_type = "Analog"
                        else:
                            conn_type = bus.upper() if bus != "Unknown" else "Virtual / Built-in"
                            
                        info["Connection"] = conn_type
                        
                        spec = sink.get("sample_specification", "")
                        parts = spec.split()
                        if len(parts) >= 3:
                            info["Channels"] = parts[1]
                            info["Sample Rate"] = parts[2]
                        else:
                            info["Channels"] = props.get("audio.channels", "Unknown")
                            info["Sample Rate"] = "Unknown"
                            
                        info["State"] = sink.get("state", "Unknown")
                        return info
        except Exception:
            pass
        return None

    def get_output_volume(self):
        try:
            res = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], capture_output=True, text=True)
            if res.returncode == 0:
                parts = res.stdout.strip().split()
                if len(parts) >= 2:
                    return int(float(parts[1]) * 100)
        except Exception:
            pass
        return 50
        
    def set_output_volume(self, value):
        try:
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{value}%"])
        except Exception:
            pass
            
    def get_output_balance(self):
        try:
            env = dict(subprocess.os.environ, LC_ALL="C")
            result = subprocess.run(["pactl", "-f", "json", "list", "sinks"], capture_output=True, text=True, env=env)
            if result.returncode == 0:
                out = result.stdout
                json_start = out.find('[')
                if json_start != -1:
                    out = out[json_start:]
                data = json.loads(out)
                res2 = subprocess.run(["pactl", "get-default-sink"], capture_output=True, text=True)
                default_name = res2.stdout.strip()
                for sink in data:
                    if sink.get("name") == default_name:
                        cmap = sink.get("channel_map", "")
                        if "front-left" in cmap and "front-right" in cmap:
                            vols = sink.get("volume", {})
                            fl = vols.get("front-left", {}).get("value_percent", "100%")
                            fr = vols.get("front-right", {}).get("value_percent", "100%")
                            fl = int(fl.replace("%", ""))
                            fr = int(fr.replace("%", ""))
                            if fl == 0 and fr == 0:
                                return 0.5
                            if fl == fr:
                                return 0.5
                            if fl > fr:
                                return 0.5 * (fr / fl)
                            else:
                                return 1.0 - 0.5 * (fl / fr)
        except Exception:
            pass
        return None

    def set_output_balance(self, bal):
        try:
            vol = self.get_output_volume()
            if bal <= 0.5:
                fl = vol
                fr = int(vol * (bal / 0.5))
            else:
                fr = vol
                fl = int(vol * ((1.0 - bal) / 0.5))
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{fl}%", f"{fr}%"])
        except Exception:
            pass

    def test_speakers(self):
        import threading
        def play():
            subprocess.run(["pw-play", "/usr/share/sounds/freedesktop/stereo/audio-channel-front-left.oga"])
            subprocess.run(["pw-play", "/usr/share/sounds/freedesktop/stereo/audio-channel-front-right.oga"])
        threading.Thread(target=play, daemon=True).start()
        
    def get_input_devices(self):
        """Returns a dict of {name: description} for input devices (sources)."""
        devices = {}
        try:
            env = dict(subprocess.os.environ, LC_ALL="C")
            result = subprocess.run(["pactl", "-f", "json", "list", "sources"], capture_output=True, text=True, env=env)
            if result.returncode == 0:
                out = result.stdout
                json_start = out.find('[')
                if json_start != -1:
                    out = out[json_start:]
                data = json.loads(out)
                for source in data:
                    # Ignore monitor sources (they are loopbacks for outputs)
                    name = source.get("name", "")
                    if name.endswith(".monitor"):
                        continue
                    desc = source.get("description")
                    if desc == "(null)":
                        desc = source.get("properties", {}).get("alsa.card_name", name)
                    if name and desc:
                        icon_name = "audio-input-microphone-symbolic"
                        props = source.get("properties", {})
                        bus = props.get("device.bus", "")
                        if "bluetooth" in bus.lower():
                            icon_name = "audio-headset-symbolic"
                        state = source.get("state", "UNKNOWN")
                        muted = source.get("mute", False)
                        devices[name] = {"label": desc, "icon": icon_name, "state": state, "muted": muted}
        except Exception as e:
            print(f"Error getting input devices: {e}")
            
        if not devices:
            devices["dummy"] = {"label": "Dummy Input", "icon": "audio-input-microphone-symbolic"}
        return devices
        
    def get_active_input_device(self):
        try:
            result = subprocess.run(["pactl", "get-default-source"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "dummy"
        
    def set_active_input_device(self, name):
        try:
            subprocess.run(["pactl", "set-default-source", name])
        except Exception as e:
            print(f"Error setting input device: {e}")

    def get_input_volume(self):
        try:
            res = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"], capture_output=True, text=True)
            if res.returncode == 0:
                parts = res.stdout.strip().split()
                if len(parts) >= 2:
                    return int(float(parts[1]) * 100)
        except Exception:
            pass
        return 50
        
    def set_input_volume(self, value):
        try:
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SOURCE@", f"{value}%"])
        except Exception:
            pass
            
    def get_system_sounds_enabled(self):
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.desktop.sound", "event-sounds"], capture_output=True, text=True)
            if res.returncode == 0:
                return res.stdout.strip() == "true"
        except Exception:
            pass
        return True

    def set_system_sounds_enabled(self, enabled):
        try:
            val = "true" if enabled else "false"
            subprocess.run(["gsettings", "set", "org.gnome.desktop.sound", "event-sounds", val])
        except Exception:
            pass
