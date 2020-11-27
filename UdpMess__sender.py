import socket
import zlib
import time
import binascii

#Custom imports
import UdpMess


class Sender:
    def __init__(self, IP, port): 
        self.__my_IP_address = IP
        self.__port = port
        self.__IP_port_tuple = (IP, port)
        print(self.__IP_port_tuple)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__active_connection = False

    def set_my_IP(self, my_IP):
        self.__my_IP_address = my_IP
        print(f"IP address set to {self.__my_IP_address}")


def start_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    
    return