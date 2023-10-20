import socket
import re
import time
import hashlib
import matplotlib.pyplot as plt
# ('10.17.7.134', 9801)
timeout = 0.001 ## now consider same as RTT sinc ebursts are sent almost paralelly
server_address = ('127.0.0.1', 9801)  # Replace with your server's address and port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.05) ## just to be on safer side RTT is 1.2 times of timeout
cwnd = 3
d = dict()


def getSize(data):
    match = re.search(r'Size:\s+(\d+)', data)
    return int(match.group(1))
    
try:
    # Send data to the server
    message = 'SendSize\nReset\n\n'  # Your message here
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
maxSize = 1350 ## 1448 could be max just to be on safer side
arr = [[x, min(x+maxSize, size)-x, 1] for x in range(0, size, maxSize)]
time1 = [time.time()]
time2 = [time.time()]
cwnd_g = []
# print(size, len(arr))


ind = 0
def findI():
    global ind 
    global d
    j = 0
    while (j < len(arr) and len(d) < len(arr)):
        x = (ind + j) % len(arr)
        if (arr[x][2] == 1):
            ind = x + 1 
            return x
        j += 1
    print('all done theoratcally\nthis line should not be printed\n\n\n\n\n')
    
    
    
    
## send a burst of k size 
def send(k):
    cnt = []
    for i in range(k):
        ind = findI()
        if (ind == None):
            break
        offset = arr[ind][0]
        size = arr[ind][1]
        if offset in cnt:
            continue
        message = f'Offset: {offset}\nNumBytes: {size}\n\n'
        try:
            sock.sendto(message.encode(), server_address)
            # print('sent', ind)
            time1.append(time.time()-time1[0])
            cnt.append(offset)
        except:
            print('error sending')
    print(f"sent {len(cnt)} packets")
    return len(cnt)


def receive():
    global d
    # print(f"receiving data for {sock.gettimeout()} seconds")
    j = 0
    try:
        while True:
            info, server = sock.recvfrom(2096)
            info = info.decode()
            offset = int(re.search(r'Offset:\s+(\d+)', info).group(1))
            size = int(re.search(r'NumBytes:\s+(\d+)', info).group(1))
            if (arr[offset//maxSize][2] == 1):
                arr[offset//maxSize][2] = 0
                d[offset//maxSize] = info.split("\n\n", 1)[1]
                # print('recieved', offset)
                j += 1
                time2.append(time.time()-time2[0])
    except socket.timeout:
        pass
    print(f"recieved {j} packets")
    return j
    
    
def writeToFile(data, file):
    with open(file, 'w') as f:
        f.write(data)
    f.close()
    
    
    
def run():
    global cwnd 
    global d
    global timeout
    start = time.time()
    while (len(d) < len(arr)):
        sent = send(cwnd)
        cwnd_g.append(sent)
        received = receive()
        # if (received < sent*0.8):
            # cwnd = max(1, cwnd // 2)
        if (received < sent):
            cwnd = max(1, cwnd // 2)
        else:
            cwnd += 1
        # time.sleep(timeout)
    ans = ""
    for i in range(len(arr)):
        ans += d[i]
    writeToFile(ans, 'mani.txt')
    md5_hash = hashlib.md5()
    md5_hash.update(ans.encode('utf-8'))
    md5_hex = md5_hash.hexdigest()
    print(md5_hex)
    submit_command = f'Submit: cs1210552@bots\nMD5: {md5_hex}\n\n'
    sock.sendto(submit_command.encode(), server_address)
    data, server = sock.recvfrom(2096)
    data = data.decode()
    print(data)
    sock.close()
    print("File received in time", time.time()-start)
            
run()
plt.plot(cwnd_g[:40])
plt.savefig('cwnd.png')