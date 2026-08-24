import subprocess
import os
from models.network_details import NetworkDetailsModel

class WiFiBackend:
    def is_enabled(self) -> bool:
        try:
            res = subprocess.run(['nmcli', 'radio', 'wifi'], capture_output=True, text=True)
            return 'enabled' in res.stdout.strip().lower()
        except Exception:
            return False

    def set_enabled(self, enable: bool) -> bool:
        cmd = 'on' if enable else 'off'
        try:
            subprocess.run(['nmcli', 'radio', 'wifi', cmd], check=True)
            return True
        except Exception:
            return False

    def get_networks(self) -> list:
        try:
            # -t = tabular, -f = fields
            res = subprocess.run(
                ['nmcli', '-t', '-f', 'IN-USE,SIGNAL,SECURITY,SSID', 'dev', 'wifi', 'list'],
                capture_output=True, text=True
            )
            networks = []
            for line in res.stdout.splitlines():
                parts = line.split(':', 3) # Split only on first 3 colons to keep SSID intact
                if len(parts) == 4:
                    in_use, signal, security, ssid = parts
                    ssid = ssid.replace('\\:', ':')
                    if ssid: # Ignore hidden networks
                        networks.append({
                            "ssid": ssid,
                            "signal": int(signal) if signal.isdigit() else 0,
                            "security": security,
                            "active": in_use == '*'
                        })
            return networks
        except Exception:
            return []

    def get_network_details(self, ssid: str) -> NetworkDetailsModel:
        details = NetworkDetailsModel(ssid=ssid, is_active=False)
        
        try:
            # 1. Check if this SSID is currently active and find its interface
            res = subprocess.run(['nmcli', '-t', '-f', 'DEVICE,CONNECTION,TYPE,STATE', 'device'], capture_output=True, text=True)
            iface = None
            for line in res.stdout.splitlines():
                parts = line.split(':')
                if len(parts) >= 4:
                    d_dev, d_conn, d_type, d_state = parts[0], parts[1], parts[2], parts[3]
                    if d_conn == ssid and 'connected' in d_state:
                        iface = d_dev
                        break
            
            if not iface:
                return details
                
            details.is_active = True
            details.interface = iface
            
            # 2. Get device details via nmcli
            dev_res = subprocess.run(['nmcli', '-t', 'device', 'show', iface], capture_output=True, text=True)
            for line in dev_res.stdout.splitlines():
                if ':' not in line: continue
                key, val = line.split(':', 1)
                if key.startswith('IP4.ADDRESS'):
                    details.ipv4 = val
                elif key.startswith('IP4.GATEWAY') and val:
                    details.gateway = val
                elif key.startswith('IP4.DNS'):
                    if val and val not in details.dns:
                        details.dns.append(val)
                elif key.startswith('IP6.ADDRESS'):
                    if details.ipv6 == "Unavailable":
                        details.ipv6 = val
                elif key == 'GENERAL.HWADDR':
                    details.mac_address = val
                elif key == 'GENERAL.MTU':
                    details.mtu = val
                    
            # 3. Get Driver
            try:
                # read symlink /sys/class/net/<iface>/device/driver
                driver_path = os.readlink(f'/sys/class/net/{iface}/device/driver')
                details.driver = os.path.basename(driver_path)
            except Exception:
                pass
                
            # 4. Get Link Speed (iw or sysfs)
            try:
                # Try iw first for wifi
                iw_res = subprocess.run(['iw', 'dev', iface, 'link'], capture_output=True, text=True)
                for line in iw_res.stdout.splitlines():
                    if 'tx bitrate:' in line:
                        details.link_speed = line.split('tx bitrate:')[1].strip()
                        break
                
                # Fallback to sysfs speed (usually wired, but good fallback)
                if details.link_speed == "Unavailable":
                    with open(f'/sys/class/net/{iface}/speed', 'r') as f:
                        speed = f.read().strip()
                        if speed.isdigit() and speed != "-1":
                            details.link_speed = f"{speed} Mbit/s"
            except Exception:
                pass
                
        except Exception:
            pass
            
        return details
