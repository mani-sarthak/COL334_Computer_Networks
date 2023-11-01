import socket
import re
import time
import hashlib
timeout = 1 ## now consider same as RTT sinc ebursts are sent almost paralelly
server_address =  ('127.0.0.1', 9801)##('10.17.51.115',9802)  #
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)
estimatedRTT = 0.1
cwnd = 3
d = dict()
squishCount = 0
init = time.time()
time_sent = []
time_received = []
burst_send = []
burst_received = []
sum_bursts_sent = []
sum_bursts_received = []
squished = []

def getRTT(sz = 50):
    rtt = []
    for i in range(sz):
        message = 'SendSize\nReset\n\n' 
        send_time = time.time()
        sock.sendto(message.encode(), server_address)
        data, server = sock.recvfrom(2096)
        receive_time = time.time()
        initial_timeout = receive_time - send_time
        rtt.append(initial_timeout)
    avg = sum(rtt)/len(rtt)
    return avg,  min(rtt)/avg, max(rtt)/avg, sorted(rtt)[len(rtt)//2]




# for x in range(20, 2000, 20):
#     print(x, getRTT(x))
    
    
    
def validateRTT(rtt, sz = 50):
    cnt = 0
    for i in range(sz):
        message = 'SendSize\nReset\n\n' 
        send_time = time.time()
        sock.sendto(message.encode(), server_address)
        data, server = sock.recvfrom(2096)
        receive_time = time.time()
        initial_timeout = receive_time - send_time
        rtt.append(initial_timeout)

 
 
rtt_pair = getRTT(50)
rtt = min(max(rtt_pair[0]*1.1 + rtt_pair[3], 0.003), 0.01)
# rtt = rtt_pair[0]
print(rtt)
sock.settimeout(rtt) ## just to be on safer side RTT is 1.2 times of timeout
# print(rtt*1.1)

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
            cnt.append(offset)
            time_sent.append([time.time()-init, offset])
        except:
            print('error sending')
    print(f"sent {len(cnt)} packets")
    burst_send.append(len(cnt))
    return len(cnt)


def receive():
    global d
    global squishCount
    global time_received
    global burst_received
    global estimatedRTT
    j = 0
    timeReceiveStart = time.time()
    try:
        while (time.time() - timeReceiveStart < estimatedRTT):
            info, server = sock.recvfrom(2096)
            receive_time_temp = time.time()
            info = info.decode()
            offset = int(re.search(r'Offset:\s+(\d+)', info).group(1))
            size = int(re.search(r'NumBytes:\s+(\d+)', info).group(1))
            headers = info.split("\n\n", 1)[0]
            if (len(headers.split("\n")) == 3):
                squishCount += 1
                squished.append([receive_time_temp-init, 1])
            else:
                squished.append([receive_time_temp-init, 0])
            if (arr[offset//maxSize][2] == 1):
                arr[offset//maxSize][2] = 0
                d[offset//maxSize] = info.split("\n\n", 1)[1]
                print('recieved', offset//maxSize)
                j += 1 
                time_received.append([receive_time_temp-init, offset])
    except socket.timeout:
        pass
    timeReceiveEnd = time.time()
    estimatedRTT = 0.875*estimatedRTT + 0.125*(timeReceiveEnd - timeReceiveStart)
    estimatedRTT /= 10
    estimatedRTT = min(max(estimatedRTT, 0.003), 0.01)
    # print((timeReceiveEnd - timeReceiveStart))
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
    global rtt
    start = time.time()
    init = time.time()
    while (len(d) < len(arr)):
        sent = send(2)
        received = receive()
        # sock.settimeout(estimatedRTT)
        # print(estimatedRTT, cwnd, sent, received)
        if (received < sent):
            cwnd = max(1, cwnd // 2)
        else:
            cwnd += 1
        time.sleep(rtt)
    ans = ""
    for i in range(len(arr)):
        ans += d[i]
    # writeToFile(ans, 'mani.txt')
    md5_hash = hashlib.md5()
    md5_hash.update(ans.encode('utf-8'))
    md5_hex = md5_hash.hexdigest()
    print(md5_hex)
    submit_command = f'Submit: cs1210095@bots\nMD5: {md5_hex}\n\n'
    sock.settimeout(1)
    sock.sendto(submit_command.encode(), server_address)
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
        ## Sequence trace
        plt.figure(1)
        plt.plot([x[0] for x in time_sent[:types[1]]], [x[1]  for x in time_sent[:types[1]]], color = 'blue', marker = 'o', linestyle = 'None', label = "requests sent")
        plt.plot([x[0] for x in time_received[:types[1]]], [x[1]  for x in time_received[:types[1]]], color = 'orange', marker = 'o', linestyle = 'None', label = "requests received")
        plt.xlabel('Time (in sec)')
        plt.ylabel('Offset (in Bytes)')
        plt.legend()
        plt.title("Sequence Number Trace")
        plt.savefig("sequence trace.png")
    if 2 in types:
        ## Burst trace
        plt.figure(2)
        plt.plot([i for i in range(types[2])], [x  for x in burst_send[:types[2]]], color = 'blue', marker = 'o', linestyle = '-', label = "burst size sent")
        plt.plot([i+delta for i in range(types[2])], [x  for x in burst_received[:types[2]]], color = 'orange', marker = 'o', linestyle = '-', label = "burst size received")
        plt.xlabel('Burst number')
        plt.ylabel('Burst Size')
        plt.legend()
        plt.title("Burst Size Trace")
        plt.savefig("burst size.png")
    if 3 in types:
        ## AIMD sawtooth
        plt.figure(3)
        plt.plot([i for i in range(types[3])], [x  for x in burst_send[:types[3]]], color = 'blue', marker = '', linestyle = '-', label = "AIMD burst size sent")
        plt.xlabel('Burst number')
        plt.ylabel('Burst Size')
        plt.legend()
        plt.title("AIMD bursts")
        plt.savefig("burst aimd.png")
        
    if 4 in types:
        ## Efficiency requests missed vs bursts sent
        s1 = 0
        for x in burst_send:
            s1 += x
            sum_bursts_sent.append(s1)
        s2 = 0
        for x in burst_received:
            s2 += x
            sum_bursts_received.append(s2)
        misses = [0]
        for i in range(min(len(sum_bursts_sent), len(sum_bursts_received))):
            misses.append(max(sum_bursts_sent[i] - sum_bursts_received[i], misses[-1]))
        plt.figure(4)
        plt.plot([i for i in range(len(misses))], [x  for x in misses[:len(misses)]], color = 'blue', marker = '', linestyle = '-', label = "requests missed")
        plt.xlabel('Burst number')
        plt.ylabel('# requests missed')
        plt.legend()
        plt.title("Efficiency (misses vs bursts sent)")
        plt.savefig("burst efficiency.png")
    if 5 in types:
        ## squished in constantrate 
        plt.figure(5)
        plt.plot([x[0] for x in squished[:types[5]]], [2 for i in range(types[5])], color = 'blue', marker = 'o', linestyle = '-', label = "burst size sent")
        plt.plot([x[0] for x in squished[:types[5]]], [x[1]  for x in squished[:types[5]]], color = 'orange', marker = 'o', linestyle = '-', label = "squished")
        plt.xlabel('Time (in sec)')
        plt.ylabel('Burst Size / squished')
        plt.title("Burst size trace")
        plt.legend()
        plt.savefig("burst size squished.png")        
run()
types = dict()
# types[1] = len(time_sent)
types[5] = 550
# types[1] = 200
# plot(types)
# types[4] = 300
# plot(types)
# types[3] = 50
plot(types)

# types