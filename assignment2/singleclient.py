import socket
import time



def extract_num_lines(submission_response):
    parts = submission_response.split(" - ")
    if len(parts) >= 3:
        num_lines_part = parts[2]
        num_lines = int(num_lines_part.split(", ")[5])
        return num_lines
    return None


def maxlines():
    server_address = ("vayu.iitd.ac.in", 9801)
    sendline_command = b"SENDLINE\n"
    submit_command = b"SUBMIT\naseth@col334-672\n1\n1\n"

    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(server_address)
            flag = 0
            
            while(flag==0):

                s.sendall(sendline_command)
                initial_response = s.recv(4096).decode("utf-8")

                if initial_response.strip() != "-1":
                    flag = 1 
                    num_lines = int(initial_response.split("\n")[0])  
                    submission_payload = submit_command + str(num_lines).encode() + b"\"Line 1\"\n"
    
                    # Send the submission payload

                    s.sendall(submission_payload)
                    submission_success = s.recv(4096).decode("utf-8")
                    num_lines = extract_num_lines(submission_success)
                    # print(num_lines)
                    return num_lines

    except (socket.timeout, ConnectionError):
        pass
    except Exception as e:
        pass



def receive_all(sock, buffer_size=4096):
    received_data = b""
    while True:
        packet = sock.recv(buffer_size)
        if not packet:
            break
        received_data += packet
        if b"\n" in packet:
            break
    return received_data

def main():
    server_address = ("vayu.iitd.ac.in", 9801)
    sendline_command = b"SENDLINE\n"
    line_num = maxlines()
    data_dict = {}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(server_address)

            while(len(data_dict) < line_num):
                print(len(data_dict))
                s.sendall(sendline_command)
                received_data = receive_all(s).decode("utf-8")
                if received_data.strip() != "-1":
                    
                    try:
                        line_number = int(received_data.strip().split("\n")[0])
                    except ValueError:
                        continue  # Continue to the next iteration of the loop

                    line_content = received_data.strip().split("\n")[1]
                    if line_number not in data_dict:
                        data_dict[line_number] = line_content
                time.sleep(1e-8)
        

    except (socket.timeout, ConnectionError):
        print("Connection error")
        pass
    except Exception as e:
        print("An error occurred:", e)
        pass
    
    
    

if __name__ == "__main__":
    main()


