import socket
from . import protocol
from ..naivechain import base


class NaiveClient(base.LoggedNaiveChain):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.log('Bind', self.socket)

    def send_broadcast(self, port: int = protocol.NaiveMessages.DEFAULT_PORT) -> None:
        protocol.NaiveMessages.send_broadcast(self.socket, port)

    def send_ping(self, port: int = protocol.NaiveMessages.DEFAULT_PORT, address: str = '127.0.0.1') -> None:
        protocol.NaiveMessages.send_ping(self.socket, port, address)
