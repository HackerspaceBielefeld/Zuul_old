#!/usr/bin/python
# coding: utf8

import string,cgi,time,sys,inc.func
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

conf['db_path'] = "zuul.db"
conf['expire'] = 60*15

class myHandler(BaseHTTPRequestHandler):
	# Fehler text Funktion
	def throwError(self,code=404):
		codes[404] = "File not Found"
		self.send_error(code,codes[code])
		
	# holt get Vars
	def getGets(self):
		tmp = string.split(self.path[1:],"/")
		vars = {}
			
		for t in range(0,len(tmp),2):
			if len(tmp) > t+1:
				vars[tmp[t]] = tmp[t+1]
			else:
				vars[tmp[t]] = ""
		return vars
	
	# holt post vars
	def getPosts(self):
		ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
		if ctype == 'multipart/form-data':
			postvars = cgi.parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers.getheader('content-length'))
			postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
		else:
			postvars = {}
		return postvars
	
	# beinhaltet die Seitenführung
	#TODO
	def requests(self,post={},get={}):
		global conf
		access False
		self.send_response(200)
		self.send_header('Content-Type','text/html')
		lite = sql(conf['db_path'])
		
		if post.has_key('uName') AND post.has_key('uPass'):
			# holt User anhand des usernamens
			data = lite.sql("SELECT uPass, uSalt, uID FROM users WHERE uName LIKE ',post["uName"],'",True)
			if res.len > 0:
				# Prüft ob Passwort stimmt
				if md5(post["uPass"],data["uSalt"]) == data["uPass"]:
					# erstelle neues uSalt und uPass
					uSalt = random(75)
					uPass = md5(post["uPass"],uSalt)
					session = random(32)
					expire = timestamp(conf['expire'])
					if lite.sql("UPDATE users SET uSalt = '",uSalt,"',uPass='",uPass,"',session='",session,"',expire='",expire,"'"):
						# db update erfolgreich
						session = session
						access = True
					else:
						# update fehlgeschlagen
						#TODO
				else:
					# Passwort stimmt nicht
					#TODO
			else:
				#user existiert nicht
				#TODO
		else:
			#token prüfen und gleich expire erneuern
			if get.has_key('s'):
				expire = timestamp(conf['expire']) #15 min
				now = timestamp()
				if lite.sql("UPDATE users SET expire='",expire,"' WHERE session = '",get['s'],"'"):
					access = True
				else:
					# Token abgelaufen
					#TODO
			else:
				# Token nicht existent
				#TODO
		
		self.end_headers()
		self.wfile.write("<html><head><title>Web-Administration Zuul</title></head><body>")	
		
	
		
		# Content
		if access == True:
			# hier kommt alles rein was nur erreichbar ist, wenn man angemeldet ist
			# Navigation
			self.wfile.write('''
			<a href="/p/stats">Statistik</a> 
			<a href="/p/user/a/list">Userliste</a> 
			<a href="/p/user/a/create">User erstellen</a>
			<hr/>''')	
			#TODO
			self.wfile.write('''Angemeldet''')
		else:
			# hier sieht man nur wenn man abgemeldet ist
			# Navigation
			self.wfile.write('''
			<a href="/p/stats">Statistik</a> 
			<a href="/p/user/a/list">Userliste</a> 
			<a href="/p/user/a/create">User erstellen</a>
			<hr/>''')	
			#TODO
			self.wfile.write('''Abgemeldet''')
		
		
		#Aufräumen
		sql_close();
		self.wfile.write("</body></html>")
		
	def do_GET(self):
		try:
			gets = self.getGets()
			self.requests({},gets)
			return
		except IOError:
			throwError(404)
			
	def do_POST(self):
		global rootnode
		try:
			gets = self.getGets()
			posts = self.getPosts()
			self.requests(posts,gets)
		except IOError:
			throwError(404)	
		
def main():
	try:
		server = HTTPServer(('',80),myHandler)
		print 'pyWebServer: starten ...'
		server.serve_forever()
	except KeyboardInterrupt:
		print 'pyWebServer: stoppen ...'
		server.socket.close()

if __name__ == '__main__':
	main()
