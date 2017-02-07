#!/usr/bin/python

import pymysql

# Open database connection
db = pymysql.connect("seniordesign.c9btkcvedeon.us-west-2.rds.amazonaws.com","root","qwe123456","senior_design" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method.
cursor.execute("show databases;")

# Fetch all row using fetchone() method.

data = cursor.fetchall()
for i in data:
	print (i[0])

# disconnect from server
db.close()