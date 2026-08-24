from backends.network_backend import NetworkBackend
from models.network_details import NetworkDetailsModel

class NetworkService:
    def __init__(self):
        self.backend = NetworkBackend()

    def get_ethernet_connections(self) -> list:
        conns = self.backend.get_filtered_connections()
        return sorted(conns, key=lambda x: not x['active'])

    def get_connection_details(self, interface: str, connection_name: str) -> NetworkDetailsModel:
        return self.backend.get_connection_details(interface, connection_name)
