import serial

port = serial.Serial("COM4", 115200, timeout=1)

def read_ser(num_char = 1):
    string = port.read(num_char)
    return string.decode()

def write_ser(cmd):
    cmd = cmd + '\n'
    port.write(cmd.encode())

while(1):
    string = read_ser(255)
    if(len(string)):
        print(string)

    cmd = input()
    print(cmd);
    if(cmd):
        write_ser(cmd)