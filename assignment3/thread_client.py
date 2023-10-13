import threading
import sys
import socket
import time
import sys
import re
import select

server_address = ('127.0.0.1', 9802)  # Replace with your server's address and port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data_dict = dict()
maxSize = 1350
offset = 0
timeout = 0.01

def writeToFile(data, file):
    with open(file, 'w') as f:
        f.write(data)
    f.close()


## maybe this might be inefficient since the text may contain two lines of break elsewhre
def extract_data(input_text):
    parts = input_text.split("\n\n", 1) # str[str.index('\n\n):]
    return parts[1]


## returns offset
def extract_data2(input_text):
    parts = input_text.split("\n\n", 1)
    byparts = parts[0].split("\n")
    pattern = r"Offset:\s+(\d+)"
    match = re.search(pattern, byparts[0])
    print(match.group(1))
    return int(match.group(1))


## returns size of the data received (in Bytes)
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
            print(len(data_dict))
            print('fetched', offset)
            print('data recieved')
            arr[offset_value//maxSize][1]=0
        else:
            continue
        time.sleep(timeout)

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
                time.sleep(timeout)
                # time.sleep(2)
                print('message sent')
            except socket.timeout:
                continue
        i+=1
        print(len(data_dict))

def main():
    start = time.time()
    try:
        message = 'SendSize\n\n'  
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
    ## how does the threads run one after another ??
    ## like we asked for the sender_thread.join() but not in the reciever_thread
    
    
    ## why shouldn't it be receiver_thread.join() ?? since the main functiion is completed when receiver thread is completed
    sender_thread.join()
    print(data_dict)
    ans = ""
    for i in range(requests):
        ans += data_dict[i]
    writeToFile(ans, 'output_thread.txt')
    finish = time.time()
    print(finish-start)
    
if __name__ == '__main__':
    main()