import socket
import sys
import select

headerSize = 10
port = int(sys.argv[1])

clients = {}
sockets = []
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('127.0.0.1', port))
serverSocket.listen(5)

while True:
    # Using select to manage multiple clients
    read_sockets, _, _ = select.select([serverSocket] + sockets, [], [])

    for notifiedSocket in read_sockets:
        if notifiedSocket == serverSocket:
            # New connection
            clientSocket, address = serverSocket.accept()
            print(f"Connection from {address} has been established.")
            
            # Receive username
            username_header = clientSocket.recv(headerSize)
            username_length = int(username_header.decode("utf-8"))
            username = clientSocket.recv(username_length).decode("utf-8")
            
            clients[clientSocket] = username # add client to the dictionary 
            sockets.append(clientSocket)
            
            welcome_msg = "Welcome to the server"
            welcome_msg = f"{len(welcome_msg):<{headerSize}}{welcome_msg}"
            clientSocket.send(bytes(welcome_msg, 'utf-8'))
            print(f"Client '{username}' connected with address {address}.")
        
        else:
            # Receive message
            try:
                message_header = notifiedSocket.recv(headerSize)
                if not len(message_header):
                    # Client disconnected
                    print(f"Client {clients[notifiedSocket]} disconnected.")
                    sockets.remove(notifiedSocket)
                    del clients[notifiedSocket]
                    continue

                message_length = int(message_header.decode("utf-8"))
                message = notifiedSocket.recv(message_length).decode("utf-8")
                
                # Broadcast the message to all other clients
                print(f"Received message from {clients[notifiedSocket]}: {message}")
                for client_socket in sockets:
                    if client_socket != notifiedSocket:
                        client_socket.send(f"{len(message):<{headerSize}}{message}".encode("utf-8"))

            except Exception as e:
                print(f"Error: {e}")
                sockets.remove(notifiedSocket)
                del clients[notifiedSocket]
