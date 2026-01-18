# Networks-Systems-Coursework
How to use the messaging system

# How to connect:
TO run the server you need to run the server code with:
python server.py 12000
To connect to the server you need to run the client code with:
python client.py username hostname port

# Commands
## For Unicast:
use @'username' to message a user directly make sure there is a space after the command 
for example @John hello world. would send 'hello world' to only john

## For All:
This is the defult messaging mode and therefore doesn't require any command to enter this mode
for example 'hello everyone' would send it to everyone connected to the server

## For Exit:
To leave the server and chatroom just /exit this command with disconnect you from the server in a errorfree way.

## For file list:
To get the list of files avaliable to download from the server use @files.
This will return a list of files avalible to download including their sizes

## Download file:
To download a file use /download 'filename' this will download that file 
for example /download text.txt. would download that text document into that clients area.

## File size

To get the size of a individual file you can you the /size 'filename'
For example /size test.txt. would send the size in bytes of that file to the user.
# Chat-Messaging-Service
