import socket
import uuid

s0 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s0.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
dest = ("localhost", 57810) #57710)

s0.sendto(b"C:/DJI_0018.MOV",dest)