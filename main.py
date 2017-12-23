#!/usr/bin/env python

import naivechain


if __name__ == '__main__':
    block = naivechain.Block.make_genesis_block()
    print(block)

    raw = block.serialize()
    print('serialized', raw)

    new_block = naivechain.Block.deserialize(raw)
    print(new_block)

    new_block.index += 1
    print(new_block)
    blockchain = naivechain.BlockChain()
    blockchain.add_block(block)

    blockchain.add_block(new_block)
    print(blockchain)

    raw_chain = blockchain.serialize()
    new_chain = naivechain.BlockChain.deserialize(raw_chain)
    print(new_chain)
    print(new_chain.blocks[0], ';', new_chain.blocks[1])

    print(id(blockchain), id(new_chain), id(naivechain.BlockChain()))
