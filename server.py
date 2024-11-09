import socket # obvs used for the sockets
import sys # used to get info from command line
import select # used to manage multiple clients
import os # Used to get the files and folders

headerSize = 10
port = int(sys.argv[1])

clients = {}
sockets = []
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('127.0.0.1', port))
serverSocket.listen(5)
serverSharedFilesPath = os.getenv("SERVER_SHARED_FILES", "SharedFiles") # Gets the path to the files
files = os.listdir(serverSharedFilesPath) # Gets the files in the location

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
            
            clients[clientSocket] = [username, 'all'] # add client to the dictionary 
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
                    print(f"Client {clients[notifiedSocket][0]} disconnected.")
                    sockets.remove(notifiedSocket)
                    del clients[notifiedSocket]
                    continue

                message_length = int(message_header.decode("utf-8"))
                message = notifiedSocket.recv(message_length).decode("utf-8")
                
                # Commands
                if message.split()[0][0] == "@":
                    # User Leaving
                    if message.split()[0][1:] == "exit":
                        message = f"{clients[notifiedSocket][0]} has left"
                        print(message)
                        for client_socket in sockets:
                            if client_socket != notifiedSocket: # All but the current person leaving 
                                client_socket.send(f"{len(message):<{headerSize}}{message}".encode("utf-8"))
                        sockets.remove(notifiedSocket)
                        del clients[notifiedSocket]
                    
                    # For when the clients want to acess the server files show the data 
                    elif message.split()[0][1:] == "files":
                        clients[notifiedSocket][1] = "files"

                    # Changing back to messaging everyone
                    elif message.split()[0][1:] == "all":
                        clients[notifiedSocket][1] = "all"
                        message = " ".join(message.split()[1:])
                        message = f"To {clients[notifiedSocket][1]} from {clients[notifiedSocket][0]}: {message}" # Adds the username to the front of message and the current messaging type
                        print(message) # For the server chat log
                        for client_socket in sockets:
                            if client_socket != notifiedSocket and (clients[notifiedSocket][1] == "all" or clients[client_socket][0]==clients[notifiedSocket][1]): # All or either the current private message
                                client_socket.send(f"{len(message):<{headerSize}}{message}".encode("utf-8"))
                    
                    # Unicast: The only other command would be messaging a username with unicast.        
                    else:
                        unicast_username = message.split()[0][1:]
                        clients[notifiedSocket][1] = unicast_username
                        message = " ".join(message.split()[1:])
                        message = f"To {clients[notifiedSocket][1]} from {clients[notifiedSocket][0]}: {message}" # Adds the username to the front of message
                        print(message) # For the server chat log
                        for client_socket in sockets:
                            if (client_socket != notifiedSocket) and (clients[client_socket][0] == unicast_username):
                                client_socket.send(f"{len(message):<{headerSize}}{message}".encode("utf-8")) 
                else:
                    # For broadcasting messages 
                    if clients[notifiedSocket][1] != "files":
                        message = f"To {clients[notifiedSocket][1]}from{clients[notifiedSocket][0]}: {message}" # Adds the username to the front of message and the current messaging type
                        print(message) # For the server chat log
                        for client_socket in sockets:
                            if client_socket != notifiedSocket and (clients[notifiedSocket][1] == "all" or clients[client_socket][0]==clients[notifiedSocket][1]): # All or either the current private message
                                client_socket.send(f"{len(message):<{headerSize}}{message}".encode("utf-8"))
                    # For when the client is interacting with the files
                    else:
                        pass
               
            # All errors but mostly used for when the client forces the terminal to shut down instead of disconecting 
            except Exception as e:
                print(f"Error: {e}")
                message = f"{clients[notifiedSocket][0]} has left"
                for client_socket in sockets:
                    if client_socket != notifiedSocket: # All but the current person leaving 
                        client_socket.send(f"{len(message):<{headerSize}}{message}".encode("utf-8"))
                sockets.remove(notifiedSocket)
                del clients[notifiedSocket]
