#!/usr/bin/python
# coding: utf8
import func

con = func.sql_connect('zuul.db')
func.sql(con,'''INSERT INTO log (tokenID, answere) VALUES ('1234567','D')''')

func.sql_close(con)