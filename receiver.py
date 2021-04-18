import socket
from packet import read_packet, build_ack

UDP_IP = '0.0.0.0'
UDP_PORT = 54321
FOLDER = './download/'
VERBOSE = True


def debug_print(msg):
    if VERBOSE:
        print(msg)


def flip_ack(ack):
    if ack == b'\00':
        return b'\01'
    else:
        return b'\00'


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((UDP_IP, UDP_PORT))

    last_ack_pkt = None
    last_ack = b'\01'  # Expect 0 at start

    while True:
        packet, addr = s.recvfrom(1024)
        cksm, ack, file_name, data, rcv_cksm = read_packet(packet)
        if cksm != rcv_cksm or last_ack == ack:
            debug_print("Invalid packet, checksum does not match or unexpected ACK.")
            if last_ack_pkt is not None:
                s.sendto(last_ack_pkt, addr)
                continue
        with open(FOLDER + file_name, 'a+b') as o:
            debug_print("Appending {0} bytes to file {1}".format(len(data), file_name))
            o.write(data)
            last_ack = flip_ack(last_ack)
            last_ack_pkt = build_ack(last_ack)
            s.sendto(last_ack_pkt, addr)

