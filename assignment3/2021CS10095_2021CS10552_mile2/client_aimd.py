import socket
import re
import hashlib
import time
import threading
import matplotlib.pyplot as plt

server_address = ('10.17.7.134', 9801) 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
maxSize = 1448
timeout=0.0035
waiting_time=0.021
cwnd=1
offset = 0
squish_count=0
duplicate=[]
buffer_dict=dict()
p=[]
s=time.time()
max_congestion=8
req=0
miss=0
cnwd=1

sock.settimeout(timeout)

def getSize():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Send data to the server
        r=time.time()
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

def extract_data2(input_text):
    global squish_count
    parts = input_text.split("\n\n", 1)
    byparts = parts[0].split("\n")
    pattern = r"Offset:\s+(\d+)"
    # if len(byparts)==3:
    #     print("squishing")
    #     p.append(byparts)
    #     squish_count+=1
    match = re.search(pattern, byparts[0])
    return int(match.group(1))

def extract_data(input_text):
    parts = input_text.split("\n\n", 1)
    return parts[1]

def recieving_thread1(file_size,requests,arr):
    global timeout
    global waiting_time
    global cwnd
    global max_congestion
    global req,miss
    count=0
    f=0
    while count<cwnd:
        try:
            data,addr=sock.recvfrom(maxSize+1000)
            data=data.decode()
            if data:
                offset_value=extract_data2(data)
                data_extract=extract_data(data)
                buffer_dict[offset_value//maxSize] = data_extract
                print(len(buffer_dict))
                print('fetched', offset)
                print('data recieved')
                # if arr[offset_value//maxSize][1]==0:
                #     duplicate.append([time.time()-s,offset_value])
                arr[offset_value//maxSize][1]=0
                f+=1
        except socket.timeout:
            print('timeout')
            miss+=1
        count+=1
    if f/cwnd>=0.9:
        # cwnd=min(max_congestion,cwnd+1)
        cwnd+=1
    else:
        cwnd=max(cwnd//2,1)
    
def sending_thread(file_size,requests,arr):
    global offset
    global cwnd
    global waiting_time
    global req
    j=0
    while len(buffer_dict)!=requests:
        i=0
        while i<cwnd:
            j=j%requests
            offset=arr[j][0]
            size=arr[j][1]
            if size>0:
                request = f"Offset: {offset}\nNumBytes: {size}\n\n"
                sock.sendto(request.encode(), server_address)
                print(request)
                print('message sent')
                req+=1
                i+=1
            j+=1
        print('waiting')
        reciever_thread=threading.Thread(target=recieving_thread1,args=(file_size,requests,arr))
        reciever_thread.start()
        reciever_thread.join()
        print(cwnd)
        time.sleep(waiting_time)

def writeToFile(data, file):
    with open(file, 'w') as f:
        f.write(data)
    f.close()
    
def main():
    file_size = getSize()
    arr = [[x, min(x+maxSize, file_size)-x] for x in range(0, file_size, maxSize)]
    requests = len(arr)
    sender_thread = threading.Thread(target=sending_thread, args=(file_size,requests,arr))
    sender_thread.start()
    sender_thread.join()
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
    sock.close()
    print("File received and saved.")
    # print("squish count id this")
    # print(squish_count)
    # print(p)
    # print("duplicates are")
    # print(duplicate)
    # print(req)
    # print(miss)
if __name__ == '__main__':
    main()