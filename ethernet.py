from zlib import crc32

GAP_BYTE = (0b10101010).to_bytes(1, 'big')
START_BYTE = (0b10101011).to_bytes(1, 'big')
STANDARD_TYPE = (0b11111111).to_bytes(2, 'big')
PREAMBLE = b''.join([GAP_BYTE for i in range(7)]) + START_BYTE
IPG = b''.join([GAP_BYTE for i in range(12)])


class Frame:
    def __init__(self, address_dst, address_src, etype, message):
        self.address_dst = address_dst
        self.address_src = address_src
        self.message = message
        self.etype = etype
        self.frame = self.address_dst + self.address_src + self.etype + self.message
        self.crc = crc32(self.frame).to_bytes(4, 'big')

    def get_packet(self):
        return PREAMBLE + self.frame + self.crc + IPG


def parse_frame(raw_bytes):
    preamble = raw_bytes[:8]
    dst = raw_bytes[8:14]
    src = raw_bytes[14:20]
    etype = raw_bytes[20:22]
    message = raw_bytes[22:-16]
    crc = raw_bytes[-16:-12]
    ipg = raw_bytes[-12:]
    frame = dst + src + etype + message
    if preamble != PREAMBLE:
        raise ValueError('wrong preamble')
    if ipg != IPG:
        raise ValueError('wrong ipg')
    crc_check = crc32(frame).to_bytes(4, 'big')
    if crc != crc_check:
        raise ValueError('wrong crc')
    return Frame(dst, src, etype, message)