class Packet:
    def __init__(self, dst: str, session_id: int, seq: int, src: str):
        self.id = session_id
        self.seq = seq
        self.dst = dst
        self.src = src

    def get_packet(self, ttl: int):
        raise NotImplementedError
