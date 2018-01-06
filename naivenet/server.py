import operator
import select
import socket
from collections import namedtuple
from . import protocol, client
from ..naivechain import base
from ..naivechain import blockchain
from ..naivechain import block


class ChainContainer(base.Root):

    def __init__(self):
        self.chain = blockchain.BlockChain()

    def __str__(self) -> str:
        return self.chain.get_data()

    def add_block(self, block: block.Block) -> bool:
        ret = True
        try:
            self.chain.add_block(block)
        except blockchain.InconsictentBlockChainException:
            ret = False
        return ret

    def add(self, data) -> bool:
        block = self.chain.generate_next_block(data)
        return self.add_block(block)

    def get(self, index: int) -> block.Block:
        try:
            return self.chain.blocks[index]
        except IndexError:
            pass

    def get_last_index(self) -> int:
        return len(self.chain.blocks)


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
                                                    f"{msg_type}{protocol.NaiveMessagesProto.DELIMITER}"
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
        self.server.client.send_ping(protocol.NaiveMessagesProto.DEFAULT_PORT,
                                     address, self.root.container.get_last_index())
        if self.root.add_node(address, int(data)):
            self.log(f'Handle broadcast from `{address}` with \'{data}\'')
        else:
            if self._increment_broadcast():
                self.server.client.send_broadcast(protocol.NaiveMessagesProto.DEFAULT_PORT,
                                                  self.root.container.get_last_index())
                self.log('Send broadcast')
            else:
                self.log(f'Listening broadcast...')

    def ping_handler(self, data: str, address: str):
        if self.root.add_node(address, int(data)):
            self.log(f'Handle ping from `{address}` with \'{data}\' (add new node or renew existing one)')
        else:
            self.log(f'Handle ping from `{address}` with \'{data}\' (do nothing)')

        sorted_nodes = sorted(self.root.known_nodes.items(), key=operator.itemgetter(1), reverse=True)
        if self.root.container.get_last_index() < sorted_nodes[0][1]:
            needed_index = self.root.container.get_last_index()
            self.log(f"Neighbour {sorted_nodes[0][0]} has more "
                     f"actual chain, synchronizing (needed_index={needed_index})")
            self.server.client.send_get_chain(protocol.NaiveMessagesProto.DEFAULT_PORT,
                                              sorted_nodes[0][0], needed_index)


class NaiveServerExchangeState(NaiveServerBaseState):

    def get_chain_handler(self, data: str, address: str):
        self.log(f'GET_CHAIN with {data} from {address}')
        self.server.client.send_update_clients(protocol.NaiveMessagesProto.DEFAULT_PORT,
                                               address, self.root.container.get(int(data)))

    def update_clients_handler(self, data: str, address: str):
        self.log(f'UPDATE_CLIENTS with {data} from {address}')
        try:
            new_block = block.Block.deserialize(data)
        except Exception:
            is_added = False
        else:
            is_added = self.root.container.add_block(new_block)

        if not is_added:
            self.log(f'Can\'t add {data}, will try it later')


class NaiveServerGlobalState(NaiveServerBaseState):

    DEFAULT_TYPE = -1
    active_state_constructor = namedtuple('ActiveState', ('msg_type', 'data', 'address'))

    def __init__(self, server: 'NaiveServer', root=None) -> None:
        super().__init__(server, self)
        self.known_nodes = {'127.0.0.1': 0}
        self.container = ChainContainer()
        self._discover = NaiveServerDiscoverState(server, self)
        self._exchange = NaiveServerExchangeState(server, self)
        self._active_state = self.active_state_constructor(0, 0, '')  # listen broadcast

    def add_node(self, address: str, weight: int = 0) -> bool:
        if not address or self.known_nodes.get(address) == weight:
            return False

        self.known_nodes[address] = weight
        return True

    def handle(self, msg_type: int, data: str = None, address: str = None) -> None:
        if msg_type == self.DEFAULT_TYPE:
            super().handle(*self._active_state)
        else:
            super().handle(msg_type, data, address)


class NaiveServer(base.LoggedRoot):

    CHUNK_SIZE = 1024
    TIMEOUT = 2

    def __init__(self, port: int = protocol.NaiveMessagesProto.DEFAULT_PORT) -> None:
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
            msg_type, payload = protocol.NaiveMessagesProto.decode(raw_data)
            self.log(':'.join(str(x) for x in address), 'Received data:', raw_data)
            self.state.handle(int(msg_type), payload, address[0])

    def listen(self) -> None:
        try:
            self._listen()
        except KeyboardInterrupt:
            self.log(f'Known nodes: {self.state.known_nodes}')
            self.log(f'Blockchain:\n{self.state.container}')

