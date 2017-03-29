#!/usr/bin/env python

import select
import socket
import sys
#import pymysql
import csv
import os
import glob
import datetime
import ConfigParser
import threading
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
  # Connect controller to server
  if result == 0: # server is alive if result = 0
    # record the serverid and current datetime (controller->server)
    controller_to_server.send(data_from_client) # foward data from client to servers
    data_from_server = controller_to_server.recv(BUFFER_SIZE) # recieve feedback from the server
    # append on the current datetime (server->controller), record in csv_index.csv
    client_to_controller.send(data_from_server) # foward back to client

  else: # server is dead
    return_statement = 'Server is down, unable to process request.'
    client_to_controller.send(return_statement.encode('utf-8'))

def ping_servers(servers, connect_status):
  for server in servers:
    controller_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # This will serve as a ping request
    result = controller_to_server.connect_ex((host, server))
    if result == 0:
      pass # keep port in server list (server is connected)
    else:
      print('Server %s has disconnected from the controller' % (server))
      index = servers.index(server) # get the index of the disconnected server
      connect_status.pop(index) # remove it from the connect_status list
      servers.remove(server) # remove port from server list (server disconnected)

def updateIndex():
    config = ConfigParser.ConfigParser()
    config.read('info.ini') # open the file
    ci = config.get('INDEX', 'CurrentIndex') # get the current value
    ci = int(ci) + 1
    config.set('INDEX','CurrentIndex', str(ci)) # set the update value
    with open('info.ini', 'w') as configfile:
        config.write(configfile) # save the updated value(s)
    threading.Timer(60, updateIndex).start() # start every 60 seconds

# Create the data folder, will need to clear all contents
# of data folder at restart of controller
try:
    os.makedirs('data')
except OSError:
    pass

files = [file for file in glob.glob("data/*.csv")]
for file in files:
    os.remove(file)

# Create the info.dat file which will be used later for
# determining server order and make it empty
info_file = open('info.ini','w+')
info_file.close()
config = ConfigParser.ConfigParser()
config.read('info.ini')
config.add_section('SERVER')
config.add_section('INDEX')
config.set('INDEX', 'CurrentIndex', 0)
with open('info.ini', 'w') as configfile:
    config.write(configfile)

# start calling f now and every 60 sec thereafter
updateIndex()

running = 1 #set running to zero to close the server
server_list = []
already_connected = []
turn = 0

print('Controller is up and awaiting connections! \n')
while running:
  inputready,outputready,exceptready = select.select(input,[],[])

  for client_to_controller in inputready: #check each socket that select() said has available data
    if client_to_controller == controller: #if select returns our server socket, there is a new remote socket trying to connect
      client, address = controller.accept()
      input.append(client) #add it to the socket list so we can check it now
      print ('New connection with controller added - information is %s' % (str(address)))
    else:
      # select has indicated that these sockets have data available to recv
      data_from_client = client_to_controller.recv(BUFFER_SIZE) # Between client and controller - foward response to server
      if data_from_client:
        if '0x4920616d206120736572766572:' in str(data_from_client):
            server_port = str(data_from_client).split(':')[-1]
            server_port = server_port # For some reason on AmazonEC2, we need to remove the [:-1]
            print('Server identified - the port is %s' % (str(server_port)))
            server_list.append(int(server_port))
            already_connected.append(False)
            print("Server list => %s " % (server_list))
        else:
            if len(server_list) <= 0:
                return_statement = 'All servers are down, unable to process request.'
                client_to_controller.send(return_statement.encode('utf-8'))
            else:
              #request are equally dustributed to servers
                if turn < len(already_connected):
                    print('The selected server (port) is %s out of the %s number of avaliable servers' % (str(server_list[turn]), len(server_list)))
                    controller_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # This will serve as a ping request
                    result = controller_to_server.connect_ex((host, int(server_list[turn])))
                    foward_to_server(data_from_client, client_to_controller, controller_to_server, result)
                    already_connected[turn] = True
                    turn = turn + 1
                else:
                    turn = 0
                    print('The selected server (port) is %s out of the %s number of avaliable servers' % (str(server_list[turn]), len(server_list)))
                    controller_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # This will serve as a ping request
                    result = controller_to_server.connect_ex((host, int(server_list[turn])))
                    foward_to_server(data_from_client, client_to_controller, controller_to_server, result)
                    already_connected[turn] = True
                    turn = turn + 1

                #requests are randomly distributed to servers
                # turn = randint(0,len(server_list)-1) # determine which server to direct to
                # if already_connected[turn] == False: # reconnect
                #     print('The selected server (port) is %s out of the %s number of avaliable servers' % (str(server_list[turn]), len(server_list)))
                #     controller_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # This will serve as a ping request
                #     result = controller_to_server.connect_ex((host, int(server_list[turn])))
                #     foward_to_server(data_from_client, client_to_controller, controller_to_server, result)
                #     already_connected[turn] = True
                # else: # already connected
                #     print('The selected server (port) is %s out of the %s number of avaliable servers' % (str(server_list[turn]), len(server_list)))
                #     foward_to_server(data_from_client, client_to_controller, controller_to_server, result)
                #     already_connected[:] = [False] * len(already_connected) # reset to false
                #     already_connected[turn] = True

      else: #if recv() returned NULL, that usually means the sender wants to close the socket.
        print('Action complete - closing connection %s with server.' % (str(address)))
        ping_servers(server_list,already_connected) # ping all connected ports, remove any disconnected servers
        client_to_controller.close()
        input.remove(client_to_controller)

#if running is ever set to zero, we will call this
controller.close()
