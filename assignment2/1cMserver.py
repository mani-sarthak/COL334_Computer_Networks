import socket
import threading

# Define a list of server addresses (host, port)
server_addresses = [ ('vayu.iitd.ac.in', 9801),('10.184.42.197', 5000)]  # Example addresses

def client_program(server_address):

    client_socket = socket.socket()  # instantiate
    client_socket.connect(server_address)  # connect to the server

    message = "SENDLINE\n"   # take input

    while message.lower().strip() != 'bye':
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(2048).decode()  # receive response

        print('Received from server: ' + data)  # show in terminal

        message = "SENDLINE\n"   # again take input

    client_socket.close()  # close the connection

# Create a list to hold thread objects
threads = []

# Create a thread for each server connection
for address in server_addresses:
    thread = threading.Thread(target=client_program, args=(address,))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

print("All server connections have been attempted.")
