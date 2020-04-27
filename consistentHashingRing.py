import json
import node

import connectionUtils as cutils

class ConsistentHashingRing:

	def __init__(self, totalRingSize):
		self.ring = {}
		self.ringSize = totalRingSize
		# self.port = ownPort
		self.DEBUG = True

	def addNewNode(self, nodeToAdd):
		nodePort = nodeToAdd.getNodePort()
		self.addNewNodePort(nodePort)

	def addNewNodePort(self, nodePort):
		nodePortHash = str(hash(nodePort) % self.ringSize)
		self.ring[nodePortHash] = nodePort

	def getConsistentHashingRing(self):
		outputJson = {}
		outputJson["ring"] = self.ring
		outputJson["ringSize"] = self.ringSize

		return outputJson

	def setConsistentHashingRing(self, remoteChr, remoteChrSize):
		outputJson = {}

		if self.ring == remoteChr and self.ringSize == remoteChrSize :
			outputJson["response"] = "Already part of the ring, skippping..."
			return outputJson

		self.ring = remoteChr
		self.ringSize = remoteChrSize
		outputJson["response"] = "Updated ConsistentHashingRing, bradcasted to all members"
		return outputJson

	def joinRing(self, currentMemberPort):
		# Create a getRing request to fetch the consistent hashing ring at that node
		request = {
			"action" : "getRing"
		}
		recvdMsg = cutils.getResponseFromServer(request, '127.0.0.1', currentMemberPort)
		remoteChr = recvdMsg["ring"]
		remoteChrSize = recvdMsg["ringSize"]

		outputJson = self.setConsistentHashingRing(remoteChr, remoteChrSize)
		outputJson["response"] = "Updated ConsistentHashingRing"
		return outputJson

	def broadcastCurrentRingToAllMembers(self, broadcastingNodePort):
		for port in self.ring.values():
			if port != broadcastingNodePort:
				toSend = {
					"action" : "setRing",
					"ring" : self.ring,
					"ringSize": self.ringSize
				}
				cutils.getResponseFromServer(toSend,'127.0.0.1', port)

	def getServerPortFromKey(self, key):
	    hashOfKey = str(hash(key) % self.ringSize)
	    allKeys = self.ring.keys()
	    serverNodeKey = -1

	    print(hashOfKey, " ", allKeys)
	    print("  ~~  ")
	    # print(type(hashOfKey), " ", type(int(max(allKeys))), " ", type(min(allKeys)))

	    if hashOfKey > max(allKeys):
	        serverNodeKey = min(allKeys)
	    else:
	        serverNodeKey = min(x for x in allKeys if x > hashOfKey)

	    serverNodePort = self.ring[serverNodeKey]

	    return serverNodePort
