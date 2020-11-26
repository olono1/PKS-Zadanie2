#The main file for sender and reciever

##Imports
import socket
import time
import sys
import os
import zlib

#Custom imports
import COMM_values


MY_IP_ADDR = "Not set"
COMM_PORT = "Not set"
OUT_IP_ADDR = "Not set"



def get_mode_from_user():
    mode = input("Enter 1 for sender \n Enter 2 for reciever \n Enter 3 to exit program")
    switcher = {
        1: start_sender(),
        2: start_reciever(),
        3: exit_prog(),
    }
    return switcher.get("Returned", "Invalid Input")


def start_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    
    return

def start_reciever():
    return

def exit_prog():
    return

#Common functions > Sending COMM packets, Bit operations, 
def send_COMM(type):
    print(COMM_values.COMM_type[type])
 


def send_DATA(type, data_in_bits, fragment_lenght):
    
    return



def get_connection_info():
    f = open("config.txt", "r")
    MY_IP_ADDR = f.readline().split()[0]
    COMM_PORT = f.readline().split()[0]
    OUT_IP_ADDR = f.readline().split()[0]

    print(os.path.realpath(f.name))
    print(OUT_IP_ADDR)
    print(COMM_PORT)
    print(MY_IP_ADDR)

get_connection_info()
send_COMM("SYN")

