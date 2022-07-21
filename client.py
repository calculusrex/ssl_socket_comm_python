import socketserver, socket, ssl
import json
from constants import *
from OpenSSL import crypto, SSL
import os
import functools as ft
import numpy as np

from common import receive_json, send_json, generate_ssl_creds, new_sock, no_ssl_creds

def request(address, data):
    generate_ssl_creds('client')
    with new_sock('client') as sock:
        sock.connect(
            address)
        send_json(sock, data)
        response = receive_json(sock)
        sock.close()
    return response

if __name__ == '__main__':
    print('client.py', '\n')

    test_data = {
        'key': 'val',
        'list': list(range(10)),
        'arr': np.array(
            [[[np.random.randint(256) for _ in range(3)] for _ in range(256)] for _ in range(512)], dtype=np.uint8),
    }

    with open('json_sample.json', 'r') as f:
        test_data_2 = json.load(f)
    
    # test_address = ('localhost', PORT)
    test_address = (
        socket.gethostname(),
        PORT,
    )
    
    # response = request(
    #     test_address, test_data)
