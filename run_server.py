import socketserver, socket, ssl
import json
from copy import deepcopy
from constants import *
import os
import functools as ft
from OpenSSL import crypto, SSL

from common import count_braces, receive_json, send_json

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

def no_server_ssl_creds():
    KEY_FILE = "server_privatekey.pem"
    CERT_FILE = "server_cert.pem"
    fnames = os.listdir()
    return not(
        ft.reduce(lambda a, b: a and b,
                  map(lambda x: x in fnames,
                      [KEY_FILE, CERT_FILE]),
                  True))
        

def generate_server_ssl_creds(
        emailAddress="emailAddress",
        commonName="commonName",
        countryName="NT",
        localityName="localityName",
        stateOrProvinceName="stateOrProvinceName",
        organizationName="organizationName",
        organizationUnitName="organizationUnitName",
        serialNumber=0,
        validityStartInSeconds=0,
        validityEndInSeconds=10*365*24*60*60,
        KEY_FILE = "server_privatekey.pem",
        # CERT_FILE="selfsigned.crt",
        CERT_FILE="server_cert.pem",):
    #can look at generated file using openssl:
    #openssl x509 -inform pem -in selfsigned.crt -noout -text
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = countryName
    cert.get_subject().ST = stateOrProvinceName
    cert.get_subject().L = localityName
    cert.get_subject().O = organizationName
    cert.get_subject().OU = organizationUnitName
    cert.get_subject().CN = commonName
    cert.get_subject().emailAddress = emailAddress
    cert.set_serial_number(serialNumber)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validityEndInSeconds)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')
    with open(CERT_FILE, "wt") as f:
        f.write(
            crypto.dump_certificate(
                crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(KEY_FILE, "wt") as f:
        f.write(
            crypto.dump_privatekey(
                crypto.FILETYPE_PEM, k).decode("utf-8"))

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

    test_server_data = {
        'handler': EchoJsonTCPHandler,
        'address': ('localhost', PORT),
    }
    
    if no_server_ssl_creds():
        generate_server_ssl_creds()

    provide_server(
        test_server_data)
