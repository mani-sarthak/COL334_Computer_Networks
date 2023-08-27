#include <iostream>
#include <thread>
#include <vector>
#include <map>
#include <mutex>
#include <chrono>
#include <cstring>
#include <cstdlib>
#include <cstdio>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

using namespace std;

const char* VAYU_SERVER_IP = "10.237.26.109";
const int VAYU_SERVER_PORT = 9801;

const int NUM_LINES = 1000;

map<int,string> shared_dict;
mutex dict_mutex;


void recieve_lines(int node_id, int client_socket){
    while(shared_dict.size()<NUM_LINES){
        string sendline_command = "SENDLINE\n";
        send(client_socket, sendline_command.c_str(), sendline_command.size(), 0);

        char buffer[1024] = {0};
        int bytes_received = recv(client_socket, buffer, sizeof(buffer), 0);
        if (bytes_received <= 0) {
            // Handle the receive error
            return;
        }
        string received_data(buffer, bytes_received);
        int line_number = 0;
        string line_content;
        sscanf(received_data.c_str(), "%d\n%[^\n]", &line_number, buffer);
        line_content = buffer;

        if (line_number == -1) {
            usleep(1);
            continue;
        }

        lock_guard<mutex> lock(dict_mutex);
        if (shared_dict.find(line_number) == shared_dict.end()) {
            shared_dict[line_number] = line_content;
        }
    }
}

void send_lines_to_peers(int node_id, map<int, int>& peers) {
    while (shared_dict.size() < NUM_LINES) {
        for (const auto& peer : peers) {
            if (peer.first != node_id) {
                lock_guard<mutex> lock(dict_mutex);
                for (const auto& entry : shared_dict) {
                    string data = to_string(entry.first) + "\n" + entry.second;
                    send(peer.second, data.c_str(), data.length(), 0);
                }
            }
        }
    }
}

void submit_lines_to_vayu(int client_socket) {
    while (shared_dict.size() < NUM_LINES) {
        usleep(1000);  // Wait for the dictionary to be populated
    }

    string submit_command = "SUBMIT\naseth@col334-672\n" + to_string(NUM_LINES) + "\n";
    send(client_socket, submit_command.c_str(), submit_command.length(), 0);

    lock_guard<mutex> lock(dict_mutex);
    for (const auto& entry : shared_dict) {
        string data = to_string(entry.first) + "\n" + entry.second;
        send(client_socket, data.c_str(), data.length(), 0);
    }

    char buffer[1024] = {0};
    recv(client_socket, buffer, sizeof(buffer), 0);
    string submission_response(buffer);
    cout << submission_response << endl;
}

void main_function(int node_id) {
    int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket == -1) {
        perror("Socket creation failed");
        return;
    }

    sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(VAYU_SERVER_PORT);
    if (inet_pton(AF_INET, VAYU_SERVER_IP, &server_address.sin_addr) <= 0) {
        perror("Invalid address or address not supported");
        return;
    }

    if (connect(client_socket, (struct sockaddr*)&server_address, sizeof(server_address)) == -1) {
        perror("Connection failed");
        return;
    }

    map<int, int> peer_sockets;
    string peer_ips[4] = {"10.181.0.1", "10.184.0.2", "10.184.0.3", "10.184.0.4"};

    for (int i = 0; i < 4; ++i) {
        if (i != node_id-1) {
            int peer_socket = socket(AF_INET, SOCK_STREAM, 0);
            if (peer_socket == -1) {
                perror("Peer socket creation failed");
                return;
            }

            sockaddr_in peer_address;
            peer_address.sin_family = AF_INET;
            peer_address.sin_port = htons(7001 + i);  // Use ports 9802, 9803, 9804
            if (inet_pton(AF_INET, peer_ips[i].c_str(), &peer_address.sin_addr) <= 0) {
                perror("Invalid address or address not supported");
                return;
            }

            if (connect(peer_socket, (struct sockaddr*)&peer_address, sizeof(peer_address)) == -1) {
                perror("Peer connection failed");
                return;
            }

            peer_sockets[i] = peer_socket;
        }
    }

    thread recv_thread(recieve_lines, node_id, client_socket);
    thread send_thread(send_lines_to_peers, node_id, peer_sockets);
    thread submit_thread(submit_lines_to_vayu, client_socket);

    recv_thread.join();
    send_thread.join();
    submit_thread.join();

    for (const auto& peer : peer_sockets) {
        close(peer.second);
    }

    close(client_socket);
}


int main() {
    //std::thread t0(main_function, 1);
    // std::thread t1(main_function, 1);
    // std::thread t2(main_function, 2);
    // std::thread t3(main_function, 3);

    // t0.join();
    // t1.join();
    // t2.join();
    // t3.join();
    main_function(1);

    return 0;
}