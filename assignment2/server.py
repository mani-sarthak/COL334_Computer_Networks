import socket
from _thread import *

host = '10.184.15.146'
port = 4000
ThreadCount = 0

def client_handler(connection):
    connection.send(str.encode('You are  now connected to the replay server... Type BYE to stop'))
    while True:
        data = connection.recv(2048)
        message = data.decode('utf-8')
        if message == 'BYE':
            break
        reply = "Hello Harshit Mani Rajat"
        connection.sendall(str.encode(reply))
    connection.close()

def accept_connections(ServerSocket):
    Client, address = ServerSocket.accept()
    print(Client)
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(client_handler, (Client, ))


def send_message(target_host, target_port, message):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((target_host, target_port))
        client_socket.send(message.encode())
        client_socket.close()

def start_server(host, port):
    ServerSocket = socket.socket()
    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))
    print(f'Server is listing on the port {port}...')
    ServerSocket.listen()

    while True:
        accept_connections(ServerSocket)
# send_message("10.184.15.146", 50000,"hello")
start_server(host,port)