import socket
import sys

headerSize = 10
userName = sys.argv[1]
ip = sys.argv[2]
port = int(sys.argv[3]) 
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((ip, port))

# Send the username to the server with header, This basically says its first hello to the server as in innits itself to it 
username_msg = f"{len(userName):<{headerSize}}{userName}"
clientSocket.send(username_msg.encode('utf-8'))

while True:
    # Recieving Messages from server and packing the buffer together
    fullmsg = ''
    newmsg = True
    while True:
        msg = clientSocket.recv(16)
        if newmsg:
            msglen = int(msg[:headerSize])
            newmsg = False

        fullmsg += msg.decode("utf-8")

        if len(fullmsg) - headerSize == msglen:
            print("Full message received")
            print(fullmsg[headerSize:])
            newmsg = True  # Reset for the next message
            break

    # Send a message to the server
    msg = input("Enter a message to send: ")
    msg = f"{len(msg):<{headerSize}}{msg}"
    clientSocket.send(msg.encode('utf-8'))
