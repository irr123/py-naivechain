Naive block-chain implementation on pure python (only 3.6 tested).
Idea similar with js-[naivechain](https://github.com/lhartikk/naivechain) but implementation based on sockets with auto-discovering pirs and synchronizing payload

For playing you can call `run.sh`:
- `chain`-arg shows how blockchain datastructure works
- `nets`-arg execute server which bind on 0.0.0.0:12345 and will listen it port
- `netc`-arg exec test clients requests to local working server instance

Solution uses UDP, so synchronizing works only between PC in one local network.
To check how it works you can exec `run.sh nets` on one PC and do it on another one PC in the same network area with little changes in main.py (remove/comment 14-15 lines, where blockchain filling by data); I suppose it will work with more than two PC, but it is not tested.

