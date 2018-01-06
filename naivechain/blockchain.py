from . import base
from . import block


class InconsictentBlockChainException(base.NaiveChainException):
    pass


AssertionError = InconsictentBlockChainException


@base.Singleton
class BlockChain(base.LoggedNaiveChain, base.ISerializable):

    DELIMITER = '@'

    @classmethod
    def deserialize(cls, data: str) -> 'BlockChain':
        _block_chain = BlockChain()
        _block_chain._clear()
        for block_chunk in data.split(cls.DELIMITER):
            _block_chain.add_block(block.Block.deserialize(block_chunk))
        return _block_chain

    def serialize(self) -> str:
        serialized = self.DELIMITER.join([x.serialize() for x in self.blocks])
        self.log(self, 'to', serialized)
        return serialized

    def __str__(self) -> str:
        return f"Contain {len(self.blocks)} items"

    def __init__(self) -> None:
        self.blocks = []
        self.log(self)

    def _clear(self) -> None:
        self.blocks = []

    @property
    def latest_block(self) -> block.Block:
        if self.blocks:
            return self.blocks[-1]

    def add_block(self, block: block.Block) -> None:
        if self.latest_block:
            assert self.latest_block.index < block.index
            assert self.latest_block.timestamp <= block.timestamp
            assert block.ownHash == self.generate_hash(self.latest_block.serialize())
        self.log('add', block)
        self.blocks.append(block)

    def generate_next_block(self, data=None) -> block.Block:
        if not self.latest_block:
            return block.Block.make_genesis_block(data)

        new_index = self.latest_block.index + 1
        assert len(self.blocks) == new_index
        return block.Block(
            new_index,
            self.latest_block.ownHash,
            self.generate_hash(self.latest_block.serialize()),
            block.Payload(data),
            self.generate_timestamp()
        )

    def get_data(self):
        repr_counter = 0

        def reprezenter(block: block.Block):
            nonlocal repr_counter
            repr_counter += 1
            return f"{repr_counter} {block.payload}"

        return '\n'.join(map(reprezenter, self.blocks))
