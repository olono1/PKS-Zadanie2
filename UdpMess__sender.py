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
timeout_pass = False
ack_done = False



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

    def reserve_SQ_num(self):
        SQ_num = self.__SQ_num
        self.__SQ_num += 1
        return SQ_num

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
                if Sender_obj.is_conn_estab() == True:
                    return True
                print("Reply for SYN timeout. Trying again...")
                no_response += 1
            if no_response > 2:
                print("Connection could not be established")
                print(Sender_obj.is_conn_estab())
                return False
            Send_recv_func.send_out_COMM(Sender_obj, "SYN", 0)



        
    
    return True

def get_list_data_file(Sender_obj):
    flag = "FILE"
    load_data = input("Enter the file name>>> ")
    file_name = load_data.encode(TEXT_ENCODING_FORMAT)
    file_name_list = Send_recv_func.prepare_DATA(flag, file_name, 500, Sender_obj)

    with open(load_data, "rb") as bin_file:
        data = bin_file.read()
        load_data = data
    
    frag_len = input("Enter Fragment lenght>>> ")
    file_bits_list = Send_recv_func.prepare_DATA(flag, load_data, int(frag_len), Sender_obj)
    return file_bits_list

def get_list_data_msg(Sender_obj):
    flag = "MSG"
    load_data = input("Enter your super-duper message>>> ")
    binary_msg = load_data.encode(TEXT_ENCODING_FORMAT)
    load_data = binary_msg
    frag_len = input("Enter fragment length>>> ")
    msg_bits_list = Send_recv_func.prepare_DATA(flag, binary_msg, int(frag_len), Sender_obj)
    return msg_bits_list
        


def start_sender(Sender_obj: Sender):
    #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_mode = input("1: Send Message\n2: Send File\n3:Disconnect")
    flag = ""
    list_data = ""
    start_SQ = Sender_obj.get_SQ_num()
    if(send_mode == "1"):
        list_data = get_list_data_msg(Sender_obj)
    elif send_mode == "2":
        list_data = get_list_data_file(Sender_obj)    
    elif send_mode == "3":
        load_data = input("The connection will be ended. Are you sure? Y/N")

    if establish_connection(Sender_obj):
        print("Connection Established")

    
    send_DATA(Sender_obj, list_data)


    #Sender_obj.get_socket().sendto(Send_recv_func.send_COMM("ACK", 5), Sender_obj.get_tuple())


    
    return


def get_window_size(list_size):
    global base
    win_size = min(WINDOW_SIZE, list_size - base)
    return win_size

def send_DATA(Sender_obj: Sender, list_data: list):
    global base
    global mutex
    global timeout_pass
    global ack_done

    next_frag = 0
    sock = Sender_obj.get_socket()
    itr_win_size = get_window_size(len(list_data))

    recv_thread = threading.Thread(target=recv_feedback, args=(Sender_obj,))

    while True:
        mutex.acquire()

        while next_frag < base + itr_win_size:
            Send_recv_func.send_out_DATA(Sender_obj, list_data[next_frag])
            next_frag += 1

        while not ack_done and not timeout_pass:
            mutex.release()
            time.sleep(TIMEOUT)
            mutex.acquire()
        
        if timeout_pass:
            timeout_pass = False
            next_frag = base
        else:
            itr_win_size = get_window_size(len(list_data))

        mutex.release()
        if base < len(list_data):
            break



   
    return

def recv_feedback(Sender_obj: Sender):
    global mutex
    global base
    global timeout_pass
    global ack_done

    sock = Sender_obj.get_socket()
    while True:
        ready = select.select([sock], [], [], TIMEOUT)
        if ready[0]:
            data, addr = sock.recvfrom(MAX_RECV_FROM)
            dec_data = Send_recv_func.decode_and_recieve(data)
            if dec_data['FLAG'] == COMM_values.COMM_type["ACK"]:
                if int(dec_data['ACK']) >= base:
                    mutex.acquire()
                    base = int(dec_data['ACK']) + 1
                    ack_done = True
                    mutex.release()
        else:
            mutex.acquire()
            timeout_pass = True
            mutex.release()
