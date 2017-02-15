#!/usr/bin/python
import socket

print ("Content-type:text/html\r\n\r\n")
print ('<title>Client</title>')
print ('<form action="action_page.php">')
print ('Function:<br>')
print ('<input type="text" name="func" value="check">')
TCP_IP = 'localhost'
TCP_PORT = 9996
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
print('Client is up and connected to controller. </br>')

i = 0
while i < 5:
	
    MESSAGE = 'hellow#input'#('Type something: ')
    s.send(MESSAGE.encode('utf-8'))
    data = s.recv(BUFFER_SIZE)
    if data:
        print('Response from the controller %s </br>' % data)
    pass
    i += 1
s.close()

