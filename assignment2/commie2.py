import socket
import threading
import time

def server_thread_func(server_socket, lines, lock):
    for i in range(2):
        try:
            conn, address = server_socket.accept()
            if conn is None:
                print("No new clients connected")
                break

            thread = threading.Thread(target=handle_client, args=(conn, address, lines, lock))
            thread.start()
        except socket.timeout:
            pass  # No new connection within the timeout, continue loop



def handle_client(conn, address, lines, lock):
    print("Connected to client", address)
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        with lock:
            lines.append(data)
        # conn.sendall('Received: '.encode() + data.encode())
    conn.close()

def client_sender(client_socket, lines, lock):
    while True:
        line = input("Enter data to send to server (or 'exit' to return to menu): ")
        if line == 'exit':
            break
        with lock:
            lines.append(line)
        client_socket.sendall(line.encode())
            
        # data = client_socket.recv(1024).decode()
        # print('Server response:', data)

def main():
    lines = []
    lock = threading.Lock()  # Create a lock object using threading.Lock()

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 7201))
    server_socket.listen(4)
    time.sleep(5)
    
    client_socket = socket.socket()
    client_socket.connect(('localhost', 7202))
    
    client_socket_2 = socket.socket()
    client_socket_2.connect(('localhost', 7203))
    print('Connected to server')
    server_thread_func(server_socket, lines, lock)  # Start the server thread
    print('Connected to clients')
    client_threads = []

    while True:
        print("\nEnter 'c1' for client 1 mode, 'c2' for client 2 mode, 's' for server mode, or 'exit' to quit:")
        choice = input("Choice: ")

        if choice == 'c1':
            client_thread = threading.Thread(target=client_sender, args=(client_socket, lines, lock))
            client_threads.append(client_thread)
            client_thread.start()
        elif choice == 'c2':
            client_thread = threading.Thread(target=client_sender, args=(client_socket_2, lines, lock))
            client_threads.append(client_thread)
            client_thread.start()
        elif choice == 's':
            print('Stored lines received ')
            with lock:
                for line in lines:
                    print(line)
        elif choice == 'exit':
            break
        else:
            print("Invalid choice. Enter 'c1', 'c2', 's', or 'exit'.")

    # for client_thread in client_threads:
    #     client_thread.join()  # Wait for all client threads to finish

    client_socket.close()
    server_socket.close()
    client_socket_2.close()


if __name__ == '__main__':
    main()
