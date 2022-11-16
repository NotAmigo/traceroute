from scapy.all import *
from scapy.layers.inet import IP, UDP, ICMP
import time

hostname = "8.8.8.8"


def ping(host, repeat=3, ttl=5):
    packet = IP(dst=host, ttl=ttl) / ICMP(id=1)/"XXXXXX"
    responses = []
    for x in range(repeat):
        response = sr1(packet, timeout=3, verbose=0)
        # response.show2()
        if response:
            responses.append(response)
            break
    return responses


for i in range(1, 30):
    replies = ping(hostname, 3, i)
    if not replies:
        print(f"{i} Превышен интервал ожидания запроса")
        continue
    elif replies[0].src == hostname:
        print(f"{i} Done!", replies[0].src)
        break
    else:
        print(f"{i} hops away: ", replies[0].src)
