import socket
import zlib
import time
import binascii
import threading
import select
import copy
import os
#Custom imports
import Send_recv_func
import COMM_values


#Globals
MAX_RECV_FROM = 508
TIMEOUT = 1
SLEEP_TIME = 0.01
WINDOW_SIZE = 5
TEXT_ENCODING_FORMAT = 'utf-8'
#Globals for thread management - keep-alives
sending_file_mutex = threading.Lock()
sending_file = True
keep_alive_error = False
disconecting = False
#Globals for ARQ
base = 0
mutex = threading.Lock()
timeout_pass = False
ack_done = False
stop_feedback = False



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

    def reset_sq(self):
        self.__SQ_num = 1

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

    return True

def get_list_data_file(Sender_obj):
    global keep_alive_error
    if keep_alive_error == True:
        return False
    flag = "FILE"
    load_data = input("Enter the file name>>> ")
    file_name = load_data.encode(TEXT_ENCODING_FORMAT)
    file_name_list = Send_recv_func.prepare_DATA(flag, file_name, 497, Sender_obj)

    with open(load_data, "rb") as bin_file:
        data = bin_file.read()
        load_data = data
        print(f"Preparing to send file: {os.path.realpath(bin_file.name)} ")
    
    frag_len = input("Enter Fragment lenght>>> ")
    file_bits_list = Send_recv_func.prepare_DATA(flag, load_data, int(frag_len), Sender_obj)
    file_name_data_bits_list = file_name_list + file_bits_list
    Send_recv_func.print_data_stats("FILE", file_name_data_bits_list)
    return file_name_data_bits_list

def get_list_data_msg(Sender_obj):
    global keep_alive_error
    if keep_alive_error == True:
        return False
    flag = "MSG"
    load_data = input("Enter your super-duper message>>> ")
    binary_msg = load_data.encode(TEXT_ENCODING_FORMAT)
    load_data = binary_msg
    frag_len = input("Enter fragment length>>> ")
    msg_bits_list = Send_recv_func.prepare_DATA(flag, binary_msg, int(frag_len), Sender_obj)
    Send_recv_func.print_data_stats("MSG", msg_bits_list)
    return msg_bits_list
        


def start_sender(Sender_obj: Sender):
    global sending_file_mutex
    global sending_file
    global keep_alive_error
    global disconecting
    sending_file = True
    keep_alive_error = False
    disconecting = False

    keep_alive_thread = threading.Thread(target=send_keep_alive, args=(Sender_obj,))
    keep_alive_thread.start()
    while True:
        send_mode = input("1: Send Message\n2: Send File\n3:Disconnect\n>>> ")
        flag = ""
        list_data = ""
        start_SQ = Sender_obj.get_SQ_num()
        if(send_mode == "1"):
            list_data = get_list_data_msg(Sender_obj)
        elif send_mode == "2":
            list_data = get_list_data_file(Sender_obj)    
        elif send_mode == "3":
            load_data = input("The connection will be ended. Are you sure? Y/N\n>>> ")
            if load_data == "y" or load_data == "Y":
                print("Stopping keep-alive packets...")
                sending_file_mutex.acquire()
                disconecting = True
                sending_file = False
                sending_file_mutex.release()
                keep_alive_thread.join()
                end_connection(Sender_obj)
                return
            else:
                continue


        if keep_alive_error == True:
            Sender_obj.set_connection_established_status(False)

        if establish_connection(Sender_obj):
            print("Connection Established")
      
        else:
            print("The Connection is not established. Try again.")
            sending_file_mutex.acquire()
            disconecting = True
            sending_file = False
            sending_file_mutex.release()
            print("Please wait, while we end proceses...")
            keep_alive_thread.join()
            return 
        corupted = input("Send 2nd packet with error? Y/N\n>>> ")

        if corupted == "Y" or corupted == "y":
            corupted = True
        else:
            corupted = False

        sending_file_mutex.acquire()
        sending_file = True
     
        send_DATA(Sender_obj, list_data, corupted)
        print("File, sent")
        sending_file = False
        sending_file_mutex.release()
    
    keep_alive_thread.join()
    return


def get_window_size(list_size):
    global base
    win_size = min(WINDOW_SIZE, list_size+ - base)
    return win_size

def create_error_packet(dict_data):
    corupted = dict_data
    corupted[-1] = 254
    print(corupted)
    return corupted
    

def send_DATA(Sender_obj: Sender, list_data: list, send_corupted):
    global base
    global mutex
    global timeout_pass
    global ack_done
    global stop_feedback

    timeout_pass = False
    ack_done = False
    stop_feedback = False
    base = 0

    

    next_frag = 0
    sock = Sender_obj.get_socket()
    itr_win_size = get_window_size(len(list_data))

    recv_thread = threading.Thread(target=recv_feedback, args=(Sender_obj,))
    recv_thread.start()

    if send_corupted == True:
        second_packet = copy.deepcopy(list_data[2])
        error_sim_packet = create_error_packet(second_packet)
        print(f"Correct  packet:{list_data[2]}\n")
        print(f"Corupted packet: {error_sim_packet}")
        print(f"\nSending...\n")
        corupted_sent = False
    else:
        corupted_sent = True
    


    while True:
        mutex.acquire()

        while next_frag < base + itr_win_size:
            if not corupted_sent and next_frag == 2:
                Send_recv_func.send_out_DATA(Sender_obj, error_sim_packet)
                corupted_sent = True
            else:
                Send_recv_func.send_out_DATA(Sender_obj, list_data[next_frag])
            next_frag += 1

        ack_done = False

        while not ack_done and not timeout_pass:
            mutex.release()
            time.sleep(SLEEP_TIME)
            mutex.acquire()
        
        if timeout_pass:
            timeout_pass = False
            next_frag = base - 1
        else:
            itr_win_size = get_window_size(len(list_data))
            

        mutex.release()
        if base >= (len(list_data)):
            break


    Send_recv_func.send_out_COMM(Sender_obj, "DONE", 0)

    mutex.acquire()
    stop_feedback = True
    mutex.release()
    recv_thread.join()
    Sender_obj.reset_sq()
    return

def recv_feedback(Sender_obj: Sender):
    global mutex
    global base
    global timeout_pass
    global ack_done
    global stop_feedback


    mutex.acquire()
    stop_feedback = False
    mutex.release()

    sock = Sender_obj.get_socket()
    while True:
        ready = select.select([sock], [], [], TIMEOUT)
        if ready[0]:
            data, addr = sock.recvfrom(MAX_RECV_FROM)
            dec_data = Send_recv_func.decode_and_recieve(data)
            if dec_data['FLAG'] == COMM_values.COMM_type["ACK"]:
                if int(dec_data['ACK']) >= base:
                    #print("Got correct ACK")
                    mutex.acquire()
                    base = int(dec_data['ACK']) + 1
                    ack_done = True
                    mutex.release()
        else:
            mutex.acquire()
            timeout_pass = True
            mutex.release()
        if stop_feedback == True:
            break

def send_keep_alive(Sender_obj):
    global sending_file
    global keep_alive_error
    global sending_file_mutex
    global disconecting
    sock = Sender_obj.get_socket()
    timeout = 10
    no_response = 0
    while True:
        while sending_file:
            time.sleep(TIMEOUT)
        time.sleep(timeout)
        if sending_file:
            continue
        else:
            sending_file_mutex.acquire()
            Send_recv_func.send_out_COMM(Sender_obj, "CONN", 0)
            while True:
                if disconecting == True:
                    break
                ready = select.select([sock], [], [], timeout)
                if ready[0]:
                    data, addr = sock.recvfrom(MAX_RECV_FROM)
                    dec_data = Send_recv_func.decode_and_recieve(data)
                    if dec_data == False:
                        Send_recv_func.send_out_COMM(Sender_obj, "CONN", 0)
                    elif dec_data['FLAG'] == COMM_values.COMM_type["ACK"]:
                        keep_alive_error = False
                        no_response = 0
                        break
                else:
                    print(f"There has been a connection issue, please wait... Retry in {timeout}s")
                    Send_recv_func.send_out_COMM(Sender_obj, "CONN", 0)
                    no_response += 1
                    
                    if no_response > 2:
                        print("Conection terminated. To return to menu press 3\n>>> ")
                        keep_alive_error = True
                        break
            if keep_alive_error == True or disconecting == True:
                break
            sending_file_mutex.release()
    sending_file_mutex.release()
                    

def end_connection(Sender_obj):
    Send_recv_func.send_out_COMM(Sender_obj, "FIN", 0)

    sock = Sender_obj.get_socket()
    timeout = TIMEOUT
    connection_ended = False
    while not connection_ended:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            data, addr = sock.recvfrom(MAX_RECV_FROM)
            dec_data = Send_recv_func.decode_and_recieve(data)
            if dec_data['FLAG'] == COMM_values.COMM_type["ACK, FIN"]:
                Send_recv_func.send_out_COMM(Sender_obj, "ACK", 0)
                connection_ended = True
            elif dec_data == False:
                Send_recv_func.send_out_COMM(Sender_obj, "ERR", 0)
        else: 
            connection_ended = True
    
    print(f"Connection ended.")
    return connection_ended
        




