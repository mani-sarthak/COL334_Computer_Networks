import threading
import hashlib
import sys
import socket
import time
import sys
import re
import select

server_address = ('10.17.7.134', 9801) 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data_dict = dict()
maxSize = 1448
offset = 0
timeout = 0.03## change it accordingly

def writeToFile(data, file):
    with open(file, 'w') as f:
        f.write(data)
    f.close()


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
            # print(len(data_dict))
            # print('fetched', offset)
            # print('data recieved')
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
        # print(len(data_dict))

def main():
    start = time.time()
    try:
        message = 'SendSize\nReset\n\n'  
        sock.sendto(message.encode(), server_address)
        data, server = sock.recvfrom(2096)
        data = data.decode()
        byte_size = getSize(data)

    finally:
        print('Done')
    # writeToFile(str(byte_size) + '\n', 'analysis.txt')
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
    # sock.settimeout(5)
    # while True:
    #     try:
    #         data, server = sock.recvfrom(2096)
    #         data = data.decode()
    #         print(data)
    #     except socket.timeout:
    #         break
    # data = data.decode()
    # writeToFile(data + "\n\n\n", 'analysis.txt')
    data, server = sock.recvfrom(2096)
    data = data.decode()
    print(data)
    finish = time.time()
    print((finish-start)*1000, "ms")
if __name__ == '__main__':
    main()
