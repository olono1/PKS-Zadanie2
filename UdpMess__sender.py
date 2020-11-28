import socket
import zlib
import time
import binascii
import threading
import select
#Custom imports
import Send_recv_func
import COMM_values



MAX_RECV_FROM = 508
TIMEOUT = 5
WINDOW_SIZE = 5
TEXT_ENCODING_FORMAT = 'utf-8'

base = 0
mutex = threading.Lock()


class Sender:
    def __init__(self, my_ip, port_my, out_ip, port_out): 
        self.__my_IP_address = my_ip
        self.__port_my = int(port_my)
        self.__out_ip = out_ip
        self.__port_out = int(port_out)
        self.__out_tuple = (out_ip, int(port_out))
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

    def set_connection_established_status(self, status):
        self.__active_connection = status

    def get_SQ_num(self):
        return self.__SQ_num

    def add_SQ_num(self):
        self.__SQ_num += 1
        return self.__SQ_num


def establish_connection(Sender_obj):
    if Sender_obj.is_conn_estab():
        return True
    else:
        sock = Sender_obj.get_socket()
        timeout = TIMEOUT
        no_response = 0
        Send_recv_func.send_out_COMM(Sender_obj, "SYN", 0)
        syn_sent_and_ack = False
        while True:
            ready = select.select([sock], [], [], timeout)
            if ready[0]:
                data, addr = sock.recvfrom(MAX_RECV_FROM)
                dec_data = Send_recv_func.decode_and_recieve(data)
                if dec_data == False:
                    Send_recv_func.send_out_COMM(Sender_obj, "ERR", 0)
                elif dec_data['FLAG'] == COMM_values.COMM_type["SYN, ACK"]:
                    Send_recv_func.send_out_COMM(Sender_obj, "ACK", 0)
                    syn_sent_and_ack = True
                    Sender_obj.set_connection_established_status(True)
                elif dec_data['FLAG'] == COMM_values.COMM_type["ERR"]:
                    if syn_sent_and_ack == True:
                        Send_recv_func.send_out_COMM(Sender_obj, "ACK", 0)
                    else:
                        Send_recv_func.send_out_COMM(Sender_obj, "SYN", 0)
            else:
                print("Reply for SYN timeout. Trying again...")
                no_response += 1
            if no_response > 2:
                print("Connection could not be established")
                return False
            Send_recv_func.send_out_COMM(Sender_obj, "SYN", 0)



        
    
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
        print("Connection Established")

    fragment_size = input("Enter fragment size>>> ")
    start_SQ = Sender_obj.get_SQ_num()




    list_data = Send_recv_func.prepare_DATA(flag, load_data, 30, 30)


    Sender_obj.get_socket().sendto(Send_recv_func.send_COMM("ACK", 5), Sender_obj.get_tuple())


    
    return