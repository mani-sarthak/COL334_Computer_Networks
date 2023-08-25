import socket,time

def inc_num_lines(submission_response):
    parts = submission_response.split(" - ")
    if len(parts) >= 3:
        num_lines_part = parts[2]
        num_lines = int(num_lines_part.split(", ")[1])
        return num_lines
    return None
  
def recv_input(sock):
  """
  Receive input in packets that are coming in the format `1\nsome message here\n`.

  Args:
    sock: The socket object.

  Returns:
    The entire input as a string.
  """

  input_buffer = b''
  while True:
    packet = sock.recv(1024)
    input_buffer += packet
    if packet.endswith(b'\n'):
      break

  # The last packet does not end with a newline, so we need to add it manually.

  if not input_buffer.endswith(b'\n'):
    input_buffer += b'\n'

  return input_buffer.decode('utf-8')


def main():
    server_address = ("vayu.iitd.ac.in", 9801)
    sendline_command = b"SENDLINE\n"
    line_num = 1000
    data_dict = {}
    try:
        start = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(server_address)
            while len(data_dict) < line_num:
                print(len(data_dict))
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
                    data_dict[line_number] = line_content
            # file_name = "output.txt"
            # with open(file_name, "w") as file:
            #     for key, value in data_dict.items():
            #         file.write(f"Key: {key}, Value: {value}\n")
            # print(f"Data written to {file_name}")
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

if __name__ == "__main__":
    main()