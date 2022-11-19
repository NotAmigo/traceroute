from packet import Packet
from ping import Ping
from answer_formatter import AnswerFormatter


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
        previous_address = None
        for ttl in range(1, self.max_ttl + 1):
            ttl_packet = self.packet.get_packet(ttl)
            ping = Ping(ttl_packet, self.timeout, self.repeat, self.interval)
            answer = ping.make_ping()
            if previous_address is not None and answer[0] == previous_address:
                break
            print(f"{str(ttl).ljust(6)} {AnswerFormatter(answer)}")
            previous_address = answer[0]
