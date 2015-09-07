#!/usr/bin/python
# coding: utf8

import string,cgi,time,sys
import func
import io
from urllib.parse import urlparse, urlsplit
from os import curdir, sep
from http.server import BaseHTTPRequestHandler, HTTPServer

conf = {}
conf['db_path'] = "./zuul.db"   #datenbank pfad
conf['expire'] = 60*15                  #zeit des session timeouts
conf['dellog'] = (-60)*60*24*30 #zeit nach der logs gelöscht werden
conf['ipblock'] = (-60)*30              #zeit der ip sperre

class myHandler(BaseHTTPRequestHandler):
        head = io.StringIO();
        body = io.StringIO();
        # Fehler text Funktion
        def throwError(self,code=404):
                codes[404] = "File not Found"
                self.send_error(code,codes[code])

        # holt get Vars
        def getGets(self):
                tmp = urlparse(self.path).path
                #tmp = string.split(self.path[1:],"/")
                #tmp = ""
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
                self.head.write("<head>")
                self.body.write("<body>")
                lite = func.sql_connect(conf['db_path'])

                if 'uName' in post and 'uPass' in post:
                        # holt User anhand des usernamens
                        
                        ipaddr = func.no_inject(self.client_address[0])
                        blocktime = func.timestamp(conf['ipblock'])
                        log = func.sql(lite,"SELECT timecode FROM log WHERE ipAddr = '%s' AND answere = 'X' AND timecode > '%s'" % (ipaddr,blocktime))
                        print(log)
                        if(len(log) < 3):
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
                                                        self.body.write('''<p>Schreiben in DB Fehlgeschlagen</p>''')
                                        else:
                                                # Passwort stimmt nicht
                                                self.body.write('''<p>Passwort nicht Korrekt</p>''')
                                                
                                                dellog = func.timestamp(conf['dellog'])
                                                now = func.timestamp()
                                                func.sql(lite,"DELETE FROM log WHERE timecode < '%s';" % dellog)
                                                func.sql(lite,"INSERT INTO log (tokenID, answere, timecode, ipAddr) VALUES  ('fffffffffffffffffffffffffffffffff','X','%s','%s')" % (now,ipaddr));
                                else:
                                        #user existiert nicht
                                        self.body.write('''<p>User nicht Korrekt</p>''')

                                        dellog = func.timestamp(conf['dellog'])
                                        now = func.timestamp()
                                        func.sql(lite,"DELETE FROM log WHERE timecode < '%s';" % dellog)
                                        func.sql(lite,"INSERT INTO log (tokenID, answere, timecode, ipAddr) VALUES  ('fffffffffffffffffffffffffffffffff','X','%s','%s')" % (now,ipaddr));
                        else:
                                #ip gesperrt
                                self.body.write('''<p>Die IP-Adresse wurde gesperrt</p>''')
                else:
                        #token prüfen und gleich expire erneuern
                        print(get)
                        if 's' in get:
                                if "logout" in get:
                                        expire = '0000-00-00- 00:00:00'
                                else:
                                        expire = func.timestamp(conf['expire'])
                                
                                now = func.timestamp()
                                session = func.no_inject(get['s'])
                                que = "UPDATE users SET expire='%s' WHERE uSession = '%s'" % (expire,session)
                                print(que)
                                if func.sql(lite,que):
                                        if "logout" in get:
                                                self.body.write('''<p>Session beendet.</p>''')
                                                access = False
                                        else:
                                                access = True
                                else:
                                        # Token abgelaufen                      
                                        self.body.write('''<p>Session abgelaufen</p>''')
                        else:
                                # Token nicht existent
                                self.body.write('''<p>Keine Session gefunden</p>''')
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
                        self.body.write(navi)        
                        if 'user' in get:
                                if get["user"] == '':
                                        get["user"] = 'list'
                                        
                                if get["user"] == 'create':
                                        if "submit" in post:
                                                #TODO
                                                pass
                                        else:
                                                content = '''<form action="/user/create/s/%s" method="post">Name<input type="text" name="uName" /><br/>Passwort <input type="password" name="uPass" />(Nur ausfüllen, wenn der user admin zugriff haben soll.)<br/><input type="submit" name="submit" value="Erstellen" /></form>''' % session
                                                self.body.write(content)
                                                
                                if get["user"] == 'edit':
                                        pass
                                        #TODO
                                if get["user"] == 'del':
                                        pass
                                        #TODO
                                
                                if get["user"] == 'detail':
                                        pass
                                        #TODO
                                        
                                if get["user"] == 'list':
                                        pass
                                        #TODO
                                        
                                
                        if "token" in get:
                                #token list gibts in user details schon
                                
                                #token create
                                
                                #token deleter
                                pass
                                
                        if "log" in get:
                                #todo
                                pass

                else:
                        # hier sieht man nur wenn man abgemeldet ist
                        # Navigation
                        self.body.write('''
                        <a href="/stats">Statistik</a> 
                        <a href="/login">Login</a> 
                        <hr/>''')       
                        
                        if "login" in get:
                                self.body.write('''<form action="" method="post">
                                        User: <input type="text" name="uName" /><br/>
                                        Pass: <input type="password" name="uPass" /></br>
                                        <input type="submit" name="submit" value="Login" />
                                </form>''')
                        
                        #TODO
                        self.body.write('''Abgemeldet''')
                
                if "stats" in get:
                        self.body.write("stats chosen");
                        pass
                        #TODO
                        
                tmp = urlsplit(self.path)
                print(tmp.path)
                if tmp.path == "/favicon.ico":
                        #todo
                        self.send_header('Content-Type','image/ico')
                        self.end_headers()
                        with open('favicon.ico', 'rb') as f:
                            self.wfile.write(f.read())
                            f.close
                        pass
                        
                if "style.css" in get:
                        pass
                        #todo
                
                #Aufräumen
                func.sql_close(lite);
                self.body.write("</body></html>")
                

        def print(self):
                self.send_header('Content-Type','text/html')
                self.end_headers()
                self.wfile.write("<html>".encode("utf-8"))
                self.wfile.write("<head>".encode("utf-8"))
                self.wfile.write("<title>Web-Administration Zuul</title>".encode("utf-8"))
                self.wfile.write(self.head.getvalue().encode("utf-8"));
                self.wfile.write("</head>".encode("utf-8"))
                self.wfile.write(self.body.getvalue().encode("utf-8"));

        def do_GET(self):
                try:
                        gets = self.getGets()
                        self.requests({},gets)
                        self.print();
                        return
                except IOError:
                        throwError(404)
                        
        def do_POST(self):
                global rootnode
                try:
                        gets = self.getGets()
                        posts = self.getPosts()
                        self.requests(posts,gets)
                        self.print();
                except IOError:
                        throwError(404) 
                
def main():
        try:
                server = HTTPServer(('',12345),myHandler)
                print('pyWebServer: starten ...')
                server.serve_forever()
        except KeyboardInterrupt:
                print('pyWebServer: stoppen ...')
                server.socket.close()

if __name__ == '__main__':
        main()
