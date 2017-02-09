#!/usr/bin/env python

import socket

TCP_IP = 'localhost'
TCP_PORT = 9996
BUFFER_SIZE = 1024
from random import randint

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
print('Client is up and connected to controller. \n')

while 1:
    MESSAGE = str(randint(0,100))
    s.send(MESSAGE.encode('utf-8'))
    data = s.recv(BUFFER_SIZE)
    if data:
        print('Response from the controller %s' % data)
    pass

s.close()
