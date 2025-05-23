
import COMM_values
import zlib
import binascii

MAX_FRAG_LENGHT = 497 ##Based on the design of the protocol

def get_byte_ack(number):
    return number.to_bytes(4, byteorder='big', signed=False)

def send_COMM(type, ack_no):
    headder = bytearray()
    

    decimal_flag = COMM_values.COMM_type[type]
    flag = decimal_flag.to_bytes(1, byteorder='big', signed=False)
    headder.append(decimal_flag)
    btarr=bytearray(get_byte_ack(ack_no))
    both = headder + btarr
    list_int = int.from_bytes([0,0,0,255], byteorder='big')
    crc32_i = zlib.crc32(both)

    b_crc32 = crc32_i.to_bytes(4, byteorder='big', signed=False)
    crc_btarr = bytearray(b_crc32)

    COMM_packet_b = bytearray()
    COMM_packet_b.append(decimal_flag)
    COMM_packet_b.extend(btarr)
    COMM_packet_b.extend(crc_btarr)

    crc_int = int.from_bytes(COMM_packet_b[5:len(COMM_packet_b)], byteorder='big')

    hexified = binascii.hexlify(COMM_packet_b)

    ### Unhexify data, to send only pure bytes
    byte_hex_arr = bytearray(binascii.unhexlify(hexified))

    return byte_hex_arr

def count_lenght(data_to_prep, frag_len):
    if(data_to_prep > int(frag_len)):
        return frag_len
    else:
        return data_to_prep
    
def prepare_DATA(pkt_type, data_in_bits, fragment_lenght, Sender_obj):
    data_to_prepare = len(data_in_bits)
    fragments = list() 
    SQ_num = 1
    if fragment_lenght > MAX_FRAG_LENGHT:
        print(f"MAX_FRAGMENT_LENGHT passed. Using {MAX_FRAG_LENGHT} for fragment lenght")
        fragment_lenght = MAX_FRAG_LENGHT

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
        print(f"Prepaded data:{decode_DATA(fragment_x)}") ##Uncoment to see how the data was prepared
        SQ_num += 1
        data_to_prepare -= frag_len

    


    return fragments

def print_data_stats(pkt_type, fragments):
    if pkt_type == "MSG":
        size_frg = decode_DATA(fragments[0])
        last_frg = decode_DATA(fragments[len(fragments)-1])
        print(f"Sending {len(fragments)} fragments. Size of fragment {size_frg['LEN']}B. Size of last fragment {last_frg['LEN']}B")
    elif pkt_type == "FILE":
        size_frg = decode_DATA(fragments[1])
        last_frg = decode_DATA(fragments[len(fragments)-1])
        print(f"Sending {len(fragments)} fragments. Size of fragment {size_frg['LEN']}B. Size of last fragment {last_frg['LEN']}B")

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
 
    ### UN-COMMENT TO SEE WHAT DATA IS BEING RECIEVED ON BOTH ENDS
    print(f"Recieved: {pkt_dict}")
    
    return pkt_dict


