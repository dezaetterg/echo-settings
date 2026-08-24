class NetworkDetailsModel:
    def __init__(self, ssid: str, is_active: bool = False, interface: str = "wlan0"):
        self.ssid = ssid
        self.is_active = is_active
        self.interface = interface
        self.ipv4 = "Unavailable"
        self.ipv6 = "Unavailable"
        self.gateway = "Unavailable"
        self.dns = []
        self.mac_address = "Unavailable"
        self.mtu = "Unavailable"
        self.driver = "Unavailable"
        self.link_speed = "Unavailable"
