#!/usr/bin/python
# coding: utf8

import string,cgi,time,sys,inc.func
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

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
		self.send_response(200)
		self.send_header('Content-Type','text/html')
		
		if post.has_key('uName') AND post.has_key('uPass'):
			#prüfen ob user und passwort passen
			#wenns passt session erzeugen in in user tab schreiben
			#sonst get in token umwalndeln
			#TODO
			
		
		self.end_headers()
		
		# Navigation
		self.wfile.write('''
		<a href="/p/stats">Statistik</a> 
		<a href="/p/user/a/list">Userliste</a> 
		<a href="/p/user/a/create">User erstellen</a>
		<hr/>''')		
		
		# Content
		self.wfile.write(post)
		self.wfile.write("<br/>-----------------------<br/>")
		self.wfile.write(get)
		self.wfile.write('''<form action="" method="post"><input type="submit" name="submitname" value="Gedr&uuml;ckt" /></form>''')

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
