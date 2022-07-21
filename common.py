import os
import json
import re
from json_upgrade import json_dumps, json_loads
import functools as ft
import socket, ssl
from OpenSSL import crypto, SSL


def generate_ssl_creds__(
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
        KEY_FILE = "privatekey.pem",
        # CERT_FILE="selfsigned.crt",
        CERT_FILE="cert.pem",):
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

def no_ssl_creds(creds_prefix):
    KEY_FILE = f"{creds_prefix}_privatekey.pem"
    CERT_FILE = f"{creds_prefix}_cert.pem"
    fnames = os.listdir()
    return not(
        ft.reduce(lambda a, b: a and b,
                  map(lambda x: x in fnames,
                      [KEY_FILE, CERT_FILE]),
                  True))

def generate_ssl_creds(creds_prefix):
    if no_ssl_creds(creds_prefix):
        generate_ssl_creds__(
            KEY_FILE = f"{creds_prefix}_privatekey.pem",
            CERT_FILE=f"{creds_prefix}_cert.pem")

def new_sock(creds_prefix):
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)

    context = ssl.SSLContext()
    context.load_cert_chain(
        f'{creds_prefix}_cert.pem',
        keyfile=f'{creds_prefix}_privatekey.pem')
    ssock = context.wrap_socket(
        sock, server_hostname='calculusrex')
    return ssock

def count_braces__regex(prev_brace_cnt, json_fragment):
    open_brace_p = re.compile('{')
    close_brace_p = re.compile('}')
    open_cnt = len(
        open_brace_p.findall(
            json_fragment))
    close_cnt = len(
        close_brace_p.findall(
            json_fragment))
    curr_cnt = prev_brace_cnt + open_cnt - close_cnt
    return curr_cnt

def count_braces__functional(prev_brace_count, json_fragment):
    # print('initial brace count:', brace_count)
    open_count = len(list(
        filter(lambda c: c == '{',
               json_fragment)))
    close_count = len(list(
        filter(lambda c: c == '}',
               json_fragment)))
    curr_count = prev_brace_count + open_count - close_count
    # print('current brace count:', curr_count)
    return curr_count

def receive_json(conn, chunk_size=1024):
    chunks = []
    chunks.append(
        conn.recv(chunk_size))
    brace_count = count_braces__regex(
        0, str(chunks[0], 'utf8'))
    while brace_count > 0:
        chunk = conn.recv(chunk_size)
        # print('chunk')
        # print(chunk, '\n')
        chunks.append(chunk)
        brace_count = count_braces__regex(
            brace_count,
            str(chunk, 'utf8'))
    chunks[-1] = chunks[-1].strip()
    json_string = "".join(
        map(lambda bts: str(bts, 'utf8'),
            chunks))
    data = json_loads(
        json_string)
    return data

def send_json(conn, data):
    json_string = json_dumps(data)
    data_bytes = bytes(
        json_string,
        'utf8')
    conn.sendall(data_bytes)
