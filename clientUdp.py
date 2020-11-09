import socket

UDP_IP = "192.168.1.10"
UPD_PORT = 5051
MESSAGE = b"Hello, World"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(MESSAGE, (UDP_IP, UPD_PORT))