#!/usr/bin/env python

import naivechain


if __name__ == '__main__':
    blockchain = naivechain.BlockChain()

    block_1 = blockchain.generate_next_block('I\'m first')
    blockchain.add_block(block_1)
    print(block_1)

    raw_1 = block_1.serialize()
    print('serialized', raw_1)

    block_2 = blockchain.generate_next_block('I\'m the second one!')
    blockchain.add_block(block_2)
    print(block_2)

    raw_2 = block_2.serialize()
    print('serialized', raw_2)

    print(blockchain)

    raw_chain = blockchain.serialize()
    print('serialized', raw_chain)

    new_chain = naivechain.BlockChain.deserialize(raw_chain)
    print(new_chain)
    print(new_chain.serialize())

    print(id(blockchain), id(new_chain), id(naivechain.BlockChain()))
