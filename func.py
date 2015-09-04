#!/usr/bin/python
# coding: utf8

from random import choice
import sqlite3 as lite

def isset(vname):
	if vname in locals() or vname in globals():
		return vname
	return False

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
	print file
	con = lite.connect(file)
	with con:
		return con.cursor()   
	return False

# funktion zur sql abfrage
#TODO
def sql(cursor,que,onlyone=False):
	if que.startswith("SELECT") or que.startswith("select"):
		cursor.execute(str(que))

		if bool(onlyone) == True:
			r = cursor.fetchone()
		else:
			r = cursor.fetchall()
		return r
	else:
		return cursor.execute(str(que))

# schließt db
def sql_close(cursor):
	if cursor:
		cursor.close()
		return True
	return False

# entfernt gefährliche zeichen
#TODO
def no_inject(str):
	return str.replace("'","`");
