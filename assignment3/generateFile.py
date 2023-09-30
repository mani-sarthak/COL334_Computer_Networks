n = 25
file = 'testcase.txt'
with open(file, 'w') as f:
    for i in range(n):
        f.write(f'this is line number {i}\n')
f.close()