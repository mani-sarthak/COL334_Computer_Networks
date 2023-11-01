import socket
import re
import hashlib
import time
import threading
import sys

server_address = ('10.17.51.115',9802)
sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
maxSize=1448
max_timeout=0.07
RTT=0.01
cwnd=1
buffer_dict=dict()
p=[]
s=time.time()
squish_count=0
req=0
miss=0
duplicate=[]
x=1
sock.settimeout(1)

def getSize():
    global RTT
    l=[]
    # message = 'SendSize\nReset\n\n'  # Your message here
    # sock.sendto(message.encode(), server_address)
    for i in range(0,50):
        # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        r=time.time()
        try:
            # r=time.time()
            message = 'SendSize\nReset\n\n'  # Your message here
            sock.sendto(message.encode(), server_address)
            data, server = sock.recvfrom(2096)
            data = data.decode()
            # print(data)
            size = int(re.search(r'Size:\s+(\d+)', data).group(1))
            s=time.time()
            l.append(s-r)
        except socket.timeout:
            print("timeout")
            continue
        print('done')
        print(i)
    l=sorted(l)
    # mean=sum(l)/len(l)
    RTT=l[len(l)//2]
    print(RTT)
    # RTT=min(0.01,max(0.003,RTT))
    RTT=1.4*sum(l)/len(l)+RTT
    sock.settimeout(RTT)
    print(RTT)
    return size

def extract_data2(input_text):
    global squish_count
    parts = input_text.split("\n\n", 1)
    if parts[1]=='':
        return -1
    byparts = parts[0].split("\n")
    pattern = r"Offset:\s+(\d+)"
    match = re.search(pattern, byparts[0])
    # print(input_text)
    if len(byparts)==3:
        print("squishing")
        p.append(byparts)
        squish_count+=1
    return int(match.group(1))

def extract_data(input_text):
    parts = input_text.split("\n\n", 1)
    return parts[1]


def writeToFile(data, file):
    with open(file, 'w') as f:
        f.write(data)
    f.close()
    
def sender(file_size,requests,arr):
    global cwnd
    global RTT
    global x
    global req
    global miss
    j=0
    e=0
    while len(buffer_dict)!=requests:
        i=0
        res=[]
        tes=[]
        
        while i<cwnd:
            j=j%requests
            offset=arr[j][0]
            size=arr[j][1]
            if size>0:
                request = f"Offset: {offset}\nNumBytes: {size}\n\n"
                # if i==cwnd-1:
                #     e=time.time()
                sock.sendto(request.encode(), server_address)
                print(request)
                print('message sent')
                req+=1
                i+=1
                res.append(time.time())
            j+=1
        print('waiting')
        count=0
        f=0
        # time.sleep(RTT)
        while count<cwnd:
            print('werty')
            try:
                data,addr=sock.recvfrom(2096)
                data=data.decode()
                if data:
                    offset_value=extract_data2(data)
                    if offset_value == -1:
                        continue
                    data_extract=extract_data(data)
                    buffer_dict[offset_value//maxSize] = data_extract
                    print(len(buffer_dict))
                    print('fetched', offset)
                    print('data recieved')
                    if arr[offset_value//maxSize][1]==0:
                        duplicate.append([time.time()-s,offset_value])
                    arr[offset_value//maxSize][1]=0
                    f+=1
                    print("hekkk")
                    tes.append(time.time())
            except socket.timeout as t:
                print('timeout')
                miss+=1
            count+=1
        if f==count:
            # cwnd=min(max_congestion,cwnd+1)
            cwnd+=1
        else:
            cwnd=max((cwnd)//2,1)
        if len(tes)>0:
            new_RTT=sum(tes)/len(tes)-sum(res)/len(res)
            RTT=0.8*RTT+0.2*new_RTT
            sock.settimeout(6*RTT)
        # time.sleep(3.8*RTT)
def main():
    r=time.time()
    file_size=getSize()
    arr = [[x, min(x+maxSize, file_size)-x] for x in range(0, file_size, maxSize)]
    requests = len(arr)
    sender(file_size,requests,arr)
    q=time.time()
    print(f"Time taken: {q-r}")
    ans = ""
    for i in range(requests):
        ans += buffer_dict[i]
    writeToFile(ans, 'output_thread_amid.txt')
    md5_hash = hashlib.md5()
    md5_hash.update(ans.encode('utf-8'))
    md5_hex = md5_hash.hexdigest()
    print(md5_hex)
    submit_command = f'Submit: cs1210552@bots\nMD5: {md5_hex}\n\n'
    sock.settimeout(1)
    sock.sendto(submit_command.encode(), server_address)
    f=time.time()
    print(f'Time taken: {f-s}')
    data=""
    while "Time:" not in data:
        data, server = sock.recvfrom(2096)
        data = data.decode()
    print(data)
    # print(l)
    # print(RTT)
    sock.close()
    print("File received and saved.")
    print("SQUISHED COUNT: ",squish_count)
    print(p)
    print(duplicate)
    print(miss,req)
    
if __name__ == '__main__':
    r=time.time()
    main()
    q=time.time()
    print(f"Time taken: {q-r}")