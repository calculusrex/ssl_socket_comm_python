import socketserver, socket, ssl
import json
from constants import *
from OpenSSL import crypto, SSL
import os
import functools as ft

from common import receive_json, send_json

def no_client_ssl_creds():
    KEY_FILE = "client_privatekey.pem"
    CERT_FILE = "client_cert.pem"
    fnames = os.listdir()
    return not(
        ft.reduce(lambda a, b: a and b,
                  map(lambda x: x in fnames,
                      [KEY_FILE, CERT_FILE]),
                  True))

def generate_client_ssl_creds(
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
        KEY_FILE = "client_privatekey.pem",
        # CERT_FILE="selfsigned.crt",
        CERT_FILE="client_cert.pem",):
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

def new_sock():
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)

    context = ssl.SSLContext()
    context.load_cert_chain(
        'client_cert.pem', keyfile='client_privatekey.pem')
    ssock = context.wrap_socket(
        sock, server_hostname='calculusrex')
    return ssock

def request(address, data):
    if no_client_ssl_creds():
        generate_client_ssl_creds()

    with new_sock() as sock:
        # Connect to server and send data
        sock.connect(
            address)
        send_json(sock, data)

        response = receive_json(sock)
        # print(f"Sent:     {data}")
        # print(f"Response: {response}")
        sock.close()
    return response

# def request(address, data):
#     if no_client_ssl_creds():
#         generate_client_ssl_creds()

#     response_data = {}
#     serialized_json = json.dumps(data)
#     with new_sock() as sock:
#         # Connect to server and send data

#         sock.connect(
#             address)

#         bytes_data = bytes(
#              json.dumps(data) + '\n',
#             'utf-8')
#         sock.sendall(bytes_data)

#         # Receive data from the server and shut down
#         received = str(
#             sock.recv(1024), "utf-8")
#         response_data = json.loads(received)

#     return response_data

if __name__ == '__main__':
    print('client.py', '\n')

    test_data = {
        'key': 'val',
        'list': list(range(10)),
    }

    with open('json_sample.json', 'r') as f:
        test_data_2 = json.load(f)
    
    test_address = ('localhost', PORT)

    # response = request(
    #     test_address, test_data)
