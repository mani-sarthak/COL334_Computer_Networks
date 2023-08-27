import socket
import threading
server_list=[]
def handle_client(conn, address):
    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        print("Connection from: " + str(address))
        data = conn.recv(2048).decode()
        if not data:
            # if data is not received break
            break
        print("from connected user: " + str(data))
        for k in server_list:
            # k.send(response.encode())
            k.send(data.encode())
        response = input(' -> ')
        for k in server_list:
            k.send(response.encode())
            # k.send(data.encode())
        # conn.send(response.encode())  # send data to the client
    conn.close()

def server_program():
    host = '192.168.197.164'
    port = 7201
    thread_list=[]
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # wrong line
    server_socket.bind((host, port))
    server_socket.listen(4)

    print("Server listening on {}:{}".format(host, port))

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
