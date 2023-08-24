import socket
import threading
import time
from singleclient import inc_num_lines,recv_input
class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.data_dict={}
        self.connections_lock = threading.Lock()
    
    def connect(self, peer_host, peer_port):
        try:
            self.socket.connect((peer_host, peer_port))
            print(f"Connected to {peer_host}:{peer_port}")
        except socket.error as e:
            print(f"Failed to connect to {peer_host}:{peer_port}. Error: {e}")
    
    def listen(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(10)
        print(f"Listening for connections on {self.host}:{self.port}")

        while True:
            connection, address = self.socket.accept()
            with self.connections_lock:
                self.connections.append(connection)
            print(f"Accepted connection from {address}")
    
    def send_data(self, data):
        with self.connections_lock:
            for connection in self.connections:
                try:
                    connection.sendall(data.encode())
                except socket.error as e:
                    print(f"Failed to send data. Error: {e}")

    def receive_data(self):
        with self.connections_lock:
            for connection in self.connections:
                try:
                    data = connection.recv(1024).decode() # now send received data to all connections
                    # but no point to send data to same guy who has send it.
                    self.data_dict[data[0]]=data[1]
                    print(f"Received data: {data}")
                except socket.error as e:
                    print(f"Failed to receive data. Error: {e}")
    
    def talk_with_vayu(self):
        server_address = ("vayu.iitd.ac.in", 9801)
        sendline_command = b"SENDLINE\n"
        line_num = 1000
        data_dict = self.data_dict
        try:
            start = time.time()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect(server_address)
                while len(self.data_dict) < line_num:
                    s.sendall(sendline_command)
                    received_data = recv_input(s)
                    try:
                        lines = received_data.split("\n")
                        line_number = int(lines[0])
                        line_content = lines[1]
                    except (ValueError, IndexError):
                        continue
                    if line_number == -1:
                        time.sleep(1e-6)
                        continue
                    if line_number not in data_dict:
                        self.data_dict[line_number]=line_content
                        self.send_data([line_number,line_content])
                        data_dict[line_number] = line_content
                    self.receive_data() # Try to receive data till all data hasn't come
                file_name = "output.txt"
                with open(file_name, "w") as file:
                    for key, value in data_dict.items():
                        file.write(f"Key: {key}, Value: {value}\n")
                print(f"Data written to {file_name}")
                print("Submitting...")
                submit_command = b"SUBMIT\naseth@col334-672\n" + str(line_num).encode() + b"\n"
                s.sendall(submit_command)
                for key in data_dict.keys():
                    s.sendall(str(key).encode() + b"\n" + data_dict[key].encode() + b"\n")
                submission_success = recv_input(s)
                print(submission_success)
                inc = inc_num_lines(submission_success)
                if(inc > 0):
                   s.sendall(b"SEND INCORRECT LINES\n")
                for i in range(inc):
                    data = recv_input(s)
                    print(data)
            finish = time.time()
            print(f"Time taken: {finish - start}")
                
        except (socket.timeout, ConnectionError):
            print("Connection error")
        except Exception as e:
            print("An error occurred:", e)

    
    def start(self): # Now we have only one server and so why to create thread of servers.
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()


def get_send():
    peer=Peer("10.184.42.12",6000)
    peer.start()
    # peer.connect("vayu.iitd.ac.in",9801)
    # host1=("10.184.49.71", 6000)
    # host2=("10.184.15.146", 6000)
    # host3=("10.184.1.210", 6000)
    # peer.connect(host1[0], host1[1])
    # peer.connect(host2[0], host2[1])
    # peer.connect(host3[0], host3[1])
    # peer.talk_with_vayu()

get_send()
    