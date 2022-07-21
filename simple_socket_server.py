# import sys
import socket, ssl, selectors
from pprint import pprint

from constants import PORT
from common import generate_ssl_creds, new_sock, receive_json, send_json, local_ip




def run_sg_conn_server():
    address = (local_ip(), PORT)
    generate_ssl_creds('simple_socket_server')
    with new_sock('simple_socket_server') as s:
        s.bind(address)
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            data = receive_json(conn)
            pprint(data)
            send_json(conn, data)
            conn.close()


if __name__ == '__main__':
    print('simple_socket_server.py')

    # address = ('192.168.100.176', PORT)
    # address = (
    #     socket.gethostname(),
    #     PORT
    # )
    
    # generate_ssl_creds('simple_socket_server')

    # serversocket = socket.socket(
    #     socket.AF_INET, socket.SOCK_STREAM)
    # serversocket.bind(address)
    # serversocket.listen(5)
    # while True:
    #     (clientsocket, address) = serversocket.accept()
    #     ct = client_thread(
    #         clientsocket)
    #     ct.run()

    # with new_sock('simple_socket_server') as s:
    #     s.bind(address)
    #     s.listen()
    #     conn, addr = s.accept()
    #     with conn:
    #         print(f"Connected by {addr}")
    #         while True:
    #             data = conn.recv(1024)
    #             print(data, '\n')
    #             if not data:
    #                 break
    #             conn.sendall(data)

    # If you’re getting requests from clients that initiate CPU bound work, look at the concurrent.futures module. It contains the class ProcessPoolExecutor, which uses a pool of processes to execute calls asynchronously.

    # with new_sock('simple_socket_server') as s:
    #     s.bind(address)
    #     s.listen()
    #     conn, addr = s.accept()
    #     with conn:
    #         print(f"Connected by {addr}")
    #         data = receive_json(conn)
    #         pprint(data)
    #         send_json(conn, data)
    #         conn.close()

    run_sg_conn_server()
