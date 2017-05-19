#!/usr/bin/python

import socket
import cgi

print ("Content-type:text/html\r\n\r\n")
print ('<title>Login Client</title>')

#get data from HTML
form = cgi.FieldStorage()
user_from_html = form.getvalue('register_user')
pass_from_html = form.getvalue('register_pass')
money_from_html = form.getvalue('register_money')
switch = 1

#recognizer to recognize where username and password are
register_recognizer = '0x7265676973746572_1:'
register_recognizer2 = '0x7265676973746572_2:'

#check if variable is int
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


#check if input value equal to None and money is int
if str(user_from_html) == 'None':
	switch = 0
if str(pass_from_html) == 'None':
	switch = 0
if str(money_from_html) == 'None' or RepresentsInt(money_from_html) == False:
	switch = 0

if switch == 1:
	#connect to server
	TCP_IP = 'localhost'
	TCP_PORT = 9996
	BUFFER_SIZE = 1024
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	print('Register client is up and connected to controller. </br>')

	#send register info to server
	MESSAGE = str(user_from_html) + str(register_recognizer) + str(pass_from_html) + str(register_recognizer2) + str(money_from_html)
	s.send(MESSAGE.encode('utf-8')) # Send request to server(s)
	data = s.recv(BUFFER_SIZE)
	if data:
		decode_data=str(data.decode('utf-8'))
		print('<META HTTP-EQUIV=refresh CONTENT=\"0;URL=http://localhost:8888/login.html\"">')
		print('<script> alert("%s")</script>' % decode_data)
	s.close()
else:
	print('<META HTTP-EQUIV=refresh CONTENT=\"0;URL=http://localhost:8888/register.html\"">')
	print('<script> alert("username and password can not be blank, money can not be letters")</script>')
