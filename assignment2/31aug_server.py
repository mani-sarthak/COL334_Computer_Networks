import socket
import threading

def handle_client(client_socket):
    while True:
        try:
            data =  client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            print('Received from client: %s' % data)
            response = input('-> ')
            client_socket.send(response.encode('utf-8'))
        except:
            break
    client_socket.close()

def main():
    host = '0.0.0.0'
    port = 8000
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print('Server is listening at %s:%s' % (host, port))
    
    while True:
        client_socket, client_address = server_socket.accept()
        print(f'Accepted connection from {client_address[0]}:{client_address[1]}')
        client_handler = threading.start_new_thread(target = handle_client, args = (client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()
        
        
        
