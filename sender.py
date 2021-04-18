import socket
import time

from packet import build_packet, read_packet

UDP_IP = '0.0.0.0'
UDP_PORT = 54321
FILE = './file.txt'
DESTINATION = './bckp.txt'
VERBOSE = True


def debug_print(msg):
    if VERBOSE:
        print(msg)


def flip_ack(ack):
    if ack == b'\0':
        return b'\1'
    else:
        return b'\0'


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    file = open(FILE, 'rb')
    s.settimeout(5)

    data = file.read(1024 - (32 + 1 + 64))
    current_ack = b'\0'

    read = 0

    while data:
        read += len(data)
        packet = build_packet(current_ack, DESTINATION, data)
        sent = False
        debug_print("Uploaded {0} bytes".format(read))
        while not sent:
            time.sleep(1)
            try:
                s.sendto(packet, (UDP_IP, UDP_PORT))
                data, addr = s.recvfrom(1024)
                cksm, ack, _, _, rcv_cksm = read_packet(data)
                debug_print("Received: Checksum: {0}, Ack: {1}\nExpected: Checksum: {2}, Ack: {3}".format(cksm, ack, rcv_cksm, current_ack))
                if cksm == rcv_cksm and ack == current_ack:
                    debug_print("Valid ACK! Proceding to next packet.")
                    sent = True
                else:
                    debug_print("Invalid packet, retrying...")
            except socket.timeout:
                debug_print("Timed out")
                pass
        current_ack = flip_ack(current_ack)
        data = file.read(1024 - (32 + 1 + 64))
    debug_print("Upload finished.")
