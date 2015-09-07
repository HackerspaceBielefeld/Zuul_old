#!/usr/bin/python
# -*- coding: utf-8 -*-
#addons nachladen
import _mysql
import RPi.GPIO as GPIO
import inc.func


# schreibt den neuen key auf die karte
#TODO
def writeKey(key):
	#TODO key schreiben
	return False

# prüft die karte
#ungeprüft
def checkCard(id,key):
	res = sql_connect()
	id = no_inject(id)
	key = no_inject(key)
	# prüft daten mit der DB abfrage
	access = sql("SELECT COUNT(*) FROM user AS u, token AS t WHERE tID = '",id,"' AND tKey = '",key,"' AND tActive = 'true' AND userID = uID AND uActive = 'true' LIMIT 1")[0]
	if(access == 1):
		#bei Übereinstimmung
		# erzeugt neuen keys
		newkey = random(32)
		# speichert key auf der Karten
		written = writeKey(newkey)

		if(written):
			# bei erfolg speichert key in der DB
			sql("UPDATE token SET tKey = '",newkey,"' WHERE tID = '",id,"' AND tKey = '",newkey,"' LIMIT 1")
			# schreibe log
			sql("INSERT INTO log (tokenID, answere) VALUES ('",id,"','G'")
			return True
		else:
			# schreibe log
			sql("INSERT INTO log (tokenID, answere) VALUES ('",id,"','D'") #TODO token key muss auch gespeichert werden
	return False	
	
# setzt leds und andere ausgänge
#TODO
def output(pin,val,time=False):
	pins {'green':24,'yellow':25,'red':26,'lock':27} #TODO ka ob das so richig ist
	
	GPIO.output(pins[pin],val)
	if(!time):
		wait(time)
		#TODO am liebsten multithread, bzw wählbar ob multithread
		GPIO.output(pins[pin],!val)
	return True

# wartet bis die karte vorgehalten wird
while True:
	if(GPIO.wait_for_edge(24, GPIO.FALLING)):
		# empfÃ¤ngt Karten Daten
		# TODO	
		# prüft mittels DB
		access = checkCard(cardID,cardKey)
		if(access):
			# gib gruen
			# oeffne tuer
			output("green",True)
			output("lock",True)
			wait(3)
			output("green",False)
			output("lock",False)
		# bei fehlschlag
		else:
			# gib 2 sek rot
			output("red",True,2)

#kommen wir nie hin
GPIO.cleanup()