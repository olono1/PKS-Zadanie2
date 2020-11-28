
#Imports
import socket
import zlib
import time
import binascii
import select


MAX_RECV_FROM = 508

#Custom Import 
import Send_recv_func

#Private variables

class Reciever:

    def __init__(self, my_ip, port_my, out_ip, port_out): 
        self.__my_IP_address = my_ip
        self.__port_my = port_my
        self.__out_ip = out_ip
        self.__port_out = port_out
        self.__out_tuple = (out_ip, port_out)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind((my_ip, port_my))
        self.__timeout = 10
        self.__active_connection = False
    
    def get_out_tuple(self):
        return self.__out_tuple

    def get_socket(self):
        return self.__sock

    def get_timeout(self):
        return self.__timeout

    def is_conn_estab(self):
        return self.__active_connection

    def set_conn_status(self, status):
        self.__active_connection = status
        return self.__active_connection





def start_reciever(Reciever_obj: Reciever):
    sock = Reciever_obj.get_socket()
    timeout = Reciever_obj.get_timeout()

    while not Reciever_obj.is_conn_estab():
        ##Wait for SYN packet
        while True:
            ready = select.select([sock], [], [], timeout)
            if ready[0]:
                data, addr = sock.recvfrom(MAX_RECV_FROM)
                dec_data = Send_recv_func.decode_and_recieve(data)
                if dec_data == False:
                    pass
                else:
                    Reciever_obj.get_socket().sendto(Send_recv_func.send_COMM("SYN, ACK", 0), Reciever_obj.get_out_tuple())




    
    while True:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            data, addr = sock.recvfrom(508)
            print(f"Recieved: {data}, from {addr} \n")
            dec_data = Send_recv_func.decode_and_recieve(data)
            print(f"We got {dec_data['FLAG']} with ACK no: {dec_data['ACK']} and a CRC: {dec_data['CRC']}")


          
        else:
            print (f" Finish!")
           
            break
    return