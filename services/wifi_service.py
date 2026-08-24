from backends.wifi_backend import WiFiBackend
from models.network_details import NetworkDetailsModel

class WiFiService:
    def __init__(self):
        self.backend = WiFiBackend()

    def is_enabled(self) -> bool:
        return self.backend.is_enabled()

    def set_enabled(self, enable: bool) -> bool:
        return self.backend.set_enabled(enable)

    def get_networks(self) -> list:
        raw_networks = self.backend.get_networks()
        
        # Deduplicate by SSID, keep highest signal, preserve active status
        unique_nets = {}
        for net in raw_networks:
            ssid = net['ssid']
            if ssid not in unique_nets:
                unique_nets[ssid] = net
            else:
                if net['active']:
                    unique_nets[ssid]['active'] = True
                if net['signal'] > unique_nets[ssid]['signal']:
                    unique_nets[ssid]['signal'] = net['signal']
                    
        # Sort: Active first, then by signal strength
        sorted_nets = sorted(unique_nets.values(), key=lambda x: (not x['active'], -x['signal']))
        return sorted_nets

    def get_network_details(self, ssid: str) -> NetworkDetailsModel:
        return self.backend.get_network_details(ssid)
