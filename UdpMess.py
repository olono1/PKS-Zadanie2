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
    Comunication = UdpMess__reciever.Reciever(MY_IP_ADDR, COMM_PORT)
    UdpMess__reciever.start_reciever(Comunication)




def exit_prog():
    return


#Common functions > Sending COMM packets, Bit operations, 

def get_byte_ack(number):
    return number.to_bytes(4, byteorder='big', signed=False)


def send_COMM(type, ack_no):
    #print(COMM_values.COMM_type[type])

    headder = bytearray()
    

    decimal_flag = COMM_values.COMM_type[type]
    flag = decimal_flag.to_bytes(1, byteorder='big', signed=False)
    #print(flag)
    headder.append(decimal_flag)
    #print(f"ACK in bytes: {get_byte_ack(ack_no)}")
    btarr=bytearray(get_byte_ack(ack_no))
    ##headder.extend(get_byte_ack(ack_no))
    
    both = headder + btarr
    #print(both)
    for v in both: print(v)
    #print(both[1:4])
    #print(f"ACK to int {int.from_bytes(both[1:5], byteorder='big')}")

    list_int = int.from_bytes([0,0,0,255], byteorder='big')
    #print(list_int)
   
    

    crc32_i = zlib.crc32(both)
    #print(f"crc value: {crc32_i}")
    #print(f"CRC23 byte value: {get_byte_ack(crc32_i)}")
    b_crc32 = crc32_i.to_bytes(4, byteorder='big', signed=False)
    #headder.extend(b_crc32)
    crc_btarr = bytearray(b_crc32)
    #print(crc_btarr)
    for v in crc_btarr: print(v)

    # print(f"CRC to int{int.from_bytes(crc_btarr, byteorder='big')}")

    COMM_packet_b = bytearray()
    COMM_packet_b.append(decimal_flag)
    COMM_packet_b.extend(btarr)
    COMM_packet_b.extend(crc_btarr)
    #print(COMM_packet_b)

    crc_int = int.from_bytes(COMM_packet_b[5:len(COMM_packet_b)], byteorder='big')
    #print(crc_int)
    #print(binascii.hexlify(COMM_packet_b))
    hexified = binascii.hexlify(COMM_packet_b)

    byte_hex_arr = bytearray(binascii.unhexlify(hexified))
    #print(binascii.unhexlify(hexified))
    #print(byte_hex_arr)



    #headder.append(get_byte_ack(ack_no))
    #print(headder)
    return hexified

 


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
send_COMM("SYN", 5)

