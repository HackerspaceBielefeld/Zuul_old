#!/usr/bin/python
# coding: utf8

import string,cgi,time,sys
import func
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

conf = {}
conf['db_path'] = "./zuul.db"
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
		access = False
		self.send_response(200)
		self.send_header('Content-Type','text/html')
		self.end_headers()
		self.wfile.write("<html><head><title>Web-Administration Zuul</title></head><body>")	
		lite = func.sql_connect(conf['db_path'])

		if post.has_key('uName') and post.has_key('uPass'):
			# holt User anhand des usernamens
			que = "SELECT uPass, uSalt, uID FROM users WHERE uName LIKE '%s'" % post["uName"][0]
			print que
			data = func.sql(lite,que,True)
			print data
			print type(data)
			if data.len > 0:
				# Prüft ob Passwort stimmt
				if md5(post["uPass"][0],data["uSalt"][0]) == data["uPass"]:
					# erstelle neues uSalt und uPass
					uSalt = random(75)
					uPass = md5(post["uPass"][0],uSalt)
					session = random(32)
					expire = timestamp(conf['expire'])
					que = "UPDATE users SET uSalt = '%s',uPass='%s',session='%s',expire='%s'" % (uSalt,uPass,session,expire)
					if func.sql(lite,que):
						# db update erfolgreich
						session = session
						access = True
					else:
						# update fehlgeschlagen
						#TODO
						pass
				else:
					# Passwort stimmt nicht
					#TODO
					pass
			else:
				#user existiert nicht
				#TODO
				pass
		else:
			#token prüfen und gleich expire erneuern
			if get.has_key('s'):
				expire = timestamp(conf['expire']) #15 min
				now = timestamp()
				que = "UPDATE users SET expire='%s' WHERE session = '%s'" % (expire,get['s'])
				if func.sql(lite,que):
					session = get['s']
					access = True
				else:
					# Token abgelaufen
					#TODO
					pass
			else:
				# Token nicht existent
				#TODO
				pass

		# Content
		if access == True:
			# hier kommt alles rein was nur erreichbar ist, wenn man angemeldet ist
			# Navigation
			self.wfile.write('''
			<a href="/stats/index/s/''',session,'''">Statistik</a> 
			<a href="/p/user/list/s/''',session,'''">Userliste</a> 
			<a href="/p/user/create/s/''',session,'''">User erstellen</a>
			<a href="/logout/index/s/''',session,'''">Logout</a>
			<hr/>''')	
			#TODO
			self.wfile.write('''Angemeldet''')
		else:
			# hier sieht man nur wenn man abgemeldet ist
			# Navigation
			self.wfile.write('''
			<a href="/stats">Statistik</a> 
			<a href="/login">Login</a> 
			<hr/>''')	
			
			if get.has_key("login"):
				self.wfile.write('''<form action="" method="post">
					User: <input type="text" name="uName" /><br/>
					Pass: <input type="password" name="uPass" /></br>
					<input type="submit" name="submit" value="Login" />
				</form>''')
			
			#TODO
			self.wfile.write('''Abgemeldet''')
		
		if get.has_key("stats"):
			pass
			#TODO
		
		#Aufräumen
		func.sql_close(lite);
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
