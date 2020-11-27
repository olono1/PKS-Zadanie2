#The main file for sender and reciever

##Imports
import socket
import time
import sys
import os
import zlib
import binascii

#Custom imports
import COMM_values
import UdpMess__reciever
import UdpMess__sender


MY_IP_ADDR = "Not set"
COMM_PORT = "Not set"
OUT_IP_ADDR = "Not set"
MAX_RECV_FROM = 508



def get_mode_from_user():
    


    mode = input("Enter 1 for sender\nEnter 2 for reciever\nEnter 3 to exit program\n")

    if mode == '1':
        init_sender()
    elif mode == '2':
        init_reciever()
    elif mode == '3':
        exit_prog()




def init_sender():
    get_connection_info()
    Comunication = UdpMess__sender.Sender(OUT_IP_ADDR, COMM_PORT)
    Comunication.set_my_IP(MY_IP_ADDR)
    UdpMess__sender.start_sender(Comunication)


def init_reciever():
    get_connection_info()
    Comuni = UdpMess__reciever.Reciever(MY_IP_ADDR, COMM_PORT)
    Comuni.define_socket((MY_IP_ADDR, COMM_PORT))
    UdpMess__reciever.start_reciever(Comuni)




def exit_prog():
    return


#Common functions > Sending COMM packets, Bit operations, 






 


def send_DATA(type, data_in_bits, fragment_lenght):
    
    return



def get_connection_info():
    global MY_IP_ADDR 
    global COMM_PORT 
    global OUT_IP_ADDR
    with open("config.txt", "r") as f:
        MY_IP_ADDR = f.readline().split()[0]
        COMM_PORT = int(f.readline().split()[0])
        OUT_IP_ADDR = f.readline().split()[0]

    print(os.path.realpath(f.name))
    print(OUT_IP_ADDR)
    print(COMM_PORT)
    print(MY_IP_ADDR)


get_mode_from_user()
get_connection_info()
#send_COMM("SYN", 5)

