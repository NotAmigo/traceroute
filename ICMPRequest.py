class ICMPRequest:
    def __init__(self, destination, id, sequence, payload, payload_size=56, ttl=64, traffic_class=0):
        self.destination = destination
        self.id = id & 0xFFFF
        self.sequence = sequence & 0xFFFF
        self.payload = payload
        self.payload_size = payload_size
        self.ttl = ttl
        self.traffic_class = traffic_class
        self.time = 0


class ICMPReply:
    def __init__(self, source, family, id, sequence, type, code, received, time):
        self.source = source
        self.family = family
        self.id = id
        self.sequence = sequence
        self.type = type
        self.code = code
        self.received = received
        self.time = time



