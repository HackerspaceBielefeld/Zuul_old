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
			data = func.sql(lite,que)
			if len(data) == 1:
				# Prüft ob Passwort stimmt
				nMD5 = "%s%s" % (post["uPass"][0],data[0][1])
				if func.md5(nMD5) == data[0][0]:
					# erstelle neues uSalt und uPass
					uSalt = func.random(75)
					nMD5 = "%s%s" % (post["uPass"][0],uSalt)
					uPass = func.md5(nMD5)
					session = func.random(32)
					expire = func.timestamp(conf['expire'])
					que = "UPDATE users SET uSalt = '%s',uPass='%s',uSession='%s',expire='%s'" % (uSalt,uPass,session,expire)
					if func.sql(lite,que):
						# db update erfolgreich
						session = session
						access = True
					else:
						# update fehlgeschlagen
						self.wfile.write('''<p>Schreiben in DD Fehlgeschlagen</p>''')
						#TODO
						pass
				else:
					# Passwort stimmt nicht
					self.wfile.write('''<p>Passwort nicht Korrekt</p>''')
					#TODO
					pass
			else:
				#user existiert nicht
				self.wfile.write('''<p>User nicht Korrekt</p>''')
				#TODO
				pass
		else:
			#token prüfen und gleich expire erneuern
			print get
			if get.has_key('s'):
				expire = func.timestamp(conf['expire'])
				now = func.timestamp()
				que = "UPDATE users SET expire='%s' WHERE session = '%s'" % (expire,get['s'])
				if func.sql(lite,que):
					session = get['s']
					access = True
				else:
					# Token abgelaufen
					self.wfile.write('''<p>Session abgelaufen</p>''')
					#TODO
					pass
			else:
				# Token nicht existent
				self.wfile.write('''<p>Keine Session gefunden</p>''')
				#TODO
				pass

		# Content
		if access == True:
			# hier kommt alles rein was nur erreichbar ist, wenn man angemeldet ist
			# Navigation
			navi = '''<a href="/stats/index/s/%s">Statistik</a>
			<a href="/user/list/s/%s">Userliste</a>
			<a href="/user/create/s/%s">User erstellen</a>
			<a href="/logout/index/s/%s">Logout</a>
			<hr/>''' % (session,session,session,session)
			self.wfile.write(navi)	
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
