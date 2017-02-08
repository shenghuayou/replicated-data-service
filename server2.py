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
port = 9998 # what port the server accepts connections on
backlog = 5  # how many connections to accept
BUFFER_SIZE = 1024 # Max receive buffer size, in bytes, per recv() call

#now initialize the server and accept connections at localhost:50000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen(backlog)
input = [server,] #a list of all connections we want to check for data
                  #each time we call select.select()

running = 1 #set running to zero to close the server
print('Server is up and awaiting connections! \n')
while running:
  inputready,outputready,exceptready = select.select(input,[],[])

  for s in inputready: #check each socket that select() said has available data

    if s == server: #if select returns our server socket, there is a new
                    #remote socket trying to connect
      client, address = server.accept()
      input.append(client) #add it to the socket list so we can check it now
      print ('New connection with controller added - id is %s'%str(address))

    else:
      # select has indicated that these sockets have data available to recv
      data = s.recv(BUFFER_SIZE)
      if data:
        #execute database queries here-----------------------------------------------------
        if data.decode("utf-8")=='checkmoney':
          result=checkmoney()
          s.send(str(result).encode('utf-8'))

        else:
          print ('%s received from %s'%(data,s.getsockname()))
          #Uncomment below to echo the recv'd data back
          #to the sender... loopback!
          return_statement = 'Successful foward from controller .'
          s.send(return_statement.encode('utf-8'))
      else: #if recv() returned NULL, that usually means the sender wants
            #to close the socket.
        print('Action complete - closing connection %s with controller.' % (str(address)))
        s.close()
        input.remove(s)

#if running is ever set to zero, we will call this
server.close()
