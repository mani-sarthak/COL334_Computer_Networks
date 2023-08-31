import socket
import threading
import time

server_list = []
broadcast_list = []
broadcast_lock = threading.Lock()
data_dict = {}
broadcasting_started=False

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

def handle_client(conn, address):
    # with broadcast_lock:
    #     server_list.append(conn)
    #     print("Client connected:", address)
        
    while True:
        data = recv_input(conn)
        # if not data:
        #     break
        lines = data.split("\n")
        line_num = int(lines[0])
        line_cont = lines[1]
        data_dict[line_num] = line_cont
        print("Received from connected user {}: {}".format(address, data))
        with broadcast_lock:
            for client_conn in server_list:
                client_conn.send(data.encode())
    
    with broadcast_lock:
        server_list.remove(conn)
        print("Client disconnected:", address)
    conn.close()

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
                                client_conn.send(received_data.encode())
                submit_command = b"SUBMIT\naseth@col334-672\n" + str(line_num).encode() + b"\n"
                s.sendall(submit_command)
                for key in data_dict.keys():
                    s.sendall(str(key).encode() + b"\n" + data_dict[key].encode() + b"\n")
                submission_success = recv_input(s)
                print(submission_success)
            finish = time.time()
            print(f"Time taken: {finish - start}")
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
    while True:
        conn, address = server_socket.accept()
        server_list.append(conn)
        print(f'client connected : {address}')
        client_thread = threading.Thread(target=handle_client, args=(conn, address))
        client_thread.start()
        thread_list.append(client_thread)
        
thread_list = []
def server_program():
    host = '192.168.197.7'
    port = 8221

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(4)

    print("Server listening on {}:{}".format(host, port))
    # time.sleep(10)
    # start_broadcasting_thread = threading.Thread(target=start_broadcasting)
    # start_broadcasting_thread.start()
    connection_accept_thread = threading.Thread(target=connection_accept_thread1,args = (server_socket,))
    connection_accept_thread.start()
    thread_list.append(connection_accept_thread)
    
    start_command_thread = threading.Thread(target=start_command_thread1)
    start_command_thread.start()
    thread_list.append(start_command_thread)
    while not broadcasting_started:
        time.sleep(1) 
    
    receive_thread = threading.Thread(target=broadcast_thread)
    receive_thread.start()
    thread_list.append(receive_thread)
    

    # while True:
    #     conn, address = server_socket.accept()
    #     server_list.append(conn)
    #     client_thread = threading.Thread(target=handle_client, args=(conn, address))
    #     client_thread.start()
    #     thread_list.append(client_thread)

    # for k in thread_list:
    #     k.join()

if __name__ == '_main_':
    server_program()