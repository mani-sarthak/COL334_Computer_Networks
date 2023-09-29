import socket
import re
import time

server_address = ('127.0.0.1', 9802)  # Replace with your server's address and port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



def getSize(data):
    match = re.search(r'Size:\s+(\d+)', data)
    return int(match.group(1))
    
try:
    # Send data to the server
    message = 'SendSize\n\n'  # Your message here
    sock.sendto(message.encode(), server_address)

    # Receive a response from the server (optional)
    data, server = sock.recvfrom(2096)
    data = data.decode()
    # print(data)
    size = getSize(data)
    print(size)
    # print(server)

finally:
    # Clean up the socket
    print('Done')



offset = 0
maxSize = 1400 ## 1448 could be max just to be on safer side
arr = [(x, min(x+maxSize, size)-x) for x in range(0, size, maxSize)]
# print(arr)

requests = len(arr)
d = dict()
i = 0
while (len(d) != requests):
    i = i % requests
    offset = arr[i][0]
    size = arr[i][1]
    message = f'Offset: {offset}\nNumBytes: {size}\n\n'
    if size > 0:
        try:
            sock.sendto(message.encode(), server_address)
            data, server = sock.recvfrom(2096)
            data = data.decode()
            print('\n\n\n\n', data, '\n\n\n\n')
            d[i] = data
            arr[i][1] = 0
        except:
            print('cant fetch data', offset, size)
        
    time.sleep(5)
    print(len(d))
    i += 1
    
print(d)