#include<iostream>
#include<cstring>
#include<unistd.h>
#include<arpa/inet.h>
using namespace std;
int main(){
    int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if(client_socket == -1){
        cout << "creating in socket error" << endl;
        return -1;
    }

    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(1234);
    server_addr.sin_addr.s_addr = inet_addr("0.0.0.0");

    if (connect(client_socket,(struct sockaddr *)&server_addr, sizeof(server_addr))==-1){
        cout << "connect error" << std::endl;
        return -1;
    }
    cout << "connection estabilished to server" << endl;
    char buffer[1024];
    while(true){
        cout<< "-> ";
        string message;
        getline(cin, message);
        send(client_socket, message.c_str(), message.size(), 0);
        memset(buffer, 0, sizeof(buffer));
        int bytes = recv(client_socket, buffer, sizeof(buffer), 0);
        if (bytes <= 0){
            cout << "server disconnected" << endl;
            break;
        }

        cout << "server: " << buffer << endl;
    }
    close(client_socket);

    return 0;
}