#!/usr/bin/env python
import socket
import sys
from random import randint

#TCP_IP = 'localhost'
TCP_IP = '52.34.59.51'
TCP_PORT = 9996
BUFFER_SIZE = 1024

if len(sys.argv) > 2 or len(sys.argv) <= 1:
    print('Usage: python bot.py [client-name]')
else:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    print('Client is up and connected to controller. \n')

    while 1: #change to while 1 to loop forever
        randNum = randint(0,9)
        MESSAGE = ''
        if (randNum < 6):
            MESSAGE = str(sys.argv[1]) + '0x757365726e616d65:' + '123' + '0x70617373776f7264:' + 'checkmoney'
        elif (randNum > 6 and randNum < 8):
            MESSAGE = str(sys.argv[1]) + '0x757365726e616d65:' + '123' + '0x70617373776f7264:' + 'addmoney' + str(randint(10,20))
        elif (randNum > 8):
            MESSAGE = str(sys.argv[1]) + '0x757365726e616d65:' + '123' + '0x70617373776f7264:' + 'subtractmoney' + str(randint(10,20))
        s.send(MESSAGE.encode('utf-8'))
        data = s.recv(BUFFER_SIZE)
        if data:
            print('Response from the controller %s' % data)
        pass

    s.close()
