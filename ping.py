import socket
import struct


PAYLOAD = '0'*64


def _checksum(data):
    '''
    Compute the checksum of an ICMP packet. Checksums are used to
    verify the integrity of packets.
    '''
    sum = 0
    data += b'\x00'

    for i in range(0, len(data) - 1, 2):
        sum += (data[i] << 8) + data[i + 1]
        sum = (sum & 0xffff) + (sum >> 16)

    sum = ~sum & 0xffff

    return sum

def make_request(seq, payload):
    '''
    Create an ICMP request packet. The packet is composed of an
    ICMP header and a payload.
    '''
    header = struct.pack('!BBHHH', 8, 0, 0, 0, seq)
    checksum = _checksum(header + payload)
    header = struct.pack('!BBHHH', 8, 0, checksum, 0, seq)
    return header + payload


def test_traceroute(seq, host):
    for i in range(1, 31):
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, i)
        s.bind(('0.0.0.0', 0))
        req = make_request(seq+i, PAYLOAD.encode('utf-8'))
        sock_destination = socket.getaddrinfo(
            host=host,
            port=None,
            family=socket.AF_INET,
            type=socket.SOCK_RAW)[0][4]
        s.sendto(req, sock_destination)
        data, addr = None, None
        while not data:
            data, addr = s.recvfrom(4096)
        host = addr[0]


test_traceroute(3600, 'google.com')
