#!/usr/bin/python

import socket
import cgi

print ("Content-type:text/html\r\n\r\n")
print ('<title>Client</title>')

#get data from HTML
form = cgi.FieldStorage()
input_from_html =  form.getvalue('html_input')
user_from_html = form.getvalue('html_user')
pass_from_html = form.getvalue('html_pass')

#recognizer to recognize where username and password are
user_recognizer = '0x757365726e616d65:'
pass_recognizer = '0x70617373776f7264:'

#check if input value equal to None
if str(input_from_html) == 'None':
	input_from_html = ''
if str(user_from_html) == 'None':
	user_from_html = ''
if str(pass_from_html) == 'None':
	pass_from_html = ''

#connect to server
TCP_IP = 'localhost'
TCP_PORT = 9996
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
print('Client is up and connected to controller. </br>')

i = 0
while i < 1:
	MESSAGE = str(user_from_html) + str(user_recognizer) + str(pass_from_html) + str(pass_recognizer) + str(input_from_html)
	s.send(MESSAGE.encode('utf-8')) # Send request to server(s)
	data = s.recv(BUFFER_SIZE)
	if data: # POST request
		print('Response from the controller %s </br>' % data)
		print("<META HTTP-EQUIV=refresh CONTENT=\"5;URL=http://localhost:8888/\">\n") # POST request -> redirect client 
																			# this closes the connection, remakes new one.
		
	pass
	i += 1
s.close()
