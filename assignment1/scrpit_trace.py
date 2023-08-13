import subprocess,sys,re,socket
def ping(host,m):
    output = subprocess.run(['ping','-c','1','-m',f'{m}',host],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True)
    match = re.search(r'bytes from (\d+\.\d+\.\d+\.\d+): Time', output.stdout)
    if output.returncode==2 and match!=None:
        return (False,match.group(1))
    elif output.returncode==2 and match==None:
        return (False,'a')
    return (True,'0')
def trace_route(destination):
    m=0
    a = False
    l=[]
    i=0
    p=[]
    q=[]
    while(i<64):
        m+=1
        a,b = ping(destination,m)
        if a==True:
            break
        else:
            l.append(b)
        i+=1
    for i in range(len(l)):
        if l[i]=='a':
            print(f'{i+1} '+ '* '+ '* '+ '*')
        else:
            output = subprocess.run(['ping','-c','1',l[i]],stdout = subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
            match1 = re.search(r'time=(\d+\.\d+)\s*ms', output.stdout)
            output = subprocess.run(['ping','-c','1',l[i]],stdout = subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
            match2 = re.search(r'time=(\d+\.\d+)\s*ms', output.stdout)
            output = subprocess.run(['ping','-c','1',l[i]],stdout = subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
            match3 = re.search(r'time=(\d+\.\d+)\s*ms', output.stdout)
            ans  = f'{i+1} '+ f'{l[i]} ({l[i]}) '
            if match1!=None:
                ans += match1.group(1) + ' ms '
            else:
                ans+= "* "
            if match2!=None:
                ans += match2.group(1) + ' ms '
            else:
                ans+= "* "
            if match3!=None:
                ans += match3.group(1) + ' ms '
            else:
                ans+= "* "
            print(ans)
    wip_address = socket.gethostbyname(destination)   
    ans = f'{len(l)+1} '+ f'{destination} ({wip_address}) '
    output = subprocess.run(['ping','-c','1',destination],stdout = subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
    match1 = re.search(r'time=(\d+\.\d+)\s*ms', output.stdout)
    output = subprocess.run(['ping','-c','1',destination],stdout = subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
    match2 = re.search(r'time=(\d+\.\d+)\s*ms', output.stdout)
    output = subprocess.run(['ping','-c','1',destination],stdout = subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
    match3 = re.search(r'time=(\d+\.\d+)\s*ms', output.stdout)
    if match1!=None:
        ans += match1.group(1) + ' ms '
    else:
        ans+= "* "
    if match2!=None:
        ans += match2.group(1) + ' ms '
    else:
        ans+= "* "
    if match3!=None:
        ans += match3.group(1) + ' ms '
    else:
        ans+= "* "
    print(ans)
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python help.py <target_host>")
        sys.exit(1)
    target_host = sys.argv[1]
    trace_route(target_host)
