#!/usr/bin/python3
# coding: utf8

import string,cgi,time,sys
import func
from os import curdir, sep
from http.server import BaseHTTPRequestHandler, HTTPServer

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
		tmp = str(self.path[1:]).split("/")
		vars = {}
			
		for t in range(0,len(tmp),2):
			if len(tmp) > t+1:
				vars[tmp[t]] = tmp[t+1]
			else:
				vars[tmp[t]] = ""
		return vars

	# holt post vars
	def getPosts(self):
		ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
		if ctype == 'multipart/form-data':
			postvars = cgi.parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers.get('content-length'))
			postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
		else:
			postvars = {}
		return postvars

	# beinhaltet die Seitenführung
	#TODO
	def requests(self,post={},get={}):
		global conf
		html = False
		access = False
		self.send_response(200)
		self.send_header('Content-Type','text/html')
		self.end_headers()
		if 'style.css' not in get.keys() and 'favicon.ico' not in get.keys():
			html = True
			self.wfile.write(bytes("<html><head><title>Web-Administration Zuul</title><link href='/style.css' type='text/css' rel='stylesheet'/></head><body>","UTF-8"))	
			lite = func.sql_connect(conf['db_path'])
			
			# session erzeugen
			if bytes('u',"UTF-8") in post.keys() and bytes('p',"UTF-8") in post.keys():
				# holt User anhand des usernamens
				
				ipaddr = func.no_inject(self.client_address[0])
				blocktime = func.timestamp(conf['ipblock'])
				log = func.sql(lite,"SELECT timecode FROM log WHERE addInfo = '%s' AND answere = 'X' AND timecode > '%s'" % (ipaddr,blocktime))
				if(len(log) < 5):
					que = "SELECT uPass, uSalt, uID FROM users WHERE uName LIKE '%s'" % post[b"u"][0].decode("utf-8") 
					print(que)
					data = func.sql(lite,que)
					if len(data) == 1:
						# Prüft ob Passwort stimmt
						nMD5 = "%s%s" % (post[b"p"][0].decode("utf-8") ,data[0][1])
						if func.md5(nMD5) == data[0][0]:
							# erstelle neues uSalt und uPass
							uSalt = func.random(75)
							nMD5 = "%s%s" % (post[b"p"][0].decode("utf-8") ,uSalt)
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
								self.wfile.write(bytes('''<p>Schreiben in DB Fehlgeschlagen</p>''',"UTF-8"))
						else:
							# Passwort stimmt nicht
							self.wfile.write(bytes('''<p>Passwort nicht Korrekt</p>''',"UTF-8"))
							
							dellog = func.timestamp(conf['dellog'])
							now = func.timestamp()
							func.sql(lite,"DELETE FROM log WHERE timecode < '%s';" % dellog)
							func.sql(lite,"INSERT INTO log (tokenID, answere, timecode, addInfo) VALUES  ('fffffffffffffffffffffffffffffffff','X','%s','%s')" % (now,ipaddr));
					else:
						#user existiert nicht
						self.wfile.write(bytes('''<p>User nicht Korrekt</p>''',"UTF-8"))

						dellog = func.timestamp(conf['dellog'])
						now = func.timestamp()
						func.sql(lite,"DELETE FROM log WHERE timecode < '%s';" % dellog)
						func.sql(lite,"INSERT INTO log (tokenID, answere, timecode, addInfo) VALUES  ('fffffffffffffffffffffffffffffffff','X','%s','%s')" % (now,ipaddr));
				else:
					#ip gesperrt
					self.wfile.write(bytes('''<p>Die IP-Adresse wurde gesperrt</p>''',"UTF-8"))
			else:
			# laufende session
				#token prüfen und gleich expire erneuern
				if 's' in get.keys():
					if 'logout' in get.keys():
						expire = '0000-00-00- 00:00:00'
					else:
						expire = func.timestamp(conf['expire'])
					
					now = func.timestamp()
					session = func.no_inject(get['s'])
					que = "UPDATE users SET expire='%s' WHERE uSession = '%s'" % (expire,session)
					if func.sql(lite,que):
						if 'logout' in get.keys():
							self.wfile.write(bytes('''<p>Session beendet.</p>''',"UTF-8"))
							access = False
						else:
							access = True
					else:
						# Token abgelaufen			
						self.wfile.write(bytes('''<p>Session abgelaufen</p>''',"UTF-8"))
				else:
					# Token nicht existent
					self.wfile.write(bytes('''<p>Keine Session gefunden</p>''',"UTF-8"))
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
				self.wfile.write(bytes(navi,"UTF-8"))	
				
				if 'token' in get.keys():
					#token search
					
					#token create
					if get['token'] == 'add':
						if 'tid' in get.keys():
							tid = func.no_inject(get['tid'])
							id = func.no_inject(get['id'])
							if func.sql(lite,"INSERT INTO token (tID,userID,tKey) VALUES ('"+tid+"','"+id+"','')"):
								self.wfile.write(bytes('''<p>Anlegen erfolgreich</p>''',"UTF-8"))
							else:
								self.wfile.write(bytes('''<p>Anlegen fehlgeschlagen</p>''',"UTF-8"))
							
							get['user'] = 'list'
						else:
							data = func.sql(lite,"SELECT tokenID,timecode FROM log WHERE answere = 'D' ORDER BY timecode DESC LIMIT 10")
							for d in data:
								self.wfile.write(bytes("[<a href='/token/add/id/"+get['id']+"/tid/"+d[0]+"/s/"+session+"'>Add to User</a>] "+ d[0] +"("+d[1]+")","UTF-8"))
					#token deleter
					pass
					#TODO
					
				if 'log' in get.keys():
					#todo
					pass
				
				if 'user' in get.keys():
					#ungeprüft
					if get["user"] == '':
						get["user"] = 'list'
						
					#ungeprüft
					if get["user"] == 'create':
						if bytes('submit',"UTF-8") in post.keys():
							uName = func.no_inject(post[b'uName'][0].decode("utf-8") )
							uMember = func.no_inject(post[b'uMember'][0].decode("utf-8") )
							if(post[b'uPass'][0].decode("utf-8")  != ''):
								uSalt = func.random(75)
								uPass = func.md5(post[b'uPass'][0].decode("utf-8") +uSalt)
							else:
								uSalt = ''
								uPass = ''
							if func.sql(lite,"INSERT INTO users (uName,uPass,uSalt,uMember,uSession) VALUES ('"+uName+"','"+uPass+"','"+uSalt+"','"+uMember+"','')"):
								self.wfile.write(bytes('''<p>User angelegt</p>''',"UTF-8"))
								get["id"] = func.sql(lite,"SELECT uID FROM users ORDER BY uID DESC LIMIT 1")[0][0]					
								get["user"] = 'edit'
							else:
								self.wfile.write(bytes('''<p>Anlegen fehlgeschlagen</p>''',"UTF-8"))
						else:
							content = '''<form action="/user/create/s/%s" method="post">Name<input type="text" name="uName" /><br/>Passwort <input type="password" name="uPass" />(Nur ausfüllen, wenn der user admin zugriff haben soll.)<br/>Member-ID<input type="text" name="uMember" /><br/><input type="submit" name="submit" value="Erstellen" /></form>''' % session
							self.wfile.write(bytes(content,"UTF-8"))
					
					#ungeprüft				
					if get["user"] == 'edit':
						if bytes('submit',"UTF-8") in post.keys():
							uName = func.no_inject(post[b'uName'][0].decode("utf-8") )
							uMember = func.no_inject(post[b'uMember'][0].decode("utf-8") )
							id = func.no_inject(get['id'])
							if(post[b'uPass'][0].decode("utf-8")  != ''):
								uSalt = func.random(75)
								uPass = func.md5(post[b'uPass'][0].decode("utf-8") +uSalt)
								res = func.sql(lite,"UPDATE users SET uName = '"+uName+"',uPass = '"+uPass+"',uSalt = '"+uSalt+"',uMember = '"+uMember+"' WHERE uID = '"+id+"'")
							else:
								res = func.sql(lite,"UPDATE users SET uName = '"+uName+"',uMember = '"+uMember+"' WHERE uID = '"+id+"'")

							if res == True:
								self.wfile.write(bytes('''<p>User editiert</p>''',"UTF-8"))
							else:
								self.wfile.write(bytes('''<p>Editieren fehlgeschlagen</p>''',"UTF-8"))				
							get["user"] = 'edit'
						else:
							self.wfile.write(bytes("User edit "+str(get['id']),"UTF-8"))
							id = func.no_inject(get['id'])
							#user daten werden in form, geladen
							self.wfile.write(bytes("<table><thead><tr><th>Feld</th><th>Daten</th></tr></thead><tbody>","UTF-8"))
							ud = func.sql(lite,"SELECT uName, uPass, uMember FROM users WHERE uID = %s" % id)
							if len(ud) == 1:
								if ud[0][1] == '':
									admin = 'User'
								else:
									admin = 'Admin'
								content = '''<form action="/user/edit/id/%s/s/%s" method="post"><span>Name</span><input type="text" name="uName" value="%s" /><br/>Gruppe: %s<br/><span>Passwort</span><input type="password" name="uPass" />(bleibt unverändert wenn leer.)<br/><span>Member-ID</span><input type="text" name="uMember" value="%s" /><br/><input type="submit" name="submit" value="Erstellen" /></form>''' % (id,session,ud[0][0],admin,ud[0][2])
								self.wfile.write(bytes(content,"UTF-8"))
							self.wfile.write(bytes("</tbody></table>[<a href='/token/add/id/"+id+"/s/"+session+"'>AddToken</a>]<table><thead><tr><th>ID</th><th>zuletzt benutzt</th><th>Optionen</th></tr></thead><tbody>","UTF-8"))
							#zugehörige tokens gelistet
							data = func.sql(lite,"SELECT tID,tActive,lastUsed FROM token WHERE userID = '%s';" % id)
							for d in data:
								if d[1] == 1:
									active = 'Aktiv'
								else:
									active = 'Deaktiviert'
								self.wfile.write(bytes("<tr><td>"+d[0]+"</td><td>"+d[3]+"</td><td>"+active+"</td><td>[De/Aktivieren][L&ouml;schen][Weitergeben]</td></tr>","UTF-8"))
							self.wfile.write(bytes("</tbody></table>","UTF-8"))
						
					#TODO
					if get["user"] == 'del':
						self.wfile.write("User del "+str(get['id']))
						#TODO
						
					#ungeprüft
					if get["user"] == 'list':
						data = func.sql(lite,"SELECT uId,uName,uPass,uMember FROM users ORDER BY uName")
						self.wfile.write(bytes('''<table><thead><tr><th>ID</th><th>Name</th><th>Optionen</th></tr></thead><tbody>''',"UTF-8"))
						for d in data:
							if d[2] != '':
								ismod = '*'
							else:
								ismod = ''
							self.wfile.write(bytes("<tr><td>"+str(d[0])+"</td><td>"+d[1]+" "+ismod+"</td><td>[<a href='/user/edit/id/"+str(d[0])+"/s/"+session+"'>Edit</a>][De/Aktivieren][<a href='/user/del/id/"+str(d[0])+"/s/"+session+"'>L&ouml;schen</a>]</td></tr>","UTF-8"))
						#TODO
						self.wfile.write(bytes("</tbody></table>","UTF-8"))
			else:
				# hier sieht man nur wenn man abgemeldet ist
				# Navigation
				self.wfile.write(bytes('''
				<a href="/stats">Statistik</a> 
				<a href="/login">Login</a> 
				<hr/>''',"UTF-8"))	
				
				if 'login' in get.keys():
					self.wfile.write(bytes('''<form action="" method="post">
						User: <input type="text" name="u" /><br/>
						Pass: <input type="password" name="p" /></br>
						<input type="submit" name="submit" value="Login" />
					</form>''',"UTF-8"))
				
				#TODO
				self.wfile.write(bytes('''Abgemeldet''',"UTF-8"))
		
		if 'stats' in get.keys():
			self.wfile.write(bytes('''Statistik''',"UTF-8"))
			
		if 'favicon.ico' in get.keys():
			#todo
			pass
			
		if 'style.css' in get.keys():
			self.wfile.write(bytes('''p {background-color: #000000; display: block; color: #ffffff;} span {width: 200px;} ''',"UTF-8"))
			#todo
		
		#Aufräumen
		
		if html == True:
			self.wfile.write(bytes("</body></html>","UTF-8"))
			func.sql_close(lite);
		
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
		server = HTTPServer(("",80),myHandler)
		print("pyWebServer: starten ... ")
		server.serve_forever()
	except KeyboardInterrupt:
		print("pyWebServer: stoppen ... ")
		server.socket.close()

if __name__ == '__main__':
	main()
