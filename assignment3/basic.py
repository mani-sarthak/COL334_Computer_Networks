import socket
import re
import time
import select
server_address = ('127.0.0.1', 9803)  # Replace with your server's address and port
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
print('requests to send :', requests)
d = dict()
i = 0
timeout = 0.01



def removeHeaders(data):
    pattern = r"Offset:\s+(\d+)\s+NumBytes:\s+(\d+)\s+(.*)"
    match = re.search(pattern, data)

    if match:
        body = match.group(3)
        return body+'\n'
    else:
        return "\n"
while (len(d) != requests):
    i = i % requests
    offset = arr[i][0]
    size = arr[i][1]
    message = f'Offset: {offset}\nNumBytes: {size}\n\n'
    if size > 0:
        try:
            sock.sendto(message.encode(), server_address)
            start_time = time.time()
            readable, _, _ = select.select([sock], [], [], timeout)
            if not readable:
                print('skipped', offset, size)
            else:
                data, server = sock.recvfrom(2096)
                data = data.decode()
                # print('\n\n\n\n', data, '\n\n\n\n')
                # print('fetched', offset, size)
                d[i] = removeHeaders(data)
                arr[i][1] = 0
        except:
            print()
        
        time.sleep(timeout)
        print(len(d), i)
        i += 1
    
print(d)
ans = ""
for i in range(requests):
    ans += d[i]



def writeToFile(data, file):
    with open(file, 'w') as f:
        f.write(data)
    f.close()
    return 

writeToFile(ans, 'output.txt')