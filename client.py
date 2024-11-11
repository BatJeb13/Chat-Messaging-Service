import socket # Used to do the whole socket thing
import sys # Used to get info from terminal 
import threading # Used to allow us to both recieve and send data
import pickle
import os # Used for folder and file stuff


headerSize = 10 # How long messages can be obvs they wont be longer than 1,000,000 but never know XD
userName = sys.argv[1]
ip = sys.argv[2]
port = int(sys.argv[3]) 
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((ip, port))

# Send the username to the server with header, This basically says its first hello to the server as in innits itself to it 
username_msg = f"{len(userName):<{headerSize}}{userName}"
clientSocket.send(username_msg.encode('utf-8'))

def sender():
    while True:
        # Send a message to the server
        msg = input("Enter a message to send: \n")
        msg = f"{len(msg):<{headerSize}}{msg}"
        clientSocket.send(msg.encode('utf-8'))

def receiver():
    while True:
        # Initialize buffer for incoming messages
        fullmsg = b''  # Treat as byte string
        newmsg = True
        fileTransfer = False
        
        while True:
            msg = clientSocket.recv(16)
            if newmsg:
                # Read header to get message length
                msglen = int(msg[:headerSize])
                newmsg = False
                
                # Check if this message is a file transfer
                if msg.split()[1].decode("utf-8") == 'file':
                    print("Transferring a file")
                    fileTransfer = True
            
            # Accumulate received bytes
            fullmsg += msg
            # Check if the full message has been received
            if len(fullmsg) - headerSize == msglen:
                if fileTransfer:
                    # Create the folder only if it doesn't exist
                    if not os.path.isdir(userName):
                        os.makedirs(userName)
                        print("Folder created")
                    print("Full file received")
                    file = pickle.loads(fullmsg[headerSize+6:])
                    filePath = os.path.join(userName, file['fileName'])
                    
                    # Write the file content to the destination folder
                    if os.path.exists(filePath):
                        print('file already exists')
                    else:
                        with open(filePath, 'wb') as f:
                            f.write(file['fileData'])  # Assuming file_data has 'filename' and 'content'
                        print(f"File saved as {filePath}")
                        fileTransfer = False
                    
                else:
                    # Decode and print only if it's a text message
                    print(fullmsg[headerSize:].decode("utf-8"))
                
                # Prepare to receive the next message
                newmsg = True
                fullmsg = b''  # Reset buffer
                break

def start():
    receive_thread = threading.Thread(target=receiver)
    send_thread = threading.Thread(target=sender)
    receive_thread.start()
    send_thread.start()


if __name__ == "__main__":
    start()
