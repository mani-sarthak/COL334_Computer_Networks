import socket
import threading
import time
# Global list to store received data
received_data = []

# Function to handle communication with clients
def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)  # Adjust buffer size as needed
        if not data:
            break
        # Process data if needed
        # Forward data to other clients
        for other_client in other_clients:
            other_client.send(data)
        received_data.append(data)

    client_socket.close()

# Function to handle communication with servers
def handle_server(server_socket):
    while True:
        data = server_socket.recv(1024)  # Adjust buffer size as needed
        # Process data if needed
        received_data.append(data)
        for other_client in other_clients:
            other_client.send(data)
        # for k in servers:
        #     k.send(data)

# Function to listen for client connections
def listen_for_clients():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 5000))  # Replace with your intermediary server's IP and port
    server.listen(3)  # Listen for up to 3 clients
    print("heloo I am there")
    while True:
        print("heloo I am there")
        client_socket, client_address = server.accept()
        print("Connected to:", client_address)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
        other_clients.append(client_socket)
        client_thread.join()

# Main server communication loop
def main_server_communication():
    main_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_server.connect(("127.0.0.1", 7000))
    print("connected to main server")
    while True:
        command = input("Enter command: ")
        # if command == "sendline":
        main_server.send(command.encode())
        line = main_server.recv(1024).decode()  # Adjust buffer size as needed
            # Send line to other clients
        for client in other_clients:
            client.send(line.encode())
        received_data.append(line)
        print(line)
        break
    main_server.close()

# Function to connect to other servers
def connect_to_servers():
    for server_info in server_list:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server_info['ip'], server_info['port']))
        server_thread = threading.Thread(target=handle_server, args=(server_socket,))
        server_thread.start()
        servers.append(server_socket)
        server_thread.join()

# Create a list to store other client sockets and servers
other_clients = []
servers = []

# List of server information (ip and port)
# server_list = [
#     {'ip': '127.0.0.1', 'port': 5001},
#     {'ip': '127.0.0.1', 'port': 5002},
#     {'ip': '127.0.0.1', 'port': 5003}
# ]
server_list = [
    {'ip': '127.0.0.1', 'port': 5001},
]


# Start thread to listen for client connections
client_listener_thread = threading.Thread(target=listen_for_clients)
client_listener_thread.start()
# time.sleep(1)
# Start thread to connect to other servers
server_connection_thread = threading.Thread(target=connect_to_servers)
server_connection_thread.start()

# Start the main server communication thread
main_server_thread = threading.Thread(target=main_server_communication)
main_server_thread.start()

# Wait for all threads to finish
server_connection_thread.join()
main_server_thread.join()
client_listener_thread.join()

print(received_data)