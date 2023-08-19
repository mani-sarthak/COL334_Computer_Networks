import socket

host = '10.184.42.197'
port = 5800

ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Waiting for connection')

try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

while True:
    try:
        Input = input('Your message: ')
        ClientSocket.sendall(Input.encode())
        Response = ClientSocket.recv(2048).decode('utf-8')
        print('Server response:', Response)
    except KeyboardInterrupt:
        print('Connection closed by the client.')
        break
    except socket.error as e:
        print('Error:', str(e))
        break

ClientSocket.close()