import select
import socket
from collections import namedtuple
from . import protocol, client
from ..naivechain import base


class NaiveServerBaseState(base.LoggedRoot):

    handlers = (
        # 0 - position is msg_type, 1 - prop in global state, 2 - method in specific state
        ('_discover', 'broadcast_handler',),
        ('_discover', 'ping_handler',),
        ('_exchange', 'get_chain_handler',),
        ('_exchange', 'update_clients_handler',),
    )

    @classmethod
    def select_msg_handler(cls, state: 'NaiveServerBaseState', msg_type: int) -> callable:
        if msg_type < len(cls.handlers):
            state_instance = getattr(state.root, cls.handlers[msg_type][0])
            handler = getattr(state_instance, cls.handlers[msg_type][1])
            return handler
        return lambda data, address: state.root.log(f"Handler not found for "
                                                    f"{msg_type}{protocol.NaiveMessages.DELIMITER}"
                                                    f"{data}({address})")

    def __init__(self, server: 'NaiveServer', root: 'NaiveServerGlobalState') -> None:
        self.server = server
        self.root = root

    def handle(self, msg_type: int, data: str, address: str) -> None:
        self.select_msg_handler(self, msg_type)(data, address)


class NaiveServerDiscoverState(NaiveServerBaseState):

    BROADCAST_COUNTER_LIMIT = 10

    def __init__(self, server: 'NaiveServer', root: 'NaiveServerGlobalState') -> None:
        super().__init__(server, root)
        self._broadcast_counter = self.BROADCAST_COUNTER_LIMIT

    def _increment_broadcast(self) -> bool:
        self._broadcast_counter += 1
        if self._broadcast_counter > self.BROADCAST_COUNTER_LIMIT:
            self._broadcast_counter = 0
            return True
        return False

    def broadcast_handler(self, data: str, address: str):
        if self.root.add_address(address):
            self.server.client.send_ping(protocol.NaiveMessages.DEFAULT_PORT, address)
            self.log(f'Handle broadcast from `{address}` with \'{data}\' (PING reply)')
        else:
            if self._increment_broadcast():
                self.server.client.send_broadcast()
                self.log('Sending broadcast')
            else:
                self.log(f'Listening broadcast...')

    def ping_handler(self, data: str, address: str):
        if self.root.add_address(address):
            self.log(f'Handle ping from `{address}` with \'{data}\' (add new node)')
        else:
            self.log(f'Handle ping from `{address}` with \'{data}\' (do nothing)')


class NaiveServerExchangeState(NaiveServerBaseState):

    def get_chain_handler(self, data: str, address: str):
        pass

    def update_clients_handler(self, data: str, address: str):
        pass


class NaiveServerGlobalState(NaiveServerBaseState):

    DEFAULT_TYPE = -1
    active_state_constructor = namedtuple('ActiveState', ['msg_type', 'data', 'address'])

    def __init__(self, server: 'NaiveServer', root=None) -> None:
        super().__init__(server, self)
        self.known_clients = ['127.0.0.1']
        self._discover = NaiveServerDiscoverState(server, self)
        self._exchange = NaiveServerExchangeState(server, self)
        self._active_state = self.active_state_constructor(0, '', '')  # listen broadcast

    def add_address(self, address: str) -> bool:
        if not address or address in self.known_clients:
            return False

        self.known_clients.append(address)
        return True

    def handle(self, msg_type: int, data: str = None, address: str = None) -> None:
        if msg_type == self.DEFAULT_TYPE:
            super().handle(*self._active_state)
        else:
            super().handle(msg_type, data, address)


class NaiveServer(base.LoggedRoot):

    CHUNK_SIZE = 1024
    TIMEOUT = 2

    def __init__(self, port: int = protocol.NaiveMessages.DEFAULT_PORT) -> None:
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(0)
        self.socket.bind(('0.0.0.0', self.port))
        self.is_working = True
        self.state = NaiveServerGlobalState(self)
        self.client = client.NaiveClient()
        self.log('Bind', self.socket)

    def disable(self):
        self.is_working = False

    def _listen(self) -> None:
        while self.is_working:
            self.log('Waiting for data...')
            ready = select.select((self.socket,), tuple(), tuple(), self.TIMEOUT)
            if not ready[0]:
                self.state.handle(NaiveServerGlobalState.DEFAULT_TYPE)
                continue

            raw_data, address = self.socket.recvfrom(self.CHUNK_SIZE)
            msg_type, payload = protocol.NaiveMessages.decode(raw_data)
            self.log(':'.join(str(x) for x in address), 'Received data:', raw_data)
            self.state.handle(int(msg_type), payload, address[0])

    def listen(self) -> None:
        try:
            self._listen()
        except KeyboardInterrupt:
            self.log(f'Known nodes: {self.state.known_clients}\n')

