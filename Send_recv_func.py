
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

def count_lenght(data_to_prep, frag_len):
    if(data_to_prep > frag_len):
        return frag_len
    else:
        return data_to_prep
    
def prepare_DATA(pkt_type, data_in_bits, fragment_lenght, Sender_obj):
    data_to_prepare = len(data_in_bits)
    fragments = list() 
    SQ_num = 1
    while data_to_prepare > 0:
        fragment_x = bytearray()
        fragment_x.append(COMM_values.COMM_type[pkt_type])
        frag_len = count_lenght(data_to_prepare, fragment_lenght)
        fragment_x.extend(frag_len.to_bytes(2, byteorder='big', signed=False))
        fragment_x.extend(get_byte_ack(Sender_obj.reserve_SQ_num()))
        
        fragment_data = bytearray(data_in_bits[((SQ_num-1) * fragment_lenght):(SQ_num*fragment_lenght)])

        data_for_crc = fragment_x + fragment_data
        crc32 = zlib.crc32(data_for_crc)
        fragment_x.extend(crc32.to_bytes(4, byteorder='big', signed=False))
        fragment_x.extend(fragment_data)
        fragments.append(fragment_x)
        #print(decode_DATA(fragment_x))
        SQ_num += 1
        data_to_prepare -= frag_len





    return fragments

def get_pkt_type(flag):
    if(flag >= 128):
        return "COMM"
    elif (flag < 128):
        return "DATA"

def send_out_COMM(Comunication_obj, flag, ACK):
    data_to_send = send_COMM(flag, ACK)
    out_tuple = Comunication_obj.get_out_tuple()
    Comunication_obj.get_socket().sendto(data_to_send, out_tuple)

def send_out_DATA(Comunication_obj, data):
    out_tuple = Comunication_obj.get_out_tuple()
    Comunication_obj.get_socket().sendto(data, out_tuple)


def check_CRC_match(recieved_crc, counted_crc):
    if recieved_crc == counted_crc:
        return True
    else:
        print(f"CRC mismatch. Packet CRC was{recieved_crc}. Counted CRC was {counted_crc}")
        return False

def decode_COMM(b_data):

    headder = bytearray(b_data[0:5])
    crc32 = zlib.crc32(headder)



    pkt_dict = {}
    pkt_dict['FLAG'] = b_data[0]
    pkt_dict['ACK'] = int.from_bytes(b_data[1:5], byteorder='big')
    pkt_dict['CRC'] = int.from_bytes(b_data[5:9], byteorder='big')

    
    if not check_CRC_match(pkt_dict['CRC'], crc32):
        return False

    return pkt_dict
    

def decode_DATA(b_data):

    headder = bytearray(b_data[0:7])
    data_arr = bytearray(b_data[11:len(b_data)])
    headd_and_data = headder + data_arr

    crc32 = zlib.crc32(headd_and_data)

    pkt_dict = {}
    pkt_dict['FLAG'] = b_data[0]
    pkt_dict['LEN'] = int.from_bytes(b_data[1:3], byteorder='big')
    pkt_dict['SQ'] = int.from_bytes(b_data[3:7], byteorder='big')
    pkt_dict['CRC'] = int.from_bytes(b_data[7:11], byteorder='big')
    pkt_dict['DATA'] = b_data[11:len(b_data)]

    if not check_CRC_match(pkt_dict['CRC'], crc32):
        return False

    return pkt_dict

def decode_and_recieve(b_data):
    decoded_data_list = list()
    pkt_dict = {}


    pkt_type = get_pkt_type(b_data[0])

    if(pkt_type == "COMM"):
        pkt_dict = decode_COMM(b_data)
    elif (pkt_type == "DATA"):
        pkt_dict = decode_DATA(b_data)
 

    print(f"Dictionary: {pkt_dict}")
    #print(f"List rep: {decoded_data_list}")
    
    return pkt_dict


#list_data = prepare_DATA("MSG", b'Hello, how are you, Im fine', 5, 30)
#decode_and_recieve(list_data[0])
#decode_and_recieve(send_COMM("SYN", 50))