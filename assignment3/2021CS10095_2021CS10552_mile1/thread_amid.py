import socket
import re
import hashlib
import time
import threading
import sys

server_address = ('127.0.0.1', 9801) 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
maxSize = 1448
max_retransmission=300
ssthresh=16
timeout=0.007
waiting_time=0.009
buffer_dict=dict()
burst_size=1
offset = 0
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
    global burst_size
    found=False
    count=0
    while count<burst_size:
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
        except socket.timeout:
            print('timeout')
            found=True
        count+=1
        # print('fghj')
    if found==False:
        burst_size+=1
        # if burst_size>ssthresh:
        #     burst_size=min(burst_size//2,1)
    else:
        burst_size=max(burst_size//2,1)
    print(f'burst size is {burst_size}')
    
def sending_thread(file_size,requests,arr):
    global offset
    # burst_size=1
    global burst_size
    j=0
    while len(buffer_dict)!=requests:
        i=0
        while i<burst_size:
            j=j%requests
            offset=arr[j][0]
            size=arr[j][1]
            if size>0:
                request = f"Offset: {offset}\nNumBytes: {size}\n\n"
                sock.sendto(request.encode(), server_address)
                print(request)
                print('message sent')
                i+=1
            j+=1
            
            # print('j',j)
        # start_time=time.time()
        # retransmissions=0
        print('waiting')
        reciever_thread=threading.Thread(target=recieving_thread,args=(file_size,requests,arr))
        reciever_thread.start()
        reciever_thread.join()
        print(burst_size)
        time.sleep(waiting_time)

def writeToFile(data, file):
    with open(file, 'w') as f:
        f.write(data)
    f.close()
    
def main():
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
    sock.sendto(submit_command.encode(), server_address)
    data, server = sock.recvfrom(2096)
    data = data.decode()
    print(data)
    sock.close()
    print("File received and saved.")

if __name__ == '__main__':
    s=time.time()
    main()
    f=time.time()
    print(f'Time taken: {f-s}')