#!/usr/bin/python
# coding: utf8

from random import choice
import sqlite3 as lite

con = lite.connect("zuul.db")
with con:
	sql = con.cursor() 
	que = "SELECT * FROM users"
	sql.execute(que)
	print sql.fetchall()

con.close()