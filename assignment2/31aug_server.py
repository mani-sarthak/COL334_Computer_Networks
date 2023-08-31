import socket
import threading
import time

server_list = []
broadcast_list = []
broadcast_lock = threading.Lock()
data_dict = {}
broadcasting_started=False
finish1 = []

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


def  sending_client(conn,address):
    for keys in data_dict.keys():
        # print(f'finally sending {keys}')
        data = str(keys) + '\n' + data_dict[keys]
        conn.sendall(data.encode())
    # with broadcast_lock:
    #     server_list.remove(conn)
    #     print("Client disconnected:", address)
    # conn.close()
    
def handle_client(conn, address):
    # with broadcast_lock:
    #     server_list.append(conn)
    #     print("Client connected:", address)
    # global finish1
        
    while True:
        data = recv_input(conn)
        # if not data:
        #     break
        lines = data.split("\n")
        line_numb = int(lines[0])
        line_cont = lines[1]
        if line_numb not in data_dict:
            print("Received from connected user {}: {}".format(address, data))
            print(line_cont)
            data_dict[line_numb] = line_cont
        # data_dict[line_num] = line_cont
        with broadcast_lock:
            for client_conn in server_list:
                if client_conn!=conn:
                    client_conn.send(data.encode())
        if len(data_dict)==1000:
            # finish1 = True
            # for keys in data_dict.keys():
            #     print(f'finally sending {keys}')
            #     data = str(keys) + '\n' + data_dict[keys] + '\n'
            #     conn.sendall(data.encode())
            print(f'final sending 1000 lines to : {address}')
            for keys in data_dict.keys():
            # print(f'finally sending {keys}')
                # data = str(keys) + '\n' + data_dict[keys] +'\n'
                conn.sendall(data.encode())
                
            # client_thread_final = threading.Thread(target=sending_client, args=(conn, address))
            # client_thread_final.start()
            time.sleep(20)
            break 
    # with broadcast_lock:
    #     server_list.remove(conn)
    #     print("Client disconnected:", address)
    # conn.close()

def start_broadcasting():
    global broadcasting_started
    while True:
        command = input("Enter command: ")
        if command.strip().lower() == "start":
            broadcasting_started = True
            print("Broadcasting started!")
            break


def broadcast_thread():
    server_address = ("vayu.iitd.ac.in", 9801)
    sendline_command = b"SENDLINE\n"
    line_num = 1000
    # global finish1
    while True:
        # message = input("Broadcast message: ")
        try:
            start = time.time()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect(server_address)
                while len(data_dict) < line_num:
                    print(len(data_dict))
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
                        with broadcast_lock:
                            for client_conn in server_list:
                                # print('line is sending form server')
                                client_conn.send(received_data.encode())
                submit_command = b"SUBMIT\naseth@col334-672\n" + str(line_num).encode() + b"\n"
                s.sendall(submit_command)
                for key in data_dict.keys():
                    s.sendall(str(key).encode() + b"\n" + data_dict[key].encode() + b"\n")
                submission_success = recv_input(s)
                print(submission_success)
            finish = time.time()
            print(f"Time taken: {finish - start}")
            finish1.append(1)
            break
        # except (socket.timeout, ConnectionError):
        #     print("Connection error")
        #     break
        except Exception as e:
            print("An error occurred:", e)
            break

def start_command_thread1():
    global line_num 
    global broadcasting_started
    while True:
        command = input("Enter 'start' to initiate interaction: \n")
        if command.strip().lower() == "start":
            print("Interaction with Vayu started!\n")
            broadcasting_started=True
            line_num = 0  # Reset line number to start interaction
            # Notify all connected clients about the start command
            with broadcast_lock:
                for client_conn in server_list:
                    client_conn.send("start".encode())
            break
        
def connection_accept_thread1(server_socket):
    # print('hjhhhhhh')
    # global finish1
    # count=0
    while len(server_list)<3:
        conn, address = server_socket.accept()
        # count+=1
        server_list.append(conn)
        print(f'client connected : {address}')
        client_thread = threading.Thread(target=handle_client, args=(conn, address))
        client_thread.start()
        thread_list.append(client_thread)
        # if len(server_list)==3:
        #     break
        
thread_list = []
def server_program():
    host = '10.194.22.115'
    port = 8225

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(10)

    print("Server listening on {}:{}".format(host, port))
    # time.sleep(10)
    # start_broadcasting_thread = threading.Thread(target=start_broadcasting)
    # start_broadcasting_thread.start()
    connection_accept_thread = threading.Thread(target=connection_accept_thread1,args = (server_socket,))
    connection_accept_thread.start()
    thread_list.append(connection_accept_thread)
    # connection_accept_thread.join()
    
    start_command_thread = threading.Thread(target=start_command_thread1)
    start_command_thread.start()
    thread_list.append(start_command_thread)
    while not broadcasting_started:
        time.sleep(1) 
    
    receive_thread = threading.Thread(target=broadcast_thread)
    receive_thread.start()
    thread_list.append(receive_thread)
    connection_accept_thread.join()
    
    

    # while True:
    #     conn, address = server_socket.accept()
    #     server_list.append(conn)
    #     client_thread = threading.Thread(target=handle_client, args=(conn, address))
    #     client_thread.start()
    #     thread_list.append(client_thread)

    # for k in thread_list:
    #     k.join()

if __name__ == '__main__':
    server_program()
