#!/usr/bin/env python

import select
import socket
import sys
#import pymysql
from random import randint

host = 'localhost' # what address is the server listening on
port = 9996 # what port the server accepts connections on
server_port_one = 9997
server_port_two = 9998
backlog = 5  # how many connections to accept
BUFFER_SIZE = 1024 # Max receive buffer size, in bytes, per recv() call

#now initialize the server and accept connections

controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
controller.bind((host,port))
controller.listen(backlog)
input = [controller,] #a list of all connections we want to check for data
                  #each time we call select.select()

#definition here-----------------------------------------------------
def foward_to_server(data_from_client, client_to_controller, controller_to_server, result):
  # Connect controller to ser{ver
  if result == 0: # server is alive if result = 0
    controller_to_server.send(data_from_client) # foward data from client to servers
    data_from_server = controller_to_server.recv(BUFFER_SIZE) # recieve feedback from the server
    client_to_controller.send(data_from_server) # foward back to client
  else: # server is dead
    return_statement = 'Server is down, unable to process request.'
    client_to_controller.send(return_statement.encode('utf-8'))

running = 1 #set running to zero to close the server
server_list = []
print('Controller is up and awaiting connections! \n')
while running:
  inputready,outputready,exceptready = select.select(input,[],[])

  for client_to_controller in inputready: #check each socket that select() said has available data
    if client_to_controller == controller: #if select returns our server socket, there is a new remote socket trying to connect
      client, address = controller.accept()
      input.append(client) #add it to the socket list so we can check it now
      print ('New connection with controller added - id is %s' % str(address))
    else:
      # select has indicated that these sockets have data available to recv
      data_from_client = client_to_controller.recv(BUFFER_SIZE) # Between client and controller - foward response to server
      if data_from_client:
        if ':' in str(data_from_client):
            server_port = str(data_from_client).split(':')[-1]
            server_port = server_port[:-1]
            print('Server identified - the port is %s' % server_port)
            server_list.append(int(server_port))
            print("Server list => %s " % (server_list))
        else:
            #turn = randint(1,2)
            print("Server list length => %s " % (len(server_list)))
            if len(server_list) <= 0:
                return_statement = 'All servers are down, unable to process request.'
                client_to_controller.send(return_statement.encode('utf-8'))
            else:
                turn = randint(0,len(server_list)-1)
                print('The selected server (port) is %s out of the %s number of avaliable servers' % (str(server_list[turn]), len(server_list)))
                controller_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # This will serve as a ping request
                result = controller_to_server.connect_ex((host, int(server_list[turn])))
                foward_to_server(data_from_client, client_to_controller, controller_to_server, result)

      else: #if recv() returned NULL, that usually means the sender wants to close the socket.
        print('Action complete - closing connection %s with server.' % (str(address)))
        client_to_controller.close()
        input.remove(client_to_controller)

#if running is ever set to zero, we will call this
controller.close()
