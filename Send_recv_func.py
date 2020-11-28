
import COMM_values
import zlib
import binascii

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
    ##for v in both: print(v)
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
    ##for v in crc_btarr: print(v)

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

    ### Unhexify data, to send only pure bytes
    byte_hex_arr = bytearray(binascii.unhexlify(hexified))
    #print(binascii.unhexlify(hexified))
    #print(byte_hex_arr)



    #headder.append(get_byte_ack(ack_no))
    #print(headder)
    return byte_hex_arr


    
def send_DATA(type, data_in_bits, fragment_lenght):
    
    return

def get_pkt_type(flag):
    if(flag >= 128):
        return "COMM"
    elif (flag < 128):
        return "DATA"

def decode_COMM(b_data):
    pkt_dict = {}
    pkt_dict['FLAG'] = b_data[0]
    pkt_dict['ACK'] = int.from_bytes(b_data[1:5], byteorder='big')
    pkt_dict['CRC'] = int.from_bytes(b_data[5:9], byteorder='big')
    return pkt_dict



    

def decode_DATA(b_data):
    pass

def decode_and_recieve(b_data):
    decoded_data_list = list()
    pkt_dict = {}
    hex_btarr = send_COMM("SYN", 50)


    pkt_type = get_pkt_type(b_data[0])

    if(pkt_type == "COMM"):
        pkt_dict = decode_COMM(b_data)
    elif (pkt_type == "DATA"):
        pkt_dict = decode_DATA(b_data)


    print(hex_btarr[0])
    decoded_data_list.append(hex_btarr[0])
    print(hex_btarr[1:5])
    print(int.from_bytes(hex_btarr[1:5], byteorder='big'))
    decoded_data_list.append(int.from_bytes(hex_btarr[1:5], byteorder='big'))
    print(int.from_bytes(hex_btarr[5:len(hex_btarr)], byteorder='big'))
    decoded_data_list.append(int.from_bytes(hex_btarr[5:len(hex_btarr)], byteorder='big'))

 

    print(f"Dictionary: {pkt_dict}")
    print(f"List rep: {decoded_data_list}")



    
    return pkt_dict

decode_and_recieve(send_COMM("SYN", 50))