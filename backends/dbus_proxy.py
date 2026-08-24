#!/usr/bin/env python3
import dbus
import json
import sys
import socket
import struct

def main():
    try:
        bus = dbus.SystemBus()
        nm_obj = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
        nm_props = dbus.Interface(nm_obj, "org.freedesktop.DBus.Properties")
        nm = dbus.Interface(nm_obj, "org.freedesktop.NetworkManager")
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    command = sys.argv[1] if len(sys.argv) > 1 else ""

    def get_prop(obj_path, interface, prop_name):
        try:
            obj = bus.get_object("org.freedesktop.NetworkManager", obj_path)
            props = dbus.Interface(obj, "org.freedesktop.DBus.Properties")
            return props.Get(interface, prop_name)
        except Exception:
            return None

    if command == "status":
        try:
            conn_state = nm_props.Get("org.freedesktop.NetworkManager", "Connectivity")
            primary_conn = nm_props.Get("org.freedesktop.NetworkManager", "PrimaryConnection")
            active_conns = nm_props.Get("org.freedesktop.NetworkManager", "ActiveConnections")

            vpn_active = False
            for ac_path in active_conns:
                ac_type = get_prop(ac_path, "org.freedesktop.NetworkManager.Connection.Active", "Type")
                if ac_type in ['vpn', 'wireguard', 'tun']:
                    vpn_active = True

            active_connection_id = "None"
            local_ip = "Unavailable"
            
            if primary_conn != "/":
                active_connection_id = str(get_prop(primary_conn, "org.freedesktop.NetworkManager.Connection.Active", "Id") or "None")
                ip4_config = get_prop(primary_conn, "org.freedesktop.NetworkManager.Connection.Active", "Ip4Config")
                if ip4_config and ip4_config != "/":
                    addresses = get_prop(ip4_config, "org.freedesktop.NetworkManager.IP4Config", "AddressData")
                    if addresses and len(addresses) > 0:
                        local_ip = str(addresses[0].get('address', 'Unavailable'))

            print(json.dumps({
                "connectivity": int(conn_state),
                "vpn_active": vpn_active,
                "primary_connection_id": active_connection_id,
                "local_ip": local_ip
            }))
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            
    elif command == "devices":
        try:
            res = []
            devices = nm.GetDevices()
            for dev_path in devices:
                dtype = get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "DeviceType")
                iface = str(get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "Interface"))
                state = int(get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "State") or 0)
                
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
                mac = str(get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "HwAddress") or "Unavailable")
                
                if active:
                    ac_path = get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "ActiveConnection")
                    if ac_path and ac_path != "/":
                        c_id = get_prop(ac_path, "org.freedesktop.NetworkManager.Connection.Active", "Id")
                        if c_id: name = str(c_id)
                        
                        ip4_config = get_prop(ac_path, "org.freedesktop.NetworkManager.Connection.Active", "Ip4Config")
                        if ip4_config and ip4_config != "/":
                            addresses = get_prop(ip4_config, "org.freedesktop.NetworkManager.IP4Config", "AddressData")
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
            print(json.dumps(res))
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            
    elif command == "details":
        target_iface = sys.argv[2] if len(sys.argv) > 2 else ""
        try:
            devices = nm.GetDevices()
            dev_path = None
            for dp in devices:
                iface = str(get_prop(dp, "org.freedesktop.NetworkManager.Device", "Interface"))
                if iface == target_iface:
                    dev_path = dp
                    break
                    
            if not dev_path:
                print(json.dumps({"error": "Device not found"}))
                return
                
            mac = str(get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "HwAddress") or "Unavailable")
            mtu = str(get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "Mtu") or "Unavailable")
            driver = str(get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "Driver") or "Unavailable")
            
            ipv4 = "Unavailable"
            gateway = "Unavailable"
            dns = []
            ipv6 = "Unavailable"
            
            ac_path = get_prop(dev_path, "org.freedesktop.NetworkManager.Device", "ActiveConnection")
            if ac_path and ac_path != "/":
                ip4_config = get_prop(ac_path, "org.freedesktop.NetworkManager.Connection.Active", "Ip4Config")
                if ip4_config and ip4_config != "/":
                    addresses = get_prop(ip4_config, "org.freedesktop.NetworkManager.IP4Config", "AddressData")
                    if addresses and len(addresses) > 0:
                        ipv4 = str(addresses[0].get('address', 'Unavailable'))
                    gateway = str(get_prop(ip4_config, "org.freedesktop.NetworkManager.IP4Config", "Gateway") or "Unavailable")
                    nameservers = get_prop(ip4_config, "org.freedesktop.NetworkManager.IP4Config", "NameserverData")
                    if nameservers:
                        for ns in nameservers:
                            dns.append(str(ns.get('address', '')))
                            
                ip6_config = get_prop(ac_path, "org.freedesktop.NetworkManager.Connection.Active", "Ip6Config")
                if ip6_config and ip6_config != "/":
                    addresses = get_prop(ip6_config, "org.freedesktop.NetworkManager.IP6Config", "AddressData")
                    if addresses and len(addresses) > 0:
                        ipv6 = str(addresses[0].get('address', 'Unavailable'))
                        
            print(json.dumps({
                "mac": mac,
                "mtu": mtu,
                "driver": driver,
                "ipv4": ipv4,
                "gateway": gateway,
                "dns": dns,
                "ipv6": ipv6
            }))
        except Exception as e:
            print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
