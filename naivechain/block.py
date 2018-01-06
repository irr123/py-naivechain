import pickle
import base64
import json
from . import base


class EqMixin(object):

    def __eq__(self, other) -> bool:
        return self.serialize() == other.serialize()


class Payload(base.NaiveChainObj, base.ISerializable, EqMixin):

    @classmethod
    def deserialize(cls, data: str) -> 'Payload':
        return cls(pickle.loads(base64.b64decode(data)))

    def serialize(self) -> str:
        return base64.b64encode(pickle.dumps(self.data)).decode('ascii')

    def __init__(self, data) -> None:
        self.data = data

    def __str__(self) -> str:
        return f"{super().__str__()}=`{self.data}`"


class Block(base.LoggedNaiveChain, base.ISerializable, EqMixin):

    @classmethod
    def make_genesis_block(cls, data) -> 'Block':
        return cls(0,
                   cls.generate_hash('-1'),
                   cls.generate_hash(cls.__name__),
                   Payload(data),
                   cls.generate_timestamp()
                   )

    @classmethod
    def deserialize(cls, data: str) -> 'Block':
        _data = json.loads(data)
        if 'payload' in _data:
            _payload = Payload.deserialize(_data.pop('payload'))
        else:
            _payload = Payload(None)

        return cls(payload=_payload, **_data)

    def serialize(self) -> str:
        serialized = json.dumps({
            'index': self.index,
            'prevHash': self.prevHash,
            'ownHash': self.ownHash,
            'payload': self.payload.serialize(),
            'timestamp': self.timestamp,
        })
        self.log(self, 'to', serialized)
        return serialized

    def __init__(self, index: int,
                 prevHash: str,
                 ownHash: str,
                 payload: Payload,
                 timestamp: int) -> None:
        self.index = index
        self.prevHash = prevHash
        self.ownHash = ownHash
        self.payload = payload
        self.timestamp = timestamp
        self.log('Init', self)

    def __str__(self) -> str:
        return f"<№{self.index}, {self.payload}>"

