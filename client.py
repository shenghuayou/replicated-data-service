#!/usr/bin/env python
 
import socket
 
 
TCP_IP = 'localhost'
TCP_PORT = 9992
BUFFER_SIZE = 1024
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
while 1:
	MESSAGE = input('Type something: ')
	s.send(MESSAGE.encode('utf-8'))
	data = s.recv(BUFFER_SIZE)
	print(data)
	pass

s.close()