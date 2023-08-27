import socket
import threading

server_list = []
broadcast_list = []
broadcast_lock = threading.Lock()

def handle_client(conn, address):
    while True:
        data = conn.recv(2048).decode()
        if not data:
            break
        print("Received from connected user {}: {}".format(address, data))
        with broadcast_lock:
            for client_conn in server_list:
                client_conn.send(data.encode())
    conn.close()

def broadcast_thread():
    while True:
        message = input("Broadcast message: ")
        with broadcast_lock:
            for client_conn in server_list:
                client_conn.send(message.encode())

def server_program():
    host = '192.168.197.228'
    port = 7215
    thread_list = []

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(4)

    print("Server listening on {}:{}".format(host, port))

    receive_thread = threading.Thread(target=broadcast_thread)
    receive_thread.start()
    thread_list.append(receive_thread)

    while True:
        conn, address = server_socket.accept()
        server_list.append(conn)
        client_thread = threading.Thread(target=handle_client, args=(conn, address))
        client_thread.start()
        thread_list.append(client_thread)

    for k in thread_list:
        k.join()

if __name__ == '__main__':
    server_program()
