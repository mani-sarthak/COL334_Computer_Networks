import socket

server_address = ('vayu.iitd.ac.in', 9801)  # Replace with your server's address and port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    # Send data to the server
    message = 'SENDLINE\n'  # Your message here
    sock.sendto(message.encode(), server_address)

    # Receive a response from the server (optional)
    data, server = sock.recvfrom(4096)
    print(f'Received: {data.decode()}')
    print(server)

finally:
    # Clean up the socket
    sock.close()
