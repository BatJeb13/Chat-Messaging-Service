import socket
import select

def start_server():
    headerLen = 10
    serverPort = 8800
    ip = "127.0.0.1"
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((ip, serverPort))
    serverSocket.listen()

    socketsList = [serverSocket]  # All the sockets we know, like the clients that are connected
    clients = {}  # Holds all the info on clients

    def recieve(clientSocket):
        try:
            messageHeader = clientSocket.recv(headerLen)  # Get the length of the message from the client
            if not len(messageHeader):  # If no message was sent
                return False
            messageLen = int(messageHeader.decode("utf-8"))  # Message length as variable
            return {"header": messageHeader, "data": clientSocket.recv(messageLen)}
        except:
            return False  # In case the client closes unexpectedly

    while True:
        readSockets, _, errorSockets = select.select(socketsList, [], socketsList)
        for notifiedSocket in readSockets:
            if notifiedSocket == serverSocket:
                clientSocket, clientAddress = serverSocket.accept()
                user = recieve(clientSocket)
                if user is False:
                    continue
                socketsList.append(clientSocket)
                clients[clientSocket] = user
                print(f"New connection from {clientAddress[0]}:{clientAddress[1]}, username {user['data'].decode('utf-8')}")
            else:
                message = recieve(notifiedSocket)
                if message is False:
                    print(f"Closed connection from {clients[notifiedSocket]['data'].decode('utf-8')}")
                    socketsList.remove(notifiedSocket)
                    del clients[notifiedSocket]
                    continue
                user = clients[notifiedSocket]
                print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
                for clientSocket in clients:
                    if clientSocket != notifiedSocket:
                        clientSocket.send(user['header'] + user['data'] + message['header'] + message['data'])

if __name__ == "__main__":
    start_server()
