import socket
import threading

host = '192.168.197.164'
port = 7212

def receive_thread(socket):
    while True:
        try:
            response = socket.recv(2048).decode('utf-8')
            print('Server response:', response)
        except socket.error as e:
            print('Error receiving:', str(e))
            break

def send_thread(socket):
    while True:
        try:
            input_message = input('Your message: ')
            socket.sendall(input_message.encode())
        except KeyboardInterrupt:
            print('Closing send thread...')
            break
        except socket.error as e:
            print('Error sending:', str(e))
            break

ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Waiting for connection')

try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))
    exit()

receive_thread = threading.Thread(target=receive_thread, args=(ClientSocket,))
send_thread = threading.Thread(target=send_thread, args=(ClientSocket,))

receive_thread.start()
send_thread.start()

receive_thread.join()
send_thread.join()

print('Client threads closed.')
ClientSocket.close()