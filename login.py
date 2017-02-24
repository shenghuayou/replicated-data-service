#!/usr/bin/python

import socket
import cgi

print ("Content-type:text/html\r\n\r\n")
print ('<title>Client</title>')

#get data from HTML
form = cgi.FieldStorage()
user_from_html = form.getvalue('login_user')
pass_from_html = form.getvalue('login_pass')

#recognizer to recognize where username and password are
user_recognizer = '0x757365726e616d65:'

#check if input value equal to None
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
print('Login client is up and connected to controller. </br>')

#send login info to server
MESSAGE = str(user_from_html) + str(user_recognizer) + str(pass_from_html)
s.send(MESSAGE.encode('utf-8')) # Send request to server(s)
data = s.recv(BUFFER_SIZE)
if data: # POST request
	if str(data) == '1':
		#if user is verified. pass user infomation to dashboard.html through url
		#may need encode url later for security
		print('<META HTTP-EQUIV=refresh CONTENT=\"0;URL=http://localhost:8888/dashboard.html?login_user=%s&login_pass=%s\">\n' % 
			(user_from_html,pass_from_html))
	else:
		print('failed to go next page')
s.close()

