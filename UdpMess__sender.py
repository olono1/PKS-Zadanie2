import socket
import zlib
import time
import binascii
import threading
#Custom imports
import Send_recv_func



MAX_RECV_FROM = 508
TIMEOUT = 5
WINDOW_SIZE = 5
TEXT_ENCODING_FORMAT = 'utf-8'

base = 0
mutex = threading.Lock()


class Sender:
    def __init__(self, my_ip, port_my, out_ip, port_out): 
        self.__my_IP_address = my_ip
        self.__port_my = port_my
        self.__out_ip = out_ip
        self.__port_out = port_out
        self.__out_tuple = (out_ip, port_out)
        self.__SQ_num = 1
        #print(self.__IP_port_tuple)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind((my_ip, port_my))
        self.__active_connection = False

    
    def get_socket(self):
        return self.__sock

    def get_out_tuple(self):
        return self.__out_tuple
    
    def is_conn_estab(self):
        return self.__active_connection

    def get_SQ_num(self):
        return self.__SQ_num

    def add_SQ_num(self):
        self.__SQ_num += 1
        return self.__SQ_num


def establish_connection(Sender_obj):
    if Sender_obj.is_conn_estab():
        return True
    else:
        
        pass
    
    return True

def start_sender(Sender_obj: Sender):
    #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_mode = input("1: Send Message\n2: Send File\n3:Disconnect")
    flag = ""
    if(send_mode == "1"):
        load_data = input("Enter your super-duper message>>> ")
        binary_msg = load_data.encode(TEXT_ENCODING_FORMAT)
        load_data = binary_msg
        flag = "MSG"
    elif send_mode == "2":
        load_data = input("Enter the file name>>> ")
        with open(load_data, "rb") as bin_file:
            data = bin_file.read()
            load_data = data
        flag = "FILE"
    elif send_mode == "3":
        load_data = input("The connection will be ended. Are you sure? Y/N")

    if establish_connection(Sender_obj):
        pass

    fragment_size = input("Enter fragment size>>> ")
    start_SQ = Sender_obj.get_SQ_num()




    list_data = Send_recv_func.prepare_DATA(flag, load_data, 30, 30)


    Sender_obj.get_socket().sendto(Send_recv_func.send_COMM("ACK", 5), Sender_obj.get_tuple())


    
    return