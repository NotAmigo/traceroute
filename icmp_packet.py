from scapy.all import RandString, IP, ICMP

from packet import Packet


class ICMPPacket(Packet):
    def __init__(self,
                 dst: str,
                 session_id: int,
                 seq: int,
                 src: str,
                 length: int,
                 payload: str | None = None):
        super(ICMPPacket, self).__init__(dst, session_id, seq, src)

        self.payload = payload if payload is not None \
            else str(RandString(length - 8))
        self.length = length

    def get_packet(self, ttl: int) -> IP:
        return (
                IP(dst=self.dst, ttl=ttl)
                / ICMP(id=self.id, seq=self.seq)
                / self.payload
                )
