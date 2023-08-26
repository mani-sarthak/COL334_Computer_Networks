import socket
import threading
import time
from vayuclient import inc_num_lines,recv_input
def server_thread_func(server_socket, lines):
    while True:
        conn, address = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, address, lines))
        thread.start()

# send to other client acting us as a server
def handle_client(conn, address, data_dict):
    print("Connected to client", address)
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        # lines.append(data)
        conn.sendall('Received: '.encode() + data.encode())
    conn.close()

# send to other server by me acting as client
def client_sender(client_socket,data_dict):
    while True:
        # line = input("Enter data to send to server at port 7002 (or 'exit' to return to menu): ")
        # if line == 'exit':
        #     break
        # client_socket.sendall(line.encode())
        # lines.append(line)
        data = client_socket.recv(1024).decode()
        print('Server response:', data)

def client_vayu(client_socket,data_dict):
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
                    fmess=str(line_number)+line_content
                    client_socket.sendall(fmess.encode())
            print("Submitting...")
            submit_command = b"SUBMIT\naseth@col334-672\n" + str(line_num).encode() + b"\n"
            s.sendall(submit_command)
            for key in data_dict.keys():
                s.sendall(str(key).encode() + b"\n" + data_dict[key].encode() + b"\n")
            submission_success = recv_input(s)
            print(submission_success)
            inc = inc_num_lines(submission_success)
            if(inc > 0):
              s.sendall(b"SEND INCORRECT LINES\n")
              for i in range(inc):
                data = recv_input(s)
                print(data)

def main():
    data_dict={}

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 7204))
    server_socket.listen(4)
    time.sleep(10)
    client_socket = socket.socket()
    client_socket.connect(('127.0.0.1', 7203))
    # client_socket_2 = socket.socket()
    # client_socket_2.connect(('vayu',9801))
    server_thread = threading.Thread(target=server_thread_func, args=(server_socket, data_dict))
    server_thread.start()

    while True:
        print("\nEnter 'c' for client mode, 's' for server mode, or 'exit' to quit:")
        choice = input("Choice: ")

        if choice == 'c1':
            client_thread = threading.Thread(target=client_sender, args=(client_socket,data_dict))
            client_thread.start()
            client_thread.join()
        elif choice == 'c2':
            client_thread = threading.Thread(target=client_vayu, args=(client_socket,data_dict))
            client_thread.start()
            client_thread.join()
        elif choice == 's':
            print('Stored lines received on port 7001:')
            # for line in data_dict:
            #     print(line)
        elif choice == 'exit':
            break
        else:
            print("Invalid choice. Enter 'c', 's', or 'exit'.")
    client_socket.close()
    server_socket.close()
    client_socket_2.close()
    # server_thread.join()

if __name__ == '__main__':
    main()
