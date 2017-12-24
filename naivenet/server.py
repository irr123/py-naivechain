import select
import socket
from . import protocol, client
from ..naivechain import base


class NaiveServer(base.LoggedNaiveChain):

    CHUNK_SIZE = 1024
    TIMEOUT = 2
    handlers = [
        'broadcast_handler',
        'ping_handler',
        'get_chain_handler',
        'update_clients_handler',
    ]

    @classmethod
    def select_msg_handler(cls, instance: 'NaiveServer', msg_type: int) -> callable:
        if msg_type < len(cls.handlers):
            handler = hasattr(instance, cls.handlers[msg_type])
            if handler:
                return getattr(instance, cls.handlers[msg_type])
        return lambda data: instance.log('Handler not found for', msg_type, protocol.NaiveMessages.DELIMITER, data)

    def __init__(self, port: int = protocol.NaiveMessages.DEFAULT_PORT) -> None:
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(0)
        self.socket.bind(('0.0.0.0', self.port))
        self.is_working = True
        self.known_clients = []
        self.client = client.NaiveClient()
        self.log('Bind', self.socket)

    def disable(self):
        self.is_working = False

    def add_address(self, address: str) -> bool:
        if address not in self.known_clients:
            self.known_clients.append(address)
            return True
        return False

    def listen(self) -> None:
        counter = 0
        while self.is_working:
            if counter % 10:
                self.client.send_broadcast(protocol.NaiveMessages.DEFAULT_PORT)
                if self.port != protocol.NaiveMessages.DEFAULT_PORT:
                    self.client.send_broadcast(self.port)

            self.log('Waiting for data')
            ready = select.select((self.socket,), tuple(), tuple(), self.TIMEOUT)
            if ready[0]:
                raw_data, address = self.socket.recvfrom(self.CHUNK_SIZE)
                msg_type, payload = protocol.NaiveMessages.decode(raw_data)
                self.log(':'.join(str(x) for x in address), 'Received data:', raw_data)

                self.select_msg_handler(self, int(msg_type))(payload, address[0])
            counter += 1

    def broadcast_handler(self, data: str, address: str):
        if self.add_address(address):
            self.client.send_ping(protocol.NaiveMessages.DEFAULT_PORT, address)
        self.log('Handle broadcast from', address, 'with', f'\'{data}\'', '(PING reply)')

    def ping_handler(self, data: str, address: str):
        self.add_address(address)
        self.log('Handle ping from', address, 'with', f'\'{data}\'', '(do nothing)')

    def get_chain_handler(self, data: str, address: str):
        pass

    def update_clients_handler(self, data: str, address: str):
        pass
