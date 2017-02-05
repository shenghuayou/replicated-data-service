#!/usr/bin/env python

import select
import socket
import sys

host = 'localhost' # what address is the server listening on
port = 9986 # what port the server accepts connections on
server_port=9987
backlog = 5  # how many connections to accept
BUFFER_SIZE = 1024 # Max receive buffer size, in bytes, per recv() call

#now initialize the server and accept connections at localhost:50000

controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
controller.bind((host,port))
controller.listen(backlog)
input = [controller,] #a list of all connections we want to check for data
                  #each time we call select.select()

running = 1 #set running to zero to close the server
print('controller is up and awaiting connections! \n')
while running:
  inputready,outputready,exceptready = select.select(input,[],[])

  for s in inputready: #check each socket that select() said has available data

    if s == controller: #if select returns our server socket, there is a new
                    #remote socket trying to connect
      client, address = controller.accept()
      input.append(client) #add it to the socket list so we can check it now
      print ('New connection with controller added - id is %s'%str(address))

    else:
      # select has indicated that these sockets have data available to recv
      data = s.recv(BUFFER_SIZE)
      if data:
        #make connection to server or check if server is running
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result=s2.connect_ex((host, server_port))
        if result ==0:
            s2.send(data)
            return_statement = '101 - Success.'
            s.send(return_statement.encode('utf-8'))
        else:
            return_statement = 'server is down'
            s.send(return_statement.encode('utf-8'))

      else: #if recv() returned NULL, that usually means the sender wants
            #to close the socket.
        print('Action complete - closing connection %s with server.' % (str(address)))
        s.close()
        input.remove(s)

#if running is ever set to zero, we will call this
controller.close()
