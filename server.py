#!/usr/bin/env python

import select
import socket
import sys
import pymysql

def checkmoney():
 db = pymysql.connect("seniordesign.c9btkcvedeon.us-west-2.rds.amazonaws.com","root","qwe123456","senior_design" )
 cursor = db.cursor()
 cursor.execute("use senior_design;")
 cursor.execute("select * from property where name='client1';")
 result = cursor.fetchall()
 db.close()
 return (result[0])


host = 'localhost' # what address is the server listening on
port = 9997 # what port the server accepts connections on
backlog = 5  # how many connections to accept
BUFFER_SIZE = 1024 # Max receive buffer size, in bytes, per recv() call

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen(backlog)
input = [server,] #a list of all connections we want to check for data
                  #each time we call select.select()

running = 1 #set running to zero to close the server
print('Server is up and connecting to the controller! \n')
controller_port = 9996
server_to_controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection_result = server_to_controller.connect_ex((host, controller_port))
if connection_result == 0:
    print('Successful connection to the controller')
    identify_as_server = str('0x4920616d206120736572766572:')+str(port)
    server_to_controller.send(identify_as_server.encode('utf-8')) # foward string to identify as server to the controller
    while running:
      inputready,outputready,exceptready = select.select(input,[],[])
      for s in inputready: #check each socket that select() said has available data
        if s == server: #if select returns our server socket, there is a new remote socket trying to connect
          client, address = server.accept()
          input.append(client) #add it to the socket list so we can check it now
          print ('New connection with server added - id is %s'%str(address))
        else:
          # select has indicated that these sockets have data available to recv
          data = s.recv(BUFFER_SIZE)
          if data:
            #execute database queries here-----------------------------------------------------
            if data.decode("utf-8")=='checkmoney':
              result = checkmoney()
              s.send(str(result).encode('utf-8'))
            else:
              print ('%s received from %s'%(data,s.getsockname()))
              return_statement = 'Successful foward from controller .'
              s.send(return_statement.encode('utf-8'))
          else: # close the socket (connection)
            print('Action complete - closing connection %s with controller.' % (str(address)))
            s.close()
            input.remove(s)
else:
    print('Failed to connect to the controller')
    server.close()

#if running is ever set to zero, we will call this
server.close()
