#!/usr/bin/env python
import select
import socket
import sys
import csv
import os
import glob
import time
import configparser
import threading
import mapreduce as mr
import json
#from random import randint


host = 'localhost' # what address is the server listening on
port = 9996 # what port the server accepts connections on
backlog = 5  # how many connections to accept
BUFFER_SIZE = 1024 # Max receive buffer size, in bytes, per recv() call

#now initialize the server and accept connections

controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
controller.bind((host,port))
controller.listen(backlog)
input = [controller,] #a list of all connections we want to check for data
                  #each time we call select.select()

#definition here-----------------------------------------------------
def foward_to_server(data_from_client, client_to_controller, controller_to_server, result, serverPort):
  # Connect controller to server
  if result == 0: # server is alive if result = 0

    ## CSV HEADERS FORMAT
    #  Port ID of Server | Start Time of Request | End time of Request

    csvList = []
    csvList.append(serverPort)
    csvList.append(int(round(time.time() * 1000))) # record the serverid and current datetime (controller->server)
    controller_to_server.send(data_from_client) # foward data from client to servers
    data_from_server = controller_to_server.recv(BUFFER_SIZE) # recieve feedback from the server
    csvList.append(int(round(time.time() * 1000))) # append on the current datetime (server->controller)
    # record in %csvIndex%.csv
    config = configparser.ConfigParser()
    config.read('info.ini') # open the file
    ci = config.get('INDEX', 'csvIndex') # get the current value
    targetCSV = 'data/' + ci + '.csv'
    with open(targetCSV, 'a') as outcsv:
        writer = csv.writer(outcsv, delimiter=',', lineterminator='\n')
        writer.writerow(csvList)
    client_to_controller.send(data_from_server) # foward back to client

  else: # server is dead
    return_statement = 'Server is down, unable to process request.'
    client_to_controller.send(return_statement.encode('utf-8'))

def ping_servers(servers, connect_status):
  for server in servers:
    controller_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # This will serve as a ping request
    result = controller_to_server.connect_ex((host, int(server)))
    if result == 0:
      pass # keep port in server list (server is connected)
    else:
      print('Server %s has disconnected from the controller' % str(server))
      #index = servers.index(server) # get the index of the disconnected server
      #connect_status.pop(index) # remove it from the connect_status list
      servers.remove(server) # remove port from server list (server disconnected)

def updateIndexes():
    config = configparser.ConfigParser()
    config.read('info.ini') # open the file

    serverOrder = config.get('SERVER','serverOrder')
    if serverOrder != '':
        print(serverOrder)
    ci = config.get('INDEX', 'csvIndex') # get the current value
    ci = int(ci) + 1
    config.set('INDEX','csvIndex', str(ci)) # set the update value

    mpi = config.get('INDEX', 'mapreduceIndex') # get the current value
    mpi = int(mpi) + 1
    config.set('INDEX','mapreduceIndex', str(mpi)) # set the update value

    with open('info.ini', 'w') as configfile:
        config.write(configfile) # save the updated value(s)
    threading.Timer(60, updateIndexes).start() # start every 60 seconds

def mapper1(line):
    yield (line, 1)

def reducer1(line):
    return (line[0][0], int(line[0][2]) - int(line[0][1]))

def mapper2(line):
    yield line

def reducer2(line):
    key = line[0]
    D = sum(line[1])
    theta = len(line[1])/60
    m =  1/D + theta
    return (key, m)

def mapReduceThread():
    config = configparser.ConfigParser()
    config.read('info.ini') # open the file
    mpi = config.get('INDEX', 'mapreduceIndex')
    if int(mpi) > 1:
        #print('Starting mapreduce on data/%s.csv...' % (mpi))
        targetCSV = 'data/' + mpi + '.csv'
        try:
            with open(targetCSV, 'r') as fi:
                reader = csv.reader(fi)
                output = mr.run(mr.run(reader, mapper1, reducer1), mapper2, reducer2)
            completed = []
            query = ''
            for items in output:
                portID = items[0]
                findInt = config.get('SERVER', str(portID)) # get the current value
                integer = items[1]
                integer = float(integer)*float(findInt)
                completed.append((portID, integer))
            for items in (sorted(completed, key=lambda x: x[1])):
                query += str(items[0]) + ','
            query = query[:-1]
            config.set('SERVER', 'serverOrder', str(query))
            with open('info.ini', 'w') as configfile:
                config.write(configfile)
        except OSError:
            pass
    threading.Timer(60, mapReduceThread).start() # start every 60 seconds

# Create the data folder
try:
    os.makedirs('data')
except OSError:
    pass

# Clear all the contents in data/* (fresh start)
files = [file for file in glob.glob("data/*.csv")]
for file in files:
    os.remove(file)

# Create the info.dat file
info_file = open('info.ini','w+') # recreate contents of info.ini
info_file.close()

# Set up defaults for info.ini
config = configparser.ConfigParser()
config.read('info.ini')
config.add_section('SERVER')
config.set('SERVER', 'serverOrder', '') # default = ''
config.add_section('INDEX')
# mapreduceIndex has to be one less than csvIndex as we want to make sure
# we dont skip any .csv files as we increment them in the same function
config.set('INDEX', 'csvIndex', '1') # default = 1
config.set('INDEX', 'mapreduceIndex', '0') # default = 0
with open('info.ini', 'w') as configfile:
    config.write(configfile)

# function calls for threading, this will run along side the main code
updateIndexes() # update csvIndex and mapreduceIndex in info.ini
mapReduceThread() # thread for map reduce

running = 1 #set running to zero to close the server
server_list = []
already_connected = [] # for random
turn = 0
firstTime = False

print('Controller is up and awaiting connections! \n')
while running:
  inputready,outputready,exceptready = select.select(input,[],[])

  for client_to_controller in inputready: #check each socket that select() said has available data
    if client_to_controller == controller: #if select returns our server socket, there is a new remote socket trying to connect
      client, address = controller.accept()
      input.append(client) #add it to the socket list so we can check it now
      #print ('New connection with controller added - information is %s' % (str(address)))
    else:
      # select has indicated that these sockets have data available to recv
      data_from_client = client_to_controller.recv(BUFFER_SIZE) # Between client and controller - foward response to server
      if data_from_client:
        if '0x4920616d206120736572766572:' in str(data_from_client):
            config = configparser.ConfigParser()
            config.read('info.ini')
            serverOrder = config.get("SERVER", "serverOrder")
            if serverOrder == '':
                server_port = str(data_from_client).split(':')[-1]
                server_port = server_port[:-1] # For some reason on AmazonEC2, we need to remove the [:-1]
                print('Server identified - the port is %s' % (str(server_port)))
                server_list.append(server_port)
                #already_connected.append(False) # for random
                print("Server list => %s " % (server_list))
            elif serverOrder != '':
                server_port = str(data_from_client).split(':')[-1]
                server_port = server_port[:-1] # For some reason on AmazonEC2, we need to remove the [:-1]
                print('Server identified - the port is %s' % (str(server_port)))
                server_list.append(server_port)
                config.set('SERVER', 'serverOrder', serverOrder+','+server_port) # default = 0
                config.set('SERVER', server_port, '1')
                with open('info.ini', 'w') as configfile:
                    config.write(configfile)
                print("Server list => %s " % (server_list))
        if '0x71756575654c656e677468:'  in str(data_from_client):
            queue_server_port = str(data_from_client).split(':')[1]
            queue_length = str(data_from_client).split(':')[2]
            queue_length = queue_length[:-1]
            #print('updating from server %s with queue length %s' % (queue_server_port, queue_length))
            config = configparser.ConfigParser()
            config.read('info.ini')
            config.set('SERVER', queue_server_port, queue_length)
            with open('info.ini', 'w') as configfile:
                config.write(configfile)
        else:
            if len(server_list) <= 0:
                return_statement = 'All servers are down, unable to process request.'
                client_to_controller.send(return_statement.encode('utf-8'))
            else:
                #print("Server list => %s " % (server_list))
                config = configparser.ConfigParser()
                config.read('info.ini')
                serverOrder = config.get("SERVER", "serverOrder")
                if serverOrder != '':
                    #request are equally dustributed to servers in specific order
                    server_list = serverOrder.split(',')
                    if turn < len(server_list) - 1:
                        turn = turn + 1
                    elif turn == len(server_list) - 1:
                        turn = 0
                    print('The selected server (port) is %s out of the %s number of avaliable servers' % (str(server_list[turn]), len(server_list)))
                    controller_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # This will serve as a ping request
                    result = controller_to_server.connect_ex((host, int(server_list[turn])))
                    foward_to_server(data_from_client, client_to_controller, controller_to_server, result, str(server_list[turn]))
                if serverOrder == '':
                    if turn < len(server_list) - 1:
                        turn = turn + 1
                    elif turn == len(server_list) - 1:
                        turn = 0
                    print('The selected server (port) is %s out of the %s number of avaliable servers' % (str(server_list[turn]), len(server_list)))
                    controller_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # This will serve as a ping request
                    result = controller_to_server.connect_ex((host, int(server_list[turn])))
                    foward_to_server(data_from_client, client_to_controller, controller_to_server, result, str(server_list[turn]))

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
        #print('Action complete - closing connection %s with server.' % (str(address)))
        ping_servers(server_list,already_connected) # ping all connected ports, remove any disconnected servers
        client_to_controller.close()
        input.remove(client_to_controller)

#if running is ever set to zero, we will call this
controller.close()
