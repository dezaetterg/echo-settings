import subprocess
import json
import os
import sys
from models.network_details import NetworkDetailsModel

# Try in-process dbus with connection reuse
try:
    if "/usr/lib/python3/dist-packages" not in sys.path:
        sys.path.append("/usr/lib/python3/dist-packages")
    import dbus
    _has_dbus = True
except Exception:
    _has_dbus = False


class NetworkBackend:
    def __init__(self):
        self.proxy_script = os.path.join(os.path.dirname(__file__), 'dbus_proxy.py')
        self._bus = None
        self._nm_obj = None
        self._nm_props = None
        self._nm = None
        if _has_dbus:
            self._ensure_dbus()

    def _ensure_dbus(self):
        if self._nm is None and _has_dbus:
            try:
                self._bus = dbus.SystemBus()
                self._nm_obj = self._bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
                self._nm_props = dbus.Interface(self._nm_obj, "org.freedesktop.DBus.Properties")
                self._nm = dbus.Interface(self._nm_obj, "org.freedesktop.NetworkManager")
            except Exception:
                self._nm = None

    def _get_prop(self, obj_path, interface, prop_name):
        try:
            if not self._bus:
                return None
            obj = self._bus.get_object("org.freedesktop.NetworkManager", obj_path)
            props = dbus.Interface(obj, "org.freedesktop.DBus.Properties")
            return props.Get(interface, prop_name)
        except Exception:
            return None

    def _run_proxy(self, *args):
        try:
            res = subprocess.run(['/usr/bin/python3', self.proxy_script] + list(args), capture_output=True, text=True)
            if res.stdout:
                return json.loads(res.stdout)
        except Exception as e:
            print("Proxy error:", e)
        return {}

    def get_global_status(self) -> dict:
        status = {
            "internet": "Unknown",
            "vpn_active": False,
            "active_connection": "None",
            "local_ip": "Unavailable"
        }
        
        if _has_dbus and self._nm_props:
            try:
                conn_state = self._nm_props.Get("org.freedesktop.NetworkManager", "Connectivity")
                primary_conn = self._nm_props.Get("org.freedesktop.NetworkManager", "PrimaryConnection")
                active_conns = self._nm_props.Get("org.freedesktop.NetworkManager", "ActiveConnections")

                vpn_active = False
                for ac_path in active_conns:
                    ac_type = self._get_prop(ac_path, "org.freedesktop.NetworkManager.Connection.Active", "Type")
                    if ac_type in ['vpn', 'wireguard', 'tun']:
                        vpn_active = True

                active_connection_id = "None"
                local_ip = "Unavailable"
                
                if primary_conn != "/":
                    active_connection_id = str(self._get_prop(primary_conn, "org.freedesktop.NetworkManager.Connection.Active", "Id") or "None")
                    ip4_config = self._get_prop(primary_conn, "org.freedesktop.NetworkManager.Connection.Active", "Ip4Config")
                    if ip4_config and ip4_config != "/":
                        addresses = self._get_prop(ip4_config, "org.freedesktop.NetworkManager.IP4Config", "AddressData")
                        if addresses and len(addresses) > 0:
                            local_ip = str(addresses[0].get('address', 'Unavailable'))

                states = {0: "Unknown", 1: "None", 2: "Portal", 3: "Limited", 4: "Full"}
                status['internet'] = states.get(int(conn_state), "Unknown")
                status['vpn_active'] = vpn_active
                status['active_connection'] = active_connection_id
                status['local_ip'] = local_ip
                return status
            except Exception:
                pass

        data = self._run_proxy("status")
        if "error" not in data and data:
            states = {0: "Unknown", 1: "None", 2: "Portal", 3: "Limited", 4: "Full"}
            status['internet'] = states.get(data.get("connectivity", 0), "Unknown")
            status['vpn_active'] = data.get("vpn_active", False)
            status['active_connection'] = data.get("primary_connection_id", "None")
            status['local_ip'] = data.get("local_ip", "Unavailable")
            
        return status

    def get_filtered_connections(self) -> list:
        connections = []
        data = None
        if _has_dbus and self._nm:
            try:
                res = []
                devices = self._nm.GetDevices()
                for dev_path in devices:
                    dtype = self._get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "DeviceType")
                    iface = str(self._get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "Interface"))
                    state = int(self._get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "State") or 0)
                    
                    type_name = "unknown"
                    if dtype == 1: type_name = "ethernet"
                    elif dtype == 2: type_name = "wifi"
                    elif dtype == 13: type_name = "tun"
                    elif dtype == 31: type_name = "wireguard"
                    
                    if type_name not in ['ethernet', 'wifi', 'tun', 'wireguard', 'vpn']:
                        continue
                    if iface.startswith(('docker', 'virbr', 'br-', 'veth', 'tap', 'amn')):
                        continue
                        
                    active = (state == 100)
                    name = iface
                    ipv4 = "Unavailable"
                    mac = str(self._get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "HwAddress") or "Unavailable")
                    
                    if active:
                        ac_path = self._get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "ActiveConnection")
                        if ac_path and ac_path != "/":
                            c_id = self._get_prop(ac_path, "org.freedesktop.NetworkManager.Connection.Active", "Id")
                            if c_id: name = str(c_id)
                            
                            ip4_config = self._get_prop(ac_path, "org.freedesktop.NetworkManager.Connection.Active", "Ip4Config")
                            if ip4_config and ip4_config != "/":
                                addresses = self._get_prop(ip4_config, "org.freedesktop.NetworkManager.IP4Config", "AddressData")
                                if addresses and len(addresses) > 0:
                                    ipv4 = str(addresses[0].get('address', 'Unavailable'))
                                    
                    res.append({
                        "interface": iface,
                        "type": type_name,
                        "name": name,
                        "active": active,
                        "state": state,
                        "ipv4": ipv4,
                        "mac": mac
                    })
                data = res
            except Exception:
                data = None

        if data is None:
            data = self._run_proxy("devices")

        if isinstance(data, list):
            for dev in data:
                iface = dev.get("interface")
                link_speed = "Unavailable"
                if dev.get("active"):
                    try:
                        with open(f'/sys/class/net/{iface}/speed', 'r') as f:
                            speed = f.read().strip()
                            if speed.isdigit() and speed != "-1":
                                link_speed = f"{speed} Mbit/s"
                    except Exception:
                        pass
                
                dev["link_speed"] = link_speed
                dev["mac"] = dev.get("mac", "Unavailable")
                connections.append(dev)
                
        return connections

    def get_connection_details(self, interface: str, connection_name: str) -> NetworkDetailsModel:
        details = NetworkDetailsModel(ssid=connection_name, is_active=False, interface=interface)
        data = None
        if _has_dbus and self._nm:
            try:
                devices = self._nm.GetDevices()
                dev_path = None
                for dp in devices:
                    iface = str(self._get_prop(dp, "org.freedesktop.NetworkManager.Device", "Interface"))
                    if iface == interface:
                        dev_path = dp
                        break
                        
                if dev_path:
                    mac = str(self._get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "HwAddress") or "Unavailable")
                    mtu = str(self._get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "Mtu") or "Unavailable")
                    driver = str(self._get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "Driver") or "Unavailable")
                    
                    ipv4 = "Unavailable"
                    gateway = "Unavailable"
                    dns = []
                    ipv6 = "Unavailable"
                    
                    ac_path = self._get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "ActiveConnection")
                    if ac_path and ac_path != "/":
                        ip4_config = self._get_prop(ac_path, "org.freedesktop.NetworkManager.Connection.Active", "Ip4Config")
                        if ip4_config and ip4_config != "/":
                            addresses = self._get_prop(ip4_config, "org.freedesktop.NetworkManager.IP4Config", "AddressData")
                            if addresses and len(addresses) > 0:
                                ipv4 = str(addresses[0].get('address', 'Unavailable'))
                            gateway = str(self._get_prop(ip4_config, "org.freedesktop.NetworkManager.IP4Config", "Gateway") or "Unavailable")
                            nameservers = self._get_prop(ip4_config, "org.freedesktop.NetworkManager.IP4Config", "NameserverData")
                            if nameservers:
                                for ns in nameservers:
                                    dns.append(str(ns.get('address', '')))
                                    
                        ip6_config = self._get_prop(ac_path, "org.freedesktop.NetworkManager.Connection.Active", "Ip6Config")
                        if ip6_config and ip6_config != "/":
                            addresses = self._get_prop(ip6_config, "org.freedesktop.NetworkManager.IP6Config", "AddressData")
                            if addresses and len(addresses) > 0:
                                ipv6 = str(addresses[0].get('address', 'Unavailable'))
                                
                    data = {
                        "mac": mac,
                        "mtu": mtu,
                        "driver": driver,
                        "ipv4": ipv4,
                        "gateway": gateway,
                        "dns": dns,
                        "ipv6": ipv6
                    }
            except Exception:
                data = None

        if data is None:
            data = self._run_proxy("details", interface)

        if "error" not in data and data:
            details.is_active = True
            details.mac_address = data.get("mac", "Unavailable")
            details.mtu = str(data.get("mtu", "Unavailable"))
            details.driver = data.get("driver", "Unavailable")
            details.ipv4 = data.get("ipv4", "Unavailable")
            details.gateway = data.get("gateway", "Unavailable")
            details.dns = data.get("dns", [])
            details.ipv6 = data.get("ipv6", "Unavailable")
            
            try:
                with open(f'/sys/class/net/{interface}/speed', 'r') as f:
                    speed = f.read().strip()
                    if speed.isdigit() and speed != "-1":
                        details.link_speed = f"{speed} Mbit/s"
            except Exception:
                pass
                
        return details

