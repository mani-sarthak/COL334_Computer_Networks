import threading
import hashlib
import sys
import socket
import time
import sys
import re
import select
import matplotlib.pyplot as plt

start = time.time()
server_address = ('127.0.0.1', 9801) 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data_dict = dict()
maxSize = 1448
offset = 0
timeout = 0.01
plot1=[]
plot2=[]
misses = []
miss = 0

def writeToFile(data, file):
    with open(file, 'w') as f:
        f.write(data)
    f.close()

def extract_data(input_text):
    parts = input_text.split("\n\n", 1)
    return parts[1]

def extract_data2(input_text):
    parts = input_text.split("\n\n", 1)
    byparts = parts[0].split("\n")
    pattern = r"Offset:\s+(\d+)"
    match = re.search(pattern, byparts[0])
    # print(match.group(1))
    return int(match.group(1))

def getSize(data):
    match = re.search(r'Size:\s+(\d+)', data)
    return int(match.group(1))
    

def recieving_thread(requests,arr):
    while True and len(data_dict) != requests:
        data, server = sock.recvfrom(2096)
        data = data.decode()
        if data:
            data_extract = extract_data(data)
            offset_value = extract_data2(data)
            data_dict[offset_value//maxSize] = data_extract
            subtime=time.time()
            plot1.append([offset_value,(subtime-start)*1000])
            print(len(data_dict))
            print('fetched', offset)
            print('data recieved')
            arr[offset_value//maxSize][1]=0
            # misses.append([len(data_dict),(-start)*1000])
        else:
            # misses.append([miss,(subtime-start)*1000])
            miss += 1
            continue
        time.sleep(timeout)
    # return misses 

def sending_thread(requests,arr):
    global offset
    i=0
    while(len(data_dict) != requests):
        i = i % requests
        offset = arr[i][0]
        size = arr[i][1]
        message = f'Offset: {offset}\nNumBytes: {size}\n\n'
        if size > 0:
            try:
                print(message)
                sock.sendto(message.encode(), server_address)
                subtime1=time.time()
                plot2.append([offset,(subtime1-start)*1000])
                time.sleep(timeout)
                # time.sleep(2)
                print('message sent')
            except socket.timeout:
                continue
        i+=1
        # print(len(data_dict))
        misses.append([len(data_dict),(time.time()-start)*1000])

def main():
    try:
        message = 'SendSize\nReset\n\n'  
        sock.sendto(message.encode(), server_address)
        data, server = sock.recvfrom(2096)
        data = data.decode()
        byte_size = getSize(data)

    finally:
        print('Done')
    arr = [[x, min(x+maxSize, byte_size)-x] for x in range(0, byte_size, maxSize)]
    requests = len(arr)
    sender_thread = threading.Thread(target=sending_thread, args=(requests,arr))
    reciever_thread = threading.Thread(target=recieving_thread,args=(requests,arr))
    sender_thread.start()
    reciever_thread.start()
    sender_thread.join()
    # print(data_dict)
    ans = ""
    for i in range(requests):
        ans += data_dict[i]
    writeToFile(ans, 'output_thread.txt')
    md5_hash = hashlib.md5()
    md5_hash.update(ans.encode('utf-8'))
    md5_hex = md5_hash.hexdigest()
    # print(md5_hex)
    submit_command = f'Submit: cs1210552@bots\nMD5: {md5_hex}\n\n'
    sock.sendto(submit_command.encode(), server_address)
    data, server = sock.recvfrom(2096)
    data = data.decode()
    print(data)
    finish = time.time()
    print((finish-start))
    # x1=[]
    # y1=[]
    # i=0
    # while plot1[i][1]<500:
    #     x1.append(plot1[i][1])
    #     y1.append(plot1[i][0])
    #     i+=1
    # x2=[]
    # y2=[]
    # i=0
    # while plot2[i][1]<500:
    #     x2.append(plot2[i][1])
    #     y2.append(plot2[i][0])
    #     i+=1
    x2 = [plot2[i][1] for i in range(len(plot2))][-20:]
    y2 = [plot2[i][0] for i in range(len(plot2))][-20:]
    x1 = [plot1[i][1] for i in range(len(plot1))][-20:]
    y1 = [plot1[i][0] for i in range(len(plot1))][-20:]
    # x1 = [misses[i][1] for i in range(len(misses))][:30]
    # y1 = [misses[i][0] for i in range(len(misses))][:30]
    # print(len(misses))
    # with open ('x1.txt','w') as f:
    #     f.write(str(x1) + '\n')
    #     f.write(str(y1) + '\n')
    #     f.write(str(x2) + '\n')
    #     f.write(str(y2) + '\n')
    # f.close()        
    fig,ax = plt.subplots()
    ax.plot(x2,y2,label = 'sending Data',marker = 'o',linestyle = '-',color = 'blue')
    ax.plot(x1,y1,label = 'recieving Data',marker = 'o',linestyle = 'None', color = 'orange')
    # ax.set_yticks(range(0, 45000, 5000))
    # ax.set_xticks(range(0, 500, 100))
    ax.set_xlabel('Time in (ms)')
    ax.set_ylabel('Offest in (bytes)')
    ax.set_title('Sequence Number Trace')
    ax.legend()
    fig.savefig('zoom_last.png')
if __name__ == '__main__':
    main()