import socket
import time
import re
import hashlib
import concurrent.futures

# Server address and port
server_address = ('127.0.0.1', 9801)

# Constants
PACKET_SIZE = 1400
SSTHRESHOLD = 16
TIMEOUT = 0.01
FACTOR = 0.8
NUM_THREADS = 10  # Adjust the number of parallel threads as needed
MAX_RETRIES = 3  # Max number of retries for timeout

def getSize():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Send data to the server
        message = 'SendSize\nReset\n\n'  # Your message here
        sock.sendto(message.encode(), server_address)

        # Receive a response from the server (optional)
        data, server = sock.recvfrom(2096)
        data = data.decode()
        # print(data)
        size = int(re.search(r'Size:\s+(\d+)', data).group(1))
        print(size)
        # print(server)

    finally:
        # Clean up the socket
        print('Done')
        sock.close()
    return size

def send_request(offset, size, client_socket):
    request = f"Offset: {offset}\nNumBytes: {size}\n\n"
    retries = 0
    while retries < MAX_RETRIES:
        try:
            client_socket.sendto(request.encode(), server_address)
            data, _ = client_socket.recvfrom(PACKET_SIZE + 1000)
            return offset, size, data
        except socket.timeout:
            print(f"Timeout for Offset {offset}, Retrying...")
            retries += 1
    return offset, size, None

def receive_file():
    start = time.time()
    file_size = getSize()
    cwnd = 1
    timeout = TIMEOUT

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)

    received_data = dict()
    num_requests = file_size // PACKET_SIZE + 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        while len(received_data) < num_requests:
            tasks = []
            for i in range(cwnd):
                idx = len(received_data) % num_requests
                offset = idx * PACKET_SIZE
                size = min(PACKET_SIZE, file_size - offset)
                tasks.append(executor.submit(send_request, offset, size, client_socket))

            cnt = 0
            for future in concurrent.futures.as_completed(tasks):
                offset, size, data = future.result()
                if data is not None:
                    cnt += 1
                    data = data.decode()
                    if data.startswith("Offset:"):
                        offset = int(re.search(r'Offset:\s+(\d+)', data).group(1))
                        received_data[offset] = data.split("\n\n", 1)[1]

            if cnt < cwnd * FACTOR:
                cwnd = max(1, cwnd // 2)
            else:
                cwnd = min(SSTHRESHOLD, cwnd + 1)

    ans = "".join(received_data[offset] for offset in sorted(received_data.keys()))

    md5_hash = hashlib.md5()
    md5_hash.update(ans.encode())
    md5_hex = md5_hash.hexdigest()
    submit_command = f'Submit: cs1210552@bots\nMD5: {md5_hex}\n\n'
    client_socket.sendto(submit_command.encode(), server_address)
    data, server = client_socket.recvfrom(2096)
    data = data.decode()
    print(data)
    client_socket.close()

    print("File received and saved.")
    finish = time.time()
    print(finish - start)

if __name__ == "__main__":
    receive_file()
