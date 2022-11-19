from packet import Packet
from scapy.all import IP, TCP, RandShort


class TCPPacket(Packet):
    def __init__(self, dst, session_id: int, seq: int, src: str, port: int):
        super(TCPPacket, self).__init__(dst, session_id, seq, src)
        self.port = port

    def get_packet(self, ttl) -> TCP:
        return (
                IP(dst=self.dst, ttl=ttl)
                / TCP(flags=0x2, dport=self.port, sport=RandShort())
        )
