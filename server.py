#!/usr/bin/env python

import select
import socket
import sys
import pymysql

def checkmoney(username, password):
    #connect to database and perform query
    
    #db = pymysql.connect(host="54.149.37.172",port=3306,user="root",passwd="qwe123456",db="slave" )
    db = pymysql.connect("seniordesign.c9btkcvedeon.us-west-2.rds.amazonaws.com","root","qwe123456","senior_design" )
    cursor = db.cursor()
    cursor.execute("select username,money from property where username=%s and password=%s;",(username,password))
    db.close()
    #check if query is empty
    if cursor.rowcount == 0 :
        return 'invalid username or password'
    else:
        result = cursor.fetchall()
        print ('result:%s' % result)
        return (result[0])

def addmoney(username,password,amount):
    #db = pymysql.connect(host="54.149.37.172",port=3306,user="root",passwd="qwe123456",db="slave" )
    db = pymysql.connect("seniordesign.c9btkcvedeon.us-west-2.rds.amazonaws.com","root","qwe123456","senior_design" )
    cursor = db.cursor()
    cursor.execute("select money from property where username=%s and password=%s;",(username,password))
    result = cursor.fetchall()
    result = int(result[0][0])
    money = result + amount
    print ('money:%s' % money)
    cursor.execute("update property set money=%s where username=%s and password=%s;",(money,username,password))
    db.commit()
    db.close()
    
#check username and password
def login(username,password):
    #db = pymysql.connect(host="54.149.37.172",port=3306,user="root",passwd="qwe123456",db="slave" )
    db = pymysql.connect("seniordesign.c9btkcvedeon.us-west-2.rds.amazonaws.com","root","qwe123456","senior_design" )
    cursor = db.cursor()
    cursor.execute("select * from property where username=%s and password=%s;",(username,password))
    db.close()
    if cursor.rowcount == 0 :
        return 0
    else:
        return 1

#decode message from client, take data and socket(s) as parameter
def decode_message(data,s):
    #split username, password and message for database query
    if '0x757365726e616d65:' in str(data) and '0x70617373776f7264:' in str(data):
      data_decode = data.decode("utf-8")
      username = str(data_decode).split('0x757365726e616d65:')[0]
      other_data = str(data_decode).split('0x757365726e616d65:')[1]
      password = str(other_data).split('0x70617373776f7264:')[0]
      message = str(other_data).split('0x70617373776f7264:')[1]

      #user functions
      if message=='checkmoney':
        result = checkmoney(username,password)
        s.send(str(result).encode('utf-8'))
      elif 'addmoney' in message:
        amount_money = message.split('addmoney')[1]
        addmoney(username,password,int(amount_money))
        response_message = "you added money"
        s.send(str(response_message).encode('utf-8'))

    #split username and password for login check
    elif '0x757365726e616d65:' in str(data):
      data_decode = data.decode("utf-8")
      username = str(data_decode).split('0x757365726e616d65:')[0]
      password = str(data_decode).split('0x757365726e616d65:')[1]
    #check if username and password are good
      login_result = str(login(username,password))
      s.send(login_result.encode('utf-8'))

    else:
      print ('%s received from %s'%(message,s.getsockname()))
      return_statement = 'Successful foward from controller .'
      s.send(return_statement.encode('utf-8'))



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
            decode_message(data,s)
          else: # close the socket (connection)
            print('Action complete - closing connection %s with controller.' % (str(address)))
            s.close()
            input.remove(s)
else:
    print('Failed to connect to the controller')
    server.close()

#if running is ever set to zero, we will call this
server.close()
