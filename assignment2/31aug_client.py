import socket
import threading
import time 
 
host = '10.194.22.115' # server address and port !
port = 8230

started = False

def inc_num_lines(submission_response):
    parts = submission_response.split(" - ")
    if len(parts) >= 3:
        num_lines_part = parts[2]
        num_lines = int(num_lines_part.split(", ")[1])
        return num_lines
    return None

def recv_input(sock):
  input_buffer = b''
  while True:
    
    packet = sock.recv(1024)
    input_buffer += packet
    if packet.endswith(b'\n'):
      break
  if not input_buffer.endswith(b'\n'):
    input_buffer += b'\n'
  return input_buffer.decode('utf-8')



def receive_thread(socket):
    global started
    while True:
        receive = socket.recv(2048).decode('utf-8')
        if receive=='start':
            started=True
            break
        
    while True:
        try:
            received_data = recv_input(socket)
            try:
                lines = received_data.split("\n")
                line_number = int(lines[0])
                line_content = lines[1]
                print(line_number," recieved from server")
            except (ValueError, IndexError):
                continue
            if line_number == -1:
                time.sleep(1e-6)
                continue
            if line_number not in data_dict:
                print(line_content)
                data_dict[line_number] = line_content
            # print('Server response:', response)
        except Exception as e:
            print('Error receiving:', str(e))
            break
        if len(data_dict)==line_num:
            break

# def send_thread(socket):
#     while True:
#         try:
#             input_message = input('Your message: ')
#             socket.sendall(input_message.encode())
#         except KeyboardInterrupt:
#             print('Closing send thread...')
#             break
#         except socket.error as e:
#             print('Error sending:', str(e))
#             break



def vayu_thread(socket,socket2):
    global started
    while True:
        if started==True:
            break
    while True:
        try:
            socket.settimeout(5)
            socket.connect(server_address)
            start = time.time()
            while len(data_dict) < line_num:
                print(len(data_dict))
                socket.sendall(sendline_command)
                received_data = recv_input(socket)
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
                socket2.sendall(received_data.encode())
            file_name = "output.txt"
            with open(file_name, "w") as file:
                for key, value in data_dict.items():
                    file.write(f"Key: {key}, Value: {value}\n")
            print(f"Data written to {file_name}")
            print("Submitting...")
            submit_command = b"SUBMIT\naseth@col334-672\n" + str(line_num).encode() + b"\n"
            socket.sendall(submit_command)
            for key in data_dict.keys():
                socket.sendall(str(key).encode() + b"\n" + data_dict[key].encode() + b"\n")
            submission_success = recv_input(socket)
            print(submission_success)
            finish = time.time()
            print(f"Time taken: {finish - start}")
            time.sleep(15)
            break
        except KeyboardInterrupt:
            print('Closing send thread...')
            break
        except Exception as e:
            print('Error sending:', str(e))
            break
    
    
    
server_address = ("vayu.iitd.ac.in", 9801)
sendline_command = b"SENDLINE\n"
line_num = 1000
data_dict = {}

ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
VayuSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print('Waiting for connection')

try:
    ClientSocket.connect((host, port))
    print('hhh')
except socket.error as e:
    # print('hello')
    print('ertyuio')
    print(str(e))
    exit()

receive_thread = threading.Thread(target=receive_thread, args=(ClientSocket,))
# send_thread = threading.Thread(target=send_thread, args=(ClientSocket,))
vayu_thread = threading.Thread(target=vayu_thread, args=(VayuSocket,ClientSocket))


receive_thread.start()
vayu_thread.start()

receive_thread.join()
vayu_thread.join()

print('Client threads closed.')
ClientSocket.close()