import os
import signal
import socket
import struct
import sys
import time

ICMP_ECHOREPLY = 0  # Echo reply (per RFC792)
ICMP_ECHO = 8  # Echo request (per RFC792)
ICMP_MAX_RECV = 2048  # Max size of incoming buffer

MAX_SLEEP = 1000


class MyStats:
    this_IP = "0.0.0.0"
    packets_sent = 0
    packets_received = 0
    minTime = 999999999
    maxTime = 0
    totTime = 0
    fracLoss = 1.0


myStats = MyStats  # Used globally


def checksum(source_string: bytes) -> int:
    """
    A port of the functionality of in_cksum() from ping.c
    Ideally this would act on the string as a series of 16-bit ints (host
    packed), but this works.
    Network data is big-endian, hosts are typically little-endian
    """
    countTo = int(len(source_string) / 2) * 2
    sum = 0
    count = 0

    # Handle bytes in pairs (decoding as short ints)
    while count < countTo:
        if sys.byteorder == "little":
            loByte = source_string[count]
            hiByte = source_string[count + 1]
        else:
            loByte = source_string[count + 1]
            hiByte = source_string[count]
        sum = sum + (hiByte * 256 + loByte)
        count += 2

    # Handle last byte if applicable (odd-number of bytes)
    # Endianness should be irrelevant in this case
    if countTo < len(source_string):  # Check for odd length
        loByte = source_string[len(source_string) - 1]
        sum += loByte

    sum &= 0xffffffff  # Truncate sum to 32 bits (a variance from ping.c, which
    # uses signed ints, but overflow is unlikely in ping)
    sum = (sum >> 16) + (sum & 0xffff)  # Add high 16 bits to low 16 bits
    sum += (sum >> 16)  # Add carry from above (if any)
    answer = ~sum & 0xffff  # Invert and truncate to 16 bits
    answer = socket.htons(answer)

    return answer


def do_one(destIP, timeout, mySeqNumber, numDataBytes):
    """
    Returns either the delay (in ms) or None on timeout.
    """
    global myStats

    delay = None

    try:  # One could use UDP here, but it's obscure
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                 socket.getprotobyname("icmp"))
        mySocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 10)
    except socket.error as e:
        # if errno == 1:
        #     # Operation not permitted - Add more information to traceback
        #     etype, evalue, etb = sys.exc_info()
        #     evalue = etype(
        #         "%s - Note that ICMP messages can only be sent from processes running as root." % evalue
        #     )
        #     raise etype, evalue, etb
        #
        print(f"failed. (socket error: '{e}')")
        raise  # raise the original error

    my_ID = os.getpid() & 0xFFFF

    sentTime = send_one_ping(mySocket, destIP, my_ID, mySeqNumber,
                             numDataBytes)
    if sentTime == None:
        mySocket.close()
        return delay

    myStats.packets_sent += 1

    recvTime, dataSize, iphSrcIP, icmpSeqNumber, iphTTL = receive_one_ping(
        mySocket, my_ID, timeout)

    mySocket.close()

    if recvTime:
        delay = (recvTime - sentTime) * 1000
        print(f"{dataSize} bytes from %s: icmp_seq={icmpSeqNumber} ttl={iphTTL} time={destIP} ms" % (
            socket.inet_ntoa(struct.pack("!I", iphSrcIP)))
              )
        myStats.packets_received += 1
        myStats.totTime += delay
        if myStats.minTime > delay:
            myStats.minTime = delay
        if myStats.maxTime < delay:
            myStats.maxTime = delay
    else:
        delay = None
        print("Request timed out.")

    return delay


def send_one_ping(mySocket, destIP, myID, mySeqNumber, numDataBytes):
    """
    Send one ping to the given >destIP<.
    """
    destIP = socket.gethostbyname(destIP)

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0

    # Make a dummy heder with a 0 checksum.
    header = struct.pack(
        "!BBHHH", ICMP_ECHO, 0, myChecksum, myID, mySeqNumber
    )

    padBytes = []
    startVal = 0x42
    for i in range(startVal, startVal + (numDataBytes)):
        padBytes += [(i & 0xff)]  # Keep chars in the 0-255 range
    data = bytes(padBytes)

    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)  # Checksum is in network order

    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack(
        "!BBHHH", ICMP_ECHO, 0, myChecksum, myID, mySeqNumber
    )

    packet = header + data

    sendTime = time.time()

    try:
        # socket send with ttl 1
        # mySocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', 1))
        mySocket.sendto(packet,
                        (destIP, 1))  # Port number is irrelevant for ICMP
    except socket.error as e:
        print(f"General failure ({e.args[1]})")
        return

    return sendTime


def receive_one_ping(mySocket, myID, timeout):
    """
    Receive the ping from the socket. Timeout = in ms
    """
    timeLeft = timeout / 1000

    while True:  # Loop while waiting for packet or timeout
        # startedSelect = time.time()
        # whatReady = select.select([mySocket], [], [], timeLeft)
        # howLongInSelect = (time.time() - startedSelect)
        # if whatReady[0] == []:  # Timeout
        #     return None, 0, 0, 0, 0

        timeReceived = time.time()

        recPacket, addr = mySocket.recvfrom(ICMP_MAX_RECV)
        ipHeader = recPacket[:20]
        iphVersion, iphTypeOfSvc, iphLength, \
        iphID, iphFlags, iphTTL, iphProtocol, \
        iphChecksum, iphSrcIP, iphDestIP = struct.unpack(
            "!BBHHHBBHII", ipHeader
        )

        icmpHeader = recPacket[20:28]
        icmpType, icmpCode, icmpChecksum, \
        icmpPacketID, icmpSeqNumber = struct.unpack(
            "!BBHHH", icmpHeader
        )

        dataSize = len(recPacket) - 28
        return timeReceived, dataSize, iphSrcIP, icmpSeqNumber, iphTTL

        if icmpPacketID == myID:  # Our packet
            dataSize = len(recPacket) - 28
            return timeReceived, dataSize, iphSrcIP, icmpSeqNumber, iphTTL

        # timeLeft = timeLeft - howLongInSelect
        # if timeLeft <= 0:
        #     return None, 0, 0, 0, 0


def dump_stats():
    """
    Show stats when pings are done
    """
    global myStats

    print(f"\n----{myStats.this_IP} PYTHON PING Statistics----")

    if myStats.packets_sent > 0:
        myStats.fracLoss = (
                                       myStats.packets_sent - myStats.packets_received) / myStats.packets_sent

    print(
        "%d packets transmitted, %d packets received, %0.1f%% packet loss" % (
            myStats.packets_sent, myStats.packets_received,
            100.0 * myStats.fracLoss
        ))

    if myStats.packets_received > 0:
        print("round-trip (ms)  min/avg/max = %d/%0.1f/%d" % (
            myStats.minTime, myStats.totTime / myStats.packets_received,
            myStats.maxTime
        ))

    print()
    return


def signal_handler(signum, frame):
    """
    Handle exit via signals
    """
    dump_stats()
    print(f"\n(Terminated with signal {signum})\n")
    sys.exit(0)


def verbose_ping(hostname, timeout=1000, count=1, num_data_bytes=55):
    """
    Send >count< ping to >destIP< with the given >timeout< and display
    the result.
    """
    global myStats

    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl-C
    if hasattr(signal, "SIGBREAK"):
        # Handle Ctrl-Break e.g. under Windows
        signal.signal(signal.SIGBREAK, signal_handler)

    myStats = MyStats()  # Reset the stats

    mySeqNumber = 0  # Starting value

    try:
        destIP = socket.gethostbyname(hostname)
        print(
            f"\nPYTHON-PING {hostname} ({destIP}): {num_data_bytes} data bytes")
    except socket.gaierror as e:
        print(f"\nPYTHON-PING: Unknown host: {hostname} ({e.args[1]})")
        print()
        return

    myStats.this_IP = destIP

    for i in range(count):
        delay = do_one(destIP, timeout, mySeqNumber, num_data_bytes)

        if delay is None:
            delay = 0

        mySeqNumber += 1

        # Pause for the remainder of the MAX_SLEEP period (if applicable)
        if MAX_SLEEP > delay:
            time.sleep((MAX_SLEEP - delay) / 1000)

    dump_stats()


if __name__ == '__main__':
    # These should work:
    # verbose_ping("heise.de")
    verbose_ping("google.com")

    # Inconsistent on Windows w/ ActivePython (Python 3.2 resolves correctly
    # to the local host, but 2.7 tries to resolve to the local *gateway*)
    # verbose_ping("localhost")

    # Should fail with 'getaddrinfo failed':
    # verbose_ping("foobar_url.foobar")

    # Should fail (timeout), but it depends on the local network:
    # verbose_ping("192.168.255.254")

    # Should fails with 'The requested address is not valid in its context':
    # verbose_ping("0.0.0.0")
