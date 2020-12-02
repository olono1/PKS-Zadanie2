
#Imports
import socket
import zlib
import time
import binascii
import threading
import select
import os





#Custom Import 
import Send_recv_func
import COMM_values

#variables
TEXT_ENCODING_FORMAT = 'utf-8'
MAX_RECV_FROM = 508
#globals for threads - keep-alive
stop_keep_alive = False
mutex_keep_alive = threading.Lock()

class Reciever:

    def __init__(self, my_ip, port_my, out_ip, port_out): 
        self.__my_IP_address = my_ip
        self.__port_my = int(port_my)
        self.__out_ip = out_ip
        self.__port_out = int(port_out)
        self.__out_tuple = (out_ip, int(port_out))
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind((my_ip, port_my))
        self.__timeout = 15
        self.__expected_SQ = 1
        self.__active_connection = False
    
    def get_out_tuple(self):
        return self.__out_tuple

    def get_socket(self):
        return self.__sock

    def get_timeout(self):
        return self.__timeout

    def use_expected_SQ(self):
        SQ = self.__expected_SQ
        self.__expected_SQ += 1
        return SQ
    
    def reset_expected_sq(self):
        self.__expected_SQ = 1

    def get_expected_SQ(self):
        return self.__expected_SQ

    def get_error_SQ(self):
        return self.__expected_SQ - 1

    def is_conn_estab(self):
        return self.__active_connection

    def set_conn_status(self, status):
        self.__active_connection = status
        return self.__active_connection


def listen_for_connection(Reciever_obj):
    sock = Reciever_obj.get_socket()
    timeout = Reciever_obj.get_timeout()
    try:
        while not Reciever_obj.is_conn_estab():
        ##Wait for SYN packet
            syn_recv_and_replied = False
            no_response = 0
            while True:
                ready = select.select([sock], [], [], timeout)
                if ready[0]:
                    data, addr = sock.recvfrom(MAX_RECV_FROM)
                    dec_data = Send_recv_func.decode_and_recieve(data)
                    if dec_data == False:
                        Send_recv_func.send_out_COMM(Reciever_obj, "ERR", 0)
                    elif dec_data['FLAG'] == COMM_values.COMM_type['SYN']:
                        Send_recv_func.send_out_COMM(Reciever_obj, "SYN, ACK", 0)
                        syn_recv_and_replied = True
                    if syn_recv_and_replied and dec_data['FLAG'] == COMM_values.COMM_type['ACK']:
                        Reciever_obj.set_conn_status(True)
                        break
                    if dec_data['FLAG'] == COMM_values.COMM_type["ERR"]:
                        if syn_recv_and_replied == True:
                            Send_recv_func.send_out_COMM(Reciever_obj, "SYN, ACK", 0)
                else:
                    if syn_recv_and_replied == True:
                        Send_recv_func.send_out_COMM(Reciever_obj, "SYN, ACK", 0)
                        no_response += 1
                    if no_response > 2:
                        print("Connection could not be established.")
                        return False
    except KeyboardInterrupt:
        print("The Reciver has stopped listening for a connection segment")


    return True


def start_reciever(Reciever_obj: Reciever):
    sock = Reciever_obj.get_socket()
    timeout = Reciever_obj.get_timeout()

    outcome = listen_for_connection(Reciever_obj)
    

    if outcome == True:
        listen(Reciever_obj)
    else:
        print("Connection was not established")

    return


def listen(Reciever_obj: Reciever):
    recieved_fragments = []
    no_respose = 0
    sock = Reciever_obj.get_socket()
    timeout = Reciever_obj.get_timeout()
    no_errors = True
    try:
        while True:
            ready = select.select([sock], [], [], timeout)
            if ready[0]:
                data, addr = sock.recvfrom(MAX_RECV_FROM)
                dec_data = Send_recv_func.decode_and_recieve(data)

                if dec_data == False:
                    Send_recv_func.send_out_COMM(Reciever_obj, "ACK", Reciever_obj.get_error_SQ())
                    no_errors = False
                elif Send_recv_func.get_pkt_type(dec_data['FLAG']) == "DATA":
                    if int(dec_data['SQ']) == Reciever_obj.get_expected_SQ():
                        Send_recv_func.send_out_COMM(Reciever_obj, "ACK", Reciever_obj.use_expected_SQ())
                        recieved_fragments.append(dec_data)
                    elif int(dec_data['SQ']) < Reciever_obj.get_expected_SQ():
                        Send_recv_func.send_out_COMM(Reciever_obj, "ACK", Reciever_obj.get_error_SQ())
                        no_errors = False
                    elif int(dec_data['SQ']) > Reciever_obj.get_expected_SQ():
                        Send_recv_func.send_out_COMM(Reciever_obj, "ACK", Reciever_obj.get_error_SQ())
                        no_errors = False
                elif Send_recv_func.get_pkt_type(dec_data['FLAG']) == "COMM":
                    if dec_data['FLAG'] == COMM_values.COMM_type["CONN"]:
                        ##time.sleep(10)
                        Send_recv_func.send_out_COMM(Reciever_obj, "ACK", 0)
                    elif dec_data['FLAG'] == COMM_values.COMM_type["DONE"]:
                        Send_recv_func.send_out_COMM(Reciever_obj, "ACK", 0)
                        if no_errors:
                            print("The data was recieved with no errors durring transmission")
                        process_recieved(recieved_fragments, Reciever_obj)
                        recieved_fragments.clear()
                        Reciever_obj.reset_expected_sq()
                        no_errors = True
                    elif dec_data['FLAG'] == COMM_values.COMM_type["FIN"]:
                        conn_ended = listen_for_conn_end(Reciever_obj)
                        return
                no_respose = 0
            else:
                no_respose += 1
                if no_respose > 3:
                    print("Sender did not send keep_alive or data. Timeout Exceeded")
                    print("Connection terminated. Sender did not send anything anymore")
                    return
    except KeyboardInterrupt:
        print("The Reciver has been forcely terminated")

            
def listen_for_conn_end(Reciever_obj):
    connection_ended = False
    Send_recv_func.send_out_COMM(Reciever_obj, "ACK, FIN", 0)
    
    sock = Reciever_obj.get_socket()
    timeout = Reciever_obj.get_timeout()
    while not connection_ended:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            data, addr = sock.recvfrom(MAX_RECV_FROM)
            dec_data = Send_recv_func.decode_and_recieve(data)
            if dec_data['FLAG'] == COMM_values.COMM_type["ACK"]:
                connection_ended = True
            elif dec_data['FLAG'] == COMM_values.COMM_type["ERR"]:
                Send_recv_func.send_out_COMM(Reciever_obj, "ACK, FIN", 0)
        else:
            connection_ended = True
    
    print(f"Connection ended.")
    return connection_ended
        


def get_data_type(fragment):
    if fragment['FLAG'] == COMM_values.COMM_type["MSG"]:
        return "MSG"
    elif fragment['FLAG'] == COMM_values.COMM_type["FILE"]:
        return "FILE"
    else:
        return False

def process_recieved(fragmetns_list, Reciever_obj):
    global stop_keep_alive
    global mutex_keep_alive
    data_type = get_data_type(fragmetns_list[0])

    keep_connection_thread = threading.Thread(target=reply_for_keep_alive, args=(Reciever_obj,))
    keep_connection_thread.start()
    if data_type == "MSG":
        msg = bytearray()
        for fragment in fragmetns_list:
            msg.extend(fragment['DATA'])
        text_msg = msg.decode(TEXT_ENCODING_FORMAT)
        print(f"Recieved message:\n {text_msg}")
        print(f"Number of recieved fragments: {len(fragmetns_list)}")
        print(f"Fragment size: {fragmetns_list[0]['LEN']}")
        print(f"Last fragment size: {fragmetns_list[len(fragmetns_list)-1]['LEN']}")

        
    elif data_type == "FILE":
        byte_file_name = bytearray()
        byte_file_name.extend(fragmetns_list[0]['DATA'])
        file_name = byte_file_name.decode(TEXT_ENCODING_FORMAT)

        file_save_proc = input("Where shall we save this file?\n1 : To this repository\n2 : Enter a path\n>>> ")
        if file_save_proc == "1":
            write_to_file(file_name, fragmetns_list)
        else:
            file_path = input("Enter the path where to save the recieved file\n>>> ")
            full_name = os.path.join(file_path, file_name)
            write_to_file(full_name, fragmetns_list)


        print("File recieved and saved sucesfully")
        print(f"Number of recieved fragments: {len(fragmetns_list)}")
        print(f"Fragment size: {fragmetns_list[1]['LEN']}")
        print(f"Last fragment size {fragmetns_list[len(fragmetns_list)-1]['LEN']}")

    mutex_keep_alive.acquire()
    stop_keep_alive = True
    mutex_keep_alive.release()
    keep_connection_thread.join()
        
        
def write_to_file(file_name, fragmetns_list):
    with open(file_name, 'wb') as f:
        print(f"Saving file to location:\n{os.path.realpath(f.name)}")
        for frag_sq in range(1, len(fragmetns_list)):
            f.write(fragmetns_list[frag_sq]['DATA'])

def reply_for_keep_alive(Reciever_obj):
    global stop_keep_alive
    global mutex_keep_alive
    sock = Reciever_obj.get_socket()
    timeout = 2

    mutex_keep_alive.acquire()
    stop_keep_alive = False
    mutex_keep_alive.release()

    while True:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            data, addr = sock.recvfrom(MAX_RECV_FROM)
            dec_data = Send_recv_func.decode_and_recieve(data)
            if Send_recv_func.get_pkt_type(dec_data['FLAG']) == "COMM":
                if dec_data['FLAG'] == COMM_values.COMM_type["CONN"]:
                    Send_recv_func.send_out_COMM(Reciever_obj, "ACK", 0)
        
        if stop_keep_alive == True:
            break ##File processing done


    