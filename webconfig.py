#!/usr/bin/python
# coding: utf8

import string,cgi,time,sys
import func
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

conf = {}
conf['db_path'] = "./zuul.db"	#datenbank pfad
conf['expire'] = 60*15			#zeit des session timeouts
conf['dellog'] = (-60)*60*24*30	#zeit nach der logs gelöscht werden
conf['ipblock'] = (-60)*30		#zeit der ip sperre

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

		if post.has_key('u') and post.has_key('p'):
			# holt User anhand des usernamens
			
			ipaddr = func.no_inject(self.client_address[0])
			blocktime = func.timestamp(conf['ipblock'])
			log = func.sql(lite,"SELECT timecode FROM log WHERE ipAddr = '%s' AND answere = 'X' AND timecode > '%s'" % (ipaddr,blocktime))
			if(len(log) < 3):
				que = "SELECT uPass, uSalt, uID FROM users WHERE uName LIKE '%s'" % post["u"][0]
				data = func.sql(lite,que)
				if len(data) == 1:
					# Prüft ob Passwort stimmt
					nMD5 = "%s%s" % (post["p"][0],data[0][1])
					if func.md5(nMD5) == data[0][0]:
						# erstelle neues uSalt und uPass
						uSalt = func.random(75)
						nMD5 = "%s%s" % (post["p"][0],uSalt)
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
							self.wfile.write('''<p>Schreiben in DB Fehlgeschlagen</p>''')
					else:
						# Passwort stimmt nicht
						self.wfile.write('''<p>Passwort nicht Korrekt</p>''')
						
						dellog = func.timestamp(conf['dellog'])
						now = func.timestamp()
						func.sql(lite,"DELETE FROM log WHERE timecode < '%s';" % dellog)
						func.sql(lite,"INSERT INTO log (tokenID, answere, timecode, ipAddr) VALUES  ('fffffffffffffffffffffffffffffffff','X','%s','%s')" % (now,ipaddr));
				else:
					#user existiert nicht
					self.wfile.write('''<p>User nicht Korrekt</p>''')

					dellog = func.timestamp(conf['dellog'])
					now = func.timestamp()
					func.sql(lite,"DELETE FROM log WHERE timecode < '%s';" % dellog)
					func.sql(lite,"INSERT INTO log (tokenID, answere, timecode, ipAddr) VALUES  ('fffffffffffffffffffffffffffffffff','X','%s','%s')" % (now,ipaddr));
			else:
				#ip gesperrt
				self.wfile.write('''<p>Die IP-Adresse wurde gesperrt</p>''')
		else:
			#token prüfen und gleich expire erneuern
			if get.has_key('s'):
				if get.has_key("logout"):
					expire = '0000-00-00- 00:00:00'
				else:
					expire = func.timestamp(conf['expire'])
				
				now = func.timestamp()
				session = func.no_inject(get['s'])
				que = "UPDATE users SET expire='%s' WHERE uSession = '%s'" % (expire,session)
				if func.sql(lite,que):
					if get.has_key("logout"):
						self.wfile.write('''<p>Session beendet.</p>''')
						access = False
					else:
						access = True
				else:
					# Token abgelaufen			
					self.wfile.write('''<p>Session abgelaufen</p>''')
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
			
								
				
			if get.has_key("token"):
				#token search
				
				#token create
				
				#token deleter
				pass
				#TODO
				
			if get.has_key("log"):
				#todo
				pass
			
			if get.has_key('user'):
				#ungeprüft
				if get["user"] == '':
					get["user"] = 'list'
					
				#ungeprüft
				if get["user"] == 'create':
					if post.has_key("submit"):
						uName = func.no_inject(post['uName'][0])
						if(post['uPass'][0] != ''):
							uSalt = func.random(75)
							uPass = func.md5(post['uPass'][0]+uSalt)
						else:
							uSalt = ''
							uPass = ''
						if func.sql(lite,"INSERT INTO users (uName,uPass,uSalt,uSession) VALUES ('"+uName+"','"+uPass+"','"+uSalt+"','')"):
							self.wfile.write('''<p>User angelegt</p>''')
							get["id"] = func.sql(lite,"SELECT uID FROM users ORDER BY uID DESC LIMIT 1")[0][0]					
							get["user"] = 'edit'
						else:
							self.wfile.write('''<p>Anlegen fehlgeschlagen</p>''')
					else:
						content = '''<form action="/user/create/s/%s" method="post">Name<input type="text" name="uName" /><br/>Passwort <input type="password" name="uPass" />(Nur ausfüllen, wenn der user admin zugriff haben soll.)<br/><input type="submit" name="submit" value="Erstellen" /></form>''' % session
						self.wfile.write(content)
						
				if get["user"] == 'edit':
					self.wfile.write("User edit "+str(get['id']))
					id = func.no_inject(get['id'])
					#user daten werden in form, geladen
					ud = func.sql(lite,"SELECT * FROM users WHERE uID = %s" % id)
					if len(ud) == 1:
						self.wfile.write(str(ud[0]))
					#TODO
					#zugehörige tokens gelistet
					data = func.sql(lite,"SELECT * FROM token WHERE userID = '%s';" % id)
					for d in data:
						print d
					#TODO
					
					
				if get["user"] == 'del':
					self.wfile.write("User del "+str(get['id']))
					#TODO
					
				#ungeprüft
				if get["user"] == 'list':
					data = func.sql(lite,"SELECT uId,uName,uPass FROM users ORDER BY uName")
					self.wfile.write('''<table><thead><tr><th>ID</th><th>Name</th><th>Optionen</th></tr></thead><tbody>''')
					for d in data:
						if d[2] != '':
							ismod = '*'
						else:
							ismod = ''
						self.wfile.write("<tr><td>"+str(d[0])+"</td><td>"+d[1]+" "+ismod+"</td><td>[<a href='/user/edit/id/"+str(d[0])+"/s/"+session+"'>Edit</a>][De/Aktivieren][<a href='/user/del/id/"+str(d[0])+"/s/"+session+"'>L&ouml;schen</a>]</td></tr>")
					#TODO
					self.wfile.write("</tbody></table>")


		else:
			# hier sieht man nur wenn man abgemeldet ist
			# Navigation
			self.wfile.write('''
			<a href="/stats">Statistik</a> 
			<a href="/login">Login</a> 
			<hr/>''')	
			
			if get.has_key("login"):
				self.wfile.write('''<form action="" method="post">
					User: <input type="text" name="u" /><br/>
					Pass: <input type="password" name="p" /></br>
					<input type="submit" name="submit" value="Login" />
				</form>''')
			
			#TODO
			self.wfile.write('''Abgemeldet''')
		
		if get.has_key("stats"):
			pass
			#TODO
			
		if get.has_key("favicon.ico"):
			#todo
			pass
			
		if get.has_key("style.css"):
			pass
			#todo
		
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
