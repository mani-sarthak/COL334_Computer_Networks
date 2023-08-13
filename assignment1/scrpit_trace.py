import subprocess
import sys
import re
import socket

def ping(host,m):
    output = subprocess.run(['ping','-c','1','-m',f'{m}',host],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True)
    match = re.search(r'bytes from (\d+\.\d+\.\d+\.\d+): Time', output.stdout)
    if output.returncode==2:
        return (False,match.group(1))
    return (True,'0')

def trace_route(destination):
    m=0
    a = False
    l=[]
    i=0
    while(i<64):
        m+=1
        a,b = ping(destination,m)
        if a==True:
            break
        else:
            l.append(b)
        i+=1
    
    for i in range(len(l)):
        output = subprocess.run(['ping','-c','1',l[i]],stdout = subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
        match = re.search(r'time=(\d+\.\d+)\s*ms', output.stdout)
        print(f'{i+1} '+ f'{l[i]} ({l[i]}) '+ match.group(1)+' ms')
    wip_address = socket.gethostbyname(destination)
    
    output = subprocess.run(['ping','-c','1',destination],stdout = subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
    match = re.search(r'time=(\d+\.\d+)\s*ms', output.stdout)
    print(f'{len(l)+1} '+ f'{destination} ({wip_address}) '+ match.group(1)+' ms')
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python help.py <target_host>")
        sys.exit(1)
    
    target_host = sys.argv[1]
    trace_route(target_host)
