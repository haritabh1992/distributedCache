import sys
import node


def main2():
    # Starting server
    argumentList = sys.argv
    print(argumentList)

    ownPort = int(argumentList[1])

    serverNode = node.Node(ownPort)
    serverNode.startServer()


if __name__ == "__main__":
    main2()
