import sys
import socket
import json

import cache as cache
import connectionUtils as cutils
import consistentHashingRing as chs


class Node:
    def __init__(self, myPort):
        self.localCache = cache.Cache()
        self.consistentHashingRing = chs.ConsistentHashingRing(1000)
        self.port = myPort
        self.MAX_BUFFER_SIZE = 1024

    def getNodePort(self):
        return self.port

    def startServer(self):
        print("Starting socket at : ", self.port)
        mysocket = socket.socket()
        mysocket.bind(('', self.port))
        mysocket.listen(5)

        while True:
            c, addr = mysocket.accept()
            print("\n~~~\nConnection from ", addr)

            c.send('Hello From server'.encode())

            recvData = c.recv(self.MAX_BUFFER_SIZE).decode()
            recvdJson = json.loads(recvData)
            print(recvdJson)

            # print(consistentHashingRing)
            dataToSend = self.processInput(recvdJson)
            # dataToSend = localConsistentHashingRing.processInput(recvdJson)
            dataToSendStr = json.dumps(dataToSend)
            c.send(dataToSendStr.encode())

            c.close()
            print("Connection from ", addr, " closed\n~~~")

            # check for killServer
            if dataToSend["status"] == "killServer":
                mysocket.close()
                break

    def processInput(self, inputJson):
        outputJson = {}

        if inputJson["action"] == "createRing":
            totalRingSize = int(inputJson["totalRingSize"])
            outputJson = self.createNewRing(totalRingSize)

        elif inputJson["action"] == "joinRing":
            currentMemberPort = int(inputJson["ringMemberPort"])
            outputJson = self.joinRing(currentMemberPort)

        elif inputJson["action"] == "getRing":
            outputJson = self.getConsistentHashingRing()

        elif inputJson["action"] == "setRing":
            outputJson = self.setConsistentHashingRing(
                inputJson["ring"], inputJson["ringSize"])

        elif inputJson["action"] == "get":
            outputJson = self.getValueFromKey(inputJson["key"])

        elif inputJson["action"] == "set":
            outputJson = self.setValueForKey(
                inputJson["key"], inputJson["value"])

        elif inputJson["action"] == "killServer":
            outputJson["status"] = "killServer"
            return outputJson

        else:
            outputJson["status"] = "Error : input action is not get or set"

        return outputJson

    def createNewRing(self, totalRingSize):
        outputJson = {}
        self.consistentHashingRing = chs.ConsistentHashingRing(totalRingSize)
        self.consistentHashingRing.addNewNode(self)
        outputJson["status"] = "Success"
        return outputJson

    def getConsistentHashingRing(self):
        outputJson = self.consistentHashingRing.getConsistentHashingRing()
        outputJson["status"] = "Success"
        return outputJson

    def joinRing(self, currentMemberPort):
        outputJson = self.consistentHashingRing.joinRing(currentMemberPort)
        self.consistentHashingRing.addNewNode(self)
        self.consistentHashingRing.broadcastCurrentRingToAllMembers(self.port)
        outputJson["status"] = "Success"
        return outputJson

    def setConsistentHashingRing(self, newChr, newChrSize):
        outputJson = self.consistentHashingRing.setConsistentHashingRing(
            newChr, newChrSize)
        outputJson["status"] = "Success"
        return outputJson

    def getValueFromKey(self, key):
        nodeWhereTheKeyResides = self.consistentHashingRing.getServerPortFromKey(
            key)
        outputJson = {}
        if nodeWhereTheKeyResides == self.port:
            outputJson = self.localCache.localFetch(key)
            outputJson["fetchNode"] = self.port
        else:
            outputJson = self.remoteGetValueFromKey(
                key, nodeWhereTheKeyResides)

        return outputJson

    def remoteGetValueFromKey(self, key, nodeWhereTheKeyResides):
        dataToSend = {
            "action": "get",
            "key": key
        }
        return cutils.getResponseFromServer(dataToSend, '127.0.0.1', nodeWhereTheKeyResides)

    def setValueForKey(self, key, value):
        nodeWhereTheKeyResides = self.consistentHashingRing.getServerPortFromKey(
            key)
        outputJson = {}
        if nodeWhereTheKeyResides == self.port:
            outputJson = self.localCache.localSet(key, value)
            outputJson["fetchNode"] = self.port
        else:
            outputJson = self.remotesetValueForKey(
                key, value, nodeWhereTheKeyResides)

        return outputJson

    def remotesetValueForKey(self, key, value, nodeWhereTheKeyResides):
        dataToSend = {
            "action": "set",
            "key": key,
            "value": value
        }
        return cutils.getResponseFromServer(dataToSend, '127.0.0.1', nodeWhereTheKeyResides)


def main():
    myNode = Node(12345)
    print("myNode.getSelfPort() = ", myNode.getSelfPort())


if __name__ == '__main__':
    main()
