import socket # Used to do the whole socket thing
import sys # Used to get info from terminal 
import threading # Used to allow us to both recieve and send data


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
        # Receiving Messages from server and packing the buffer together
        fullmsg = ''
        newmsg = True
        while True:
            msg = clientSocket.recv(16)
            if newmsg:
                msglen = int(msg[:headerSize])
                newmsg = False

            fullmsg += msg.decode("utf-8")

            if len(fullmsg) - headerSize == msglen: # If the full message is recieved
                print(fullmsg[headerSize:])
                newmsg = True  # Reset for the next message
                break

def start():
    send_thread = threading.Thread(target=sender)
    receive_thread = threading.Thread(target=receiver)
    receive_thread.start()
    send_thread.start()


if __name__ == "__main__":
    start()
