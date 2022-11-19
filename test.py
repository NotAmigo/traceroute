# Дополнительная часть:
# Поддержка IPv6.
# Работа через TCP SYN + указание порта.
# Разрешать хопы в DNS-имя.
# debug-режим.
from scapy.all import *
import time
from typing import List, Tuple, Optional
from collections import namedtuple

# TODO: Want to rewrite tuple to namedtuple ^^^

Answer = Tuple[Optional[str], List[Optional[int]]]  # TODO: python 3.10 change to | also is there better place to do it

hostname = "8.8.8.8"
NETWORK_ROUTER_ADMIN_LOGIN = '192.168.1.120'


class ICMPPacket:
    def __init__(self, dst, ttl=1, id=RandShort(), seq=0, length=40, payload=None):
        self.id = id
        self.seq = seq
        self.payload = payload if payload is not None else str(RandString(length - 8))
        self.ttl = ttl
        self.dst = dst
        self.length = length

    def get_packet(self) -> IP:
        return IP(dst=self.dst, ttl=self.ttl) / ICMP(id=self.id, seq=self.seq) / self.payload

    def get_ping_packet(self, ttl) -> IP:
        return IP(dst=self.dst, ttl=ttl) / ICMP(id=self.id, seq=self.seq) / self.payload


class Ping:
    def __init__(self, packet: IP, timeout: int, repeat: int, interval: int):
        self.timeout = timeout
        self.packet = packet
        self.repeat = repeat
        self.interval = interval

    def make_ping(self) -> Answer:
        timestamps = []
        address = None
        for i in range(self.repeat):
            response = sr1(self.packet, timeout=self.timeout, verbose=0)  # TODO: convert ticks to ms
            timestamp = round((response.time - self.packet.sent_time)*1000) if response is not None else None
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
    def __init__(self, dst: str, packet: ICMPPacket, src: str = NETWORK_ROUTER_ADMIN_LOGIN,
                 max_ttl: int = 30, repeat: int = 3, timeout: int = 3, interval: int = 0):
        self.dst = dst
        self.src = src
        self.packet = packet
        self.interval = interval
        self.max_ttl = max_ttl
        self.repeat = repeat
        self.timeout = timeout

    def run(self):
        for ttl in range(1, self.max_ttl + 1):
            ttl_packet = self.packet.get_ping_packet(ttl)
            ping = Ping(ttl_packet, self.timeout, self.repeat, self.interval)
            answer = ping.make_ping()
            print(f"{str(ttl).ljust(6)} {AnswerFormatter(answer)}")


traceroute = Traceroute(hostname, ICMPPacket(hostname))
traceroute.run()
