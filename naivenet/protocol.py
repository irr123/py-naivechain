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


class NaiveMessages(base.LoggedRoot):
    DEFAULT_PORT = 12345
    DELIMITER = '~'

    BROADCAST = 0
    PING = 1
    GET_CHAIN = 2
    UPDATE_CLIENTS = 3

    def __init__(self, *args, **kwargs):
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
    def send_broadcast(cls, s: socket.socket, port: int):
        s.sendto(cls.encode(cls.BROADCAST), ('255.255.255.255', port))
        cls.log('Send BROADCAST')

    @classmethod
    def send_ping(cls, s: socket.socket, port: int, address: str):
        s.sendto(cls.encode(cls.PING), (address, port))
        cls.log('Send PING to', (address, port))
