import sys
import socket
import json

MAX_BUFFER_SIZE = 1024

def getResponseFromServer(dataToSend, ip, port):
    s = socket.socket()
    s.connect((ip, port))
    msg = s.recv(MAX_BUFFER_SIZE).decode()
    s.send(json.dumps(dataToSend).encode())
    recvdMsg = s.recv(MAX_BUFFER_SIZE).decode()
    s.close()

    return json.loads(recvdMsg)
