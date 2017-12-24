from . import base
from . import block


class InconsictentBlockChainException(Exception):
    pass


@base.Singleton
class BlockChain(base.Root):

    DELIMITER = '@'

    @classmethod
    def deserialize(cls, data: str) -> 'BlockChain':
        _block_chain = BlockChain()
        _block_chain._clear()
        for block_chunk in data.split(cls.DELIMITER):
            _block_chain.add_block(block.Block.deserialize(block_chunk))
        return _block_chain

    def serialize(self) -> str:
        return self.DELIMITER.join([x.serialize() for x in self.blocks])

    def __str__(self) -> str:
        return f"{super().__str__()}, {len(self.blocks)} items"

    def __init__(self) -> None:
        self.blocks = []

    def _clear(self) -> None:
        self.blocks = []

    def add_block(self, block: block.Block) -> None:
        if self.blocks:
            if len(self.blocks) != block.index:
                raise InconsictentBlockChainException(
                    f"New block index is unacceptable! "
                    f"(last={len(self.blocks)}, new={block.index})"
                )
            if self.blocks[-1].ownHash != block.prevHash:
                raise InconsictentBlockChainException(
                    f"New block hash is incorrect! "
                    f"(last={self.blocks[-1].ownHash}, new={block.prevHash})"
                )
        self.blocks.append(block)

    def generate_next_block(self, data=None) -> block.Block:
        if not self.blocks:
            return block.Block.make_genesis_block(data)

        return block.Block(
            len(self.blocks),
            self.blocks[-1].ownHash,
            self.generate_hash(str(self.generate_timestamp())),
            block.Payload(data),
            self.generate_timestamp()
        )
