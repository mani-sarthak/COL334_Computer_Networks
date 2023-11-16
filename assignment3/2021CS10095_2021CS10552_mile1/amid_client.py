import socket
import hashlib
import time
import re
# Server address and port
server_address =  ('127.0.0.1', 9801)


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
    # Initialize variables
    start=time.time()
    offset = 0
    packet_size = 1448  # Initial packet size
    file_size = getSize()  # Get the target file size
    cwnd = 1
    ssthresh = 16  # Set the threshold value
    timeout = 0.016 # Initial timeout value
    max_retransmissions = 40

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)  # Set a timeout for receiving ACKs

    # Create a buffer to store received data
    buffer = bytearray(file_size)

    # Create a hash object for data verification

    while offset < file_size:
        # Send a request to the server with the current offset and packet size
        request = f"Offset: {offset}\nNumBytes: {packet_size}\n\n"
        client_socket.sendto(request.encode(), server_address)
        print(request)
        print('message sent')

        # Start the timer
        start_time = time.time()
        retransmissions = 0

        while True:
            try:
                data, addr = client_socket.recvfrom(packet_size+1000)

                # Extract and remove the header from the received data
                header, data = data.split(b'\n\n', 1)
                offset += len(data)
                cwnd += 1

                # Write the received data into the buffer
                buffer[offset - len(data):offset] = data

                # Check if the entire file is fetched
                # print(len(buffer))
                print('fetched', offset)
                print('data recieved')
                if offset >= file_size:
                    break

                if cwnd >= ssthresh:
                    # Multiplicative Decrease (congestion avoidance)
                    cwnd = max(1, cwnd // 2)
                else:
                    # Additive Increase (slow start)
                    cwnd += 1

                break
            except socket.timeout:
                retransmissions += 1
                if retransmissions > max_retransmissions:
                    # Too many retransmissions, abort and handle the error
                    print("Max retransmissions reached. Aborting.")
                    break

                # Timeout occurred, retransmit the request
                client_socket.sendto(request.encode(), server_address)

            if time.time() - start_time > timeout:
                # Timeout occurred, double timeout
                cwnd = 1
                ssthresh = max(cwnd // 2, 1)
                # packet_size = 1448  # Reduce the packet size
                timeout *= 2

    # Close the UDP socket

    # Send the received data to a file
    with open('received_file.txt', 'wb') as f:
        f.write(buffer[:file_size])
    md5_hash = hashlib.md5()
    md5_hash.update(buffer[:file_size])
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