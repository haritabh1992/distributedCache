import sys
import socket
import json

### Constants
DEBUG = 0
MAX_BUFFER_SIZE = 1024


def createDataToSend(inputArgList):
    assert (len(inputArgList))%2 == 0
    output = {}
    for i in range(2,len(inputArgList),2):
        output[inputArgList[i]] = inputArgList[i+1]

    return output

def getResponseFromServer(dataToSend, ip, port):
    s = socket.socket()
    s.connect((ip, port))
    msg = s.recv(MAX_BUFFER_SIZE).decode()
    s.send(json.dumps(dataToSend).encode())
    recvdMsg = s.recv(MAX_BUFFER_SIZE).decode()
    s.close()

    return json.loads(recvdMsg)

def main():
    argumentList = sys.argv
    serverPort = int(argumentList[1])
    dataToSend = createDataToSend(argumentList)
    outputData = getResponseFromServer(dataToSend, '127.0.0.1', serverPort)
    print(outputData)

if __name__ == "__main__":
    main()