import socket
import re
import hashlib
import time
import threading
import sys
import matplotlib.pyplot as plt

server_address = ('10.17.7.134', 9801) 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
maxSize = 1448
max_retransmission=300
ssthresh=100
timeout=0.0058
waiting_time=0.0069
phase='1'
buffer_dict=dict()
cwnd=1
offset = 0
plot1=[]
plot2=[]
plot3=[]
s=time.time()

sock.settimeout(timeout)

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

def extract_data2(input_text):
    parts = input_text.split("\n\n", 1)
    byparts = parts[0].split("\n")
    pattern = r"Offset:\s+(\d+)"
    match = re.search(pattern, byparts[0])
    # print(match.group(1))
    return int(match.group(1))

def extract_data(input_text):
    parts = input_text.split("\n\n", 1)
    return parts[1]

def recieving_thread(file_size,requests,arr):
    global waiting_time
    global timeout
    global cwnd
    global ssthresh
    global phase
    found=False
    count=0
    h=0
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
                arr[offset_value//maxSize][1]=0
                if phase=='1':
                    h+=1
                if len(plot1)<30:
                    plot1.append([time.time()-s,offset_value])
        except socket.timeout:
            print('timeout')
            found=True
        count+=1
    if phase=='1':
        if found==True:
            ssthresh=cwnd//2
            cwnd=1
        else:
            cwnd+=h
        if cwnd>=ssthresh:
            phase='2'
    elif phase=='2':
        if found==True:
            ssthresh=cwnd//2
            cwnd=1
            phase='1'
        else:
            cwnd+=1
    print(f'congestion_window is {cwnd}')
    
def sending_thread(file_size,requests,arr):
    global offset
    # burst_size=1
    global cwnd
    global waiting_time
    global ssthresh
    global phase
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
                if len(plot2)<30:
                    plot2.append([time.time()-s,offset])
                i+=1
            j+=1
        print('waiting')
        reciever_thread=threading.Thread(target=recieving_thread,args=(file_size,requests,arr))
        reciever_thread.start()
        reciever_thread.join()
        print(cwnd)
        plot3.append([time.time()-s,cwnd])
        time.sleep(waiting_time)

def writeToFile(data, file):
    with open(file, 'w') as f:
        f.write(data)
    f.close()
    
def main():
    # s=time.time()
    
    file_size = getSize()
    # buffer=bytearray(file_size) 
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
    data, server = sock.recvfrom(2096)
    data = data.decode()
    print(data)
    sock.close()
    print("File received and saved.")
    x1=[]
    y1=[]
    i=0
    while i<len(plot1):
        x1.append(plot1[i][1])
        y1.append(plot1[i][0])
        i+=1
    x2=[]
    y2=[]
    i=0
    while i<len(plot2):
        x2.append(plot2[i][1])
        y2.append(plot2[i][0])
        i+=1
        
    fig,ax = plt.subplots()
    ax.plot(y2,x2,label = 'sending Data',marker = 'o',linestyle = 'None',color = 'blue')
    ax.plot(y1,x1,label = 'recieving Data',marker = 'o',linestyle = 'None',color = 'orange')
    # ax.set_yticks(range(0, 1000000, 100000))
    # ax.set_xticks(range(0,5000,500))
    ax.set_xlabel('Time')
    ax.set_ylabel('Offset')
    ax.set_title('Sequence-Number Trace')
    
    ax.legend()
    plt.show()
    x2=[]
    y2=[]
    i=0
    while i<len(plot3):
        x2.append(plot3[i][1])
        y2.append(plot3[i][0])
        i+=1
        
    fig,ax = plt.subplots()
    ax.plot(y2,x2,label = 'sending Data',marker = 'o',linestyle = '-',color = 'blue')
    # ax.plot(y1,x1,label = 'recieving Data',marker = 'o',linestyle = 'None',color = 'orange')
    # ax.set_yticks(range(0, 1000000, 100000))
    # ax.set_xticks(range(0,5000,500))
    ax.set_xlabel('Time')
    ax.set_ylabel('Offset')
    ax.set_title('Sequence-Number Trace')
    
    ax.legend()
    plt.show()  

if __name__ == '__main__':
    # s=time.time()
    main()
    # f=time.time()
    # print(f'Time taken: {f-s}')