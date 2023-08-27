#include<iostream>
#include<cstring>
#include<unistd.h>
#include<arpa/inet.h>

using namespace std;

int main(){
    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if(server_socket == -1){
        cout << "creating in socket error" << endl;
        return -1;
    }

    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(1234);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    // if (bind(server_socket, (struct sockaddr *)&server_addr, sizeof(server_addr))==-1){
    //     cout << "bind error" << endl;
    //     return -1;
    // }
    cout<<"server is listening..."<<endl;
    if (listen(server_socket, 5) == -1){
        cout << "server listened but none responded" << endl;
        return -1;
    }
    sockaddr_in client_addr;
    socklen_t client_addr_size = sizeof(client_addr);

    int client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &client_addr_size);
    if(client_socket==-1){
        cout<<"error accepting connection"<<endl;
        return -1;
    }
    cout <<"connection estabilished"<<endl;
    char buffer[1024];

    while(true){
        memset(buffer, 0, sizeof(buffer));
        int recv_size = recv(client_socket, buffer, sizeof(buffer), 0);
        if(recv_size <=0){
            cout << "client disconnected" << endl;
            break;
        }
        cout << "client: " << buffer << endl;

        cout<< "-> ";
        string msg;
        getline(cin, msg);
        send(client_socket, msg.c_str(), msg.size(), 0);
    }
    close(client_socket);
    close(server_socket);
    return 0;
}