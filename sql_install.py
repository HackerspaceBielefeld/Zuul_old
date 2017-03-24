#!/usr/bin/python
# coding: utf8
import func

con = func.sql_connect('zuul.db')
print "Erstelle log tabelle"
func.sql(con,'''CREATE TABLE log (
  tokenID BLOB NOT NULL,
  answere TEXT NOT NULL ,
  timecode timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  addInfo TEXT NULL DEFAULT ''
)''')
print "Erstelle token tabelle"
func.sql(con,'''CREATE TABLE token (
  tID BLOB NOT NULL,
  userID int(11) NOT NULL,
  tKey BLOB NOT NULL,
  tActive INTEGER NOT NULL DEFAULT '1',
  lastUsed timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'
)''')

print "Erstelle users Tabelle"
func.sql(con,'''CREATE TABLE users (
  uID INTEGER PRIMARY KEY AUTOINCREMENT,
  uName varchar(35) NOT NULL,
  uPass varchar(32) NOT NULL,
  uSalt varchar(75) NOT NULL,
  uMember INTEGER,
  uSession varchar(32) NOT NULL,
  uActive int(1) NOT NULL DEFAULT 1,
  expire timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'
);''')

print "Erstelle pi:raspberry User"
func.sql(con,'''INSERT INTO users (uName, uPass, uSalt,uSession) VALUES ('pi','b89749505e144b564adfe3ea8fc394aa','','')''')

func.sql_close(con)