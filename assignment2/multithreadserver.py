import socket
import threading

def handle_client(conn, address):
    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        print("Connection from: " + str(address))
        data = conn.recv(2048).decode()
        if not data:
            # if data is not received break
            break
        print("from connected user: " + str(data))
        response = input(' -> ')
        conn.send(response.encode())  # send data to the client
    conn.close()

def server_program():
    host = '127.0.0.1'
    port = 7000

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(4)

    print("Server listening on {}:{}".format(host, port))

    while True:
        conn, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, address))
        client_thread.start()

if __name__ == '__main__':
    server_program()
