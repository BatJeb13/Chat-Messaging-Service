import socket # obvs used for the sockets
import sys # used to get info from command line
import select # used to manage multiple clients
import os # Used to get the files and folders
import pickle # Used to send the files to client 

headerSize = 10
port = int(sys.argv[1])

clients = {}
sockets = []
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('127.0.0.1', port))
serverSocket.listen(5)
SERVER_SHARED_FILES = os.getenv("SERVER_SHARED_FILES", "SharedFiles") # Gets the path to the files
files = os.listdir(SERVER_SHARED_FILES) # Gets the files in the location

# For sending messages to clients 
def sendMessage(sender, reciever, message):
    # Global broadcast
    if reciever == 'all':
        for clientSocket in sockets:
           if clientSocket != sender:
               clientSocket.send(f"{len(message):<{headerSize}}{message}".encode("utf-8"))
    # Unicast
    else:
        for clientSocket in sockets:
            if clients[clientSocket] == reciever:
                clientSocket.send(f"{len(message):<{headerSize}}{message}".encode("utf-8"))

# For sending files to clients
def sendFile(reciever, fileName, type):
    if type == "send":
        filePath = SERVER_SHARED_FILES+'/'+fileName
        if not os.path.exists(filePath):
            message = f"To {clients[reciever]} from server file not found"
            print(message) # for server log
            reciever.send(f"{len(message):<{headerSize}}{message}".encode("utf-8"))
        else:
            with open(filePath, 'rb') as file:
                fileData = file.read()
            # Need to send over both file name and the data within the file
            fileDataAndName = {
                'fileName': fileName,
                'fileData': fileData
            }
            print(f"sent file {fileName} to {clients[reciever]}")# For server log
            message = pickle.dumps(fileDataAndName) # Pickling the data makes it possible to send over the network
            message = b" file " + message # This is used for the client side to check if it is a file or a message
            message = bytes(f"{len(message):<{headerSize}}", "utf-8") + message
            reciever.send(message)
    else:
        message = f"{fileName} has size of {os.path.getsize(filePath)} bytes"
        print(message) # For server log
        sendMessage("Server", clients[notifiedSocket], message)


while True:
    # Using select to manage multiple clients
    readSockets, _, _ = select.select([serverSocket] + sockets, [], [])

    for notifiedSocket in readSockets:
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
            message = f"Welcome to the server {username}"
            print(message) # For server log
            sendMessage('Server', username , message)
            message = f'{username} has joined the server'
            sendMessage(clientSocket, 'all', message)
        else:
            try:
                messageHeader = notifiedSocket.recv(headerSize)
                if not len(messageHeader):
                    print(f"Client {clients[notifiedSocket]} disconnected.")
                    sockets.remove(notifiedSocket)
                    del clients[notifiedSocket]
                    continue
                messageLength = int(messageHeader.decode("utf-8"))
                message = notifiedSocket.recv(messageLength).decode("utf-8")

                # Commands
                if message.split()[0][0] == "@":
                    # Files
                    if message.split()[0][1:] == "files":
                        message = f"From server to {clients[notifiedSocket]} You have accessed the SharedFile Folder there is {len(files)} avaliable they are:\n"
                        for file in files:
                            filePath = SERVER_SHARED_FILES +'/'+ file
                            message += f"{file} With size: {os.path.getsize(filePath)} Bytes\n" # Gets the size of file in bytes
                        print(message) # For server log
                        sendMessage("Server", clients[notifiedSocket], message)
                    # UniCast
                    else:
                        reciever = message.split()[0][1:]
                        message = " ".join(message.split()[1:])
                        message = f"From {clients[notifiedSocket]} to {reciever} "+message
                        sendMessage(notifiedSocket, reciever, message)

                elif message.split()[0][0] == "/":
                    # For when client leaves normally 
                    if message.split()[0][1:] == "exit":
                        message = f"{clients[notifiedSocket]} has left"
                        print(message)
                        sendMessage(notifiedSocket, "all", message)
                        sockets.remove(notifiedSocket)
                        del clients[notifiedSocket]
                    # For downloading files
                    elif message.split()[0][1:] == "download":
                        file = " ".join(message.split()[1:])
                        sendFile(notifiedSocket, file, "send")

                    elif message.split()[0][1:] == "size":
                        file = " ".join(message.split()[1:])
                        sendFile(notifiedSocket, file, "size")                       

                # To everyone
                else:
                    sendMessage(notifiedSocket, "all", message)
            
            except Exception as e:
                print(f"Error: {e}")
                message = f"{clients[notifiedSocket]} has left"
                print(message)
                sendMessage(notifiedSocket, "all", message)
                sockets.remove(notifiedSocket)
                del clients[notifiedSocket]