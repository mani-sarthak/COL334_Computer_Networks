import socket
import re
import time
import hashlib
timeout = 1 ## now consider same as RTT sinc ebursts are sent almost paralelly
estimatedRTT = 0.5
server_address =   ('127.0.0.1', 9802)  #('127.0.0.1', 9801)##
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)
cwnd = 3
d = dict()
squishCount = 0
init = time.time()
time_sent = []
time_received = []
increase=1
burst_send = []
burst_received = []

req=0
miss=0

def getRTT(sz = 50):
    rtt = []
    for i in range(sz):
        try:
            message = 'SendSize\nReset\n\n' 
            send_time = time.time()
            sock.sendto(message.encode(), server_address)
            data, server = sock.recvfrom(2096)
            receive_time = time.time()
            initial_timeout = receive_time - send_time
            rtt.append(initial_timeout)
        except socket.timeout as t:
            pass
    avg = sum(rtt)/len(rtt)
    return avg,  min(rtt)/avg, max(rtt)/avg, sorted(rtt)[len(rtt)//2]

rtt_pair = getRTT(50)
if server_address[0]=="vayu.iitd.ac.in":
    rtt=3*rtt_pair[3]
    increase=2
elif server_address[0]=="127.0.0.1":
    rtt = 0.01
else:
    rtt = max(rtt_pair[0]*1.1 + rtt_pair[3], 0.003)
sock.settimeout(rtt)
print(rtt)

def getSize(sock):
    try:
        message = 'SendSize\nReset\n\n' 
        send_time = time.time()
        sock.sendto(message.encode(), server_address)
        data, server = sock.recvfrom(2096)
        receive_time = time.time()
        initial_timeout = receive_time - send_time
        data = data.decode()
        size = int(re.search(r'Size:\s+(\d+)', data).group(1))
        print(size, initial_timeout)

    finally:
        print()
        
        
    return size

size = getSize(sock)    

offset = 0
maxSize = 1448
arr = [[x, min(x+maxSize, size)-x, 1] for x in range(0, size, maxSize)]
currRequests = []

print(size, len(arr))

d = dict()
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
    
## send a burst of k size 
def send(k):
    global time_sent
    global burst_send
    global req
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
            req+=1
            cnt.append(offset)
            time_sent.append([time.time()-init, offset])
        except:
            print('error sending')
    print(f"sent {len(cnt)} packets")
    burst_send.append(len(cnt))
    return len(cnt)


def receive():
    global d
    global miss
    global squishCount
    global time_received
    global burst_received
    j = 0
    timeReceiveStart = time.time()
    try:
        while (time.time() - timeReceiveStart < estimatedRTT):
            info, server = sock.recvfrom(2096)
            receive_time_temp = time.time()
            
            info = info.decode()
            if info.split("\n\n", 1)[1]== '':
                continue
            offset = int(re.search(r'Offset:\s+(\d+)', info).group(1))
            size = int(re.search(r'NumBytes:\s+(\d+)', info).group(1))
            headers = info.split("\n\n", 1)[0]
            if (len(headers.split("\n")) == 3):
                squishCount += 1
            if (arr[offset//maxSize][2] == 1):
                arr[offset//maxSize][2] = 0
                d[offset//maxSize] = info.split("\n\n", 1)[1]
                print('recieved', offset//maxSize)
                j += 1 
                time_received.append([receive_time_temp-init, offset])
    except socket.timeout:
        miss+=1
        pass
    print(f"recieved {j} packets")
    burst_received.append(j)
    return j
     
def writeToFile(data, file):
    with open(file, 'w') as f:
        f.write(data)
    f.close()
    
def run():
    global cwnd 
    global d
    global increase
    global rtt
    start = time.time()
    init = time.time()
    while (len(d) < len(arr)):
        sent = send(cwnd)
        received = receive()
        if (received < sent):
            cwnd = max(1, cwnd // 2)
        else:
            cwnd += increase
        time.sleep(rtt)
    ans = ""
    for i in range(len(arr)):
        ans += d[i]
    writeToFile(ans, 'output_thread_amid.txt')
    md5_hash = hashlib.md5()
    md5_hash.update(ans.encode('utf-8'))
    md5_hex = md5_hash.hexdigest()
    print(md5_hex)
    submit_command = f'Submit: cs1210552@bots\nMD5: {md5_hex}\n\n'
    print("File received in time", time.time()-start)
    sock.settimeout(1)
    sock.sendto(submit_command.encode(), server_address)
    data=""
    while "Time:" not in data:
        data, server = sock.recvfrom(2096)
        data = data.decode()
    print(data)
    print("Squish Count:  ", squishCount)
    sock.close()
    print("File received in time", time.time()-start)
     
     
delta = 0.1
def plot(types):
    import matplotlib.pyplot as plt
    if 1 in types:
        plt.figure(1)
        plt.plot([x[0] for x in time_sent[:types[1]]], [x[1]  for x in time_sent[:types[1]]], color = 'blue', marker = 'o', linestyle = 'None', label = "requests sent")
        plt.plot([x[0] for x in time_received[:types[1]]], [x[1]  for x in time_received[:types[1]]], color = 'orange', marker = 'o', linestyle = 'None', label = "requests received")
        plt.xlabel('Time (in sec)')
        plt.ylabel('Offset (in Bytes)')
        plt.legend()
        plt.title("Sequence Number Trace")
        plt.savefig("sequence trace.png")
    if 2 in types:
        plt.figure(2)
        plt.plot([i for i in range(types[2])], [x  for x in burst_send[:types[2]]], color = 'blue', marker = 'o', linestyle = '-', label = "burst size sent")
        plt.plot([i+delta for i in range(types[2])], [x  for x in burst_received[:types[2]]], color = 'orange', marker = 'o', linestyle = '-', label = "burst size received")
        plt.xlabel('Burst number')
        plt.ylabel('Burst Size')
        plt.legend()
        plt.title("Burst Size Trace")
        plt.savefig("burst size.png")
    if 3 in types:
        plt.figure(3)
        plt.plot([i for i in range(types[3])], [x  for x in burst_send[:types[3]]], color = 'blue', marker = '', linestyle = '-', label = "AIMD burst size sent")
        plt.xlabel('Burst number')
        plt.ylabel('Burst Size')
        plt.legend()
        plt.title("AIMD bursts")
        plt.savefig("burst aimd.png")
            
run()
# types = dict()
# print(req,miss)
# # types[1] = len(time_sent)
# # types[2] = len(burst_send)
# # types[3] = 20
# plot(types)
