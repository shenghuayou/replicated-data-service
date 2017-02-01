#!/usr/bin/env python

import select
import socket
import sys

host = 'localhost' # what address is the controller listening on
port = 9999 # what port the controller accepts connections on
backlog = 5  # how many connections to accept
BUFFER_SIZE = 1024 # Max receive buffer size, in bytes, per recv() call

# now initialize the controller and accept connections

controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
controller.bind((host,port))
controller.listen(backlog)
input = [controller,] #a list of all connections we want to check for data
#each time we call select.select()

# set up TCP ports for server connections
TCP_IP = 'localhost'
TCP_PORT = 9998
TCP_BUFFER_SIZE = 1024
TCP_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCP_s.connect((TCP_IP, TCP_PORT))
print('Controller is now connected to %s : %s' % (TCP_IP, TCP_PORT))

running = 1 #set running to zero to close the controller
print('Controller is up and awaiting connections from users!')
while running:
    inputready,outputready,exceptready = select.select(input,[],[])
    for s in inputready: #check each socket that select() said has available data
        if s == controller: #if select returns our controller socket, there is a new
        #remote socket trying to connect
            client, address = controller.accept()
            input.append(client) #add it to the socket list so we can check it now
            print('New client added - id is %s'%str(address))

        else:
        # select has indicated that these sockets have data available to recv
            data = s.recv(BUFFER_SIZE)
            if data:
                print('%s received from %s'%(data,s.getsockname()))
                TCP_s.send(data)

            TCP_data = TCP_s.recv(BUFFER_SIZE)
            if TCP_data:
                print('%s received from %s'%(TCP_data,TCP_s.getsockname()))
                s.send(TCP_data)

            else: #if recv() returned NULL, that usually means the sender wants to close the socket.
                print('The user %s has closed the connection with controller.' % (str(address)))
                s.close()
                input.remove(s)

#if running is ever set to zero, we will call this
controller.close()
