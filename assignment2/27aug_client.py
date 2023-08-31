import socket
import threading

host = '192.168.197.164'
port = 7212

def receive_thread(socket):
    while True:
        try:
            data = recv_input(socket)
            lines = data.split("\n")
            line_number = int(lines[0])
            line_content = lines[1]
            data_dict[line_number] = line_content
            if (len(data_dict)==1000):
                break
            # response = socket.recv(2048).decode('utf-8')
            # print('Server response:', response)
        except socket.error as e:
            print('Error receiving:', str(e))
            break


def send_thread(csocket):
    start = time.time()
    while True:
            # input_message = input('Your message: ')
            server_address = ("vayu.iitd.ac.in", 9801) # do we have to restablish again and again
            sendline_command = b"SENDLINE\n"
            line_num = 1000
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect(server_address)
                    while len(data_dict) < line_num:
                        # print(len(data_dict))
                        s.sendall(sendline_command)
                        received_data = recv_input(s)
                        try:
                            lines = received_data.split("\n")
                            line_number = int(lines[0])
                            line_content = lines[1]
                        except (ValueError, IndexError):
                            continue
                        if line_number == -1:
                            time.sleep(1e-6)
                            continue
                        if line_number not in data_dict:
                            data_dict[line_number] = line_content
                            fmess=str(line_number)+'\n'+line_content+'\n'
                            csocket.sendall(fmess.encode())
                    print("Submitting...")
                    submit_command = b"SUBMIT\naseth@col334-672\n" + str(line_num).encode() + b"\n"
                    s.sendall(submit_command)
                    for key in data_dict.keys():
                        s.sendall(str(key).encode() + b"\n" + data_dict[key].encode() + b"\n")
                    submission_success = recv_input(s)
                    print(submission_success)
                    finish = time.time()
                    print(finish-start)
                    break
                    

ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Waiting for connection')

try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))
    exit()


receive_thread = threading.Thread(target=receive_thread, args=(ClientSocket,))
send_thread = threading.Thread(target=send_thread, args=(ClientSocket,))
# vayu_thread = threading.Thread(target=vayu_bhai, args=(data_dict,))

receive_thread.start()
send_thread.start()

receive_thread.join()
send_thread.join()

print('Client threads closed.')
ClientSocket.close()