#include <iostream>
#include <cstdlib>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>

int main() {
    // Create socket
    int serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket == -1) {
        std::cerr << "Error creating socket." << std::endl;
        return -1;
    }

    // Bind socket
    sockaddr_in serverAddress;
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = INADDR_ANY;
    serverAddress.sin_port = htons(9001);  // Port number

    if (bind(serverSocket, (struct sockaddr*)&serverAddress, sizeof(serverAddress)) == -1) {
        std::cerr << "Error binding socket." << std::endl;
        return -1;
    }

    // Listen for connections
    if (listen(serverSocket, 5) == -1) {
        std::cerr << "Error listening on socket." << std::endl;
        return -1;
    }

    std::cout << "Server waiting for incoming connections..." << std::endl;

    // Accept connections
    int clientSocket;
    sockaddr_in clientAddress;
    socklen_t clientAddrSize = sizeof(clientAddress);

    clientSocket = accept(serverSocket, (struct sockaddr*)&clientAddress, &clientAddrSize);
    if (clientSocket == -1) {
        std::cerr << "Error accepting connection." << std::endl;
        return -1;
    }

    std::cout << "Client connected." << std::endl;

    // Send and receive messages
    char message[1024];
    while (true) {
        memset(message, 0, sizeof(message));

        // Receive message from client
        recv(clientSocket, message, sizeof(message), 0);
        std::cout << "Client: " << message << std::endl;

        std::cout << "-> ";
        // Send message to client
        std::cin.getline(message, sizeof(message));
        send(clientSocket, message, strlen(message), 0);
    }

    // Close sockets
    close(clientSocket);
    close(serverSocket);
 
    return 0;
}
