import hashlib
from io import BytesIO


def calc_cksm(data):
    return hashlib.md5(data).hexdigest()


def build_packet(ack, file, data):
    p = ack + pad_bytes(file.encode(), 64) + data
    cksm = calc_cksm(p)
    return cksm.encode() + p


def build_ack(ack):
    p = ack
    cksm = calc_cksm(p)
    return cksm.encode() + p


def pad_bytes(b, n):
    to_pad = n - len(b)
    if n > 0:
        return (b'\0' * to_pad) + b
    return b


def read_packet(packet):
    buffer = BytesIO(packet)
    cksm = buffer.read(32)
    ack = buffer.read(1)
    file_name = buffer.read(64)
    data = buffer.read(1024-(32+1+64))
    rcv_cksm = calc_cksm(ack + file_name + data)
    return cksm, ack, file_name.decode().strip('\x00'), data, rcv_cksm.encode()
