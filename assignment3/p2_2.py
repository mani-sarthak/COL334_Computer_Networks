## self written code for aimd congestion control

import socket
import time
import re
import hashlib

# Server address and port
server_address = ('127.0.0.1', 9801)

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




def receive_file():
    start = time.time()
    packet_size = 1400  # Initial packet size
    file_size = getSize()  # Get the target file size
    cwnd = 1
    ssthresh = 16  # Set the threshold value
    timeout = 0.0035  # Initial timeout value
    factor = 0.8

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)  # Set a timeout for receiving ACKs

    # Create a dictionary to store received data
    received_data = dict()

    # Create an array to track offsets, packet sizes, and received status
    arr = [[x, min(x + packet_size, file_size) - x, True] for x in range(0, file_size, packet_size)]

    number_requests = len(arr)
    i = 0
    while (len(received_data) < number_requests):
        
        idx = i % number_requests
        offset = arr[idx][0]
        size = arr[idx][1]
        received = arr[idx][2]
        if received:
            client_socket.settimeout(timeout*cwnd)
            print("starting a section")
            for j in range(idx, idx + cwnd):
                j = j % number_requests
                offset = arr[j][0]
                size = arr[j][1]
                received = arr[j][2]
                request = f"Offset: {offset}\nNumBytes: {size}\n\n"
                client_socket.sendto(request.encode(), server_address)
                start_time = time.time() ############################
            cnt = 0
            while True:
                try:
                    data, server = client_socket.recvfrom(packet_size + 1000)
                    cnt += 1
                    data = data.decode()
                    # print(data)
                    if data.startswith("Offset:"):
                        offset = int(re.search(r'Offset:\s+(\d+)', data).group(1))
                        size = int(re.search(r'NumBytes:\s+(\d+)', data).group(1))
                        received_data[offset] = data.split("\n\n", 1)[1]
                        arr[offset // packet_size][2] = False
                        print(f"received {offset} {size}")
                        
                except socket.timeout:
                    print("timeout")
                    break
                except:
                    print("error")
                    break     
            if cnt  < cwnd * factor :
                cwnd = max(1, cwnd // 2) 
                # timeout *= 0.5  
            else :
                cwnd = min(ssthresh, cwnd + 1)
                # timeout *= 2

        
        i+=1

    # Send the received data to a file
    ans = ""
    with open('received_file.txt', 'wb') as f:
        for offset in sorted(received_data.keys()):
            f.write(received_data[offset].encode())
            ans += received_data[offset]
    
    # print(ans)
    md5_hash = hashlib.md5()
    md5_hash.update(ans.encode())
    md5_hex = md5_hash.hexdigest()
    print(md5_hex)
    submit_command = f'Submit: cs1210552@bots\nMD5: {md5_hex}\n\n'
    client_socket.sendto(submit_command.encode(), server_address)
    data, server = client_socket.recvfrom(2096)
    data = data.decode()
    print(data)
    
    client_socket.close()
    

    print("File received and saved.")
    finish=time.time()
    print(finish-start)
    
    
    
if __name__ == "__main__":
    receive_file()
