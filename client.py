import socket  # Used to do the whole socket thing
import sys  # Used to get info from terminal
import threading  # Used to allow us to both receive and send data
import pickle # Used for serlization 
import os  # Used for folder and file stuff

# Constants
headerSize = 10  # Maximum length for the header


try:
    # Get command-line arguments
    if len(sys.argv) != 4:
        raise ValueError("Please make sure that all fields are given before atempting to connect to the server")

    userName = sys.argv[1]
    ip = sys.argv[2]
    port = int(sys.argv[3])

    # Create a socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    try:
        clientSocket.connect((ip, port))
        print("Connected to the server.")
    except Exception as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)

    # Send the username to the server
    try:
        username_msg = f"{len(userName):<{headerSize}}{userName}"
        clientSocket.send(username_msg.encode('utf-8'))
    except Exception as e:
        print(f"Error sending username: {e}")
        sys.exit(1)

    # Sender function
    def sender():
        while True:
            try:
                msg = input("Enter a message to send: \n")
                if not msg:
                    print("Message cannot be empty.")
                    continue
                msg = f"{len(msg):<{headerSize}}{msg}"
                clientSocket.send(msg.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")
                break

    # Receiver function
    def receiver():
        while True:
            try:
                fullmsg = b''  # Initialize buffer
                newmsg = True
                fileTransfer = False

                while True:
                    msg = clientSocket.recv(16)
                    if not msg:
                        print("Server connection closed.")
                        break

                    if newmsg:
                        try:
                            msglen = int(msg[:headerSize].strip())
                            newmsg = False
                        except ValueError:
                            print("Received invalid header.")
                            break

                        # Check for file transfer
                        if b'file' in msg:
                            print("Transferring a file")
                            fileTransfer = True

                    fullmsg += msg

                    # Check if full message has been received
                    if len(fullmsg) - headerSize == msglen:
                        if fileTransfer:
                            if not os.path.isdir(userName):
                                os.makedirs(userName)
                                print("Folder created")

                            print("Full file received")
                            file = pickle.loads(fullmsg[headerSize + 6:])

                            filePath = os.path.join(userName, file['fileName'])
                            if os.path.exists(filePath):
                                print("File already exists.")
                            else:
                                with open(filePath, 'wb') as f:
                                    f.write(file['fileData'])
                                print(f"File saved as {filePath}")

                            fileTransfer = False
                        else:
                            print(fullmsg[headerSize:].decode('utf-8'))

                        newmsg = True
                        fullmsg = b''  # Reset buffer
                        break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    # Start threads for sending and receiving
    def start():
        try:
            receive_thread = threading.Thread(target=receiver, daemon=True)
            send_thread = threading.Thread(target=sender, daemon=True)

            receive_thread.start()
            send_thread.start()

            # Join threads to keep the program running
            receive_thread.join()
            send_thread.join()
        except Exception as e:
            print(f"Error starting threads: {e}")

    if __name__ == "__main__":
        start()

except ValueError as ve:
    print(f"Value Error: {ve}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
