import socket
import select

UDP_IP = "192.168.1.10"
IN_PORT = 5050
timeout = 3


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, IN_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    if data:
        print (f"File name:{data}")
        file_name = data.strip()

    f = open(file_name, 'wb')

    while True:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            data, addr = sock.recvfrom(1024)
            f.write(data)
        else:
            print (f" Finish! {file_name}")
            f.close()
            break