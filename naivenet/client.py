import socket
from . import protocol
from ..naivechain import base


class NaiveClient(base.LoggedNaiveChain):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.proto = protocol.NaiveMessagesProto
        self.log('Bind', self.socket)

    def send_broadcast(self, port: int = protocol.NaiveMessagesProto.DEFAULT_PORT, weight: int = 0) -> None:
        self.proto.send_broadcast(self.socket, port, weight)

    def send_ping(self, port: int = protocol.NaiveMessagesProto.DEFAULT_PORT,
                  address: str = '127.0.0.1', weight: int = 0) -> None:
        self.proto.send_ping(self.socket, port, address, weight)

    def send_get_chain(self, port: int = protocol.NaiveMessagesProto.DEFAULT_PORT,
                       address: str = '127.0.0.1', block_index: int = 0) -> None:
        self.proto.send_get_chain(self.socket, port, address, block_index)

    def send_update_clients(self, port: int = protocol.NaiveMessagesProto.DEFAULT_PORT,
                            address: str = '127.0.0.1', blockchain: base.ISerializable = None) -> None:
        self.proto.send_update_clients(self.socket, port, address, blockchain.serialize())

