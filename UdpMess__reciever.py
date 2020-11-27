
#Imports
import socket
import zlib
import time
import binascii
import select


#Custom Import 
import Send_recv_func

#Private variables

class Reciever:

    def __init__(self, IP, port): 
        self.__my_IP_address = IP
        self.__port = port
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__timeout = 10
        self.__active_connection = False
    
    def define_socket(self, tuple_IP_port):
        self.__sock.bind(tuple_IP_port)

    def get_socket(self):
        return self.__sock
    
    def get_timeout(self):
        return self.__timeout


def __activate_connection():
    __active_connection = True


def start_reciever(Reciever_obj: Reciever):
    sock = Reciever_obj.get_socket()
    timeout = Reciever_obj.get_timeout()
    
    while True:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            data, addr = sock.recvfrom(508)
            print(f"Recieved: {data}, from {addr} \n")
          
        else:
            print (f" Finish!")
           
            break
    return