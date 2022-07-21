import json

def receive_metadata(sock):
    chunks = []
    while not(
            is_metadata_message_finished(
                chunks[-1])):
        chunk = sock.request.recv(1024)
        chunks.append(chunk)
    chunks[-1] = chunks[-1].strip()

    json_string = "".join(
        map(lambda bts: str(bts, 'utf8'),
            chunks))
    metadata = json.loads(
        json_string)
    return metadata

# def is_metadata_message_finished(chunk):
#     str(chunk, 'utf8')

def count_braces(brace_count, json_fragment):
    # print('initial brace count:', brace_count)
    open_brace_count = len(list(
        filter(lambda c: c == '{',
               json_fragment)))

    close_brace_count = len(list(
        filter(lambda c: c == '}',
               json_fragment)))

    curr_count = brace_count + open_brace_count - close_brace_count
    # print('current brace count:', curr_count)
    return curr_count

def receive_json(sock, chunk_size=1024):
    chunks = []
    chunks.append(
        sock.recv(chunk_size))
    brace_count = count_braces(
        0, str(chunks[0], 'utf8'))
    while brace_count > 0:
        chunk = sock.recv(chunk_size)
        # print('chunk')
        # print(chunk, '\n')
        chunks.append(chunk)
        brace_count = count_braces(
            brace_count,
            str(chunk, 'utf8'))
    chunks[-1] = chunks[-1].strip()

    json_string = "".join(
        map(lambda bts: str(bts, 'utf8'),
            chunks))
    data = json.loads(
        json_string)
    return data

def send_json(sock, data):
    json_string = json.dumps(data)
    data_bytes = bytes(
        json_string,
        'utf8')
    sock.sendall(data_bytes)
