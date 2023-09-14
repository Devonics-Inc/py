import socket
import sys
import time



ip = "192.168.1.177"
port = 8888




# Create socket for server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
print("Do Ctrl+c to exit the program !!")

# Let's send data through UDP protocol
while True:
    send_data = input("input numbers example: 100,200,300")
    s.sendto(send_data.encode('utf-8'), (ip, port))
    print("\n\n 1. Client Sent : ", send_data, "\n\n")
    data, address = s.recvfrom(4096)
    print("\n\n 2. Client received : ", data.decode('utf-8'), "\n\n")
    time.sleep(10)
# close the socket
s.close()
