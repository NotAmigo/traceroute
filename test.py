# Дополнительная часть:
# Поддержка IPv6.
# Разрешать хопы в DNS-имя.
# debug-режим.
from scapy.all import *
import time
from typing import List, Tuple, Optional
import click

Answer = Tuple[Optional[str], List[Optional[int]]]  # TODO: python 3.10 change to | also is there better place to do it

hostname = "8.8.8.8"
NETWORK_ROUTER_ADMIN_LOGIN = '192.168.1.120'


class Packet:
    def __init__(self, dst, id, seq, src):
        self.id = id
        self.seq = seq
        self.dst = dst
        self.src = src

    def get_packet(self, ttl):
        raise NotImplementedError


class ICMPPacket(Packet):
    def __init__(self, dst, id: int, seq: int, src: str, length: int, payload):
        super(ICMPPacket, self).__init__(dst, id, seq, src)
        self.payload = payload if payload is not None else str(RandString(length - 8))
        self.length = length

    def get_packet(self, ttl) -> IP:
        return IP(dst=self.dst, ttl=ttl) / ICMP(id=self.id, seq=self.seq) / self.payload


class TCPPacket(Packet):
    def __init__(self, dst, id: int, seq: int, src: str, port: int):
        super(TCPPacket, self).__init__(dst, id, seq, src)
        self.port = port

    def get_packet(self, ttl) -> TCP:
        return IP(dst=self.dst, ttl=ttl) / TCP(flags=0x2, dport=self.port, sport=RandShort())


class Ping:
    def __init__(self, packet: Packet, timeout: int, repeat: int, interval: int):
        self.timeout = timeout
        self.packet = packet
        self.repeat = repeat
        self.interval = interval

    def make_ping(self) -> Answer:
        timestamps = []
        address = None
        for i in range(self.repeat):
            response = sr1(self.packet, timeout=self.timeout, verbose=0)  # TODO: convert ticks to ms
            timestamp = round((response.time - self.packet.sent_time) * 1000) if response is not None else None
            addr = response.src if response is not None else None
            if addr is not None:
                address = addr
            timestamps.append(timestamp)
            time.sleep(self.interval)
        return address, timestamps


class AnswerFormatter:
    def __init__(self, answer: Answer):
        self.answer = answer

    def __str__(self):
        return " ".join(f"{(str(i) + ' ms').ljust(6)}" if i is not None else '*'.ljust(6) for i in self.answer[1]) + \
               f" {self.answer[0].ljust(6) if self.answer[0] is not None else ''}"


class Traceroute:
    def __init__(self, dst: str, packet: Packet,
                 max_ttl: int, repeat: int, timeout: int, interval: int):
        self.dst = dst
        self.packet = packet
        self.interval = interval
        self.max_ttl = max_ttl
        self.repeat = repeat
        self.timeout = timeout

    def run(self):
        for ttl in range(1, self.max_ttl + 1):
            ttl_packet = self.packet.get_packet(ttl)
            ping = Ping(ttl_packet, self.timeout, self.repeat, self.interval)
            answer = ping.make_ping()
            print(f"{str(ttl).ljust(6)} {AnswerFormatter(answer)}")
            if answer[0] == self.dst:
                break


@click.command()
@click.option('--type', prompt='Type TCP or ICMP', help='Choose, ICMP or TCP traceroute')
@click.option('--destination', prompt='Traceroute to', help='Destination IP address')
@click.option('--source', default=NETWORK_ROUTER_ADMIN_LOGIN, help='Source IP address')
@click.option('--id', default=0, help='Custom id')
@click.option('--seq', default=0, help='Custom SEQ')
@click.option('--len', default=40, help='Length of the ICMP packet. '
                                        'If you type custom, payload, length will be ignored, length ignored for TCP')
@click.option('--payload', default=None, help='Custom ICMP packet payload')
@click.option('--tcp_port', default=80, help='Custom TCP destination port')
@click.option('--max_ttl', default=30, help='Max TTL')
@click.option('--repeat', default=3, help='Requests per TTL')
@click.option('--timeout', default=3, help='Timeout for each request')
@click.option('--interval', default=0, help='Interval between requests')
def main(type, destination, source, id, seq, len, payload, tcp_port, max_ttl, repeat, timeout, interval):
    if type == 'ICMP':
        packet = ICMPPacket(destination, id, seq, source, len, payload)
    elif type == 'TCP':
        packet = TCPPacket(destination, id, seq, source, tcp_port)
    else:
        print('Wrong type')
        return
    traceroute = Traceroute(destination, packet, max_ttl, repeat, timeout, interval)
    traceroute.run()

main()
