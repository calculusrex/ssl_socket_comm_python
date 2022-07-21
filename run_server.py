import socketserver, socket, ssl
import json
from copy import deepcopy
from constants import *
import os
import functools as ft
from OpenSSL import crypto, SSL

from common import receive_json, send_json, generate_ssl_creds

class EchoJsonTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """    
    def handle(self):
        # self.request is the TCP socket connected to the client

        self.data = receive_json(self.request)

        print("{} wrote:".format(self.client_address[0]))
        print(self.data)

        send_json(
            self.request, self.data)

# class EchoJsonTCPHandler(socketserver.StreamRequestHandler):
#     def handle(self):
#         # self.rfile is a file-like object created by the handler;
#         # we can now use e.g. readline() instead of raw recv() calls
#         self.data = self.rfile.readline().strip()
#         data = json.loads(self.data)
#         serialized_json = json.dumps(data)
#         print("{} wrote:".format(self.client_address[0]))
#         print(self.data, '\n')
#         # Likewise, self.wfile is a file-like object used to write back to the client
#         self.wfile.write(
#             bytes(serialized_json + '\n',
#                   'utf8'))

def provide_server(server_data):
    print(f'SEVER PROVIDED ON: {server_data}', '\n')
    with socketserver.TCPServer(
        server_data['address'],
        server_data['handler']) as server:
        context = ssl.SSLContext()
        context.load_cert_chain(
            'server_cert.pem', keyfile='server_privatekey.pem')
        server.socket = context.wrap_socket(
            server.socket,
            server_hostname='calculusrex')

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

if __name__ == '__main__':
    print('run_server.py', '\n')

    # test_server_data = {
    #     'handler': EchoJsonTCPHandler,
    #     'address': ('localhost', PORT),
    # }

    test_server_data = {
        'handler': EchoJsonTCPHandler,
        'address': (socket.gethostname(),
                    PORT),
    }
    
    generate_ssl_creds('server')

    provide_server(
        test_server_data)
