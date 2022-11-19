import time

from scapy.all import sr1, TCP, IP
from answer_formatter import Answer


def to_milliseconds(response_time: float) -> int:
    return int(response_time * 1000)


class Ping:
    def __init__(self,
                 packet: IP | TCP,
                 timeout: int,
                 repeat: int,
                 interval: int):
        self.timeout = timeout
        self.packet = packet
        self.repeat_count = repeat
        self.interval = interval

    def make_ping(self) -> Answer:
        timestamps = []
        address = None

        for i in range(self.repeat_count):
            timestamp, address = None, None
            response = sr1(self.packet, timeout=self.timeout, verbose=0)

            if response is not None:
                timestamp = to_milliseconds(
                    response.time - self.packet.sent_time
                )
                address = response.src

            timestamps.append(timestamp)
            time.sleep(self.interval)
        return address, timestamps
