import socket

HEADDER = 64
FORMAT = 'utf-8'
PORT = 5050
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.1.14"
ADDR = (SERVER, PORT)


client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADDER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

send("Hello sir!") 
send("Hello sir!") 
send("Hello sir!") 
send("Hello sir!") 

send(DISCONNECT_MESSAGE)