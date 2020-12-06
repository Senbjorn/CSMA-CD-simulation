import socket
import sys
import time

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler(sys.stdout)
c_handler.setLevel(logging.DEBUG)
logger.addHandler(c_handler)


def run_client():
    server_port = 3001
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((socket.gethostname(), server_port))
    time.sleep(3)

    while True:
        medium_idle = False
        
        logger.info('send data')
        client_socket.send(b'a')
        data = client_socket.recv(1)
        if len(data) != b'a':
            logger.info('collision')
            # send jam signal
            # wait random time
        logger.info('response:' + str(data))


if __name__ == '__main__':
    run_client()