import socket
from select import select
import sys
import time
import random
from ethernet import GAP_BYTE

import logging
from multiprocessing import Process, Manager, Queue

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler(sys.stdout)
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


def select_process(conn_q, sim_time):
    connections = {}
    while True:
        # add new connections
        while not conn_q.empty():
            sock, addr = conn_q.get()
            connections[addr] = sock
        

        byte_list = []
        pop_list = []
        for conn in connections:
            sock = connections[conn]
            try:
                data = sock.recv(1)
                if data == b'':
                    pop_list.append(conn)
                else:
                    byte_list.append(data)
            except Exception as e:
                pass
                # logger.info(f'recv error at {conn}: ' + str(e))
        for conn in pop_list:
            connections.pop(conn, None)

        
        if len(byte_list) > 1:
            data = random.randint(0, 2 ** 8 - 1).to_bytes(1, 'big')
        elif len(byte_list) == 1:
            data = byte_list[0]
        else:
            data = GAP_BYTE


        pop_list = []
        for conn in connections:
            sock = connections[conn]
            try:
                sock.send(data)
            except BrokenPipeError:
                pop_list.append(conn)
        for conn in pop_list:
            connections.pop(conn, None)
        time.sleep(sim_time)

            
            
        


def run_server(port, sim_time):
    logger.info('get server socket')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_host = socket.gethostname()
    server_port = port
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)
    logger.info('connection was established: ' + str(server_socket.getsockname()))
    logger.info('proceed to mainloop')

    manager = Manager()
    conn_q = manager.Queue()
    sp = Process(target=select_process, args=(conn_q, sim_time), daemon=True)
    sp.start()
    try:
        while True:
            client_socket, address = server_socket.accept()
            client_socket.setblocking(False)
            conn_q.put((client_socket, address))
            logger.info('connection accepted: ' + str(address))
    except KeyboardInterrupt:
        logger.info('server was stopped')
    server_socket.shutdown(socket.SHUT_RDWR)
    server_socket.close()


if __name__ == '__main__':
    port = int(sys.argv[1])
    sim_time = float(sys.argv[2])
    run_server(port, sim_time)
