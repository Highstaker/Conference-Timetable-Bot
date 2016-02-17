#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sqlite3
import re
import datetime

from os import path

# The folder containing the script itself
SCRIPT_FOLDER = path.dirname(path.realpath(__file__))

TABLE_NAME = "Events"

class TimetableDatabase(object):
	"""docstring for TimetableDatabase"""
	def __init__(self, filename):
		"""

		:param filename: name of database file without extension
		:return:
		"""
		super(TimetableDatabase, self).__init__()
		self.filename = filename + ".db"

		# if database already exists, do nothnig
		if path.isfile(path.join(SCRIPT_FOLDER, self.filename)):
			pass
		else:
			#database doesn't exist, create it
			self.createTable()

	def parseTimetable(self, data):
		"""
		Parses the text data into the database
		:param data: Format of the input data (example):
		##2016/10/23
		#14:00@@Event Name@@Event Description@@Event location
		#15:59@@Event Name@@Event Description@@Event location
		##2016/10/24
		#16:00@@Event Name@@Event Description@@Event location
		#17:30@@Event Name@@Event Description@@Event location
		:return:
		"""
		print(data)#debug
		# Split lines
		parse = data.split("\n")
		# Removing empty lines and leading/trailing spaces/tabs/etc
		parse = [i.strip(" \t\r") for i in parse if i.strip(" \t\r")]
		print(parse)#debug

		grouped_parse = []
		date = None
		for i in parse:
			if re.match("^#{2}([^#].*)",i):
				#it's a date, store it temporarily
				print("date", i)#debug
				date = i[2:]
			elif re.match("^#([^#].*)",i):
				print("event", i)#debug
				# it's an event, parse it with the current stored date
				if date:
					event = i[1:].split("@@")
					grouped_parse += [dict(date=date, time=event[0], name=event[1], desc=event[2], location=event[3])]

		print(grouped_parse)#debug

		for i in grouped_parse:
			self.createEvent(date=i['date'], time=i['time'], name=i['name'], desc=i['desc'], location=i['location'])



	def createTable(self):
		"""
		Initializes the database and the timetable
		:return:
		"""
		command = """CREATE TABLE {0}(id INTEGER PRIMARY KEY,
								date TEXT,
								time TEXT,
								name TEXT,
								description TEXT,
								location TEXT
								);""".format(TABLE_NAME)

		self._run_command(command)

	def createEvent(self, date, time, name, desc, location):
		"""
		Creates a database entry for an even with the given parameters
		:param date:
		:param time:
		:param name:
		:param desc:
		:param location:
		:return:
		"""

		# unix_time = datetime.datetime.strptime(timedate,"%Y-%m-%d %H:%M")
		command = """INSERT INTO {0}(date, time, name, description, location) VALUES ('{1}','{2}','{3}','{4}','{5}')
		""".format(TABLE_NAME, date, time, name, desc, location)
		print(command)#debug

		self._run_command(command)

	def _run_command(self, command):
		"""
		Runs a given command and returns the output.
		:param command:
		:return:
		"""
		conn = sqlite3.connect(self.filename)
		cursor = conn.execute(command)
		data =[i for i in cursor]
		conn.commit()
		conn.close()

		return data

if __name__ == '__main__':
	T = TimetableDatabase("test002")

	data = """##2016/02/16
	#14:00@@Dinner@@Nomnom time@@Dining room
	#16:00@@Day nap@@ZZZZZ time@@Couch
	#18:00@@Tea time@@Drinking tea@@Living room
	##2016/02/17
	 #14:00@@Dinner@@Nomnom time again@@Dining room
	#15:59@@Day nap@@ZZZZZ time. AGAIN!@@Couch
	  #18:00@@Tea time@@Drinking tea. As usual.@@Living room

	"""

	T.parseTimetable(data)