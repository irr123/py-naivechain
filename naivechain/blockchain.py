from . import base
from . import block


class InconsictentBlockChainException(base.NaiveChainException):
    pass


AssertionError = InconsictentBlockChainException


@base.Singleton
class BlockChain(base.LoggedNaiveChain):

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
            if self.latest_block.index + 1 != block.index:
                raise InconsictentBlockChainException(
                    f"New block index is unacceptable! "
                    f"(last={self.latest_block.index}, new={block.index})"
                )
            if self.latest_block.ownHash != block.prevHash:
                raise InconsictentBlockChainException(
                    f"New block hash is incorrect! "
                    f"(last={self.latest_block.ownHash}, new={block.prevHash})"
                )
            if self.latest_block.timestamp > block.timestamp:
                raise InconsictentBlockChainException(
                    f"Creation timestamp of new block early than existing"
                    f"last={self.latest_block.timestamp}, new={block.timestamp}"
                )
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
            self.generate_hash(str(self.generate_timestamp())),
            block.Payload(data),
            self.generate_timestamp()
        )
