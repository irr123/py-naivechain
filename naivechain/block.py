import pickle
import base64
import datetime
import json
from . import base


class Payload(base.Root):
    
    @classmethod
    def deserialize(cls, data: str) -> 'Payload':
        return cls(pickle.loads(base64.b64decode(data)))

    def serialize(self) -> str:
        return base64.b64encode(pickle.dumps(self.data)).decode('ascii')

    def __init__(self, data) -> None:
        self.data = data

    def __str__(self) -> str:
        return f"{super().__str__()}={self.data}"


class Block(base.Root):

    @classmethod
    def make_genesis_block(cls) -> 'Block':
        _hash = cls.generate_hash(None)
        return cls(0,
                   _hash,
                   _hash,
                   Payload(None),
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
        return json.dumps({
            'index': self.index,
            'prevHash': self.prevHash,
            'ownHash': self.ownHash,
            'payload': self.payload.serialize(),
            'timestamp': self.timestamp,
        })

    def __init__(self, index: int, prevHash: str, ownHash: str, payload: Payload, timestamp: int) -> None:
        self.index = index
        self.prevHash = prevHash
        self.ownHash = ownHash
        self.payload = payload
        self.timestamp = timestamp
    

    def __str__(self) -> str:
        return f"{super().__str__()}_{self.index}, {self.payload}"



