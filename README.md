# Distributed Cache

This is a toy example for a distributed `<key,value>` store. It follows the classical `consistent hashing ring` protocol to distribute the entries. The final goal is to have a fully distributed system where there is no master-slave paradigm in play. All nodes are just members of a network and clients can connect to ANY of the nodes in the network to carry out the operations.

Currently supported features on the distributed cache:
1. CREATE RING : Instantiate a new ring on a node 
`python tcpClient.py <port> action createRing totalRingSize <size>`
1. JOIN RING : Make a node part of an existing network 
`python tcpClient.py <port> action joinRing ringMemberPort <port>`
1. GET RING : fetch the snapshot of the network of nodes from any one node 
`python tcpClient.py <port> action getRing`
1. SET : Insert a `<key,value>` pair in the distributed cache. The pair is cached at the correct node as per the caching strategy. The pair is stored at ONLY ONE node currently (no fault tolerance). 
`python tcpClient.py <port> action set key <key> value <value>`
1. GET : Fetch the value against a key from the cache if it is present. 
`python tcpClient.py <port> action get key <key>
`

To Run:
1. From terminal : `python tcpServer.py <any_local_port>`
1. From another terminal: `python tcpClient.py 12345 <[get|set]> <key> <value>`

Sample run commands `Server` run from separate terminals:

```bash
python tcpServer.py 12345
python tcpServer.py 23456
python tcpServer.py 34567
```

Note: Remember to export PYTHONHASHSEED on all terminals
```bash
export PYTHONHASHSEED=0
```

Sample run commands for `Client`:

```bash
python tcpClient.py 12345 action createRing totalRingSize 1000
python tcpClient.py 23456 action joinRing ringMemberPort 12345
python tcpClient.py 34567 action joinRing ringMemberPort 12345

python tcpClient.py 23456 action getRing

python tcpClient.py 23456 action get key abcd
python tcpClient.py 12345 action get key abcd
python tcpClient.py 34567 action get key abcd

python tcpClient.py 23456 action set key abcd value cat
python tcpClient.py 34567 action get key abcd
```