
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

    ### Unhexify data, to send only pure bytes
    byte_hex_arr = bytearray(binascii.unhexlify(hexified))
    #print(binascii.unhexlify(hexified))
    #print(byte_hex_arr)



    #headder.append(get_byte_ack(ack_no))
    #print(headder)
    return byte_hex_arr