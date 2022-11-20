# Дополнительная часть:
# Поддержка IPv6.
# Разрешать хопы в DNS-имя.
# debug-режим.
import click
from icmp_packet import ICMPPacket
from tcp_packet import TCPPacket
from traceroute import Traceroute

hostname = "8.8.8.8"
NETWORK_ROUTER_ADMIN_LOGIN = '192.168.1.120'


@click.command()
@click.option('--type', prompt='Type TCP or ICMP',
              help='Choose, ICMP or TCP traceroute')
@click.option('--destination', prompt='Traceroute to',
              help='Destination IP address')
@click.option('--source', default=NETWORK_ROUTER_ADMIN_LOGIN,
              help='Source IP address')
@click.option('--id', default=0, help='Custom id')
@click.option('--seq', default=0, help='Custom SEQ')
@click.option('--len', default=40, help='Length of the ICMP packet. '
                                        'If you type custom, payload, length '
                                        'will be ignored, length ignored for '
                                        'TCP')
@click.option('--payload', default=None, help='Custom ICMP packet payload')
@click.option('--tcp_port', default=80, help='Custom TCP destination port')
@click.option('--max_ttl', default=30, help='Max TTL')
@click.option('--repeat', default=3, help='Requests per TTL')
@click.option('--timeout', default=3, help='Timeout for each request')
@click.option('--interval', default=0, help='Interval between requests')
@click.option('--debug', is_flag=True, help='Debug mode')
def main(type, destination, source, id, seq, len, payload, tcp_port, max_ttl, repeat, timeout, interval, debug):
    if type == 'ICMP':
        packet = ICMPPacket(destination, id, seq, source, len, payload)
    elif type == 'TCP':
        packet = TCPPacket(destination, id, seq, source, tcp_port)
    else:
        print('Wrong type')
        return
    traceroute = Traceroute(destination, packet, max_ttl,
                            repeat, timeout, interval, debug)
    traceroute.run()


if __name__ == '__main__':
    main()
