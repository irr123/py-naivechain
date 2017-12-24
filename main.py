#!/usr/bin/env python

import naivechain


if __name__ == '__main__':
    naivechain.base.DEBUG = True

    blockchain = naivechain.BlockChain()

    block_1 = blockchain.generate_next_block('I\'m first')
    blockchain.add_block(block_1)

    block_2 = blockchain.generate_next_block('I\'m the second one!')
    blockchain.add_block(block_2)

    raw_chain = blockchain.serialize()
    new_chain = naivechain.BlockChain.deserialize(raw_chain)

    assert id(blockchain) == id(new_chain) and id(new_chain) == id(naivechain.BlockChain())
