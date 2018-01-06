#!/usr/bin/env python

import sys
import multiprocessing
from . import naivechain
from . import naivenet

PAYLOAD = ['Dushiyat', 'Naamu', 'Irois', 'Moufo', 'Zhuoyuo']


def chain_factory():
    blockchain = naivechain.BlockChain()

    for block in PAYLOAD:
        blockchain.add_block(blockchain.generate_next_block(block))

    return blockchain


BLOCKCHAIN = chain_factory()
SUBPROCESS = False


def test_chain():
    raw_chain = BLOCKCHAIN.serialize()
    new_chain = naivechain.BlockChain.deserialize(raw_chain)

    assert id(BLOCKCHAIN) == id(new_chain) and id(new_chain) == id(naivechain.BlockChain())
    for node1, node2 in zip(BLOCKCHAIN.blocks, new_chain.blocks):
        assert node1 == node2
    print(f'\nData, which is in chain:\n{BLOCKCHAIN.get_data()}')


def test_net_server():
    server = naivenet.NaiveServer()
    if SUBPROCESS:
        multiprocessing.Process(target=server.listen).start()
    else:
        server.listen()


def test_net_client():
    client = naivenet.NaiveClient()

    for counter in range(5):
        client.send_broadcast()

    for counter in range(5):
        client.send_ping()

    for new_payload in map(lambda x: f'new_{x}', PAYLOAD):
        new_block = BLOCKCHAIN.generate_next_block(new_payload)
        client.send_update_clients(12345, '127.0.0.1', new_block)

    for num, _ in enumerate(BLOCKCHAIN.blocks):
        client.send_get_chain(12345, '127.0.0.1', num)


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

