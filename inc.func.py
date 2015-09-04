from random import choice
import sqlite3 as lite
import hashlib

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
	con = lite.connect(file)
	with con:
		return con.cursor()   
	return False

# funktion zur sql abfrage
#TODO
def sql(cursor,que,onlyone=False):
	cursor.execute(que)

	if(onlyone):
		return cursor.fetchone()
	return cursor.fetchall()

# schließt db
def sql_close(cursor):
	if cursor:
		cursor.commit()
		cursor.close()
		return True
	return False

# entfernt gefährliche zeichen
#TODO
def no_inject(str):
	return str.replace("'","`");

# md5 erzeugen
#ungeprüft
def md5(str):
	return hashlib.md5(str).hexdigest()
	
# liefert Zeit Sting mit offset
#ungeprüft
def timestamp(offset=0):
	t = time()+offset
	return time.strftime('%Y-%m-%d %H:%M:%S', t)