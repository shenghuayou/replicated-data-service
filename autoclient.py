#!/usr/bin/env python

import socket

TCP_IP = 'localhost'
TCP_PORT = 9996
BUFFER_SIZE = 1024

input_from_html = 'addmoney100'
user_from_html = 'sheng'
pass_from_html = '123'

user_recognizer = '0x757365726e616d65:'
pass_recognizer = '0x70617373776f7264:'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
print('Client is up and connected to controller. \n')

MESSAGE = str(user_from_html) + str(user_recognizer) + str(pass_from_html) + str(pass_recognizer) + str(input_from_html)

while 1:
	s.send(MESSAGE.encode('utf-8'))
	data = s.recv(BUFFER_SIZE)
	if data:
		print('Response from the controller %s </br>' % data)


s.close()
