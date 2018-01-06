import socket
from ..naivechain import base


class NaiveDisallow(NotImplementedError, base.NaiveChainException):
    pass


class DataExchanger(base.Root):
    @staticmethod
    def serialize(data: str) -> bytes:
        return data.encode('utf-8')

    @staticmethod
    def deserialize(data: bytes) -> str:
        return data.decode('utf-8')


class NaiveMessagesProto(base.LoggedRoot):
    DEFAULT_PORT = 12345
    DELIMITER = '~'

    BROADCAST = 0
    PING = 1
    GET_CHAIN = 2
    UPDATE_CLIENTS = 3

    def __init__(self, *args, **kwargs) -> None:
        raise NaiveDisallow(f"{self} is static")

    @classmethod
    def encode(cls, msg_type: int, data: str = '') -> bytes:
        return DataExchanger.serialize(cls.DELIMITER.join([str(msg_type), data]))

    @classmethod
    def decode(cls, data: bytes) -> tuple:
        try:
            msg_type, payload = DataExchanger.deserialize(data).split(cls.DELIMITER)
        except Exception as e:
            raise NaiveDisallow(e)
        return int(msg_type), payload

    @classmethod
    def send_broadcast(cls, s: socket.socket, port: int, weight: int = 0) -> None:
        cls.log('Send BROADCAST')
        s.sendto(cls.encode(cls.BROADCAST, str(weight)), ('255.255.255.255', port))

    @classmethod
    def send_ping(cls, s: socket.socket, port: int, address: str, weight: int = 0) -> None:
        cls.log('Send PING to', (address, port))
        s.sendto(cls.encode(cls.PING, str(weight)), (address, port))

    @classmethod
    def send_get_chain(cls, s: socket.socket, port: int, address: str, block_index: int) -> None:
        cls.log(f'Send GET_CHAIN to {(address, port)}, index={block_index}')
        s.sendto(cls.encode(cls.GET_CHAIN, str(block_index)), (address, port))

    @classmethod
    def send_update_clients(cls, s: socket.socket, port: int, address: str, serialized_block: str) -> None:
        cls.log(f'Send UPDATE_CLIENTS to {(address, port)}, serialized_block={serialized_block}')
        s.sendto(cls.encode(cls.UPDATE_CLIENTS, serialized_block), (address, port))

