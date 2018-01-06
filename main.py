#!/usr/bin/env python

import sys
import random
import multiprocessing
from . import naivechain
from . import naivenet


def test_chain():
    blockchain = naivechain.BlockChain()

    for block in ['Dushiyat', 'Naamu', 'Irois', 'Moufo', 'Zhuoyuo']:
        blockchain.add_block(blockchain.generate_next_block(block))

    raw_chain = blockchain.serialize()
    new_chain = naivechain.BlockChain.deserialize(raw_chain)

    assert id(blockchain) == id(new_chain) and id(new_chain) == id(naivechain.BlockChain())
    for node1, node2 in zip(blockchain.blocks, new_chain.blocks):
        assert node1 == node2
    print(f'\nData, which is in chain:\n{blockchain.get_data()}')


def test_net_server():
    server = naivenet.NaiveServer()
    multiprocessing.Process(target=server.listen).start()


def test_net_client():
    client = naivenet.NaiveClient()
    for counter in range(10):
        client.send_broadcast() if random.random() > 0.5 else client.send_ping()


if __name__ == '__main__':
    naivechain.base.DEBUG = True

    args = ['chain', 'nets', 'netc']

    if len(sys.argv) != 2:
        print("Call with param:", args)
        sys.exit(1)

    {
        'chain': test_chain,
        'nets': test_net_server,
        'netc': test_net_client,
    }.get(sys.argv[1], lambda: print(sys.argv[1], 'not in', args))()

    sys.exit(0)
