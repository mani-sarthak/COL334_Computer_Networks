#include <iostream>
#include <fstream>
#include <cstring>
#include <unistd.h>
#include <vector>
#include <map>
#include <chrono>
#include <arpa/inet.h>
using namespace std;

int inc_num_lins(string submission_response){
    size_t pos = submission_response.find(" - ");
    if (pos != string::npos){
        string num_lines_part = submission_response.substr(pos+3);
        size_t pos2 = num_lines_part.find(", ");
        if (pos2 != string::npos){
            return stoi(num_lines_part.substr(pos2+2));
        }
    }
    return -1;
}

string recv_input(int sock){
    string input_buffer = "";
    while(true){
        char packet[1025];
        int bytes  =recv(sock, packet, sizeof(packet)-1, 0);
        if (bytes <= 0){
            break;
        }
        packet[bytes] = '\0';
        input_buffer += packet;
        if(packet[bytes-1] == '\n'){
            break;
        }
    }
    return input_buffer;
}

int main(){
    const char* server_ip = "10.237.26.109";
    int server_port = 9801;
    const char* command = "SENDLINE\n";
    int line_nums = 1000;
    map<int, string> line_map;
    try {
        timeval timeout;
        timeout.tv_sec = 5;
        timeout.tv_usec = 0;
        int s = socket(AF_INET, SOCK_STREAM, 0);
        if(s==-1){
            cout<<"error creating socket" <<endl;
        }

        sockaddr_in server_addr;
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(server_port);
        server_addr.sin_addr.s_addr = inet_addr(server_ip);

        if (connect(s, (struct sockaddr*)&server_addr, sizeof(server_addr)) ==-1){
            cout<<"error connecting to server " << strerror(errno)<<endl;
            close(s);
            return -1;
        }
        cout<<"connected to vayu"<<endl;
        auto start = chrono::high_resolution_clock::now();
        while(line_map.size()<line_nums){
            cout<<line_map.size()<<endl;
            send(s, command, strlen(command), 0);
            string recieved_data = recv_input(s);
            size_t newline_pos = recieved_data.find("\n");
            if (newline_pos != string::npos){
                int line_num = stoi(recieved_data.substr(0, newline_pos));
                string line_content = recieved_data.substr(newline_pos+1);
                if (line_num==-1){
                    usleep(1); // Sleep for a short duration if rate limit exceeded
                    continue;
                }
                if (line_map.find(line_num) == line_map.end()){
                    line_map[line_num] = line_content;
                }
            }
        }
        cout<<"final count: "<<line_map.size()<<endl;
        //printing the dictionary

        cout<<"Unique lines "<<endl;
        ofstream output_file("cpp_output.txt");
        for(const auto &entry: line_map){
            // cout<<entry.first<<": "<<entry.second<<endl;
            output_file<<entry.first<<": "<<entry.second;
        }
        output_file.close();

        // submission

        cout<<"Submitting ...."<<endl;
        string email = "aseth@col334-672\n";
        string submit_command = "SUBMIT\n" + email + to_string(line_map.size())+ "\n";
        send(s, submit_command.c_str(), submit_command.size(), 0);
        for(const auto &entry : line_map){
            string line_submission = to_string(entry.first) + "\n" + entry.second;
            send(s, line_submission.c_str(), line_submission.size(), 0);
        }

        //recieving submission response
        string submission_result = recv_input(s);
        cout << submission_result << endl;
        auto end = std::chrono::high_resolution_clock::now();
        chrono::duration<double> duration = end - start;
        cout << "Time elapsed: " << duration.count() << " seconds" << endl;
        //handling incorrect lines
        int incorrect_lines = inc_num_lins(submission_result);
        if(incorrect_lines>0){
            send(s, "SEND INCORRECT LINES\n", strlen("SEND INCORRECT LINES\n"), 0);
            for(int i=0;i<incorrect_lines;++i){
                string incorrect_line = recv_input(s);
                cout<<incorrect_line<<endl;
            }
        }

        close(s);
    }catch(...){
        cout<<"error"<<endl;
    }
    return 0;
}
