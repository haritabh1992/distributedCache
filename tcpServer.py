import sys
import socket
import json


MAX_BUFFER_SIZE = 1024



def initRing(myCache, consistentHashingRing):
    # clear all ring related info
    myCache.clear()
    consistentHashingRing.clear()

def createNewRing(totalRingSize, myCache, consistentHashingRing, ownPort):
    initRing(myCache, consistentHashingRing)

    outputJson = {}
    # hash current node
    ownHash = str(hash(ownPort) % totalRingSize)

    # Create nodeHashTable containing only current node against its hash value
    myTempRing = {}
    myTempRing[ownHash] = ownPort
    consistentHashingRing["size"] = totalRingSize
    consistentHashingRing["ring"] = myTempRing
    outputJson["status"] = "Successfully created ring"

    return outputJson

def joinRing(ringMemberPort, ownPort, consistentHashingRing, myCache):
    assert ringMemberPort!=ownPort

    outputJson = {}

    remoteConsistentHashingRing = getConsistentHashingRingFromRemote(ringMemberPort)
    if remoteConsistentHashingRing != consistentHashingRing:
        print("updating local ring")
        initRing(myCache, consistentHashingRing)
        myTempRing = remoteConsistentHashingRing["ring"]
        totalRingSize = remoteConsistentHashingRing["size"]
        ownHash = str(hash(ownPort) % totalRingSize)
        myTempRing[ownHash] = ownPort

        consistentHashingRing["ring"] = myTempRing
        consistentHashingRing["size"] = totalRingSize

        # print(consistentHashingRing["ring"].values())
        broadcastNewConsistentHashingRing(consistentHashingRing, ownPort)

    outputJson["status"] = "Success"
    return outputJson

def broadcastNewConsistentHashingRing(consistentHashingRingToSend, ownPort):
    for port in consistentHashingRingToSend["ring"].values():
        if port != ownPort:
            toSend = {
                "action" : "setRing",
                "newRing" : consistentHashingRingToSend
            }
            getResponseFromServer(toSend,'127.0.0.1', port)







def getValueFromKey(inputJson, consistentHashingRing, ownPort):
    outputJson = {}

    key = inputJson["key"]
    serverNodePort = getServerPortFromKey(key, consistentHashingRing)

    if serverNodePort == ownPort:
        outputJson = localFetch(key, consistentHashingRing["ring"], ownPort)
    else:
        outputJson = remoteFetch(key, serverNodePort)

    return outputJson

def remoteFetch(key, serverNodePort):
    dataToSend = {
        "action" : "get",
        "key" : key
    }

    return getResponseFromServer(dataToSend,'127.0.0.1', serverNodePort)

def localFetch(key, myCache, ownPort):
    outputJson = {}

    cachedValue = myCache.get(key)
    if cachedValue is None:
        outputJson["status"] = "Not Found"
    else:
        outputJson["status"] = "Success"

    outputJson["key"] = key
    outputJson["value"] = cachedValue
    outputJson["serverNodePort"] = ownPort

    return outputJson







def setValueForKey(inputJson, consistentHashingRing, ownPort):
    outputJson = {}

    key = inputJson["key"]
    value = inputJson["value"]

    serverNodePort = getServerPortFromKey(key, consistentHashingRing)

    if serverNodePort == ownPort:
        outputJson = localSet(key, value, consistentHashingRing["ring"], ownPort)
    else:
        outputJson = remoteSet(key, value, serverNodePort)

    return outputJson

def localSet(key, value, myCache, ownPort):
    outputJson = {}
    outputJson["status"] = "Succcess"
    outputJson["key"] = key
    outputJson["value"] = value
    outputJson["serverNodePort"] = ownPort

    myCache[key] = value

    return outputJson

def remoteSet(key, value, serverNodePort):
    dataToSend = {
        "action" : "set",
        "key" : key,
        "value" : value
    }

    return getResponseFromServer(dataToSend, '127.0.0.1', serverNodePort)







def getConsistentHashingRingFromRemote(remotePort):
    toSend = {
        "action" : "getRing"
    }

    remoteRing = getResponseFromServer(toSend, '127.0.0.1', remotePort)
    return remoteRing["ring"]

def getConsistentHashingRing(consistentHashingRing):
    outputJson = {}
    outputJson["status"] = "Success"
    outputJson["ring"] = consistentHashingRing
    return outputJson

def setConsistentHashingRing(consistentHashingRingFromRemote, localConsistentHashingRing):
    outputJson = {}
    outputJson["status"] = "Ignored update"

    if localConsistentHashingRing != consistentHashingRingFromRemote:
        print("setting consistentHashingRing...")
        localConsistentHashingRing.clear()
        localConsistentHashingRing["ring"] = consistentHashingRingFromRemote["ring"]
        localConsistentHashingRing["size"] = consistentHashingRingFromRemote["size"]
        outputJson["status"] = "Successfully updated consistentHashingRing"

    return outputJson

def getServerPortFromKey(key, consistentHashingRing):
    hashOfKey = str(hash(key) % consistentHashingRing["size"])
    allKeys = consistentHashingRing["ring"].keys()
    serverNodeKey = -1
    if hashOfKey > max(allKeys):
        serverNodeKey = min(allKeys)
    else:
        serverNodeKey = min(x for x in allKeys if x > hashOfKey)

    serverNodePort = consistentHashingRing["ring"][serverNodeKey]

    return serverNodePort

def getResponseFromServer(dataToSend, ip, port):
    s = socket.socket()
    s.connect((ip, port))
    msg = s.recv(MAX_BUFFER_SIZE).decode()
    s.send(json.dumps(dataToSend).encode())
    recvdMsg = s.recv(MAX_BUFFER_SIZE).decode()
    s.close()

    return json.loads(recvdMsg)







def processInput(inputJson, myCache, consistentHashingRing, ownPort):
    outputJson = {}

    if inputJson["action"] == "createRing":
        totalRingSize = int(inputJson["totalRingSize"])        
        outputJson = createNewRing(totalRingSize, myCache, consistentHashingRing, ownPort)

    elif inputJson["action"] == "joinRing":
        currentMemberPort = int(inputJson["ringMemberPort"])
        outputJson = joinRing(currentMemberPort, ownPort, consistentHashingRing, myCache)

    elif inputJson["action"] == "getRing":
        outputJson = getConsistentHashingRing(consistentHashingRing)

    elif inputJson["action"] == "setRing":
        outputJson = setConsistentHashingRing(inputJson["newRing"], consistentHashingRing)

    elif inputJson["action"] == "get":
        outputJson = getValueFromKey(inputJson, consistentHashingRing, ownPort)

    elif inputJson["action"] == "set" :
        outputJson = setValueForKey(inputJson, consistentHashingRing, ownPort)

    elif inputJson["action"] == "killServer":
        outputJson["status"] = "killServer"
        return outputJson

    else:
        outputJson["status"] = "Error : input action is not get or set"

    return outputJson


def main():
    # Starting server
    argumentList = sys.argv
    print(argumentList)

    ownPort = int(argumentList[1])

    print("Starting socket at : ", ownPort)
    mysocket = socket.socket()
    mysocket.bind(('', ownPort))
    mysocket.listen(5)

    # Code specific to distributed cache
    myCache = {}
    consistentHashingRing = {}


    while True:
        c, addr = mysocket.accept()
        print("\n~~~\nConnection from ", addr)

        c.send('Hello From server'.encode())

        recvData = c.recv(MAX_BUFFER_SIZE).decode()
        recvdJson = json.loads(recvData)
        print(recvdJson)

        print(consistentHashingRing)
        dataToSend = processInput(recvdJson, myCache, consistentHashingRing, ownPort)
        dataToSendStr = json.dumps(dataToSend)
        c.send(dataToSendStr.encode())

        c.close()
        print("Connection from ", addr, " closed\n~~~")

        # check for killServer
        if dataToSend["status"] == "killServer":
            mysocket.close()
            break



if __name__ == "__main__":
    main()


