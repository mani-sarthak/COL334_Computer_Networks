import socket
import threading
import time

def server_thread_func(server_socket, lines):
    while True:
        conn, address = server_socket.accept()

        thread = threading.Thread(target=handle_client, args=(conn, address, lines))
        thread.start()

def handle_client(conn, address, lines):
    print("Connected to client", address)
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        lines.append(data)
        conn.sendall('Received: '.encode() + data.encode())
    conn.close()

def client_sender(client_socket):
    while True:
        line = input("Enter data to send to server at port 7002 (or 'exit' to return to menu): ")
        if line == 'exit':
            break
        client_socket.sendall(line.encode())
        data = client_socket.recv(1024).decode()
        print('Server response:', data)

def main():
    lines = []

    server_socket = socket.socket()
    server_socket.bind(('localhost', 7202))
    server_socket.listen(4)
    time.sleep(10)
    client_socket = socket.socket()
    client_socket.connect(('localhost', 7201))

    server_thread = threading.Thread(target=server_thread_func, args=(server_socket, lines))
    server_thread.start()

    while True:
        print("\nEnter 'c' for client mode, 's' for server mode, or 'exit' to quit:")
        choice = input("Choice: ")

        if choice == 'c':
            client_thread = threading.Thread(target=client_sender, args=(client_socket,))
            client_thread.start()
            client_thread.join()
        elif choice == 's':
            print('Stored lines received on port 7001:')
            for line in lines:
                print(line)
        elif choice == 'exit':
            break
        else:
            print("Invalid choice. Enter 'c', 's', or 'exit'.")

    server_thread.join()

if __name__ == '__main__':
    main()
