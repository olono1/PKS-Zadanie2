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
OUT_COMM_PORT = "Not set"
MAX_RECV_FROM = 508



def get_mode_from_user():
    

    while True:
        mode = input("Enter 1 for sender\nEnter 2 for reciever\nEnter 3 to exit program\n")

        if mode == '1':
            init_sender()
        elif mode == '2':
            init_reciever()
        elif mode == '3':
            exit_prog()




def init_sender():
    get_connection_info()
    ##TODO: #5 add a try statement, that handles the Error, telling the user to check the config file
    Comunication = UdpMess__sender.Sender(MY_IP_ADDR, COMM_PORT, OUT_IP_ADDR, OUT_COMM_PORT)
    UdpMess__sender.start_sender(Comunication)


def init_reciever():
    get_connection_info()
    Comuni = UdpMess__reciever.Reciever(MY_IP_ADDR, COMM_PORT, OUT_IP_ADDR, OUT_COMM_PORT)
    UdpMess__reciever.start_reciever(Comuni)




def exit_prog():
    exit()

#Common functions > Sending COMM packets, Bit operations, 

def get_connection_info():
    global MY_IP_ADDR 
    global COMM_PORT 
    global OUT_IP_ADDR
    global OUT_COMM_PORT
    with open("config.txt", "r") as f:
        MY_IP_ADDR = f.readline().split()[0]
        COMM_PORT = int(f.readline().split()[0])
        OUT_IP_ADDR = f.readline().split()[0]
        OUT_COMM_PORT = int(f.readline().split()[0])

    print(f"My IP address: {MY_IP_ADDR} : {COMM_PORT}")
    print(f"Connecting to: {OUT_IP_ADDR} : {OUT_COMM_PORT}")


get_mode_from_user()
get_connection_info()
#send_COMM("SYN", 5)

