import socket
import sys
import time
import random

from ethernet import *

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler(sys.stdout)
c_handler.setLevel(logging.DEBUG)
logger.addHandler(c_handler)


class Station:
    def __init__(self, port, message):
        self.port = port
        self.all_bytes = []
        self.address_src = bytes(6)
        self.address_dst = bytes(6)
        self.message = message
        self.frame = Frame(self.address_src, self.address_dst, STANDARD_TYPE, self.message)
        self.packet = self.frame.get_packet()
        self.packet_pos = 0
        self.attemp = 0
        self.collision_counter = 0
        self.jam_counter = 0
        self.sending_data = False
        self.reading_data = False
        self.reading_counter = 0
        self.max_attemp = 16
        self.sent = False

    def next_packet_byte(self):
        pb = self.packet[self.packet_pos: self.packet_pos + 1]
        self.packet_pos += 1
        return pb

    def add_byte(self, b):
        self.all_bytes.append(b)
        if len(self.all_bytes) > 5000:
            self.all_bytes.pop(0)
    
    def get_bytes(self):
        return self.all_bytes

    def check_idle(self):
        last12 = b''.join(self.all_bytes[-12:])
        return last12 == IPG

    def collision_wait(self):
        return self.collision_counter != 0 or self.jam_counter != 0

    def check_preamble(self):
        last8 = b''.join(self.all_bytes[-8:])
        return last8 == PREAMBLE

    def read_byte(self):
        data = self.client_socket.recv(1)
        if data == b'':
            raise RuntimeError('connection is lost')
        return data

    def run_client(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((socket.gethostname(), self.port))
        try:
            while True:
                if self.jam_counter != 0:
                    self.jam_counter -= 1
                    self.client_socket.send(GAP_BYTE)
                    data = self.read_byte()
                if self.collision_counter != 0:
                    self.collision_counter -= 1
                if not self.sending_data and not self.reading_data:
                    logger.info('status: waiting')
                    data = self.read_byte()
                    logger.info('signal: ' + str(data))
                    self.add_byte(data)
                    if self.check_idle() and not self.collision_wait() and not self.sent:
                        self.sending_data = True
                    if self.check_preamble():
                        self.reading_data = True
                        self.reading_counter = 8
                elif self.sending_data:
                    logger.info('status: sending data')
                    f_byte = self.next_packet_byte()
                    if f_byte == b'':
                        logger.info('frame has been sent')
                        self.sending_data = False
                        self.sent = True
                    else:
                        self.client_socket.send(f_byte)
                        data = self.read_byte()
                        self.add_byte(data)
                        if data != f_byte:
                            logger.info(f'collision {self.attemp + 1}')
                            self.sending_data = False
                            upper = (2 ** min(10, self.attemp + 1))
                            n_steps = random.randint(0, upper - 1)
                            self.collision_counter = n_steps * 64
                            logger.info(f'collision {self.attemp + 1}, wait for {self.collision_counter} steps')
                            self.attemp += 1
                            self.jam_counter = 4
                            if self.attemp >= self.max_attemp:
                                raise RuntimeError('attemps exceeded')
                elif self.reading_data:
                    logger.info('status: reading data')
                    data = self.read_byte()
                    logger.info('signal: ' + str(data))
                    self.add_byte(data)
                    self.reading_counter += 1
                    if self.check_idle():
                        self.reading_data = False
                        data = self.get_bytes()[-self.reading_counter:]
                        data = b''.join(data)
                        try:
                            frame = parse_frame(data)
                            logger.info('successful read of a frame')
                            logger.info('message: ' + frame.message.decode('utf-8'))
                        except ValueError as e:
                            logger.info('frame corrupted: ' + str(e))
                            logger.info(f'bytes: {data}')

        except Exception as e:
            logger.info('terminated on: ' + str(e))
        except KeyboardInterrupt:
            logger.info('terminated by user')


if __name__ == '__main__':
    port = int(sys.argv[1])
    message = sys.argv[2].encode('utf-8')
    s = Station(3000, message)
    s.run_client()