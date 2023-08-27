#include <iostream>
#include <cstring>
#include <vector>
#include <thread>
#include <mutex>
#include <unistd.h>
#include <arpa/inet.h>

using namespace std;

vector<int> clients;
void handle_client(int client_socket) {
    clients.push_back(client_socket);
    cout << "Client " << client_socket << " connected." <<endl;

    char buffer[1024];
    while (true) {
        memset(buffer, 0, sizeof(buffer));
        int bytes_received = recv(client_socket, buffer, sizeof(buffer), 0);
        if (bytes_received <= 0) {
            cout << "Client " << client_socket << " disconnected." << std::endl;
            break;
        }

        cout << "Received from client " << client_socket << ": " << buffer << endl;

        for (auto client : clients) {
            if (client != client_socket) {
                send(client, buffer, bytes_received, 0);
            }
        }
    }

    close(client_socket);
    clients.erase(remove(clients.begin(), clients.end(), client_socket), clients.end());
}

int main() {
    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == -1) {
        cerr << "Error creating socket" << endl;
        return 1;
    }

    sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(9001);
    server_address.sin_addr.s_addr = INADDR_ANY;

    // if (bind(server_socket, (struct sockaddr *)&server_address, sizeof(server_address)) == -1) {
    //     std::cerr << "Error binding socket" << std::endl;
    //     return 1;
    // }

    if (listen(server_socket, 5) == -1) {
        cerr << "Error listening" << endl;
        return 1;
    }

    cout << "Server listening on port 12345..." << endl;

    while (true) {
        sockaddr_in client_address;
        socklen_t client_addr_size = sizeof(client_address);
        int client_socket = accept(server_socket, (struct sockaddr *)&client_address, &client_addr_size);
        if (client_socket == -1) {
            cerr << "Error accepting connection" << endl;
            continue;
        }

        // Create a lambda expression that calls the handle_client() function.
        auto client_thread = std::thread([client_socket]() {
            handle_client(client_socket);
        });

        // Detach the thread so that it does not block the main thread.
        client_thread.detach();
    }

    close(server_socket);

    return 0;
}
