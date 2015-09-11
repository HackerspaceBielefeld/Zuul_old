#!/usr/bin/python3
# coding: utf8

from random import choice
import sqlite3 as lite
import hashlib
from time import *

def md5(s):
	ss = str(s).encode("utf-8")
	return hashlib.md5(ss).hexdigest()

def timestamp(offset=0):
	t = int(time()) + int(offset)
	return strftime("%Y-%m-%d %H:%M:%S",localtime(t))
	
	
# funktion zum erzeugen willkÃ¼rlicher strings
def random(num):
	ret = ""
	rand_arr = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","y","Z","0","1","2","3","4","5","6","7","8","9"]
	for i in range(num):
		ret+=choice(rand_arr)
	return ret
	
# verbindet die datenbank
#ungeprüft
def sql_connect(file):
	con = lite.connect(file)
	return con

# funktion zur sql abfrage
#TODO
def sql(con,que):
	cur = con.cursor()
	if que.startswith("SELECT") or que.startswith("select"):
		cur.execute(str(que))
		return cur.fetchall()
	else:
		#try:
			cur.execute(str(que))
			con.commit()
			return True
		#except:
		#	return False

# schließt db
def sql_close(con):
	if con:
		con.close()
		return True
	return False

# entfernt gefährliche zeichen
#TODO
def no_inject(inp):
	inp = str(inp)
	return inp.replace("'","`");
